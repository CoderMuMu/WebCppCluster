import ActionCfg
import Config
from proto.message_pb2 import Message

def SendAction(userid, msgid, action, protoinfo):
    strKey = ActionCfg.KEY_ACTION_LIST
    msg = Message()
    msg.userid = userid
    msg.msgid = msgid
    msg.actiontype = action
    msg.string = protoinfo
    Config.grds.rpush(strKey, msg.SerializeToString())