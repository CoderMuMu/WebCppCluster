import json
import pymysql
import pymysql.cursors
import Config
import logging
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('webpy')

def CatchError(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
    return wrapper

def DBCatchError(func):
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn:pymysql.Connection = Config.pool.connection()
            cursor:pymysql.cursors.Cursor = conn.cursor()
            kwargs['cursor'] = cursor
            conn.begin()  # 开启事务
            res = func(*args, **kwargs)
            conn.commit()  # 提交事务
            return res
        except pymysql.MySQLError as e:
            if conn:
                conn.rollback()  # 回滚事务
            # 打印日志
            logger.exception(e)
        finally:
            if cursor:
                cursor.close()  # 关闭游标
            if conn:
                conn.close()  # 关闭连接
    return wrapper

def ErrResult(code, reason):
    return json.dumps({'code':code, 'reason':reason})