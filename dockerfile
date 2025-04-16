# Dockerfile
FROM python:3.11-slim

LABEL maintainer="MCP Platform Team"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        libssl-dev \
        pkg-config \
        nodejs \
        npm && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir flasgger flask-migrate

# 复制后端代码
COPY backend/ ./backend/

# 复制前端代码
COPY frontend/ ./frontend/

# 复制项目文件
COPY docs/ ./docs/
COPY README.md .

# 设置环境变量
ENV FLASK_APP=backend/app.py
ENV FLASK_ENV=production
ENV FLASK_DEBUG=False
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5005

# 前端构建
RUN cd frontend && \
    npm install && \
    npm run build && \
    cd ..

# 创建必要的目录
RUN mkdir -p logs mcp_tools templates

# 暴露端口
EXPOSE 5005

# 启动命令
CMD ["gunicorn", "-b", "0.0.0.0:5005", "--timeout", "120", "backend.app:create_app()"]