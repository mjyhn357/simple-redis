import shlex  # 添加这个导入

def encode_command_to_resp(cmdline: str) -> bytes:
    """
    将诸如 'set foo bar' 的字符串命令转为RESP协议的字节流
    """
    try:
        # 使用shlex来正确解析命令行，支持引号
        parts = shlex.split(cmdline.strip())
    except ValueError:
        # 如果shlex解析失败（比如引号不匹配），回退到简单分割
        parts = cmdline.strip().split()

    if not parts:
        parts = [""]

    arr = [f"*{len(parts)}\r\n".encode()]
    for part in parts:
        s = part.encode('utf-8')
        arr.append(f"${len(s)}\r\n".encode())
        arr.append(s + b"\r\n")
    return b"".join(arr)

def encode_response_to_resp(obj):
    """
    将Python对象编码为RESP协议格式的字节流，用于服务器返回数据给客户端
    """
    if obj is None:
        # NULL字符串
        return b"$-1\r\n"

    elif isinstance(obj, str):
        if obj.startswith("-ERR"):
            # 错误消息
            return f"-{obj[1:]}\r\n".encode()
        elif obj.startswith("+"):
            # 简单字符串 (如 "+OK")
            return f"{obj}\r\n".encode()
        elif obj == "OK":
            # 特殊处理OK
            return b"+OK\r\n"
        else:
            # 普通字符串
            obj_bytes = obj.encode('utf-8')
            return f"${len(obj_bytes)}\r\n".encode() + obj_bytes + b"\r\n"


    elif isinstance(obj, int):
        # 整数
        return f":{obj}\r\n".encode()

    elif isinstance(obj, list):
        # 数组 - 这是HGETALL需要的！
        if not obj:  # 空数组
            return b"*0\r\n"

        lines = [f"*{len(obj)}\r\n"]
        for item in obj:
            if isinstance(item, str):
                item_bytes = item.encode('utf-8')
                lines.append(f"${len(item_bytes)}\r\n")
                lines.append(item)
                lines.append("\r\n")
            elif isinstance(item, int):
                lines.append(f":{item}\r\n")
            elif item is None:
                lines.append("$-1\r\n")
            else:
                # 其他类型转为字符串
                item_str = str(item)
                item_bytes = item_str.encode('utf-8')
                lines.append(f"${len(item_bytes)}\r\n")
                lines.append(item_str)
                lines.append("\r\n")

        return "".join(lines).encode('utf-8')

    else:
        # 其他类型转为字符串处理
        s = str(obj)
        s_bytes = s.encode('utf-8')
        return f"${len(s_bytes)}\r\n".encode() + s_bytes + b"\r\n"

def parse_resp(data):
    """解析一段RESP协议内容，返回Python对象和剩余bytes（如果有半包情况）"""
    def _decode_one(buffer, pos):
        if pos >= len(buffer):
            return None, pos
        b = buffer[pos:pos+1]
        if b == b'+':  # 简单字符串
            end = buffer.find(b'\r\n', pos)
            if end == -1:
                return None, pos
            return buffer[pos+1:end].decode(), end+2
        elif b == b'-': # 错误
            end = buffer.find(b'\r\n', pos)
            if end == -1:
                return None, pos
            return Exception(buffer[pos+1:end].decode()), end+2
        elif b == b':': # 整数
            end = buffer.find(b'\r\n', pos)
            if end == -1:
                return None, pos
            return int(buffer[pos+1:end]), end+2
        elif b == b'$': # 字符串
            end = buffer.find(b'\r\n', pos)
            if end == -1:
                return None, pos
            strlen = int(buffer[pos+1:end])
            if strlen == -1:
                return None, end+2
            start = end+2
            if start+strlen > len(buffer):
                return None, pos  # 半包
            s = buffer[start:start+strlen]
            return s.decode(), start+strlen+2  # +2 for \r\n
        elif b == b'*': # 数组（多条）
            end = buffer.find(b'\r\n', pos)
            if end == -1:
                return None, pos
            arrlen = int(buffer[pos+1:end])
            arr = []
            p = end + 2
            for _ in range(arrlen):
                item, p2 = _decode_one(buffer, p)
                if item is None:
                    return None, pos  # 半包
                arr.append(item)
                p = p2
            return arr, p
        else:
            raise Exception('Unknown RESP type: ' + repr(b))
    out, nextpos = _decode_one(data, 0)
    return out, data[nextpos:]