# Simple Redis - Python实现的Redis服务器

🚀 一个基于Python和Twisted框架实现的简化版Redis服务器，支持基本的Redis协议和命令。

## ✨ 功能特性

- 🔧 **支持的Redis命令**
  - `PING` - 测试连接
  - `SET key value` - 设置键值对
  - `GET key` - 获取键的值
  - `DEL key` - 删除键
  - `EXISTS key` - 检查键是否存在
  - `KEYS pattern` - 列出匹配的键
  - `FLUSHDB` - 清空数据库

- 🌐 **网络协议**
  - 完整的RESP(Redis Serialization Protocol)支持
  - TCP连接处理
  - 多客户端并发支持

- 🛠️ **管理工具**
  - 服务器启动/停止脚本
  - 实时日志记录
  - 进程管理
  - 状态监控

## 🏗️ 项目结构
simple_redis/
├── redis-server.py # 主服务器代码
├── redis-client.py # 客户端代码
├── redis_manager.sh # 服务管理脚本
├── config/ # 配置文件
├── logs/ # 日志文件
├── tests/ # 测试文件
└── docs/ # 文档

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Twisted框架

### 安装依赖

```bash
# 创建虚拟环境
python -m venv redis_env
source redis_env/bin/activate  # Linux/Mac
# 或 redis_env\Scripts\activate  # Windows

# 安装依赖
pip install twisted

# 方法1：直接启动
python redis-server.py

# 方法2：使用管理脚本
chmod +x redis_manager.sh
./redis_manager.sh start

# 使用自带客户端
python redis-client.py

# 或使用telnet
telnet localhost 6379

# 或使用redis-cli（如果安装了）
redis-cli -h localhost -p 6379

# 连接到服务器
$ python redis-client.py

redis> PING
PONG

redis> SET mykey hello
OK

redis> GET mykey
hello

redis> EXISTS mykey
1

redis> DEL mykey
1

redis> GET mykey
(nil)


添加新命令
在 redis-server.py 中添加命令处理函数
在 handle_command 方法中注册命令
添加相应的测试用例

架构说明
协议层：RESP协议解析和构造
命令层：Redis命令实现
存储层：内存数据结构
网络层：Twisted异步网络处理

已知限制
仅支持内存存储（无持久化）
不支持Redis集群
部分高级命令未实现
无用户认证

许可证
MIT License

👨‍💻 作者
hanch - 学习项目
