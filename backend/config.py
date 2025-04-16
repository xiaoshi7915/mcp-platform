#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置基类"""
    # 调试模式
    DEBUG = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    
    # 密钥
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key_for_development_only')
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///mcp_platform.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MCP工具配置目录
    MCP_TOOLS_DIR = os.environ.get('MCP_TOOLS_DIR', os.path.join(os.getcwd(), 'mcp_tools'))
    
    # 日志目录
    LOG_DIR = os.environ.get('LOG_DIR', os.path.join(os.getcwd(), 'logs'))
    
    # 模板目录
    TEMPLATE_DIR = os.environ.get('TEMPLATE_DIR', os.path.join(os.getcwd(), 'templates'))
    
    # 每页显示数量
    PER_PAGE = int(os.environ.get('PER_PAGE', 10))

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    
    # 使用SQLite数据库（如果没有在环境变量中指定）
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///mcp_platform.db')

class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    TESTING = True
    
    # 测试数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///mcp_platform_test.db'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    
    # 生产环境默认使用MySQL数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///mcp_platform.db')

# 配置映射
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# 获取当前环境配置
def get_config():
    flask_env = os.environ.get('FLASK_ENV', 'development')
    return config_by_name.get(flask_env, config_by_name['default']) 