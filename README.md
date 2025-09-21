# WebCppCluster
本仓库为本人的学习类项目，欢迎各位交流学习

## 各部分的含义
webcppcluster2025/
├── app.py                    # 主Web应用入口
├── service.py                # 服务间通信工具
├── Config.py                 # 配置管理
├── Account.py                # 用户账户管理
├── Shop.py                   # 商店系统
├── Task.py                   # 任务系统
├── Lobby.py                  # 大厅/邮件系统
├── Error.py                  # 错误处理
├── DBManage.py               # 数据库管理
├── RedisStore.py             # Redis会话存储
├── MailServer/               # C++邮件服务器
│   ├── mail_server.cpp       # 邮件服务器主程序
│   ├── protorpc.c            # protobuf RPC实现
│   ├── protorpc.h            # protobuf RPC头文件
│   ├── generated/            # 生成的protobuf文件
│   ├── include/              # 头文件目录
│   └── 编译命令               # 编译脚本
├── proto/                    # Python protobuf文件
│   ├── general.proto         # 通用消息定义
│   ├── general_pb2.py        # 生成的Python文件
│   └── proto.sh              # protobuf生成脚本
├── log/                      # 日志目录
├── uwsgi.ini                 # uWSGI配置
├── logging.conf              # 日志配置
