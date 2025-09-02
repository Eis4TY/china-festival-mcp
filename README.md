# 中国节假日MCP服务器

一个基于模型上下文协议（MCP）的中国节假日和农历信息服务器，为AI助手提供准确的法定节假日、调休安排、中国传统节日、农历转换、二十四节气和八字计算功能。西方节日都是固定公历日期，不需要查询工具。

## 🌟 功能特性

- **节假日查询**: 查询中国法定节假日、传统节日和调休安排
- **农历转换**: 公历与农历日期相互转换
- **农历信息**: 获取详细的农历日期描述，包括生肖、干支等
- **二十四节气**: 查询二十四节气信息和季节划分
- **八字计算**: 根据出生日期时间计算四柱八字和五行属性
- **FastMCP架构**: 基于官方推荐的FastMCP框架，提供更好的性能和稳定性

## 🏗️ 技术架构

本项目基于官方推荐的FastMCP框架开发，具有以下特性：

- **简化的工具注册**: 使用 `@mcp.tool()` 装饰器
- **自动类型验证**: 自动处理参数验证和类型转换
- **标准化接口**: 完全符合MCP协议最佳实践

## 📦 安装

### 环境要求

- Python 3.8+
- 支持MCP协议的AI客户端（如Claude Desktop）

### 使用uvx安装（推荐）

```bash
# 直接从PyPI安装并运行
uvx china-festival-mcp
```

### 本地开发安装

```bash
# 克隆项目
git clone https://github.com/your-username/china-festival-mcp.git
cd china-festival-mcp

# 使用uvx运行（会自动安装依赖）
uvx --from . python -m src.server_fastmcp
```

## 🚀 使用方法

```bash
# 从PyPI直接运行
uvx china-festival-mcp

# 或本地开发运行
uvx --from . python -m src.server_fastmcp
```

## ⚙️ MCP客户端配置

### Claude Desktop配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：

#### 从PyPI安装（推荐）

```json
{
  "mcpServers": {
    "china-festival-mcp": {
      "command": "uvx",
      "args": ["china-festival-mcp"]
    }
  }
}
```

#### 本地开发

```json
{
  "mcpServers": {
    "china-festival-mcp": {
      "command": "uvx",
      "args": ["--from", ".", "python", "-m", "src.server_fastmcp"],
      "cwd": "/path/to/china-festival-mcp"
    }
  }
}
```

### 其他MCP客户端

对于其他支持MCP协议的客户端，使用相同的uvx配置方式：

```json
{
  "mcpServers": {
    "china-festival-mcp": {
      "command": "uvx",
      "args": ["china-festival-mcp"]
    }
  }
}
```

## 📚 API文档

### 节假日工具

#### `holiday_info`
查询指定日期的节假日信息，包含是否为节假日的判断

**返回:**
```json
{
  "date": "2024-01-01",
  "name": "元旦",
  "type": "holiday",
  "is_holiday": true,
  "is_work_day": false,
  "note": "法定节假日",
  "weekday_name_en": "Monday"
}
```

#### `next_holiday`
获取下一个节假日

**返回:**
```json
{
  "name": "春节",
  "date": "2024-02-10",
  "days_until": 40,
  "note": "法定节假日",
  "weekday_name_en": "Saturday"
}
```

#### `current_year_holidays`
获取当前年份所有节假日

**返回:**
```json
{
  "year": 2024,
  "holidays": [
    {
      "date": "2024-01-01",
      "name": "元旦",
      "note": "法定节假日"
    }
  ],
  "total_count": 1
}
```

#### `current_year_work_days`
获取当前年份调休工作日安排

**返回:**
```json
{
  "year": 2024,
  "work_days": [
    {
      "date": "2024-02-04",
      "name": "春节调休",
      "note": "调休工作日"
    }
  ],
  "total_count": 1
}
```

### 农历工具

#### `gregorian_to_lunar`
公历转农历

**返回:**
```json
{
  "gregorian_date": "2024-01-01",
  "lunar_year": 2023,
  "lunar_month": 11,
  "lunar_day": 20,
  "is_leap_month": false,
  "zodiac": "兔"
}
```

#### `lunar_to_gregorian`
农历转公历

**返回:**
```json
{
  "lunar_date": "2023年十一月二十",
  "gregorian_year": 2024,
  "gregorian_month": 1,
  "gregorian_day": 1,
  "gregorian_date": "2024-01-01"
}
```

#### `get_lunar_string`
获取农历日期的详细中文描述

**返回:**
```json
{
  "gregorian_date": "2024-01-01",
  "lunar_year": 2023,
  "lunar_month": 11,
  "lunar_day": 20,
  "is_leap_month": false,
  "zodiac": "兔",
  "year_gan_zhi": "癸卯",
  "tian_gan": "癸",
  "di_zhi": "卯",
  "lunar_month_name": "十一月",
  "lunar_day_name": "二十",
  "lunar_string": "癸卯年 十一月 二十"
}
```

#### `get_24_lunar_feast`
获取二十四节气信息

**返回:**
```json
{
  "year": 2024,
  "month": 1,
  "solar_terms": [
    {
      "name": "小寒",
      "date": "2024-01-06",
      "days_until": 5,
      "season": "冬季"
    },
    {
      "name": "大寒",
      "date": "2024-01-20",
      "days_until": 19,
      "season": "冬季"
    }
  ]
}
```

#### `get_8zi`
计算八字（四柱）

**返回:**
```json
{
  "eight_characters": "甲辰 丙寅 甲子 庚午"
}
```

### 日期工具

#### `get_weekday`
根据公历日期计算星期几

**返回:**
```json
{
  "weekday_number": 1,
  "weekday_name_zh": "星期一",
  "weekday_name_en": "Monday",
  "date": "2024-01-01"
}
```

## 📁 项目结构

```
china-festival-mcp/
├── src/                       # 核心源代码
│   ├── __init__.py
│   ├── server_fastmcp.py      # FastMCP服务器主程序
│   ├── data/                  # 数据模块
│   │   ├── bazi_calculator.py # 八字计算模块
│   │   └── solar_terms.py     # 二十四节气数据
│   ├── tools/                 # 工具模块
│   │   ├── __init__.py
│   │   ├── holiday.py         # 节假日查询工具
│   │   ├── lunar.py           # 农历转换工具
│   │   └── weekday.py         # 星期计算工具
│   └── utils/                 # 工具函数
│       ├── __init__.py
│       ├── date_utils.py      # 日期工具
│       └── logger.py          # 日志管理
├── scripts/                   # 发布脚本
│   └── publish.py             # 自动发布脚本
├── test_solar_terms.py        # 节气测试脚本
├── .gitignore                 # Git忽略文件
├── pyproject.toml             # 项目配置和依赖
├── README.md                  # 项目说明
├── LICENSE                    # 许可证
├── PUBLISH_GUIDE.md           # 发布指南
└── publish.sh                 # 发布脚本
```




## 🙏 致谢

本项目基于 [PyLunar](https://github.com/swordzjj/PyLunar/tree/master) 项目和 [holiday-cn](https://github.com/NateScarlet/holiday-cn)项目开发，感谢原作者的贡献。
