# MCP管理平台

MCP管理平台是一个用于管理和监控各种工具、配置、模板和日志的综合性系统。该平台提供了友好的用户界面，可以方便地创建、编辑、删除和调用各类工具，管理系统和应用配置，以及查看运行日志。

## 功能特性

- **工具管理**：创建、编辑、激活/停用和删除工具，支持工具调用测试
- **配置管理**：管理系统和应用的配置信息，支持不同配置类型和状态
- **模板管理**：创建和管理工具模板，快速从模板导入创建新工具
- **日志系统**：记录所有工具调用和系统操作日志，支持按类型和级别筛选
- **仪表盘**：展示系统概览数据和统计信息
- **用户认证**：提供用户注册、登录和权限管理功能
- **Swagger API文档**：完整的API接口文档，方便开发和集成

## 技术栈

### 前端
- Vue.js 3 (使用Composition API)
- Vite 构建工具
- Element Plus 组件库
- Axios 用于API请求
- Vue Router 路由管理
- Pinia 状态管理
- Vue I18n 国际化支持

### 后端
- Flask Web框架
- SQLAlchemy ORM
- SQLite/MySQL 数据库
- Flask-CORS 跨域支持
- Flasgger Swagger文档
- JWT 用户认证

## 安装与部署

### 方式一：常规安装

#### 要求
- Node.js 14+
- Python 3.8+
- npm 或 yarn

#### 后端安装

```bash
# 进入后端目录
cd backend

# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 创建环境变量文件
cp .env.example .env
# 编辑.env文件，设置适当的配置值

# 初始化数据库
python -m migrations.migration_manager upgrade

# 启动服务器
python app.py
```

后端服务默认运行在 http://localhost:5005

#### 前端安装

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
# 或 yarn install

# 开发模式启动
npm run dev
# 或 yarn dev

# 构建生产版本
npm run build
# 或 yarn build
```

前端开发服务器默认运行在 http://localhost:3003

### 方式二：Docker部署

#### 要求
- Docker 19+
- Docker Compose 1.25+

#### 使用Docker Compose部署

```bash
# 克隆代码库
git clone https://github.com/xiaoshi7915/mcp-platform.git
cd mcp-platform

# 创建环境变量文件
cp .env.example .env
# 编辑.env文件，设置适当的配置值

# 使用Docker Compose启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

服务将在 http://localhost:5005 上运行

#### 仅使用Dockerfile部署

```bash
# 克隆代码库
git clone https://github.com/xiaoshi7915/mcp-platform.git
cd mcp-platform

# 创建环境变量文件
cp .env.example .env
# 编辑.env文件，设置适当的配置值

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

### 安全配置指南

在生产环境部署时，请务必进行以下安全配置：

1. **环境变量设置**
   - 使用强随机生成的密钥作为 `SECRET_KEY`
   - 不要在代码或公开仓库中存储敏感信息，使用 `.env` 文件管理
   - 确保 `.env` 文件被添加到 `.gitignore` 中

2. **数据库安全**
   - 使用强密码保护数据库
   - 限制数据库服务器对外访问权限
   - 定期备份数据库

3. **容器安全**
   - 定期更新Docker镜像和依赖
   - 使用非root用户运行容器
   - 限制容器网络和资源访问权限

4. **Web服务器**
   - 在生产环境中使用反向代理（如Nginx）
   - 配置SSL/TLS加密（HTTPS）
   - 设置适当的安全标头

#### 示例Nginx配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 重定向HTTP到HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # 安全标头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 反向代理到MCP平台
    location / {
        proxy_pass http://localhost:5005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 数据库迁移

MCP平台支持数据库迁移，方便在不同版本之间升级和回滚数据库结构。

### 创建迁移

```bash
# 进入后端目录
cd backend

# 生成新的迁移文件
python -m migrations.migration_manager generate add_new_feature
```

这将在 `backend/migrations/versions/` 目录下创建一个新的迁移文件，您需要编辑此文件，在 `upgrade()` 和 `downgrade()` 函数中实现数据库更改。

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

## 使用说明

### 工具管理

1. 在侧边菜单点击"工具管理"进入工具列表页面
2. 点击"新建工具"按钮创建新工具
3. 填写工具名称、类型、命令和配置等信息
4. 在工具列表中可以直接启用/停用、查看详情和删除工具
5. 在工具详情页可以：
   - 编辑工具信息
   - 启用/停用工具
   - 调用测试工具
   - 查看工具调用日志

### 配置管理

1. 在侧边菜单点击"配置管理"进入配置列表页面
2. 点击"新建配置"按钮创建新配置
3. 填写配置名称、类型和内容（支持JSON编辑器和表单编辑两种模式）
4. 在配置列表中可以直接查看详情和删除配置
5. 在配置详情页可以：
   - 编辑配置信息
   - 启用/停用配置
   - 查看配置详细内容

### 模板管理

1. 在侧边菜单点击"模板库"进入模板列表页面
2. 点击"新建模板"按钮创建新模板
3. 填写模板名称、类型、应用场景和内容
4. 在模板列表中可以直接导入创建工具、查看详情和删除模板
5. 在模板详情页可以编辑模板信息

### 日志管理

1. 在侧边菜单点击"日志管理"进入日志列表页面
2. 可以按工具ID、日志级别和时间范围筛选日志
3. 点击日志记录查看详情，包括调用参数和结果

### 用户管理

1. 在侧边菜单点击"用户管理"进入用户列表页面
2. 管理员可以创建、编辑和删除用户
3. 可以设置用户权限和状态

## API文档

### Swagger在线文档

应用启动后，可以通过以下地址访问Swagger在线API文档：

```
http://localhost:5005/docs
```

如果访问不到文档，请检查以下事项：
1. 确认已安装flasgger包: `pip install flasgger`
2. 确认后端服务正在运行
3. 检查后端日志是否有错误信息

在文档页面，您可以查看所有API接口的详细说明，并可以直接在浏览器中测试API调用。

### 工具相关API

| 接口                    | 方法   | 描述                     | 参数                                        |
|------------------------|-------|--------------------------|---------------------------------------------|
| /api/tools             | GET   | 获取工具列表              | `page`, `per_page`, `search`, `type`, `status` |
| /api/tools/:id         | GET   | 获取单个工具详情          | `id`: 工具ID                                  |
| /api/tools             | POST  | 创建新工具                | 工具信息JSON对象                               |
| /api/tools/:id         | PUT   | 更新工具信息              | `id`: 工具ID, 工具信息JSON对象                 |
| /api/tools/:id         | DELETE| 删除工具                  | `id`: 工具ID                                  |
| /api/tools/:id/activate| POST  | 激活工具                  | `id`: 工具ID                                  |
| /api/tools/:id/deactivate| POST| 停用工具                  | `id`: 工具ID                                  |
| /api/tools/:id/invoke  | POST  | 调用工具                  | `id`: 工具ID, 调用参数JSON对象                 |

### 配置相关API

| 接口                      | 方法   | 描述                     | 参数                                       |
|--------------------------|-------|--------------------------|-------------------------------------------|
| /api/configs             | GET   | 获取配置列表              | `page`, `per_page`, `search`, `type`       |
| /api/configs/:id         | GET   | 获取单个配置详情          | `id`: 配置ID                               |
| /api/configs             | POST  | 创建新配置                | 配置信息JSON对象                            |
| /api/configs/:id         | PUT   | 更新配置信息              | `id`: 配置ID, 配置信息JSON对象              |
| /api/configs/:id         | DELETE| 删除配置                  | `id`: 配置ID                               |
| /api/configs/:id/activate| POST  | 激活配置                  | `id`: 配置ID                               |
| /api/configs/:id/deactivate| POST| 停用配置                  | `id`: 配置ID                               |

### 日志相关API

| 接口                  | 方法   | 描述                     | 参数                                        |
|----------------------|-------|--------------------------|---------------------------------------------|
| /api/logs            | GET   | 获取日志列表              | `page`, `per_page`, `tool_id`, `level`, `start_date`, `end_date` |
| /api/logs/:id        | GET   | 获取单个日志详情          | `id`: 日志ID                                 |
| /api/logs/tool/:id   | GET   | 获取工具相关的日志        | `id`: 工具ID, `page`, `per_page`             |
| /api/logs            | POST  | 创建日志                  | 日志信息JSON对象                              |
| /api/logs/:id        | DELETE| 删除日志                  | `id`: 日志ID                                 |
| /api/logs/clear      | POST  | 清空日志                  | 筛选参数JSON对象（可选）                      |

### 模板相关API

| 接口                     | 方法   | 描述                     | 参数                                     |
|-------------------------|-------|--------------------------|------------------------------------------|
| /api/templates          | GET   | 获取模板列表              | `page`, `per_page`, `search`, `type`     |
| /api/templates/:id      | GET   | 获取单个模板详情          | `id`: 模板ID                             |
| /api/templates          | POST  | 创建新模板                | 模板信息JSON对象                          |
| /api/templates/:id      | PUT   | 更新模板信息              | `id`: 模板ID, 模板信息JSON对象            |
| /api/templates/:id      | DELETE| 删除模板                  | `id`: 模板ID                             |
| /api/templates/:id/import| POST | 从模板导入创建工具        | `id`: 模板ID, 自定义参数JSON对象（可选）   |

### 用户认证API

| 接口                   | 方法   | 描述                     | 参数                                    |
|-----------------------|-------|--------------------------|----------------------------------------|
| /api/auth/login       | POST  | 用户登录                  | `username`, `password`                  |
| /api/auth/register    | POST  | 用户注册                  | `username`, `password`, `email`         |
| /api/auth/logout      | POST  | 用户退出                  | 需要认证Token                            |
| /api/auth/profile     | GET   | 获取用户信息              | 需要认证Token                            |
| /api/auth/profile     | PUT   | 更新用户信息              | 需要认证Token, 用户信息JSON对象          |
| /api/auth/change-password | POST | 修改密码               | 需要认证Token, `old_password`, `new_password` |

## 项目维护

### 代码提交到GitHub

```bash
# 克隆仓库 (如果尚未克隆)
git clone https://github.com/xiaoshi7915/mcp-platform.git
cd mcp-platform

# 创建并配置.gitignore文件，确保敏感信息不会被提交
# 确保.env文件不被上传，使用.env.example作为模板

# 添加文件
git add .

# 提交更改
git commit -m "更新说明: 添加了xxx功能"

# 推送到GitHub
git push origin main
```

### 管理敏感信息

- 使用`.env`文件存储敏感信息，该文件不应该被提交到版本控制系统
- 创建`.env.example`作为模板，提供配置项但不包含实际敏感信息
- 在部署时，根据`.env.example`创建适合的`.env`文件

## 开发进度

- [x] 基础架构设计与实现
- [x] 工具管理功能
- [x] 配置管理功能
- [x] 日志系统实现
- [x] 仪表盘页面
- [x] 模板管理功能
- [x] 用户认证系统
- [x] API文档（Swagger）
- [x] Docker部署支持
- [x] 数据库迁移功能
- [x] 安全配置指南
- [ ] 多语言支持
- [ ] 接口权限控制
- [ ] 工具执行队列
- [ ] 系统监控告警
- [ ] 定时任务功能

## 故障排除

### Swagger文档不可访问

如果无法访问Swagger文档页面(http://localhost:5005/docs)，请尝试以下解决方法：

1. 确认后端服务正在运行并监听在端口5005
2. 检查是否已安装flasgger包: `pip install flasgger`
3. 查看后端服务日志是否有错误信息
4. 尝试访问 http://localhost:5005/docs/swagger.json 查看原始API文档数据

### 数据库迁移失败

如果数据库迁移失败，请尝试以下解决方法：

1. 检查迁移文件中的SQL语法是否正确
2. 确认数据库连接配置正确
3. 查看数据库日志是否有错误信息
4. 尝试手动执行迁移SQL语句

## 贡献

欢迎提交问题报告和功能建议。如果您希望贡献代码，请先创建issue讨论您想要实现的功能或修复的bug。

## 许可

MIT 