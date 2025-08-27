"""缓存工具模块"""

import os
import time
import json
import hashlib
from typing import Any, Dict, Optional, Callable, Union
from functools import wraps
from threading import Lock
from pathlib import Path

class SimpleCache:
    """简单的内存缓存实现"""
    
    def __init__(self, default_ttl: int = 3600, max_size: int = 1000):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._lock = Lock()
        self._hits = 0
        self._misses = 0
        self._sets = 0
        self._deletes = 0
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if time.time() < entry['expires']:
                    self._hits += 1
                    entry['last_accessed'] = time.time()
                    return entry['value']
                else:
                    del self._cache[key]
                    self._deletes += 1
            
            self._misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        if ttl is None:
            ttl = self.default_ttl
        
        with self._lock:
            # 如果缓存已满，清理最旧的条目
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_oldest()
            
            current_time = time.time()
            self._cache[key] = {
                'value': value,
                'expires': current_time + ttl,
                'created': current_time,
                'last_accessed': current_time,
                'access_count': 0
            }
            self._sets += 1
    
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._deletes += 1
                return True
            return False
    
    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            cleared_count = len(self._cache)
            self._cache.clear()
            self._deletes += cleared_count
    
    def cleanup(self) -> int:
        """清理过期缓存，返回清理的数量"""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, entry in self._cache.items()
                if current_time >= entry['expires']
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            self._deletes += len(expired_keys)
            return len(expired_keys)
    
    def _evict_oldest(self) -> None:
        """清理最旧的缓存条目"""
        if not self._cache:
            return
        
        # 找到最旧的条目（最少访问的）
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k]['last_accessed']
        )
        del self._cache[oldest_key]
        self._deletes += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            current_time = time.time()
            total_entries = len(self._cache)
            expired_entries = sum(
                1 for entry in self._cache.values()
                if current_time >= entry['expires']
            )
            
            hit_rate = self._hits / (self._hits + self._misses) if (self._hits + self._misses) > 0 else 0
            
            return {
                'total_entries': total_entries,
                'active_entries': total_entries - expired_entries,
                'expired_entries': expired_entries,
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'sets': self._sets,
                'deletes': self._deletes,
                'hit_rate': hit_rate,
                'memory_usage_estimate': self._estimate_memory_usage()
            }
    
    def _estimate_memory_usage(self) -> int:
        """估算内存使用量（字节）"""
        total_size = 0
        for key, entry in self._cache.items():
            # 粗略估算
            total_size += len(str(key)) * 2  # Unicode字符
            total_size += len(str(entry['value'])) * 2
            total_size += 64  # 元数据开销
        return total_size

class PersistentCache(SimpleCache):
    """持久化缓存实现"""
    
    def __init__(self, cache_dir: str = "cache", default_ttl: int = 3600, max_size: int = 1000):
        super().__init__(default_ttl, max_size)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self._load_from_disk()
    
    def _get_file_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        # 使用MD5哈希避免文件名问题
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.cache"
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值并持久化"""
        super().set(key, value, ttl)
        self._save_to_disk(key)
    
    def delete(self, key: str) -> bool:
        """删除缓存值和文件"""
        result = super().delete(key)
        if result:
            file_path = self._get_file_path(key)
            if file_path.exists():
                file_path.unlink()
        return result
    
    def _save_to_disk(self, key: str) -> None:
        """保存单个缓存条目到磁盘"""
        if key in self._cache:
            file_path = self._get_file_path(key)
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    cache_data = {
                        'key': key,
                        'entry': self._cache[key]
                    }
                    json.dump(cache_data, f, ensure_ascii=False, default=str)
            except Exception:
                pass  # 忽略持久化错误
    
    def _load_from_disk(self) -> None:
        """从磁盘加载缓存"""
        if not self.cache_dir.exists():
            return
        
        current_time = time.time()
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    key = cache_data['key']
                    entry = cache_data['entry']
                    
                    # 检查是否过期
                    if current_time < entry['expires']:
                        self._cache[key] = entry
                    else:
                        cache_file.unlink()  # 删除过期文件
            except Exception:
                cache_file.unlink()  # 删除损坏的文件

# 缓存配置
CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))
CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', '1000'))
CACHE_TYPE = os.getenv('CACHE_TYPE', 'memory')  # memory 或 persistent
CACHE_DIR = os.getenv('CACHE_DIR', 'cache')

# 全局缓存实例
if CACHE_TYPE == 'persistent':
    _global_cache = PersistentCache(CACHE_DIR, CACHE_TTL, CACHE_MAX_SIZE)
else:
    _global_cache = SimpleCache(CACHE_TTL, CACHE_MAX_SIZE)

def cache_result(ttl: Optional[int] = None, key_func: Optional[Callable] = None, enabled: bool = True):
    """缓存装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 如果缓存被禁用，直接执行函数
            if not CACHE_ENABLED or not enabled:
                return func(*args, **kwargs)
            
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 创建更稳定的缓存键
                args_str = '_'.join(str(arg) for arg in args)
                kwargs_str = '_'.join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = f"{func.__module__}.{func.__name__}:{args_str}:{kwargs_str}"
            
            # 尝试从缓存获取
            cached_result = _global_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            _global_cache.set(cache_key, result, ttl or CACHE_TTL)
            
            return result
        
        # 添加缓存管理方法
        wrapper.cache_clear = lambda: _global_cache.clear()
        wrapper.cache_info = lambda: _global_cache.get_stats()
        
        return wrapper
    return decorator

def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息"""
    stats = _global_cache.get_stats()
    stats['cache_enabled'] = CACHE_ENABLED
    stats['cache_type'] = CACHE_TYPE
    stats['default_ttl'] = CACHE_TTL
    return stats

def clear_cache() -> None:
    """清空所有缓存"""
    _global_cache.clear()

def cleanup_cache() -> int:
    """清理过期缓存"""
    return _global_cache.cleanup()

def warm_cache(func: Callable, *args_list) -> int:
    """预热缓存"""
    warmed = 0
    for args in args_list:
        try:
            if isinstance(args, (list, tuple)):
                func(*args)
            else:
                func(args)
            warmed += 1
        except Exception:
            pass  # 忽略预热错误
    return warmed

# 保持向后兼容性
class CacheManager(SimpleCache):
    """向后兼容的缓存管理器"""
    
    def __init__(self, default_ttl: int = 86400):
        super().__init__(default_ttl)
    
    def cleanup_expired(self) -> int:
        """清理过期的缓存项"""
        return self.cleanup()
    
    def size(self) -> int:
        """获取缓存项数量"""
        with self._lock:
            return len(self._cache)

# 全局缓存实例（向后兼容）
cache_manager = CacheManager()