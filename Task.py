import TaskCfg
import datetime
import Config
import json
import Lobby
from proto.general_pb2 import *
import Action
import MessageCfg
import ActionCfg

def InitTaskCfg(userid, datestr):
    strKey = TaskCfg.KEY_TASK.format(userid = userid, date = datestr)
    taskinfo = {}
    for id in TaskCfg.TASK_LIST:
        if id not in TaskCfg.TASK_CFG:
            continue
        cfg = TaskCfg.TASK_CFG[id]
        taskinfo['count_' + str(id)] = 0
        taskinfo['total_' + str(id)] = cfg['total']
        taskinfo['state_' + str(id)] = TaskCfg.STATE_NOT_FINISH
        taskinfo['reward_' + str(id)] = json.dumps(cfg['rewardlist'])
    Config.grds.hset(strKey, mapping=taskinfo)
    Config.grds.expire(strKey, 7*24*60*60)

def GetTaskDatestr(type, today):
    datestr = today.strftime("%Y_%m_%d")
    if type == TaskCfg.TYPE_WEEK:
        datestr = Lobby.GetMonday(today)
    elif type == TaskCfg.TYPE_MONTH:
        datestr = datetime.datetime(today.year, today.month, 1).strftime("%Y_%m_%d")  
    elif type == TaskCfg.TYPE_YEAR:
        datestr = datetime.datetime(today.year, 1, 1).strftime("%Y_%m_%d")  
    return datestr

def GetTaskCfg(userid, version):
    task = TaskCfg.TASK_LIST
    tasklist = []
    now = datetime.date.today()
    datestr = now.strftime("%Y_%m_%d")
    strKey = TaskCfg.KEY_TASK.format(userid = userid, date = datestr)
    if not Config.grds.exists(strKey):
        InitTaskCfg(userid, datestr)
    for id in task:
        if id not in TaskCfg.TASK_CFG:
            continue
        cfg = TaskCfg.TASK_CFG[id]
        if version < cfg['version']:
            continue
        taskdict = {
            'tid':cfg['tid'], 'type':cfg['type'], 'iconid':cfg['iconid'],
            'series':cfg['series'], 'name':cfg['name'], 'desc':cfg['desc'],
            'total':cfg['total'], 'version':cfg['version'],'rewardlist':cfg['rewardlist'],
            'count': 0, 'state': TaskCfg.STATE_INVALID,
        }
        # 获取存放该任务缓存信息的日期
        datestr = GetTaskDatestr(cfg['type'], now)
        strKey = TaskCfg.KEY_TASK.format(userid = userid, date = datestr)
        if not Config.grds.exists(strKey):
            tasklist.append(taskdict)
            continue
        countfield = 'count_' + str(id)
        statefield = 'state_' + str(id)
        rewardfield = 'reward_' + str(id)
        taskinfo = Config.grds.hmget(strKey, countfield, statefield, rewardfield)
        taskdict['count'] = taskinfo[0].decode() if taskinfo[0] else 0
        taskdict['state'] = taskinfo[1].decode() if taskinfo[1] else TaskCfg.STATE_INVALID
        taskdict['rewardlist'] = json.loads(taskinfo[2].decode()) if taskinfo[2] else []
        tasklist.append(taskdict)
    return tasklist

def UserSign(userid, signtype, date):
    # 判断签到类型
    if signtype == TaskCfg.SIGN_TYPE_TODAY:
        date = datetime.datetime.today()
    else:
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    
    # 根据日期设置签到key
    day = date.day
    month_first = datetime.datetime(date.year, date.month, 1)
    date = date.strftime("%Y_%m_%d")
    month_first = month_first.strftime("%Y_%m_%d")
    strKey = TaskCfg.KEY_SIGN.format(userid = userid, date = month_first)

    # 签到 
    # 使用位图存储签到数据 setbit用于操作字符串的位 day为偏移位 1为将该位置为1
    Config.grds.setbit(strKey, day, 1)

    # 签到proto
    signproto = Sign()
    signproto.userid = int(userid)
    signproto.signtype = int(signtype)
    signproto.date = date

    # 发送签到事件，后续任务等脚本需要读取该事件，从而进行任务进度的增加
    Action.SendAction(userid, MessageCfg.MSGID_SIGN, ActionCfg.ACTION_SIGN, signproto.SerializeToString())