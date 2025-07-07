## 所有具体的方法
def cmd_set(server, args):
    if len(args) != 2:
        return "-ERR wrong number of arguments for 'set'"
    key, value = args[0], args[1]
    server.db.set_value(key, value)
    return "OK"

def cmd_get(server, args):
    if len(args) != 1 :
        return "-ERR wrong number of arguments for 'get'"
    return server.db.get_value(args[0])

def cmd_del(server, args):
    if len(args) < 1:
        return "-ERR wrong number of arguments for 'del'"
    count = 0
    for key in args:
        if server.db.delete_key(key):
            count += 1
    return count  # Redis会返回整数

def cmd_expire(server, args):
    if len(args) < 2:
        return "-ERR wrong number of arguments for 'expire'"
    key, seconds_str = args[0], args[1]

    # ✅ 参数类型验证
    try:
        seconds = int(seconds_str)
    except ValueError:
        return "-ERR value is not an integer or out of range"

    if seconds < 0:
        return "-ERR invalid value for 'expire'"

    if server.db.set_expire(key, seconds):
        return 1
    return "-ERR wrong key for 'expire'"

# Hash 操作
def cmd_hset(server, args):
    if len(args) != 3:
        return "-ERR wrong number of arguments for 'hset'"
    key, field, value = args[0], args[1], args[2]

    hash_obj = server.db.get_value(key)
    if hash_obj is None:
        hash_obj = {}
        server.db.set_value(key, hash_obj)
    elif not isinstance(hash_obj, dict):
        return "-ERR WRONGTYPE Operation against a key holding the wrong kind of value"

    is_new = field not in hash_obj
    hash_obj[field] = value

    return 1 if is_new else 0

def cmd_hget(server, args):
    if len(args) < 2:
        return "-ERR wrong number of arguments for 'hget'"
    key, field = args[0], args[1]

    hash_obj = server.db.get_value(key)

    # 键不存在时返回None
    if hash_obj is None:
        return None

    # 键存在但不是hash时返回错误
    if not isinstance(hash_obj, dict):
        return "-ERR WRONGTYPE Operation against a key holding the wrong kind of value"

    return hash_obj.get(field)

def cmd_hgetall(server, args):
    if len(args) < 1:
        return "-ERR wrong number of arguments for 'hgetall'"
    key = args[0]

    hash_obj = server.db.get_value(key)
    if not isinstance(hash_obj, dict):
        return []

    result = []
    for k, v in hash_obj.items():
        result.extend([k, v])
    return result

def cmd_hdel(server, args):
    if len(args) < 2:
        return "-ERR wrong number of arguments for 'hdel'"
    key, fields = args[0], args[1:]

    hash_obj = server.db.get_value(key)
    if not isinstance(hash_obj, dict):
        return 0

    count = 0
    for field in fields:
        if field in hash_obj:
            del hash_obj[field]
            count += 1
    return count

def cmd_hmset(server, args):
    """批量设置哈希字段"""
    if len(args) < 3 or len(args) % 2 == 0:
        return "-ERR wrong number of arguments for 'hmset'"

    key = args[0]
    field_value_pairs = args[1:]  # 剩余的参数

    # 获取或创建hash对象
    hash_obj = server.db.get_value(key)
    if hash_obj is None:
        hash_obj = {}
        server.db.set_value(key, hash_obj)
    elif not isinstance(hash_obj, dict):
        return "-ERR WRONGTYPE Operation against a key holding the wrong kind of value"

    # 批量设置字段
    for i in range(0, len(field_value_pairs), 2):
        field = field_value_pairs[i]
        value = field_value_pairs[i + 1]
        hash_obj[field] = value

    return "OK"

def cmd_hmget(server, args):
    """批量获取哈希字段"""
    if len(args) < 2:
        return "-ERR wrong number of arguments for 'hmget'"

    key = args[0]
    fields = args[1:]  # 要获取的字段列表

    hash_obj = server.db.get_value(key)
    if not isinstance(hash_obj, dict):
        # 如果key不存在或不是hash，返回对应数量的nil
        return [None] * len(fields)

    # 按顺序获取各个字段的值
    result = []
    for field in fields:
        value = hash_obj.get(field)  # 不存在的字段返回None
        result.append(value)

    return result

def cmd_keys(server, args):
    """列出所有键"""
    if len(args) != 1:
        return "-ERR wrong number of arguments for 'keys'"

    pattern = args[0]
    if pattern == "*":
        return server.db.get_all_keys()
    else:
        return "-ERR pattern matching not implemented"


def cmd_exists(server, args):
    """检查键是否存在"""
    if len(args) < 1:
        return "-ERR wrong number of arguments for 'exists'"

    count = 0
    for key in args:
        if server.db.exists(key):
            count += 1
    return count


def cmd_type(server, args):
    """返回键的类型"""
    if len(args) != 1:
        return "-ERR wrong number of arguments for 'type'"

    value = server.db.get_value(args[0])
    if value is None:
        return "none"
    elif isinstance(value, str):
        return "string"
    elif isinstance(value, dict):
        return "hash"
    else:
        return "string"

COMMANDS = {
    "SET": cmd_set,
    "GET": cmd_get,
    "DEL": cmd_del,
    "EXPIRE": cmd_expire,
    "HSET": cmd_hset,
    "HGET": cmd_hget,
    "HDEL": cmd_hdel,
    "HGETALL": cmd_hgetall,
    "HMSET": cmd_hmset,
    "HMGET": cmd_hmget,
    "KEYS": cmd_keys,
    "EXISTS": cmd_exists,
    "TYPE": cmd_type,
    # 可以继续添加
}