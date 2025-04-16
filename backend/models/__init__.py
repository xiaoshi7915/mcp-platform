#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .db import db, BaseModel
from .tool import Tool, TOOL_TYPES, TOOL_STATUS
from .log import Log, LOG_LEVELS
from .config import Config, CONFIG_TYPES
from .template import Template
from backend.models.user import User

# 所有模型类列表，用于数据库初始化
models = [
    Tool,
    Log,
    Config,
    Template,
    User
] 

"""
数据模型包

此包包含应用程序的所有数据模型，包括：
- 工具模型
- 配置模型
- 日志模型
- 模板模型
- 用户模型
""" 