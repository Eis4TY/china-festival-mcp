# 中国节假日MCP服务器 - 安装配置指南

## 🚀 快速开始

### 1. 安装项目

```bash
# 克隆项目
git clone https://github.com/your-username/china-festival-mcp.git
cd china-festival-mcp

# 使用uvx直接运行（推荐）
uvx --from . python -m src.server_fastmcp
```

### 2. 配置MCP客户端

#### Claude Desktop

1. 打开Claude Desktop配置文件：
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. 添加以下配置：

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

3. 重启Claude Desktop

#### Cline VSCode扩展

1. 在VSCode中安装Cline扩展
2. 打开Cline设置
3. 在MCP服务器配置中添加：

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

## 🔧 高级配置

### 本地开发配置

如果您需要修改代码或进行本地开发：

```bash
# 安装依赖
pip install fastmcp httpx pydantic psutil

# 运行服务器
python -m src.server_fastmcp
```

对应的客户端配置：

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

### 环境变量配置

支持的环境变量：

- `LOG_LEVEL`: 日志级别（DEBUG, INFO, WARNING, ERROR）
- `PYTHONPATH`: Python模块搜索路径

## 🧪 测试安装

### 1. 测试服务器启动

```bash
# 使用uvx测试
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | uvx --from . python -m src.server_fastmcp
```

### 2. 测试工具调用

```bash
# 测试获取下一个节假日
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"next_holiday","arguments":{}}}' | uvx --from . python -m src.server_fastmcp
```

## 🐛 故障排除

### 常见问题

1. **命令未找到错误**
   ```
   command not found: uvx
   ```
   解决方案：安装uv工具
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **模块导入错误**
   ```
   ModuleNotFoundError: No module named 'fastmcp'
   ```
   解决方案：确保依赖已安装
   ```bash
   pip install fastmcp
   ```

3. **权限错误**
   ```
   Permission denied
   ```
   解决方案：检查文件权限或使用虚拟环境

### 日志查看

服务器运行时会生成日志文件，位于 `logs/` 目录下：

- `china_festival_mcp_YYYYMMDD.log`: 主服务器日志
- 其他工具模块的专用日志文件

## 📞 获取帮助

如果遇到问题，请：

1. 查看项目的 [README.md](./README.md) 文档
2. 检查 [Issues](https://github.com/your-username/china-festival-mcp/issues) 页面
3. 提交新的Issue描述您的问题

## 🔄 更新项目

```bash
# 拉取最新代码
git pull origin main

# 重新安装依赖（如果有更新）
uvx --from . python -m src.server_fastmcp
```

更新后记得重启您的MCP客户端以加载新版本。