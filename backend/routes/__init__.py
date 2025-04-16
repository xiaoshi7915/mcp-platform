#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .tool_routes import tool_bp
from .config_routes import config_bp
from .log_routes import log_bp
from .dashboard_routes import dashboard_bp
from .template_routes import template_bp
from .auth_routes import auth_bp

# 所有路由蓝图列表，用于应用程序初始化
blueprints = [
    tool_bp,
    config_bp,
    log_bp,
    dashboard_bp,
    template_bp,
    auth_bp
] 