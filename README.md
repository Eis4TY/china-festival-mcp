# 中国节假日MCP服务器

一个基于模型上下文协议（MCP）的中国节假日和农历信息服务器，为AI助手提供准确的法定节假日、调休安排、中国传统节日、农历转换、二十四节气和八字计算功能。西方节日都是固定公历日期，不需要查询工具。

## 🌟 功能特性

- **节假日查询**: 查询中国法定节假日、传统节日和调休安排
- **农历转换**: 公历与农历日期相互转换
- **农历信息**: 获取详细的农历日期描述，包括生肖、干支等
- **二十四节气**: 查询二十四节气信息和季节划分
- **八字计算**: 根据出生日期时间计算四柱八字和五行属性
- **错误处理**: 完善的参数验证和错误处理机制
- **日志记录**: 详细的操作日志和性能监控
- **FastMCP架构**: 基于官方推荐的FastMCP框架，提供更好的性能和稳定性

## 🏗️ 技术架构

本项目采用了官方推荐的FastMCP框架重构，相比传统MCP实现具有以下优势：

### FastMCP 核心特性

- **简化的工具注册**: 使用 `@mcp.tool()` 装饰器，代码更简洁直观
- **自动类型验证**: FastMCP自动处理参数验证和类型转换，减少手动验证代码
- **更好的错误处理**: 统一的异常处理机制，自动包装错误响应
- **性能优化**: 更高效的请求处理和资源管理，支持异步操作
- **标准化接口**: 完全符合MCP协议最佳实践
- **开发体验**: 提供丰富的开发工具和调试信息

### 架构对比

| 特性 | 传统MCP | FastMCP |
|------|---------|----------|
| 工具注册 | 手动注册 | 装饰器自动注册 |
| 类型验证 | 手动验证 | 自动验证 |
| 错误处理 | 手动包装 | 自动处理 |
| 代码量 | 较多 | 显著减少 |
| 维护性 | 中等 | 优秀 |
| 性能 | 良好 | 更优 |

## 📦 安装

### 环境要求

- Python 3.8+
- FastMCP 2.11.3+
- 支持MCP协议的AI客户端（如Claude Desktop）

### 快速安装（推荐）

使用uvx可以直接运行，无需手动管理依赖：

```bash
# 克隆项目
git clone https://github.com/your-username/china-festival-mcp.git
cd china-festival-mcp

# 直接运行（uvx会自动安装依赖）
uvx --from . python -m src.server_fastmcp
```

### 传统安装方式

1. 克隆项目
```bash
git clone https://github.com/your-username/china-festival-mcp.git
cd china-festival-mcp
```

2. 安装依赖
```bash
pip install fastmcp httpx pydantic psutil
```

## 🚀 使用方法

### 方法一：使用uvx运行（推荐）

使用uvx可以直接运行，无需创建虚拟环境：

```bash
uvx --from . python -m src.server_fastmcp
```

### 方法二：传统方式运行

```bash
python -m src.server_fastmcp
```

## ⚙️ MCP客户端配置

本项目提供了多种MCP客户端配置方式，适用于不同的使用场景。配置文件位于项目根目录：

- `mcp_client_config.json` - 基础配置文件
- `mcp_config_examples.json` - 详细配置示例

### Claude Desktop配置

#### 方式一：使用uvx（推荐）

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "china-festival-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "china-festival-mcp",
        "fastmcp",
        "run",
        "src/server_fastmcp.py:mcp"
      ]
    }
  }
}
```

#### 方式二：本地开发

```json
{
  "mcpServers": {
    "china-festival-mcp": {
      "command": "python3",
      "args": ["-m", "src.server_fastmcp"],
      "cwd": "/path/to/china-festival-mcp",
      "env": {
        "PYTHONPATH": ".",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Cline VSCode扩展配置

在Cline设置中添加MCP服务器：

```json
{
  "mcpServers": {
    "china-festival-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "china-festival-mcp",
        "fastmcp",
        "run",
        "src/server_fastmcp.py:mcp"
      ]
    }
  }
}
```

### 其他MCP客户端

对于其他支持MCP协议的客户端，请参考 `mcp_config_examples.json` 文件中的详细配置示例。

### 配置说明

- **command**: 执行命令，推荐使用 `uvx` 进行依赖管理
- **args**: 命令参数，FastMCP使用 `fastmcp run` 启动服务器
- **cwd**: 工作目录，设置为项目根目录
- **env**: 环境变量，可设置日志级别等参数

## 📚 API文档

### 节假日工具

#### `holiday_info`
查询指定日期的节假日信息，包含是否为节假日的判断

**参数:**
- `date` (string, 可选): 日期，格式为 YYYY-MM-DD，不指定则查询当前日期

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

**参数:**
无

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

**参数:**
无

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

**参数:**
无

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

**参数:**
- `date` (string): 公历日期，格式为 YYYY-MM-DD

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

**参数:**
- `year` (integer): 农历年份
- `month` (integer): 农历月份
- `day` (integer): 农历日期
- `is_leap` (boolean, 可选): 是否闰月，默认false

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

**参数:**
- `date` (string): 公历日期，格式为 YYYY-MM-DD

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

**参数:**
- `date` (string): 日期，格式为 YYYY-MM-DD

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

**参数:**
- `date` (string): 日期，格式为 YYYY-MM-DD
- `hour` (integer, 可选): 小时，0-23，默认12
- `minute` (integer, 可选): 分钟，0-59，默认0

**返回:**
```json
{
  "eight_characters": "甲辰 丙寅 甲子 庚午"
}
```

### 日期工具

#### `get_weekday`
根据公历日期计算星期几

**参数:**
- `date` (string): 日期，格式为 YYYY-MM-DD，如：2024-01-01

**返回:**
```json
{
  "weekday_number": 1,
  "weekday_name_zh": "星期一",
  "weekday_name_en": "Monday",
  "date": "2024-01-01"
}
```

## 🧪 测试

运行基础测试：
```bash
python tests/test_server.py
```

运行全面测试：
```bash
python tests/comprehensive_test.py
```

运行性能测试：
```bash
python tests/performance_test.py
```

## 📁 项目结构

```
china-festival-mcp/
├── src/                       # 核心源代码
│   ├── __init__.py
│   ├── server.py              # 传统MCP服务器（已弃用）
│   ├── server_fastmcp.py      # FastMCP服务器主程序
│   ├── data/                  # 数据模块
│   │   ├── bazi_calculator.py # 八字计算模块
│   │   └── solar_terms.py     # 二十四节气数据
│   ├── tools/                 # 工具模块
│   │   ├── holiday.py         # 节假日查询工具
│   │   ├── lunar.py           # 农历转换工具
│   │   └── weekday.py         # 星期计算工具
│   └── utils/                 # 工具函数
│       ├── cache.py           # 缓存管理
│       ├── date_utils.py      # 日期工具
│       ├── error_handler.py   # 错误处理
│       ├── logger.py          # 日志管理
│       └── performance.py     # 性能监控
├── tests/                     # 测试文件
│   ├── comprehensive_test.py  # 综合测试
│   ├── performance_test.py    # 性能测试
│   ├── test_server.py         # 服务器测试
│   ├── test_24_lunar_feast_format.py
│   └── test_8zi_format.py
├── docs/                      # 文档
│   ├── INSTALLATION_GUIDE.md  # 安装指南
│   ├── USAGE_EXAMPLES.md      # 使用示例
│   └── 中国节假日MCP_PRD.md   # 产品需求文档
├── scripts/                   # 参考脚本
│   ├── CalendarConvert.py     # 日历转换参考
│   └── holiday_query.py       # 节假日查询参考
├── logs/                      # 日志文件（git忽略）
├── build/                     # 构建文件（git忽略）
├── venv/                      # 虚拟环境（git忽略）
├── .gitignore                 # Git忽略文件
├── pyproject.toml             # 项目配置和依赖
├── README.md                  # 项目说明
├── LICENSE                    # 许可证
├── mcp_client_config.json     # MCP客户端配置
└── mcp_config_examples.json   # 配置示例
│   ├── tools/
│   │   ├── holiday.py         # 节假日查询工具
│   │   ├── lunar.py           # 农历相关工具
│   │   └── weekday.py         # 星期几查询工具
│   └── utils/
│       ├── cache.py           # 缓存工具
│       ├── date_utils.py      # 日期工具
│       ├── error_handler.py   # 错误处理
│       ├── logger.py          # 日志记录
│       └── performance.py     # 性能监控
├── test_server.py             # 基础测试脚本
├── comprehensive_test.py      # 全面测试脚本
├── pyproject.toml            # 项目配置（已更新为FastMCP）
└── README.md                 # 项目文档
```

## 🔧 配置

### 日志配置

日志文件默认保存在 `logs/` 目录下，按日期分割。可以通过环境变量配置：

```bash
export LOG_LEVEL=INFO
export LOG_DIR=./logs
```

### 缓存配置

支持内存缓存以提高性能，可以通过环境变量配置：

```bash
export CACHE_ENABLED=true
export CACHE_TTL=3600
```


## 🙏 致谢

本项目基于 [PyLunar](https://github.com/swordzjj/PyLunar/tree/master) 项目和 [holiday-cn](https://github.com/NateScarlet/holiday-cn)项目开发，感谢原作者的贡献。

- 感谢所有贡献者
- 基于传统农历算法和现代计算方法
- 参考了多个开源农历转换项目
