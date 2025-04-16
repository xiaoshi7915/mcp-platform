#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# 确保可以导入当前目录的模块
# sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.models.db import db
from backend.routes.tool_routes import tool_bp
from backend.routes.config_routes import config_bp
from backend.routes.log_routes import log_bp
from backend.routes.dashboard_routes import dashboard_bp
from backend.routes.template_routes import template_bp
from backend.routes.auth_routes import auth_bp

def create_app(config_class=Config):
    """
    创建并配置Flask应用
    
    Args:
        config_class: 配置类，默认使用Config类
        
    Returns:
        配置好的Flask应用实例
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化CORS
    CORS(app)
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册蓝图
    app.register_blueprint(tool_bp, url_prefix='/api/tools')
    app.register_blueprint(config_bp, url_prefix='/api/configs')
    app.register_blueprint(log_bp, url_prefix='/api/logs')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(template_bp, url_prefix='/api/templates')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        """处理404错误"""
        return jsonify({"error": "资源不存在"}), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """处理500错误"""
        return jsonify({"error": "服务器内部错误"}), 500
    
    @app.route('/api/health')
    def health_check():
        """健康检查接口"""
        return jsonify({"status": "ok", "port": "5005"})
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5005, debug=True) 