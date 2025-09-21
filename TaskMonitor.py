from proto.message_pb2 import Message
from proto.general_pb2 import Sign
import MessageCfg
import Config
import ActionCfg
import TaskCfg
import Task
import datetime

def TaskMonitor():
    while True:
        res = Config.grds.blpop(ActionCfg.KEY_ACTION_TASK_LIST)[1]
        msg = Message()
        msg.ParseFromString(res)
        msgid = int(msg.msgid) & MessageCfg.MSGID
        actiontype = int(msg.actiontype)
        if msgid == MessageCfg.MSGID_SIGN:
            signinfo = Sign()
            signinfo.ParseFromString(msg.string)
            userid = int(signinfo.userid)
            date = signinfo.date
            for id in TaskCfg.TASK_LIST:
                if not id in TaskCfg.TASK_CFG:
                    continue
                cfg = TaskCfg.TASK_CFG[id]
                date = Task.GetTaskDatestr(cfg['type'], datetime.datetime.strptime(date, "%Y_%m_%d"))
                strKey = TaskCfg.KEY_TASK.format(userid = userid, date = date)
                print(signinfo)
                if not Config.grds.exists(strKey):
                    Task.InitTaskCfg(userid, date)
                if cfg['action'] == actiontype:
                    countfield = 'count_' + str(id)
                    totalfield = 'total_' + str(id)
                    statefield = 'state_' + str(id)
                    count = Config.grds.hincrby(strKey, countfield, 1)
                    result = Config.grds.hmget(strKey, statefield, totalfield)
                    state = int(result[0])
                    total = int(result[1])
                    if count >= total and state == TaskCfg.STATE_NOT_FINISH:
                        Config.grds.hset(strKey, statefield, TaskCfg.STATE_FINISH)
                        # 通知客户端
                        # 存储日志
                        # 写数据库，任务完成未领奖

if __name__ == "__main__":
    TaskMonitor()