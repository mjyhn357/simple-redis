# 导入 Twisted 的 Protocol 和 Factory 基类，以及主事件循环调度器 reactor
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor, task
from resp_protocol import *
from handlers import COMMANDS
from Redis_db import RedisDB

# 定义一个继承自 Protocol 的类作为“工人模板”，负责具体每个连接的数据处理
class RedisServerProtocol(Protocol):
    def __init__(self, db_id: int = 0):
        self._buffer = b''

    def connectionMade(self):
        # 初始化数据库 - 更接近Redis的结构
        if not hasattr(self.factory, "databases"):
            # Redis默认有16个数据库
            self.factory.databases = {
                i: RedisDB(db_id=i) for i in range(16)
            }
            # 启动过期清理任务
            self._start_expire_cleaner()

        # 默认使用0号数据库
        self.current_db = 0
        self.db = self.factory.databases[self.current_db]

    def _start_expire_cleaner(self):
        """启动定期清理过期键的任务"""
        def cleanup_all_dbs():
            total_cleaned = 0
            for db in self.factory.databases.values():
                total_cleaned += db.cleanup_expired()
            if total_cleaned > 0:
                print(f"Cleaned {total_cleaned} expired keys")

        # 每秒清理一次过期键
        task.LoopingCall(cleanup_all_dbs).start(1.0)

    # 当客户端发来数据时
    def dataReceived(self, data):
        command = parse_resp(data)[0]
        response = self.handle_command(command)
        self.transport.write(encode_response_to_resp(response))

    def handle_command(self, cmd):
        # 通用参数校验
        if not isinstance(cmd, list) or not cmd:
            return "-ERR unknown or invalid command"

        name = cmd[0].upper()
        args = cmd[1:]
        func = COMMANDS.get(name)
        if not func:
            return f"-ERR unknown command '{cmd[0]}'"
        try:
            return func(self, args)
        except Exception as e:
            return f"-ERR internal error: {str(e)}"
        # self.transport.write(result)

# 创建一个“工厂”实例，负责生产 Protocol (工人) 实例
factory = Factory()
# 指定工厂生产的工人的模板/类型为上面定义的 RedisServerProtocol
factory.protocol = RedisServerProtocol

# listenTCP 的第二个参数就是工厂，新的连接会由工厂生产实例处理
reactor.listenTCP(6379, factory)
print("SimpleRedis Server running on port 6379...")

# 启动 reactor 的事件循环，接收并处理各种网络事件.
reactor.run()