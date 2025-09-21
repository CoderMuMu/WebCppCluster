/*
 * mail server
 *
 * @server  mail_server 1234
 *
 */

#include "TcpServer.h"
#include <iostream>
#include <string>
#include <pthread.h>

#include <hiredis/hiredis.h>
#include <hiredis/async.h>
#include <adapters/libhv.h>

using namespace hv;

#include "protorpc.h"
// #include "router.h"
// #include "handler/handler.h"
// #include "handler/calc.h"
// #include "handler/login.h"
// #include "include/hv/generated/general.pb.h"
#include "generated/proto/general.pb.h"
#include "time.h"


// valgrind --leak-check=full --show-leak-kinds=all
class ProtobufRAII {
public:
    ProtobufRAII() {
    }
    ~ProtobufRAII() {
        // 自动清理protobuf库
        google::protobuf::ShutdownProtobufLibrary();
    }
};

// 记录已完成命令的数量
int completed_commands = 0;
// 总命令数量
int total_commands = 0;
// 互斥锁
pthread_mutex_t mutex;

// redis 回调函数
void commandCallback(redisAsyncContext *c, void *r, void *privdata);
void getCallback(redisAsyncContext *c, void *r, void *privdata);
void debugCallback(redisAsyncContext *c, void *r, void *privdata);
void connectCallback(const redisAsyncContext *c, int status);
void disconnectCallback(const redisAsyncContext *c, int status);

void send_mail(redisAsyncContext *c, Mail mail)
{
    std::vector<long long> useridlist;
    for (int i = 0; i < mail.userid_size(); i++)
    {
        // 全服邮件
        // std::cout << "userid" << i << ": " << mail.userid(i) << std::endl;
        useridlist.push_back(mail.userid(i));
    }
    
    // 解析 mail proto 对象的字段
    // 移除 base64 解码，直接使用原始数据
    std::string title = mail.title();
    std::string type = std::to_string(mail.type());
    std::string context = mail.context();
    std::string attach = mail.attach();
    std::string buttontext = mail.buttontext();
    std::string fromuserid = std::to_string(mail.fromuserid());
    std::string getattach = std::to_string(0);
    std::string hasattach = std::to_string(1);
    std::string empty_attach = "{}";
    if(attach == empty_attach)
    {
        hasattach = std::to_string(0);
    }

    std::string userid;
    std::string mailid;
    std::string listKey;

    const char *mail_title = title.c_str();
    const char *mail_type = type.c_str();
    const char *mail_context = context.c_str();
    const char *mail_attach = attach.c_str();
    const char *mail_buttontext = buttontext.c_str();
    const char *mail_fromuserid = fromuserid.c_str();
    const char *mail_getattach = getattach.c_str();
    const char *mail_hasattach = hasattach.c_str();
    
    // 获取字符串的字节长度（用于UTF-8编码）
    size_t title_len = title.length();
    size_t type_len = type.length();
    size_t context_len = context.length();
    size_t attach_len = attach.length();
    size_t buttontext_len = buttontext.length();
    size_t fromuserid_len = fromuserid.length();
    size_t getattach_len = getattach.length();
    size_t hasattach_len = hasattach.length();

    for (int i = 0; i < mail.userid_size(); i++)
    {
        userid = std::to_string(mail.userid(i));
        mailid = userid + '_' + std::to_string(time(NULL));

        std::string KEY_MAIL_LIST = "KEY_MAIL_LIST_" + userid;
        size_t argvlen[18];
        const char *argv[18];
        argv[0] = "RPUSH";
        argvlen[0] = strlen("RPUSH");
        argv[1] = KEY_MAIL_LIST.c_str();
        argvlen[1] = strlen(KEY_MAIL_LIST.c_str());
        argv[2] = mailid.c_str();
        argvlen[2] = strlen(mailid.c_str());

        // 执行命令
        redisAsyncCommandArgv(c, commandCallback, NULL, 3, argv, argvlen);
        total_commands++;

        // redisReply *reply;
        memset(argvlen, 0, sizeof(argvlen));
        memset(argv, 0, sizeof(argv));

        std::string KEY_MAILDETAIL = "KEY_MAIL_DETAIL_" + mailid;
        argv[0] = "HMSET";
        argvlen[0] = strlen("HMSET");
        argv[1] = KEY_MAILDETAIL.c_str();
        argvlen[1] = strlen(KEY_MAILDETAIL.c_str());
        argv[2] = "title";
        argvlen[2] = strlen("title");
        argv[3] = mail_title;
        argvlen[3] = title_len;
        argv[4] = "context";
        argvlen[4] = strlen("context");
        argv[5] = mail_context;
        argvlen[5] = context_len;
        argv[6] = "type";
        argvlen[6] = strlen("type");
        argv[7] = mail_type;
        argvlen[7] = type_len;
        argv[8] = "attach";
        argvlen[8] = strlen("attach");
        argv[9] = mail_attach;
        argvlen[9] = attach_len;
        argv[10] = "buttontext";
        argvlen[10] = strlen("buttontext");
        argv[11] = mail_buttontext;
        argvlen[11] = buttontext_len;
        argv[12] = "fromuserid";
        argvlen[12] = strlen("fromuserid");
        argv[13] = mail_fromuserid;
        argvlen[13] = fromuserid_len;
        argv[14] = "getattach";
        argvlen[14] = strlen("getattach");
        argv[15] = mail_getattach;
        argvlen[15] = getattach_len;
        argv[16] = "hasattach";
        argvlen[16] = strlen("hasattach");
        argv[17] = mail_hasattach;
        argvlen[17] = hasattach_len;
        
        // 执行命令
        redisAsyncCommandArgv(c, commandCallback, NULL, 18, argv, argvlen);
        total_commands++;
    }
}

void handle_mail(Mail mail) {
    #ifndef _WIN32
        signal(SIGPIPE, SIG_IGN);
    #endif

    // 初始化互斥锁
    pthread_mutex_init(&mutex, NULL);

    //创建redis异步连接
    redisAsyncContext *c = redisAsyncConnect("127.0.0.1", 6379);

  
    if (c == NULL || c->err) {
        if (c) {
            printf("Error: %s\n", c->errstr);
            // handle error
            return;
        } else {
            printf("Can't allocate redis context\n");
            return;
        }
    }

    hloop_t* loop = hloop_new(HLOOP_FLAG_QUIT_WHEN_NO_ACTIVE_EVENTS);
    redisLibhvAttach(c, loop);

    //为Redis连接设置了超时时间
    //redisAsyncSetTimeout(c, (struct timeval){.tv_sec = 0, .tv_usec = 10000});
    // 异步超时设置（需确保 hiredis 版本支持）
    struct timeval tv = {.tv_sec = 0, .tv_usec = 10000};
    // 使用异步上下文的超时字段（不同版本可能有差异）
    c->c.timeout = &tv;  // 通过异步上下文的内部同步上下文设置超时

    redisAsyncSetConnectCallback(c,connectCallback);

    redisAsyncSetDisconnectCallback(c,disconnectCallback);

    //认证
    redisAsyncCommand(c, NULL, NULL, "auth %s", "123456");

    // redisAsyncCommand(c, getCallback, (char*)"end-1", "GET key");
    // total_commands = mail.userid_size() * 2;
    send_mail(c, mail);

    hloop_run(loop);
    hloop_free(&loop);

    // 销毁互斥锁
    pthread_mutex_destroy(&mutex);
}

class ProtoRpcServer : public TcpServer {
public:
    ProtoRpcServer() : TcpServer()
    {
        onConnection = [](const SocketChannelPtr& channel) {
            std::string peeraddr = channel->peeraddr();
            if (channel->isConnected()) {
                printf("%s connected! connfd=%d\n", peeraddr.c_str(), channel->fd());
            } else {
                printf("%s disconnected! connfd=%d\n", peeraddr.c_str(), channel->fd());
            }
        };
        onMessage = handleMessage;
        // init protorpc_unpack_setting
        unpack_setting_t protorpc_unpack_setting;
        memset(&protorpc_unpack_setting, 0, sizeof(unpack_setting_t));
        protorpc_unpack_setting.mode = UNPACK_BY_LENGTH_FIELD;
        protorpc_unpack_setting.package_max_length = DEFAULT_PACKAGE_MAX_LENGTH;
        protorpc_unpack_setting.body_offset = PROTORPC_HEAD_LENGTH;
        protorpc_unpack_setting.length_field_offset = PROTORPC_HEAD_LENGTH_FIELD_OFFSET;
        protorpc_unpack_setting.length_field_bytes = PROTORPC_HEAD_LENGTH_FIELD_BYTES;
        protorpc_unpack_setting.length_field_coding = ENCODE_BY_BIG_ENDIAN;
        setUnpack(&protorpc_unpack_setting);
    }

    int listen(int port) { return createsocket(port); }

private:
    static void handleMessage(const SocketChannelPtr& channel, Buffer* buf) {
        protorpc_message msg;
        printf("%s", (char*)buf->data());
        printf("%ld", buf->size());
        memset(&msg, 0, sizeof(msg));
        int packlen = protorpc_unpack(&msg, buf->data(), buf->size());
        if (packlen < 0) {
            printf("protorpc_unpack failed!\n");
            return;
        }
        // 断言判断 packlen 是否等于 buf->size()，解包后的消息长度和接收的消息长度是否一致
        assert(packlen == buf->size());
        if (protorpc_head_check(&msg.head) != 0) {
            printf("protorpc_head_check failed!\n");
            return;
        }

        Mail mail;
        printf("head.length = %d", msg.head.length);
        if(mail.ParseFromArray(msg.body, msg.head.length))
        {
            handle_mail(mail);
        }
    }
};

void commandCallback(redisAsyncContext *c, void *r, void *privdata) {
    pthread_mutex_lock(&mutex);
    completed_commands++;
    redisReply *reply = (redisReply*)r;
    std::cout<<completed_commands << " " << total_commands << std::endl;
    if (completed_commands == total_commands) {
        std::cout<< " ======= " << completed_commands << " " << total_commands << std::endl;
        redisAsyncDisconnect(c);
    }else if (reply->type == REDIS_REPLY_ERROR) {
        std::cerr << "Redis command error: " << reply->str << std::endl;
    }

    pthread_mutex_unlock(&mutex);
}

void getCallback(redisAsyncContext *c, void *r, void *privdata) {
    redisReply *reply = (redisReply*)r;
    if (reply == NULL) return;
    //printf("argv[%s]: %s\n", (char*)privdata, reply->str);

    /* Disconnect after receiving the reply to GET */
    redisAsyncDisconnect(c);
}

void debugCallback(redisAsyncContext *c, void *r, void *privdata) {
    (void)privdata;
    redisReply *reply = (redisReply*)r;

    if (reply == NULL) {
        printf("`DEBUG SLEEP` error: %s\n", c->errstr ? c->errstr : "unknown error");
        return;
    }

    redisAsyncDisconnect(c);
}

void connectCallback(const redisAsyncContext *c, int status) {
    if (status != REDIS_OK) {
        printf("Error: %s\n", c->errstr);
        return;
    }
    printf("Connected...\n");
}

void disconnectCallback(const redisAsyncContext *c, int status) {
    if (status != REDIS_OK) {
        printf("Error: %s\n", c->errstr);
        return;
    }
    printf("Disconnected...\n");
}

int main(int argc, char** argv) {
    if (argc < 2) {
        printf("Usage: %s port\n", argv[0]);
        return -10;
    }
    int port = atoi(argv[1]);

    ProtoRpcServer srv;
    int listenfd = srv.listen(port);
    if (listenfd < 0) {
        return -20;
    }
    printf("protorpc_server listen on port %d, listenfd=%d ...\n", port, listenfd);
    srv.setThreadNum(4);
    srv.start();
    
    while (1) hv_sleep(1);
    return 0;
}
