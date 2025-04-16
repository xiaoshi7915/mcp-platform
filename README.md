# MCP管理平台

MCP管理平台是一个用于管理和监控各种工具、配置、模板和日志的综合性系统。该平台提供了友好的用户界面，可以方便地创建、编辑、删除和调用各类工具，管理系统和应用配置，以及查看运行日志。

## 功能特性

- **工具管理**：创建、编辑、激活/停用和删除工具，支持工具调用测试
- **配置管理**：管理系统和应用的配置信息，支持不同配置类型和状态
- **模板管理**：创建和管理工具模板，快速从模板导入创建新工具
- **日志系统**：记录所有工具调用和系统操作日志，支持按类型和级别筛选
- **仪表盘**：展示系统概览数据和统计信息
- **用户认证**：提供用户注册、登录和权限管理功能

## 安装与部署

### 方式一：常规安装

#### 后端安装

```bash
# 克隆代码库
git clone https://github.com/xiaoshi7915/mcp-platform.git
cd mcp-platform

cd backend

python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

pip install -r requirements.txt

# 创建环境变量文件
cp .env.example .env
# 编辑.env文件，设置适当的配置值

# 初始化数据库
python -m migrations.migration_manager upgrade

# 启动服务器
python app.py
```
#### 前端安装

```bash
cd frontend

npm install
# 或 yarn install

# 开发模式启动
npm run dev
# 或 yarn dev

# 构建生产版本
npm run build
# 或 yarn build
```

### 方式二：Docker部署

#### 使用Docker Compose部署

```bash
# 克隆代码库
git clone https://github.com/xiaoshi7915/mcp-platform.git
cd mcp-platform

# 创建环境变量文件
cp .env.example .env

# 使用Docker Compose启动服务
docker-compose up -d
```
#### 仅使用Dockerfile部署

```bash
# 克隆代码库
git clone https://github.com/xiaoshi7915/mcp-platform.git
cd mcp-platform

# 创建环境变量文件
cp .env.example .env

# 构建Docker镜像
docker build -t mcp-platform .

# 运行容器
docker run -d -p 5005:5005 --name mcp-platform \
  --env-file .env \
  -v ./data:/app/data \
  -v ./logs:/app/logs \
  -v ./mcp_tools:/app/mcp_tools \
  -v ./templates:/app/templates \
  mcp-platform
```

## 数据库迁移

MCP平台支持数据库迁移，方便在不同版本之间升级和回滚数据库结构。

### 创建迁移

```bash
cd backend

# 生成新的迁移文件
python -m migrations.migration_manager generate add_new_feature
```
### 应用迁移

```bash
# 应用所有迁移
python -m migrations.migration_manager upgrade
```

### 回滚迁移

```bash
# 回滚所有迁移
python -m migrations.migration_manager downgrade
```

## 贡献

欢迎提交问题报告和功能建议。如果您希望贡献代码，请先创建issue讨论您想要实现的功能或修复的bug。

## 许可

MIT 
