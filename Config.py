import web
import time
import pymysql
import pymysql.cursors
import redis
from dbutils.pooled_db import PooledDB
# from dbutils.pooled_db import PooledDB

# gdb = web.database(
#     dbn='mysql',
#     host='ip',
#     port='3306',
#     user='root',
#     pw='123456',
#     db='gamedb'
# )

# sudu apt-get install mysql-server 安装
# systemctl status mysql.service 测试
# python3 -V

"""
host 主机名
port 端口号
user 用户名
password 密码
charset 编码方式
database 数据库名
cursorclass 游标类型
connect_timeout 连接超时时间
autocommit 是否自动提交事务
"""

DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'lpl'
DB_PWD = '123'
DB_NAME = 'gamedb'

# dbconn = pymysql.connect(
#     host = DB_HOST,
#     port = DB_PORT,
#     user = DB_USER,
#     password = DB_PWD,
#     charset = 'utf8',
#     database = DB_NAME,
#     cursorclass = pymysql.cursors.DictCursor
# )

# 数据库连接池
pool = PooledDB(
    creator=pymysql,    # 数据库驱动，使用pymysql连接MySQL数据库
    maxconnections=10,  # 连接池中允许的最大连接数
    mincached=2,        # 初始化时创建的空闲连接数
    maxcached=5,         # 连接池中空闲连接的最大数量
    maxshared=3,        # 连接池中共享连接的最大数目
    blocking=True,      # 如果没有可用连接时，是否允许阻塞等待
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PWD,
    db=DB_NAME,
    cursorclass = pymysql.cursors.DictCursor
)

# conn:pymysql.Connection = pool.connection()

# cursor:pymysql.cursors.Cursor = conn.cursor()

# try:
#     cursor.execute("select * from user")
#     res = cursor.fetchall()
#     for r in res:
#         print(r)
# except:
#     pass
# finally:
#     cursor.close()  # 关闭游标
#     conn.close()  # 将连接归还数据库连接池

# 获取结果
# cursor.fetchall()  # 获取所有记录
# cursor.fetchone()  # 获取一个记录
# cursor.fetchmany(2)  # 获取指定个数记录
# userid = '13839365430'

# sql注入
# 解决sql注入问题：参数化查询
# sqlStr = "select * from user where userid = %s"
# cursor.execute(sqlStr, (userid,))

# cursor = dbconn.cursor()
# sqlStr = "select * from user"
# cursor.execute(sqlStr)
# res = cursor.fetchall()
# print(res)
# dbconn.commit()

# time.sleep(10)

# sqlStr = "select * from user"
# cursor.execute(sqlStr)
# res = cursor.fetchall()
# print(res)

# # 批量操作
# data = []
# for i in range(1,101):
#     data.append((i, '123456'))

# cursor = dbconn.cursor()

# start_time = time.time()

# # for d in data:
# #     sqlStr = "insert into test values(%s, %s)"
# #     cursor.execute(sqlStr, d)
# sqlStr = "insert into test values(%s, %s)"
# cursor.executemany(sqlStr, data)

# dbconn.commit()

# end_time = time.time()
# print(end_time - start_time)

# 账号初始信息配置
DEFAULT_SECPASSWORD = 000000

# 账号状态
USER_STATUS_NOLMAL = 0
USER_STATUS_FREEZE = 1

grds = redis.Redis(
    host='127.0.0.1',
    port=6379,
    password='123456',
    decode_responses=False,
    encoding='utf-8',
    #charset='utf-8'
)

KEY_PACKAGE = "KEY_PACKAGE_{userid}"
KEY_PACKAGE_EXPIRE_TIME = 7*24*60*60

SESSION_EXPIRETIME = 10 * 60

MAIL_HOST = "127.0.0.1"
MAIL_PORT = 1234

KEY_MAIL_LIST = "KEY_MAIL_LIST_{userid}"
KEY_MAIL_DETAIL = "KEY_MAIL_DETAIL_{mailid}"

KEY_SHOP_INVENTORY = "KEY_SHOP_INVENTORY_{propid}"

"""
KEY_MAIL_LIST_18988888888
18988888888_1741951739
18988888888_1741952008

KEY_MAIL_DETAIL_18988888888_1741951739

"""