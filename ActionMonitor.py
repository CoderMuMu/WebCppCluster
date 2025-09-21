import ActionCfg
import Config
from proto.message_pb2 import Message
import MessageCfg

def DistributeAction(actiontype, res):
    for strKey in ActionCfg.ACTION_MAPPING[actiontype]:
        print("actiontype:" + str(actiontype))
        print("rpush msg to: " + strKey)
        Config.grds.rpush(strKey, res)

def ActionMonitor():
    while True:
        # 循环阻塞弹出redis列表，模拟消息队列
        res = Config.grds.blpop(ActionCfg.KEY_ACTION_LIST)
        print("------------ start ---------------")
        print("res: ")
        print(res)
        res = res[1]
        msg = Message()
        msg.ParseFromString(res)
        msgid = int(msg.msgid) & MessageCfg.MSGID
        actiontype = int(msg.actiontype)
        print("msgid: " + str(msgid))
        if msgid == MessageCfg.MSGID_SIGN:
            DistributeAction(actiontype, res)
        elif msgid == MessageCfg.MSGID_LOGIN:
            DistributeAction(actiontype, res)

if __name__ == "__main__":
    ActionMonitor()