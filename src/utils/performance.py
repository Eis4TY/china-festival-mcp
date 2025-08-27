"""性能监控模块"""

import time
import psutil
import threading
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    function_name: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    timestamp: datetime
    success: bool = True
    error_message: Optional[str] = None
    
class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, max_records: int = 1000):
        self.max_records = max_records
        self._metrics: deque = deque(maxlen=max_records)
        self._function_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'total_calls': 0,
            'total_time': 0.0,
            'avg_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'success_count': 0,
            'error_count': 0,
            'last_called': None
        })
        self._lock = threading.Lock()
        
    def record_metric(self, metric: PerformanceMetrics) -> None:
        """记录性能指标"""
        with self._lock:
            self._metrics.append(metric)
            
            # 更新函数统计
            stats = self._function_stats[metric.function_name]
            stats['total_calls'] += 1
            stats['total_time'] += metric.execution_time
            stats['avg_time'] = stats['total_time'] / stats['total_calls']
            stats['min_time'] = min(stats['min_time'], metric.execution_time)
            stats['max_time'] = max(stats['max_time'], metric.execution_time)
            stats['last_called'] = metric.timestamp
            
            if metric.success:
                stats['success_count'] += 1
            else:
                stats['error_count'] += 1
    
    def get_function_stats(self, function_name: Optional[str] = None) -> Dict[str, Any]:
        """获取函数统计信息"""
        with self._lock:
            if function_name:
                return dict(self._function_stats.get(function_name, {}))
            return {name: dict(stats) for name, stats in self._function_stats.items()}
    
    def get_recent_metrics(self, minutes: int = 10) -> List[PerformanceMetrics]:
        """获取最近的性能指标"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        with self._lock:
            return [m for m in self._metrics if m.timestamp >= cutoff_time]
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统性能指标"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage_percent': cpu_percent,
                'memory_usage_percent': memory.percent,
                'memory_available_mb': memory.available / 1024 / 1024,
                'memory_total_mb': memory.total / 1024 / 1024,
                'disk_usage_percent': disk.percent,
                'disk_free_gb': disk.free / 1024 / 1024 / 1024,
                'disk_total_gb': disk.total / 1024 / 1024 / 1024,
                'timestamp': datetime.now()
            }
        except Exception as e:
            return {
                'error': f'Failed to get system metrics: {str(e)}',
                'timestamp': datetime.now()
            }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        with self._lock:
            total_functions = len(self._function_stats)
            total_calls = sum(stats['total_calls'] for stats in self._function_stats.values())
            total_errors = sum(stats['error_count'] for stats in self._function_stats.values())
            
            # 找出最慢的函数
            slowest_function = None
            slowest_time = 0
            for name, stats in self._function_stats.items():
                if stats['avg_time'] > slowest_time:
                    slowest_time = stats['avg_time']
                    slowest_function = name
            
            # 找出调用最频繁的函数
            most_called_function = None
            most_calls = 0
            for name, stats in self._function_stats.items():
                if stats['total_calls'] > most_calls:
                    most_calls = stats['total_calls']
                    most_called_function = name
            
            return {
                'total_functions_monitored': total_functions,
                'total_function_calls': total_calls,
                'total_errors': total_errors,
                'error_rate': total_errors / total_calls if total_calls > 0 else 0,
                'slowest_function': {
                    'name': slowest_function,
                    'avg_time': slowest_time
                },
                'most_called_function': {
                    'name': most_called_function,
                    'call_count': most_calls
                },
                'system_metrics': self.get_system_metrics()
            }
    
    def clear_metrics(self) -> None:
        """清空所有指标"""
        with self._lock:
            self._metrics.clear()
            self._function_stats.clear()

# 全局性能监控器实例
_performance_monitor = PerformanceMonitor()

def monitor_performance(include_system_metrics: bool = False):
    """性能监控装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = 0
            start_cpu = 0
            
            if include_system_metrics:
                try:
                    process = psutil.Process()
                    start_memory = process.memory_info().rss / 1024 / 1024  # MB
                    start_cpu = process.cpu_percent()
                except Exception:
                    pass
            
            success = True
            error_message = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_message = str(e)
                raise
            finally:
                end_time = time.time()
                execution_time = end_time - start_time
                
                end_memory = 0
                end_cpu = 0
                
                if include_system_metrics:
                    try:
                        process = psutil.Process()
                        end_memory = process.memory_info().rss / 1024 / 1024  # MB
                        end_cpu = process.cpu_percent()
                    except Exception:
                        pass
                
                metric = PerformanceMetrics(
                    function_name=f"{func.__module__}.{func.__name__}",
                    execution_time=execution_time,
                    memory_usage=end_memory - start_memory,
                    cpu_usage=end_cpu - start_cpu,
                    timestamp=datetime.now(),
                    success=success,
                    error_message=error_message
                )
                
                _performance_monitor.record_metric(metric)
        
        # 添加性能统计方法
        wrapper.get_performance_stats = lambda: _performance_monitor.get_function_stats(f"{func.__module__}.{func.__name__}")
        
        return wrapper
    return decorator

def get_performance_stats(function_name: Optional[str] = None) -> Dict[str, Any]:
    """获取性能统计信息"""
    return _performance_monitor.get_function_stats(function_name)

def get_performance_summary() -> Dict[str, Any]:
    """获取性能摘要"""
    return _performance_monitor.get_performance_summary()

def get_recent_metrics(minutes: int = 10) -> List[Dict[str, Any]]:
    """获取最近的性能指标"""
    metrics = _performance_monitor.get_recent_metrics(minutes)
    return [
        {
            'function_name': m.function_name,
            'execution_time': m.execution_time,
            'memory_usage': m.memory_usage,
            'cpu_usage': m.cpu_usage,
            'timestamp': m.timestamp.isoformat(),
            'success': m.success,
            'error_message': m.error_message
        }
        for m in metrics
    ]

def clear_performance_metrics() -> None:
    """清空性能指标"""
    _performance_monitor.clear_metrics()

class PerformanceProfiler:
    """性能分析器上下文管理器"""
    
    def __init__(self, name: str, include_system_metrics: bool = True):
        self.name = name
        self.include_system_metrics = include_system_metrics
        self.start_time = None
        self.start_memory = 0
        self.start_cpu = 0
    
    def __enter__(self):
        self.start_time = time.time()
        
        if self.include_system_metrics:
            try:
                process = psutil.Process()
                self.start_memory = process.memory_info().rss / 1024 / 1024  # MB
                self.start_cpu = process.cpu_percent()
            except Exception:
                pass
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        execution_time = end_time - self.start_time
        
        end_memory = 0
        end_cpu = 0
        
        if self.include_system_metrics:
            try:
                process = psutil.Process()
                end_memory = process.memory_info().rss / 1024 / 1024  # MB
                end_cpu = process.cpu_percent()
            except Exception:
                pass
        
        success = exc_type is None
        error_message = str(exc_val) if exc_val else None
        
        metric = PerformanceMetrics(
            function_name=self.name,
            execution_time=execution_time,
            memory_usage=end_memory - self.start_memory,
            cpu_usage=end_cpu - self.start_cpu,
            timestamp=datetime.now(),
            success=success,
            error_message=error_message
        )
        
        _performance_monitor.record_metric(metric)

def profile_performance(name: str, include_system_metrics: bool = True) -> PerformanceProfiler:
    """创建性能分析器"""
    return PerformanceProfiler(name, include_system_metrics)