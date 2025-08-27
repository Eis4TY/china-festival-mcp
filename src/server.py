import asyncio
import json
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 导入工具模块
from .tools.holiday import HolidayTools
from .tools.lunar import LunarTools
from .tools.weekday import WeekdayTools
from .utils.logger import setup_logger

# 设置日志
logger = setup_logger(__name__)

# 创建服务器实例
server = Server("china-festival-mcp")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """列出所有可用工具"""
    tools = []
    
    # 添加节假日工具
    tools.extend(HolidayTools.get_tools())
    
    # 添加农历工具
    tools.extend(LunarTools.get_tools())
    
    # 添加星期几工具
    tools.extend(WeekdayTools.get_tools())
    
    logger.info(f"提供 {len(tools)} 个工具")
    return tools

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    """处理工具调用"""
    logger.info(f"调用工具: {name}, 参数: {arguments}")
    
    # 节假日工具
    holiday_tool_names = ["holiday_info", "current_year_holidays", "next_holiday", "current_year_work_days"]
    if name in holiday_tool_names:
        return await HolidayTools.handle_tool_call(name, arguments)
    
    # 农历工具
    lunar_tool_names = ["gregorian_to_lunar", "lunar_to_gregorian", "get_lunar_string", "get_24_lunar_feast", "get_8zi"]
    if name in lunar_tool_names:
        return await LunarTools.handle_tool_call(name, arguments)
    
    # 星期几工具
    weekday_tool_names = ["get_weekday"]
    if name in weekday_tool_names:
        return await WeekdayTools.handle_tool_call(name, arguments)
    
    # 未知工具
    error_msg = f"未知工具: {name}"
    logger.error(error_msg)
    return [TextContent(type="text", text=error_msg)]

async def main():
    """主函数"""
    logger.info("启动中国节假日MCP服务器...")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())