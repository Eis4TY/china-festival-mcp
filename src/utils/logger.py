"""日志配置模块"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 创建日志目录
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """设置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
    
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 设置日志级别
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 创建文件处理器（如果可能）
    try:
        log_file = LOG_DIR / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        # 如果无法创建文件处理器，只使用控制台处理器
        pass
    
    return logger

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取日志记录器"""
    if name is None:
        name = "china_festival_mcp"
    return logging.getLogger(name)

def log_function_call(func_name: str, args: dict, result: any = None, error: Exception = None):
    """记录函数调用日志"""
    logger = get_logger()
    
    if error:
        logger.error(f"函数 {func_name} 调用失败: {error}, 参数: {args}")
    else:
        logger.info(f"函数 {func_name} 调用成功, 参数: {args}")
        if result is not None:
            logger.debug(f"函数 {func_name} 返回结果类型: {type(result).__name__}")

def log_api_request(endpoint: str, params: dict, response_time: float = None, error: Exception = None):
    """记录API请求日志"""
    logger = get_logger()
    
    if error:
        logger.error(f"API请求失败 {endpoint}: {error}, 参数: {params}")
    else:
        logger.info(f"API请求成功 {endpoint}, 参数: {params}, 响应时间: {response_time:.2f}s")

# 初始化默认日志记录器
default_logger = setup_logger("china_festival_mcp")