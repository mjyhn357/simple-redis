import time
from typing import Any, Optional, Dict, Union


class RedisDB:
    """模拟Redis的数据库结构"""

    def __init__(self, db_id: int = 0):
        self.db_id = db_id
        self.data = {}  # 主键值存储 - 类似Redis的dict
        self.expires = {}  # 过期时间存储 - 类似Redis的expires

    def set_value(self, key: str, value: Any, expire_ts: Optional[float] = None):
        """设置键值，可选过期时间"""
        self.data[key] = value
        if expire_ts:
            self.expires[key] = expire_ts
        elif key in self.expires:
            # 如果重新set但没设置过期时间，清除旧的过期时间
            del self.expires[key]

    def get_value(self, key: str) -> Any:
        """获取值，自动检查过期"""
        if self._is_expired(key):
            self._delete_expired(key)
            return None
        return self.data.get(key, None)

    def delete_key(self, key: str) -> bool:
        """删除键，返回是否成功删除"""
        if key not in self.data:
            return False
        del self.data[key]
        if key in self.expires:
            del self.expires[key]
        return True

    def set_expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        if key not in self.data:
            return False
        self.expires[key] = time.time() + seconds
        return True

    def exists(self, key: str) -> bool:
        """检查键是否存在（会自动清理过期键）"""
        if self._is_expired(key):
            self._delete_expired(key)
            return False
        return key in self.data

    def _is_expired(self, key: str) -> bool:
        """检查键是否过期"""
        if key not in self.expires:
            return False
        return time.time() > self.expires[key]

    def _delete_expired(self, key: str):
        """删除过期的键"""
        self.data.pop(key, None)
        self.expires.pop(key, None)

    def cleanup_expired(self):
        """批量清理过期键（定时任务用）"""
        now = time.time()
        expired_keys = [
            key for key, expire_ts in self.expires.items()
            if expire_ts < now
        ]
        for key in expired_keys:
            self._delete_expired(key)
        return len(expired_keys)

    def get_all_keys(self):
        """获取所有有效键（自动过滤过期）"""
        valid_keys = []
        for key in list(self.data.keys()):
            if not self._is_expired(key):
                valid_keys.append(key)
            else:
                self._delete_expired(key)
        return valid_keys