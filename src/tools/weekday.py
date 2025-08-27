"""星期几计算工具模块"""

from typing import Any, Sequence
from mcp.types import Tool, TextContent
import json

from ..utils.date_utils import get_weekday
from ..utils.logger import setup_logger
from ..utils.error_handler import handle_errors

# 设置日志
logger = setup_logger(__name__)

class WeekdayTools:
    """星期几计算工具类"""
    
    @staticmethod
    def get_tools() -> list[Tool]:
        """获取所有星期几工具"""
        return [
            Tool(
                name="get_weekday",
                description="根据公历日期计算星期几",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "日期，格式：YYYY-MM-DD，如：2024-01-01",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        }
                    },
                    "required": ["date"]
                }
            )
        ]
    
    @staticmethod
    async def handle_tool_call(name: str, arguments: dict) -> Sequence[TextContent]:
        """处理工具调用"""
        try:
            if name == "get_weekday":
                return await WeekdayTools._get_weekday(arguments)
            
            raise ValueError(f"未知的星期几工具: {name}")
        except Exception as e:
            logger.error(f"工具调用错误: {e}")
            return [TextContent(
                type="text",
                text=json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)
            )]
    
    @staticmethod
    async def _get_weekday(arguments: dict) -> Sequence[TextContent]:
        """计算星期几"""
        date_str = arguments.get("date")
        
        if not date_str:
            raise ValueError("缺少必需参数: date")
        
        # 严格验证日期格式
        import re
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            raise ValueError("日期格式错误，请使用YYYY-MM-DD格式，如：2024-01-01")
        
        # 解析日期字符串
        try:
            year, month, day = map(int, date_str.split('-'))
        except ValueError:
            raise ValueError("日期格式错误，请使用YYYY-MM-DD格式，如：2024-01-01")
        
        # 参数验证
        if year < 1:
            raise ValueError("年份必须是正整数")
        
        if not (1 <= month <= 12):
            raise ValueError("月份必须是1-12之间的整数")
        
        if not (1 <= day <= 31):
            raise ValueError("日期必须是1-31之间的整数")
        
        # 计算星期几
        result = get_weekday(year, month, day)
        
        logger.info(f"函数 get_weekday 调用成功, 参数: {{'args': ('{date_str}',), 'kwargs': {{}}}}")
        
        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]