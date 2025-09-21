"""
    pid 道具id
    name 道具名称
    ename 道具名称（英文）
    type 类型（按次数消耗、按时间消耗）
    money 消耗游戏豆 1000
    coin 金币
    paytype 支付类型
    iconid 客户端展示图标的id
    version 版本
    discount 折扣
    des 描述
    inventory 库存
    buylimittype 限购类型（日、周、月、年）
    buylimitnum 限购数量
    proplist 道具列表
    initnum 初始道具数量
"""

"""
双倍经验卡：[{pid:1 pnum:1}]
改名卡：[{pid:2 pnum:1}]
大礼包1：[{pid:1,pnum:2},{pid:2,pnum:2}]
"""

# 商城版本 1.0.0
SHOP_VERSION = 1000000

# 限购类型
BUYLIMITTYPE_INVALID = 0
BUYLIMITTYPE_DAY = 1
BUYLIMITTYPE_WEEK = 2
BUYLIMITTYPE_MONTH = 3
BUYLIMITTYPE_YEAR = 4

# 道具id
ID_MONEY = 1000  # 游戏豆
ID_COIN = 1001  # 金币
ID_EXPCARD = 1010  # 双倍经验卡
ID_RENAMECARD = 1003  # 改名卡
ID_GAMECLEARCARD = 1004 # 战绩清零卡
ID_YEARVIP = 1005  # 年会员
ID_MONTHVIP = 1006  # 月会员
ID_YEARVIP_PACKAGE = 1007  # 年会员大礼包
ID_MONTHVIP_PACKAGE = 1008  # 月会员大礼包

# 道具类型 1：消耗型 2：时间型
TYPE_USE = 1
TYPE_TIME = 2

# 支付类型
TYPE_PAY_MONEY = 1
TYPE_PAY_COIN = 2
TYPE_PAY_RMB = 3

# 无库存限制
NO_INVENTORY = -1

SHOP_LIST = [
    ID_MONEY,
    ID_COIN,
    ID_EXPCARD,
    ID_RENAMECARD,
    ID_GAMECLEARCARD,
    ID_YEARVIP_PACKAGE,
    ID_MONTHVIP_PACKAGE,
]

SHOP_INIT_LIST = [
    ID_MONEY,
    ID_COIN,
    ID_EXPCARD,
    ID_RENAMECARD,
    ID_GAMECLEARCARD,
    ID_YEARVIP_PACKAGE,
    ID_MONTHVIP_PACKAGE,
]

SHOP_CFG = {
    ID_MONEY:{"pid":ID_MONEY, "ename":"money", "name":"游戏豆", "type": TYPE_USE, "pay":{TYPE_PAY_MONEY: -1, TYPE_PAY_COIN:1, TYPE_PAY_RMB:1},"money": -1, "coin": 1, "rmb":1, "paytype":[TYPE_PAY_COIN,TYPE_PAY_RMB], "iconid":1000, "version":10000, "discount":1, "inventory":NO_INVENTORY, "buylimittype":BUYLIMITTYPE_INVALID, "buylimitnum": -1, "proplist":[{"pid":ID_MONEY, "num":1}], "initnum":10000},
    ID_COIN:{"pid":ID_COIN, "ename":"coin", "name":"金币", "type": TYPE_USE, "pay":{TYPE_PAY_MONEY: -1, TYPE_PAY_COIN:-1, TYPE_PAY_RMB:1}, "money": -1, "coin": -1, "rmb":1, "paytype":[TYPE_PAY_RMB], "iconid":1001, "version":10000, "discount":1, "inventory":NO_INVENTORY, "buylimittype":BUYLIMITTYPE_INVALID, "buylimitnum": -1, "proplist":[{"pid":ID_COIN, "num":1}], "initnum":10},
    ID_EXPCARD:{"pid":ID_EXPCARD, "ename":"expcard", "name":"双倍经验卡", "type": TYPE_TIME, "pay":{TYPE_PAY_MONEY: 100, TYPE_PAY_COIN:-1, TYPE_PAY_RMB:-1}, "money": 100, "coin": -1, "rmb":-1, "paytype":[TYPE_PAY_MONEY], "iconid":1002, "version":10000, "discount":1, "inventory":100, "buylimittype":BUYLIMITTYPE_INVALID, "buylimitnum": -1, "proplist":[{"pid":ID_EXPCARD, "num":1}], "initnum":0},
    ID_RENAMECARD:{"pid":ID_RENAMECARD, "ename":"renamecard", "name":"改名卡", "type": TYPE_USE, "pay":{TYPE_PAY_MONEY: 1000, TYPE_PAY_COIN:-1, TYPE_PAY_RMB:-1}, "money": 1000, "coin": -1, "rmb":-1, "paytype":[TYPE_PAY_MONEY], "iconid":1003, "version":10000, "discount":1, "inventory":NO_INVENTORY, "buylimittype":BUYLIMITTYPE_INVALID, "buylimitnum": -1, "proplist":[{"pid":ID_RENAMECARD, "num":1}], "initnum":0},
    ID_GAMECLEARCARD:{"pid":ID_GAMECLEARCARD, "ename":"gameclearcard", "name":"战绩清零卡", "type": TYPE_USE, "pay":{TYPE_PAY_MONEY: 1000, TYPE_PAY_COIN:-1, TYPE_PAY_RMB:-1}, "money": 1000, "coin": -1, "rmb":-1, "paytype":[TYPE_PAY_MONEY], "iconid":1004, "version":10000, "discount":1, "inventory":NO_INVENTORY, "buylimittype":BUYLIMITTYPE_INVALID, "buylimitnum": -1, "proplist":[{"pid":ID_GAMECLEARCARD, "num":1}], "initnum":0},
    ID_YEARVIP_PACKAGE:{"pid":ID_YEARVIP_PACKAGE, "ename":"yearvip", "name":"年会员大礼包", "type": TYPE_USE,"pay":{TYPE_PAY_MONEY: 1000, TYPE_PAY_COIN:-1, TYPE_PAY_RMB:-1}, "money": 10000, "coin": -1, "rmb":-1, "paytype":[TYPE_PAY_MONEY], "iconid":1005, "version":10000, "discount":1, "inventory":NO_INVENTORY, "buylimittype":BUYLIMITTYPE_INVALID, "buylimitnum": -1, "proplist":[{"pid":ID_EXPCARD, "num":30},{"pid":ID_RENAMECARD, "num":30},{"pid":ID_YEARVIP, "num":1}], "initnum":0},
    ID_MONTHVIP_PACKAGE:{"pid":ID_MONTHVIP_PACKAGE, "ename":"monthvip", "name":"月会员大礼包", "type": TYPE_USE,"pay":{TYPE_PAY_MONEY: 1000, TYPE_PAY_COIN:-1, TYPE_PAY_RMB:-1}, "money": 1000, "coin": -1, "rmb":-1, "paytype":[TYPE_PAY_MONEY], "iconid":1006, "version":10000, "discount":1, "inventory":NO_INVENTORY, "buylimittype":BUYLIMITTYPE_INVALID, "buylimitnum": -1, "proplist":[{"pid":ID_EXPCARD, "num":2},{"pid":ID_RENAMECARD, "num":2},{"pid":ID_MONTHVIP, "num":1}], "initnum":0},
}