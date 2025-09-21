#-*- coding:utf-8 -*-

import redis
import json
from web.session import Store

class RedisStore(Store):
    def __init__(self, grds, timeout):
        self.redis = grds
        self.timeout = timeout
        print("redis store init success")

    def encode(self, session_dict):
        try:
            return json.dumps(session_dict, ensure_ascii=False)
        except Exception as e:
            print(f"ERROR: RedisStore encode error: {e}")
            return json.dumps({})
    
    def decode(self, session_data):
        try:
            return json.loads(session_data)
        except Exception as e:
            print(f"ERROR: RedisStore decode error: {e}")
            return {}

    def __contains__(self, key):
        return self.redis.exists(key)

    def __getitem__(self, key):
        value = self.redis.get(key)
        if value:
            self.redis.expire(key, self.timeout)
            return self.decode(value)
        else:
            raise KeyError(key)

    def __setitem__(self, key, value):
        encoded_value = self.encode(value)
        self.redis.setex(key, self.timeout, encoded_value)

    def __delitem__(self, key):
        self.redis.delete(key)

    def cleanup(self, timeout):
        # Redis自身支持过期时间，因此这里不需要实现清理逻辑
        pass