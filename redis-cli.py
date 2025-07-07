from twisted.internet import reactor, protocol, stdio
from twisted.protocols.basic import LineReceiver
from resp_protocol import *

# 定义终端输入处理类，用于处理终端输入
class StdinInputProtocol(LineReceiver):
    delimiter = b'\n'
    def __init__(self, redis_protocol=None):
        self.redis_protocol = redis_protocol

    def connectionMade(self):
        self.transport.write(b"Redis, Please input the order> ") # 初始提示

    def lineReceived(self, line):
        cmd = line.decode().strip()

        if cmd.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            reactor.stop()  # 停止reactor，退出程序
            return

        if self.redis_protocol and self.redis_protocol.transport:
            resp_bytes = encode_command_to_resp(cmd)
            self.redis_protocol.transport.write(resp_bytes)

# 定义客户端协议类，负责与服务器握手、通信等逻辑
class RedisClientProtocol(protocol.Protocol):
    def __init__(self):
        self.stdin_input = None

    # 当TCP连接成功建立后，Twisted会自动调用此方法
    def connectionMade(self):
        self.stdin_input = StdinInputProtocol(self)
        stdio.StandardIO(self.stdin_input)

    # 当接收到服务器发送的数据时，Twisted会自动调用此方法
    def dataReceived(self, data):
        print("Server responded:", parse_resp(data)[0])
        # 重现命令行提示符（防止回车显示混乱）
        if self.stdin_input:
            self.stdin_input.transport.write(b"Redis> ")

# 定义用于生产 Protocol（工人）的工厂类
class RedisClientFactory(protocol.ClientFactory):
    # 每次建立一个新的TCP连接时，Twisted会调用此方法
    # 用来生成对应的协议实例（工人）
    def buildProtocol(self, addr):
        return RedisClientProtocol()
    def clientConnectionFailed(self, connector, reason):
        print("Redis server not running or connection failed:", reason.getErrorMessage())
        reactor.stop()

# 用 reactor 向本地 6379 端口发起 TCP 客户端连接
# 连接建立后由 RedisClientFactory 负责生产协议类
reactor.connectTCP("localhost", 6379, RedisClientFactory())
# 启动事件循环，等待连接、数据等事件异步发生
reactor.run()