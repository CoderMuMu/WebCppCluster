import re
import AccountCfg
import pymysql
import pymysql.cursors
import Error
import ErrorCfg
import DBManage
import datetime
import ShopCfg
import Config
import web
import json

def CheckLogin(func):
    def wrapper(*args, **kwargs):
        session = web.config._session
        userid = session.get('userid')
        
        if userid:
            return func(*args, **kwargs)
        else:
            return Error.ErrResult(ErrorCfg.EC_LOGIN_INVALID, ErrorCfg.ER_LOGIN_INVALID)
    return wrapper

def CheckPhonenum(phonenum):
    phonelist = [139, 138, 137, 136, 134, 135, 147, 150, 151, 152, 157, 158, 159, 172, 178,
            130, 131, 132, 140, 145, 146, 155, 156, 166, 185, 186, 175, 176, 196,
            133, 149, 153, 177, 173, 180, 181, 189, 191, 193, 199,
            162, 165, 167, 170, 171]
    
    if len(phonenum) == 11 and str(phonenum).isdigit() and (int(phonenum[:3]) in phonelist):
        return True
    else:
        return False
    
    #2.使用正则表达式判断
    # pattern = re.compile('^(13[0-9]|14[0|5|6|7|9]|15[0|1|2|3|5|6|7|8|9]|16[2|5|6|7]|17[0|1|2|3|5|6|7|8]|18[0-9]|19[1|3|5|6|7|8|9])\d{8}$')
    # if re.match(pattern, phonenum):
    #     return True
    # else:
    #     return False

def CheckPassword(password):
    pattern = re.compile('^(?=.*[0-9])(?=.*[A-z])[0-9a-zA-Z]{8,16}$')
    if re.match(pattern, password):
        return True
    return False

@Error.DBCatchError
def CheckUserIdNotRepeat(userid, cursor:pymysql.cursors.DictCursor = None):
    sqlStr = "select count(*) as num from user where userid = %s"
    cursor.execute(sqlStr, (userid,))
    res = cursor.fetchone()
    if res and res['num'] == 1:
        return False
    return True

def CheckIdCard(idcard):
    stridcard = str(idcard)
    stridcard = stridcard.strip()
    idcard_list = list(stridcard)
    # 地区校验
    if (stridcard)[0:2] not in AccountCfg.AREAID:
        return False

    # 15位身份号码检测
    if len(stridcard) == 15:
        if ((int(stridcard[6:8]) + 1900) % 400 == 0 or (
                (int(stridcard[6:8]) + 1900) % 100 != 0 and (int(stridcard[6:8]) + 1900) % 4 == 0)):
            pattern = re.compile(
                '[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}$')  # //测试出生日期的合法性
        else:
            pattern = re.compile(
                '[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}$')  # //测试出生日期的合法性
        if re.match(pattern, stridcard):
            return True
        else:
            return False
    # 18位身份号码检测
    elif len(stridcard) == 18:
        # 出生日期的合法性检查
        # 闰年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))
        # 平年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))
        if (int(stridcard[6:10]) % 400 == 0 or (int(stridcard[6:10]) % 100 != 0 and int(stridcard[6:10]) % 4 == 0)):
            # 闰年出生日期的合法性正则表达式
            pattern = re.compile(
                '[1-9][0-9]{5}(18|19|20)[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}[0-9Xx]$')
        else:
            # 平年出生日期的合法性正则表达式
            pattern = re.compile(
                '[1-9][0-9]{5}(18|19|20)[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}[0-9Xx]$')
        # 测试出生日期的合法性
        if re.match(pattern, stridcard):
            # 计算校验位
            ten = ['X', 'x']
            ID = ["10" if x in ten else x for x in idcard_list]     #将字母X/x替换为10
            IDWeight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2] #国家统一标准
            Checkcode = [1, 0, 'X', 9, 8, 7, 6, 5, 4, 3, 2]
            sum = 0
            for i in range(17):
                sum += int(ID[i]) * IDWeight[i]
            if Checkcode[sum % 11] == int(ID[17]):
                return True
            else:
                return False
        else:
            return False
    else:
        return False

def InitPackage(userid, now):
    strKey = Config.KEY_PACKAGE.format(userid=userid)
    if not Config.grds.exists(strKey):
        res = DBManage.DBGetPackageIdAndNum(userid)
        if res:
            # 设置缓存
            packageInfo = {}
            for r in res:
                packageInfo[r['propid']] = r['propnum']
            Config.grds.hset(strKey, mapping=packageInfo)
        else:
            # 创建数据库信息，并设置缓存
            packageInfo = {}
            packageInfoList = []
            for id in ShopCfg.SHOP_INIT_LIST:
                if id not in ShopCfg.SHOP_CFG:
                    continue
                cfg = ShopCfg.SHOP_CFG[id]
                info = {
                    'propid':cfg['pid'],
                    'propnum':cfg['initnum'],
                    'proptype':cfg['type']
                }
                packageInfo[cfg['pid']] = cfg['initnum']
                packageInfoList.append(info)
            Config.grds.hset(strKey, mapping=packageInfo)
            DBManage.DBInitPackage(userid, packageInfoList, now)
    Config.grds.expire(strKey, Config.KEY_PACKAGE_EXPIRE_TIME)

def InitUser(phonenum, password, nick, sex, idcard):
    # 向数据库中添加一条用户信息
    now = datetime.datetime.now()
    DBManage.DBInsertRegisterUser(phonenum, password, nick, sex, idcard, now)
    # 初始化用户背包信息
    InitPackage(phonenum, now)

@Error.DBCatchError
def VerifyAccount(userid, password, cursor:pymysql.cursors.DictCursor = None):
    sqlStr = "select password from user where userid = %s"
    cursor.execute(sqlStr, (userid, ))
    res = cursor.fetchone()
    if not res:
        return {'code': ErrorCfg.EC_LOGIN_USERID_ERROR, 'reason':ErrorCfg.ER_LOGIN_USERID_ERROR}

    realpw = res['password']
    if realpw != password:
        return {'code': ErrorCfg.EC_LOGIN_PASSWORD_ERROR, 'reason':ErrorCfg.ER_LOGIN_PASSWORD_ERROR}
    
    return {'code': 0}

@Error.DBCatchError
def HandleLogin(userid, session, cursor:pymysql.cursors.DictCursor = None):
    now = datetime.datetime.now()
    
    # 设置登录缓存信息
    session['userid'] = userid

    strKey = AccountCfg.KEY_LOGIN.format(userid=userid)
    logininfo = {
        "userid":userid,
        "freshtime":str(now),
    }
    Config.grds.hset(strKey, mapping=logininfo)
    # 更新最后一次登录时间
    Config.grds.expire(strKey, AccountCfg.KEY_LOGIN_EXPIRE_TIME)

    sqlStr = "update user set lastlogintime = %s where userid = %s"
    cursor.execute(sqlStr, (now, userid))
    
    return {'code': 0}