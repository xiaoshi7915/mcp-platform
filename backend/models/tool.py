#!/usr/bin/env python
# -*- coding: utf-8 -*-
from backend.models.db import db, BaseModel
import json

# 工具类型枚举
TOOL_TYPES = [
    'filesystem',    # 文件系统工具
    'network',       # 网络工具
    'data_analysis', # 数据分析工具
    'media',         # 媒体处理工具
    'system',        # 系统工具
    'puppeteer',     # 浏览器自动化工具
    'other'          # 其他类型
]

# 工具状态枚举
TOOL_STATUS = [
    'active',        # 活跃状态
    'inactive',      # 非活跃状态
    'error'          # 错误状态
]

class Tool(db.Model, BaseModel):
    """MCP工具模型"""
    __tablename__ = 'tools'
    
    # 工具ID
    id = db.Column(db.Integer, primary_key=True)
    # 工具名称
    name = db.Column(db.String(100), nullable=False, unique=True)
    # 工具描述
    description = db.Column(db.Text, nullable=True)
    # 工具类型
    type = db.Column(db.String(50), nullable=False)
    # 工具状态
    status = db.Column(db.String(20), default='inactive')
    # 工具命令
    command = db.Column(db.String(200), nullable=True)
    # 工具配置（JSON格式）
    config = db.Column(db.Text, nullable=True)
    # 最近调用时间
    last_invoked_at = db.Column(db.DateTime, nullable=True)
    # 调用次数
    invoke_count = db.Column(db.Integer, default=0)
    
    def __init__(self, name, description=None, type='other', command=None, config=None):
        """
        初始化工具实例
        
        Args:
            name: 工具名称
            description: 工具描述
            type: 工具类型
            command: 工具命令
            config: 工具配置
        """
        self.name = name
        self.description = description
        self.type = type if type in TOOL_TYPES else 'other'
        self.command = command
        
        # 如果配置是字典，转换为JSON字符串
        if isinstance(config, dict):
            self.config = json.dumps(config)
        else:
            self.config = config
            
        self.status = 'inactive'
        self.invoke_count = 0
    
    def get_config(self):
        """获取工具配置（解析JSON）"""
        if self.config:
            try:
                return json.loads(self.config)
            except:
                return {}
        return {}
    
    def set_config(self, config):
        """设置工具配置（转换为JSON）"""
        if isinstance(config, dict):
            self.config = json.dumps(config)
        else:
            self.config = config
    
    def to_dict(self):
        """转换为字典（包括解析的配置）"""
        tool_dict = super().to_dict()
        # 将配置JSON字符串转换为Python字典
        tool_dict['config'] = self.get_config()
        return tool_dict 