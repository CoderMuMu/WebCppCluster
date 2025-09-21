import Error
import pymysql.cursors
import Config

@Error.DBCatchError
def DBInsertRegisterUser(phonenum, password, nick, sex, idcard, now, cursor:pymysql.cursors.DictCursor = None):
    sqlStr = "insert into user(userid,password,secpassword,nick,phonenum,sex,idcard,status,createtime) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(sqlStr, (int(phonenum), password, Config.DEFAULT_SECPASSWORD, nick, phonenum, sex, idcard, Config.USER_STATUS_NOLMAL, now))

@Error.DBCatchError
def DBInitPackage(userid, packageInfoList, now, cursor:pymysql.cursors.DictCursor = None):
    sqlStr = "insert into package(userid, propid, propnum, proptype, freshtime) values(%s,%s,%s,%s,%s)"
    data = []
    for info in packageInfoList:
        data.append((userid, info['propid'], info['propnum'], info['proptype'], now))
    cursor.executemany(sqlStr, data)

@Error.DBCatchError
def DBGetPackageIdAndNum(userid, cursor:pymysql.cursors.DictCursor = None):
    sqlStr = "select propid, propnum from package where userid = %s"
    cursor.execute(sqlStr, (userid,))
    res = cursor.fetchall()
    return res

@Error.DBCatchError
def DBUpdatePackageInfoByField(userid, propid, propnum, now, cursor:pymysql.cursors.DictCursor = None):
    sqlStr = "update package set propnum = %s, freshtime = %s where userid = %s and propid = %s"
    cursor.execute(sqlStr, (propnum, now, userid, propid))

@Error.DBCatchError
def DBUpdatePackageInfo(data, cursor:pymysql.cursors.DictCursor = None):
    sqlStr = "update package set propnum = %s, freshtime = %s where userid = %s and propid = %s"
    cursor.executemany(sqlStr, data)