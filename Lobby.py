import Config
import ShopCfg
import Error
import pymysql
import pymysql.cursors
import datetime
import Account
from proto.general_pb2 import Mail
import json
import base64
import service

# 保证缓存存在
@Error.DBCatchError
def GetMoney(userid, cursor:pymysql.cursors.DictCursor = None):
    strKey = Config.KEY_PACKAGE.format(userid=userid)
    money = 0
    if Config.grds.exists(strKey):
        money = int(Config.grds.hget(strKey, ShopCfg.ID_MONEY))
    else:
        sqlStr = "select propnum from package where userid = %s and propid = %s"
        cursor.execute(sqlStr, (userid, ShopCfg.ID_MONEY))
        res = cursor.fetchone()
        money = int(res['propnum'])
        now = datetime.datetime.now()
        Account.InitPackage(userid, now)
    return money

def GetMonday(today):
    today = datetime.datetime.strptime(str(today), "%Y-%m-%d")
    return datetime.datetime.strftime(today - datetime.timedelta(today.weekday()), "%Y_%m_%d")

def SendMail(mailinfo):
    # 校验
    # 组合数据到proto中
    # 发送给C++邮件服务器
    mailproto = Mail()
    for userid in mailinfo['useridlist']:
        mailproto.userid.append(int(userid))
    
    # 确保字符串是UTF-8编码
    mailproto.title = mailinfo['title'].encode('utf-8').decode('utf-8')
    mailproto.context = mailinfo['context'].encode('utf-8').decode('utf-8')
    mailproto.type = int(mailinfo['type'])
    attach = {}
    for propid, propnum in mailinfo['attach'].items():
        if int(propid) not in ShopCfg.SHOP_LIST:
            continue
        attach[int(propid)] = int(propnum)
    mailproto.attach = json.dumps(attach, ensure_ascii=False)  # 确保JSON不转义Unicode字符
    mailproto.buttontext = mailinfo['buttontext'].encode('utf-8').decode('utf-8')
    mailproto.fromuserid = int(mailinfo['fromuserid'])

    # 发送给C++邮件服务器
    service.SendSvrd(Config.MAIL_HOST, Config.MAIL_PORT, mailproto.SerializeToString())

def GetMailList(userid):
    # GetGlobalMail()
    strKeyList = Config.KEY_MAIL_LIST.format(userid = userid)
    mailidlist = Config.grds.lrange(strKeyList, 0, -1)
    mailinfolist = []
    for mailid in mailidlist:
        strKey = Config.KEY_MAIL_DETAIL.format(mailid = mailid)
        res = Config.grds.hgetall(strKey)
        
        # 这里获取邮件信息，有两种方法：
        # 1. 直接获取Redis的hgetall
        # 2.先获取部分信息，例如邮件的标题，是否已读，是否领取附件奖励
        # 然后新增一个maildetaillist的接口，当用户点进来的时候调用这个接口，获取剩余信息
        # 第二种方法的好处就是减少这里GetMailList的压力。
        # 具体实现可以在GetMailList中hmget必要的字段，然后GetMailDetailList中获取剩余信息
        # 然后返回给前端
        
        
        if not res:
            Config.grds.lrem(strKeyList, 1, mailid)
            continue
        
        # 确保从Redis读取的数据正确处理编码
        mailinfo = {}
        for key, value in res.items():
            if isinstance(value, bytes):
                mailinfo[key] = value.decode('utf-8')
            else:
                mailinfo[key] = value
        
        mailinfolist.append(mailinfo)
    return mailinfolist