"""错误处理模块"""

import functools
import traceback
from typing import Any, Callable, Dict, Optional, Union
from .logger import get_logger, log_function_call

class MCPError(Exception):
    """MCP服务器基础异常类"""
    
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR", details: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

class ValidationError(MCPError):
    """参数验证错误"""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        self.value = value
        self.details = {"field": field, "value": str(value) if value is not None else None}

class APIError(MCPError):
    """API调用错误"""
    
    def __init__(self, message: str, status_code: int = None, response: str = None):
        super().__init__(message, "API_ERROR")
        self.status_code = status_code
        self.response = response
        self.details = {"status_code": status_code, "response": response}

class DataError(MCPError):
    """数据处理错误"""
    
    def __init__(self, message: str, data_type: str = None):
        super().__init__(message, "DATA_ERROR")
        self.data_type = data_type
        self.details = {"data_type": data_type}

def handle_errors(return_on_error: Any = None, log_errors: bool = True):
    """错误处理装饰器
    
    Args:
        return_on_error: 发生错误时返回的默认值
        log_errors: 是否记录错误日志
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            func_name = func.__name__
            logger = get_logger(f"error_handler.{func_name}")
            
            try:
                # 记录函数调用开始
                if log_errors:
                    logger.debug(f"开始执行函数 {func_name}")
                
                result = await func(*args, **kwargs)
                
                # 记录成功调用
                if log_errors:
                    log_function_call(func_name, {"args": args, "kwargs": kwargs}, result)
                
                return result
                
            except MCPError as e:
                # 处理自定义MCP错误
                if log_errors:
                    logger.error(f"MCP错误 in {func_name}: {e.message} (代码: {e.error_code})")
                    log_function_call(func_name, {"args": args, "kwargs": kwargs}, error=e)
                
                if return_on_error is not None:
                    return return_on_error
                raise
                
            except Exception as e:
                # 处理其他异常
                if log_errors:
                    logger.error(f"未预期错误 in {func_name}: {str(e)}")
                    logger.error(f"错误堆栈: {traceback.format_exc()}")
                    log_function_call(func_name, {"args": args, "kwargs": kwargs}, error=e)
                
                if return_on_error is not None:
                    return return_on_error
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            func_name = func.__name__
            logger = get_logger(f"error_handler.{func_name}")
            
            try:
                # 记录函数调用开始
                if log_errors:
                    logger.debug(f"开始执行函数 {func_name}")
                
                result = func(*args, **kwargs)
                
                # 记录成功调用
                if log_errors:
                    log_function_call(func_name, {"args": args, "kwargs": kwargs}, result)
                
                return result
                
            except MCPError as e:
                # 处理自定义MCP错误
                if log_errors:
                    logger.error(f"MCP错误 in {func_name}: {e.message} (代码: {e.error_code})")
                    log_function_call(func_name, {"args": args, "kwargs": kwargs}, error=e)
                
                if return_on_error is not None:
                    return return_on_error
                raise
                
            except Exception as e:
                # 处理其他异常
                if log_errors:
                    logger.error(f"未预期错误 in {func_name}: {str(e)}")
                    logger.error(f"错误堆栈: {traceback.format_exc()}")
                    log_function_call(func_name, {"args": args, "kwargs": kwargs}, error=e)
                
                if return_on_error is not None:
                    return return_on_error
                raise
        
        # 检查函数是否是异步函数
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator

def safe_execute(func: Callable, *args, default_return=None, **kwargs) -> Union[Any, Dict[str, str]]:
    """安全执行函数，捕获所有异常
    
    Args:
        func: 要执行的函数
        *args: 函数参数
        default_return: 发生错误时的默认返回值
        **kwargs: 函数关键字参数
    
    Returns:
        函数执行结果或错误信息字典
    """
    logger = get_logger("safe_execute")
    
    try:
        return func(*args, **kwargs)
    except MCPError as e:
        logger.error(f"MCP错误: {e.message}")
        return default_return if default_return is not None else {
            "error": e.message,
            "error_code": e.error_code,
            "details": e.details
        }
    except Exception as e:
        logger.error(f"未预期错误: {str(e)}")
        return default_return if default_return is not None else {
            "error": f"执行失败: {str(e)}",
            "error_code": "EXECUTION_ERROR"
        }

def validate_date_string(date_str: str) -> bool:
    """验证日期字符串格式"""
    if not date_str or not isinstance(date_str, str):
        raise ValidationError("日期字符串不能为空", "date", date_str)
    
    try:
        from datetime import datetime
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        raise ValidationError(f"日期格式错误，应为YYYY-MM-DD格式", "date", date_str)

def validate_year(year: Union[int, str]) -> int:
    """验证年份"""
    try:
        year_int = int(year)
        if year_int < 1900 or year_int > 2100:
            raise ValidationError(f"年份应在1900-2100之间", "year", year)
        return year_int
    except (ValueError, TypeError):
        raise ValidationError(f"年份格式错误", "year", year)

def validate_month(month: Union[int, str]) -> int:
    """验证月份"""
    try:
        month_int = int(month)
        if month_int < 1 or month_int > 12:
            raise ValidationError(f"月份应在1-12之间", "month", month)
        return month_int
    except (ValueError, TypeError):
        raise ValidationError(f"月份格式错误", "month", month)

def validate_day(day: Union[int, str]) -> int:
    """验证日期"""
    try:
        day_int = int(day)
        if day_int < 1 or day_int > 31:
            raise ValidationError(f"日期应在1-31之间", "day", day)
        return day_int
    except (ValueError, TypeError):
        raise ValidationError(f"日期格式错误", "day", day)

def create_error_response(error: Exception) -> Dict[str, Any]:
    """创建标准化的错误响应"""
    if isinstance(error, MCPError):
        return {
            "error": error.message,
            "error_code": error.error_code,
            "details": error.details
        }
    else:
        return {
            "error": str(error),
            "error_code": "UNKNOWN_ERROR",
            "details": {"type": type(error).__name__}
        }