import redis


class Redis:
    def __init__(self, cp: bool=False, cs: int=8, *args, **kwargs):
        """初始化
            cp: 是否使用连接池，默认否
            cs: 连接池的最大连接数 默认8
        """

        kwargs['decode_responses'] = True  # 使Redis默认返回字符串
        if cp:
            cp = redis.ConnectionPool(max_connections=cs)
            kwargs['connection_pool'] = cp
        self.redis = redis.Redis(*args, **kwargs)

    def getSet(self, key: str):
        """返回集合容器
            key: 集合的名字
        """
        return Redis.Set(self.redis, key)

    class Set:
        def __init__(self, redis, key: str):
            self.redis = redis
            self.key = key
            self.pipeline = None

        def getRedis(self):
            if self.pipeline:
                return self.pipeline
            return self.redis

        def getPipeline(self):
            if self.pipeline:
                return False
            self.pipeline = self.redis.pipeline()
            return True

        def execute(self):
            if self.pipeline:
                r = self.pipeline.execute()
                self.pipeline = None
                return r

        def __len__(self):
            """返回容器中元素个数"""
            return self.getRedis().scard(self.key)

        def __contains__(self, x):
            """判断元素是否存在于容器中"""
            return self.getRedis().sismember(self.key, x)

        def __iter__(self):
            """迭代访问容器中的所有元素"""
            return self.getRedis().smembers(self.key)

        def insert(self, x):
            return self.inserts(x)
        def delete(self, x):
            return self.deletes(x)

        def inserts(self, x, *args):
            return self.getRedis().sadd(self.key, x, *args)
        def deletes(self, x, *args):
            return self.getRedis().srem(self.key, x, *args)


if __name__=='__main__':
    redis = Redis(cp=True)
    set = redis.getSet('BilibiliVideoList76')
    print([set.__len__(), list(set.__iter__())])

    set.inserts('Hello', 'world', 'world!', 'Hello', 'lalala')
    print([set.__len__(), list(set.__iter__())])

    set.deletes('lala')
    print([set.__len__(), list(set.__iter__())])

    set.deletes('lalala')
    print([set.__len__(), list(set.__iter__())])
