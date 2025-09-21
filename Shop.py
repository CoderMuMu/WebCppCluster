from telnetlib import STATUS
import ShopCfg
import ErrorCfg
import math
import Lobby
import Config
import DBManage
import datetime
import Error

def GetShopCfg(version):
    shoplist = []
    shop = ShopCfg.SHOP_LIST
    # 遍历商店列表，获取商品id对应的配置
    for id in shop:
        if id not in ShopCfg.SHOP_CFG:
           continue
        cfg = ShopCfg.SHOP_CFG[id]
        if version < cfg['version']:
            continue
        propdict = {
            'pid': cfg['pid'], 'ename': cfg['ename'], 'name': cfg['name'],
            'type': cfg['type'], 'pay':cfg['pay'], 'money': cfg['money'], 'coin': cfg['coin'], 'rmb':cfg['rmb'],
            'paytype': cfg['paytype'], 'iconid': cfg['iconid'], 'version': cfg['version'],
            'discount': cfg['discount'], 'inventory': cfg['inventory'], 'buylimittype': cfg['buylimittype'],
            'buylimitnum': cfg['buylimitnum'], 'proplist': cfg['proplist'], 'initnum':cfg['initnum']
        }
        shoplist.append(propdict)
    return {'shoplist': shoplist, 'shopversion': ShopCfg.SHOP_VERSION}

# 初始化库存
def InitInventory():
    for id in ShopCfg.SHOP_INIT_LIST:
        if id not in ShopCfg.SHOP_CFG:
            continue
        cfg = ShopCfg.SHOP_CFG[id]
        if cfg['inventory'] != ShopCfg.NO_INVENTORY:
            inventoryKey = Config.KEY_SHOP_INVENTORY.format(propid = id)
            Config.grds.hset(inventoryKey,'inventory',cfg['inventory'])
        
# 检查库存
def GetInventory(propid):
    cfg = ShopCfg.SHOP_CFG[propid]
    if cfg['inventory'] == ShopCfg.NO_INVENTORY:
        return cfg['inventory']
    inventoryKey = Config.KEY_SHOP_INVENTORY.format(propid=propid)
    
    if Config.grds.exists(inventoryKey):
        inventory = Config.grds.hget(inventoryKey,'inventory')
        return int(inventory)
    else:
        # 懒加载初始化库存
        Config.grds.hset(inventoryKey,'inventory',cfg['inventory'])
        return cfg['inventory']
   
# 减少库存
def ReduceInventory(propid,propnum):    
    cfg = ShopCfg.SHOP_CFG[propid]
    if cfg['inventory'] == ShopCfg.NO_INVENTORY:
        return
    inventoryKey = Config.KEY_SHOP_INVENTORY.format(propid=propid)
    remain = Config.grds.hincrby(inventoryKey,'inventory',-propnum)
    return remain
    
# 发货
def PresentProp(userid, propid, propnum, now):
    strKey = Config.KEY_PACKAGE.format(userid=userid)
    proplist = ShopCfg.SHOP_CFG[propid]['proplist']
    propdict = {}
    dbproplist = []
    for prop in proplist:
        num = Config.grds.hincrby(strKey, prop['pid'], prop['num'] * propnum)
        propdict[prop['pid']] = num
        dbproplist.append((num, now, userid, prop['pid']))
    propdict['freshtime'] = str(now)
    # freshtime 用来判断道具包数据最后一次被修改的时间
    Config.grds.hset(strKey, mapping=propdict)
    DBManage.DBUpdatePackageInfo(dbproplist)
    
# 获取所有商品库存状态,作为商品的监控，检测商品是否缺货
def GetPropInventoryStatus():
    status = {}
    for id in ShopCfg.SHOP_INIT_LIST:
        if id not in ShopCfg.SHOP_CFG:
            continue
        else:
            status[id] = GetInventory(id)
    return status      
    
def ShopBuy(userid, propid, propnum, shopversion, version, paytype):
    
    # 检查商城版本号
    if shopversion < ShopCfg.SHOP_VERSION:
        return {'code': ErrorCfg.EC_SHOP_VERSION_LOW, 'reason': ErrorCfg.ER_SHOP_VERSION_LOW}

    # 判断道具是否存在
    if not propid in ShopCfg.SHOP_CFG:
        return {'code': ErrorCfg.EC_SHOP_NOT_EXIST, 'reason': ErrorCfg.ER_SHOP_NOT_EXIST}

    # 获取道具配置，验证客户端版本是否支持该道具
    cfg = ShopCfg.SHOP_CFG[propid]
    if version < cfg['version']:
        return {'code': ErrorCfg.EC_SHOP_CLIENT_VERSION_LOW, 'reason': ErrorCfg.ER_SHOP_CLIENT_VERSION_LOW}

    # 判断库存逻辑
    inventory = cfg['inventory']
    if inventory != ShopCfg.NO_INVENTORY:
        currentInventory = GetInventory(propid)
        if currentInventory < propnum:
            return {'code': ErrorCfg.EC_SHOP_INVENTORY_NOT_ENONGH,'reason': ErrorCfg.ER_SHOP_INVENTORY_NOT_ENONGH}
        
    # 计算实际所需要的金额
    if paytype not in cfg['paytype']:
        return {'code': ErrorCfg.EC_SHOP_PAYTYPE_ERROR, 'reason': ErrorCfg.ER_SHOP_PAYTYPE_ERROR}
    
    needmoney = int(math.floor(cfg['pay'][paytype] * cfg['discount'] * propnum))
    #向下取整，可以避免小数价格，有利于玩家的购买体验

    # 判断余额是否充足 
    money = Lobby.GetMoney(userid)
    if money < needmoney:
        return {'code':ErrorCfg.EC_SHOP_MONEY_NOT_ENONGH, 'reason':ErrorCfg.ER_SHOP_MONEY_NOT_ENONGH}

    # 扣款
    strKey = Config.KEY_PACKAGE.format(userid=userid)
    money = Config.grds.hincrby(strKey, ShopCfg.ID_MONEY, -needmoney)
    if money < 0:
        Config.grds.hincrby(strKey, ShopCfg.ID_MONEY, needmoney)
        return {'code':ErrorCfg.EC_SHOP_MONEY_NOT_ENONGH, 'reason':ErrorCfg.ER_SHOP_MONEY_NOT_ENONGH}

    now = datetime.datetime.now()
    dbproplist = [(money, now, userid, ShopCfg.ID_MONEY)]
    DBManage.DBUpdatePackageInfo(dbproplist)
    # DBManage.DBUpdatePackageInfoByField(userid, ShopCfg.ID_MONEY, money, now)
    Config.grds.hset(strKey, 'freshtime', str(now))

    # 发货
    PresentProp(userid, propid, propnum, now)
    '''
    发货后再减少库存，防止发货后没有库存，导致库存数量错误
    '''
    # 减少库存
    ReduceInventory(propid,propnum)
    return {'code': 0, 'money': money}

# sudo apt install redis-server

# redis-server