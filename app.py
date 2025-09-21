import web
import Account
import json
import ErrorCfg
import Error
import Shop
import Task
from RedisStore import RedisStore
import Config
import Lobby

# 关闭调试模式以避免session问题
web.config.debug = False

urls = (
    '/', 'Hello',
    '/register', 'Register',
    '/login', 'Login',
    '/shop/cfg', 'Shopcfg',
    '/shop/buy', 'Shopbuy',
    '/task/cfg', 'Taskcfg',
    '/task/reward', 'Taskreward',
    '/sign', 'Sign',
    '/mail/send', 'Mailsend',
    '/mail/list', 'Maillist',
)


app = web.application(urls, globals())

# 初始化库存
Shop.InitInventory()

if web.config.get('_session') is None:
    # 使用RedisStore进行session存储
    session = web.session.Session(app, RedisStore(Config.grds, Config.SESSION_EXPIRETIME), initializer={'userid': None})
    # 使用数据库对session进行存储
    # DBStore创建需要两个参数，db对象和session的表名
    # session_store = web.session.DBStore(数据库连接，'sessions')
    web.config._session = session
    print(f"Session initialized with RedisStore, timeout: {Config.SESSION_EXPIRETIME}")
else:
    session = web.config._session



class Hello:
    def GET(self):
        return 'Hello, World!'

class Register:
    @Error.CatchError
    def POST(self):
        req = web.input(phonenum = '', password = '', nick = '', sex = '', idcard = '')
        phonenum = req['phonenum']
        password = req['password']
        nick = req['nick']
        sex = req['sex']
        idcard = req['idcard']

        # 检测手机号格式
        if not Account.CheckPhonenum(phonenum):
            return Error.ErrResult(ErrorCfg.EC_REGISTER_PHONENUM_TYPE_ERROR,ErrorCfg.ER_REGISTER_PHONENUM_TYPE_ERROR)

        # 检测密码格式
        if not Account.CheckPassword(password):
            return Error.ErrResult(ErrorCfg.EC_REGISTER_PASSWORD_TYPE_ERROR,ErrorCfg.ER_REGISTER_PASSWORD_TYPE_ERROR)

        # 检测账号是否重复
        if not Account.CheckUserIdNotRepeat(phonenum):
            return Error.ErrResult(ErrorCfg.EC_REGISTER_USERID_REPEAT,ErrorCfg.ER_REGISTER_USERID_REPEAT)

        # 检测身份证号格式
        # if not Account.CheckIdCard(idcard):
        #     return Error.ErrResult(ErrorCfg.EC_REGISTER_IDCARD_TYPE_ERROR,ErrorCfg.ER_REGISTER_IDCARD_TYPE_ERROR)

        # 注册账号
        Account.InitUser(phonenum, password, nick, sex, idcard)

        return json.dumps({'code': ErrorCfg.EC_REQ_NOLMAL})
    

class Login:
    @Error.CatchError
    def POST(self):
        req = web.input(userid = '', password = '')
        userid = req['userid']
        password = req['password']
        res = Account.VerifyAccount(userid, password)
        if res['code'] != ErrorCfg.EC_REQ_NOLMAL:
            return Error.ErrResult(res['code'], res['reason'])
        
        res = Account.HandleLogin(userid, web.config._session)
        if res['code'] != ErrorCfg.EC_REQ_NOLMAL:
            return Error.ErrResult(res['code'], res['reason'])
        
        return json.dumps({'code': 0})

class Shopcfg:
    @Error.CatchError
    @Account.CheckLogin
    def GET(self):
        req = web.input(version = "")
        version = int(req['version'])
        shopcfg = Shop.GetShopCfg(version)
        return {'code': 0, 'shopcfg': shopcfg}

class Shopbuy:
    @Error.CatchError
    @Account.CheckLogin
    def POST(self):
        req = web.input(userid = '', propid = '', propnum = '', shopversion = '', version = '', paytype = '')
        userid = int(req['userid'])
        propid = int(req['propid'])
        propnum = int(req['propnum'])
        shopversion = int(req['shopversion'])
        version = int(req['version'])
        paytype = int(req['paytype'])
        dictInfo = Shop.ShopBuy(userid, propid, propnum, shopversion, version, paytype)
        return json.dumps(dictInfo)


class Taskcfg:
    @Error.CatchError
    @Account.CheckLogin
    def GET(self):
        req = web.input(userid = '', version = '')
        userid = req['userid']
        version = int(req['version'])
        taskcfg = Task.GetTaskCfg(userid, version)
        return json.dumps({'code': 0, 'taskcfg':taskcfg})
    
class Taskreward:
    @Error.CatchError
    @Account.CheckLogin
    def POST(self):
        req = web.input(userid = '', taskid = '')
        # 领取奖励
        return {'code':0}

class Sign:
    @Error.CatchError
    @Account.CheckLogin
    def POST(self):
        req = web.input(userid = '', signtype = '1', date = '')
        userid = int(req['userid'])
        signtype = int(req['signtype'])
        date = req['date']
        Task.UserSign(userid, signtype, date)
        return json.dumps({'code': 0})
application = app.wsgifunc()

class Mailsend:
    @Error.CatchError
    def POST(self):
        req = web.input(
            useridlist = '', title = '', context = '', type = '',
            attach = {}, isglobal = 0, fromuserid = 0, buttontext = '',
        )
        req['useridlist'] = req['useridlist'].split(',')
        req['attach'] = json.loads(req['attach'])
        Lobby.SendMail(req)
        return json.dumps({"code": 0})
    
class Maillist:
    @Error.CatchError
    @Account.CheckLogin
    def GET(self):
        req = web.input(userid = '')
        userid = int(req.userid)
        mailinfolist = Lobby.GetMailList(userid)
        return json.dumps({'code': 0, 'mailinfolist': mailinfolist})
    
if __name__ == "__main__":
    app.run()
