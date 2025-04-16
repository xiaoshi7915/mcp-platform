# MCP管理平台开发文档

## 项目概览

MCP管理平台是一个用于管理大模型通用协议(Model Control Protocol)工具调用的综合管理系统。该平台提供直观的用户界面，帮助用户轻松管理、配置和监控各种MCP工具的运行状态和调用记录。

## 开发环境配置

### 系统要求
- Python 3.8+
- Node.js 16+
- npm 8+
- Git

### 环境搭建

1. **克隆代码库**
   ```bash
   git clone https://github.com/your-org/mcp_platform.git
   cd mcp_platform
   ```

2. **创建Python虚拟环境**
   ```bash
   # 使用conda创建虚拟环境
   conda create -n mcp_env python=3.8
   conda activate mcp_env
   
   # 安装后端依赖
   pip install -r requirements.txt
   ```

3. **安装前端依赖**
   ```bash
   cd frontend
   npm install
   ```

4. **配置环境变量**
   ```bash
   # 创建.env文件
   cp .env.example .env
   # 根据需要编辑.env文件
   ```

5. **初始化数据库**
   ```bash
   cd ../
   python -c "from backend.app import create_app; from backend.models.db import db; app = create_app(); app.app_context().push(); db.create_all()"
   ```

## 启动开发服务器

1. **启动后端服务**
   ```bash
   # 设置环境变量
   export FLASK_ENV=development
   export FLASK_DEBUG=True
   
   # 启动开发服务器
   python backend/app.py
   ```
   后端API将在 http://localhost:5005 上运行。

2. **启动前端服务**
   ```bash
   cd frontend
   npm run dev
   ```
   前端将在 http://localhost:3003 上运行。

## 功能开发状态

### 页面布局与设计

| 模块 | 状态 | 备注 |
|-----|------|------|
| 顶部导航栏 | ✅ 已完成 | 包含Logo、菜单和用户信息 |
| 左侧边栏 | ✅ 已完成 | 包含工具分类、搜索功能 |
| 主内容区 | ✅ 已完成 | 根据页面显示不同内容 |
| 底部状态栏 | ✅ 已完成 | 显示连接状态和版本信息 |
| 响应式设计 | ✅ 已完成 | 适配不同屏幕尺寸 |

### 功能模块开发

#### 仪表盘模块

| 功能 | 状态 | 备注 |
|-----|------|------|
| 概览统计 | ✅ 已完成 | 显示工具数量、状态统计 |
| 资源使用情况 | ✅ 已完成 | 显示CPU、内存使用情况 |
| 最近事件 | ✅ 已完成 | 显示最近的日志和事件 |
| 快速操作 | ✅ 已完成 | 添加工具、查看日志的快捷入口 |

#### 工具管理模块

| 功能 | 状态 | 备注 |
|-----|------|------|
| 工具列表 | ✅ 已完成 | 表格展示、搜索、筛选功能 |
| 工具详情 | ✅ 已完成 | 显示基本信息和配置参数 |
| 添加/编辑工具 | ✅ 已完成 | 表单验证、JSON配置编辑 |
| 启动/停止工具 | ✅ 已完成 | 状态管理功能 |
| 删除工具 | ✅ 已完成 | 删除确认功能 |
| 调用工具 | ❓ 部分完成 | 基础功能已完成，实际调用执行逻辑待完善 |

#### 配置管理模块

| 功能 | 状态 | 备注 |
|-----|------|------|
| 配置列表 | ✅ 已完成 | 表格展示、搜索、筛选功能 |
| 配置详情 | ✅ 已完成 | 显示配置详细信息 |
| 配置编辑器 | ✅ 已完成 | JSON编辑器、语法高亮 |
| 配置验证 | ✅ 已完成 | JSON格式验证功能 |
| 配置应用 | ✅ 已完成 | 应用配置到工具功能 |

#### 日志管理模块

| 功能 | 状态 | 备注 |
|-----|------|------|
| 日志列表 | ✅ 已完成 | 表格展示、搜索、筛选功能 |
| 日志详情 | ✅ 已完成 | 显示完整日志信息 |
| 日志过滤 | ✅ 已完成 | 按工具、级别、时间过滤 |
| 日志下载 | ✅ 已完成 | 支持CSV/JSON格式导出 |
| 实时日志流 | ❓ 部分完成 | 基础UI已完成，WebSocket推送待实现 |

#### 工具库模块

| 功能 | 状态 | 备注 |
|-----|------|------|
| 模板列表 | ✅ 已完成 | 展示可用的工具模板 |
| 模板详情 | ✅ 已完成 | 显示模板详细信息 |
| 模板导入 | ✅ 已完成 | 支持变量替换的导入功能 |
| 模板编辑 | ✅ 已完成 | 创建和编辑模板功能 |
| 模板导出 | ✅ 已完成 | 导出为JSON格式 |

## 代码规范

### 后端(Python)

- 遵循PEP 8编码规范
- 使用类型注解
- 编写docstring文档
- 单元测试覆盖率目标：80%+

### 前端(Vue.js)

- 遵循Vue风格指南
- 使用Composition API
- 组件采用.vue单文件组件
- 使用TypeScript类型注解

## 开发流程

1. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **开发功能**
   - 实现功能
   - 编写测试
   - 确保代码符合规范

3. **提交代码**
   ```bash
   git add .
   git commit -m "feat: 添加xxx功能"
   ```

4. **创建Pull Request**
   - 提交到远程仓库
   - 创建Pull Request
   - 等待代码审查

5. **合并到主分支**
   - 通过代码审查后合并
   - 删除功能分支

## 部署指南

### 开发环境
按照「开发环境配置」一节配置即可。

### 测试环境
```bash
# 后端
export FLASK_ENV=testing
python backend/app.py

# 前端
npm run build:test
```

### 生产环境
```bash
# 后端
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5005 "backend.app:create_app()"

# 前端
npm run build
# 配置Nginx服务静态文件
```

## 常见问题

### 1. 环境变量配置问题
确保.env文件中的配置正确，特别是数据库连接信息。

### 2. 前端构建失败
检查Node.js和npm版本是否满足要求，尝试清除node_modules并重新安装。

### 3. 后端启动错误
检查Python版本、依赖包是否完整安装，数据库是否正确配置。

## 联系与支持

- 项目负责人：[负责人姓名](mailto:email@example.com)
- 技术支持：[支持邮箱](mailto:support@example.com)
- 问题跟踪：[Issue Tracker](https://github.com/your-org/mcp_platform/issues) 