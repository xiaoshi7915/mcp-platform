#!/usr/bin/env python
# -*- coding: utf-8 -*-
from backend.models.db import db, BaseModel
import json

# 配置类型枚举
CONFIG_TYPES = [
    'tool',          # 工具配置
    'environment',   # 环境配置
    'system',        # 系统配置
    'user',          # 用户配置
    'other'          # 其他配置
]

class Config(db.Model, BaseModel):
    """配置模型"""
    __tablename__ = 'configs'
    
    # 配置ID
    id = db.Column(db.Integer, primary_key=True)
    # 配置名称
    name = db.Column(db.String(100), nullable=False, unique=True)
    # 配置描述
    description = db.Column(db.Text, nullable=True)
    # 配置类型
    type = db.Column(db.String(50), nullable=False)
    # 配置内容（JSON格式）
    content = db.Column(db.Text, nullable=False)
    # 是否激活
    is_active = db.Column(db.Boolean, default=True)
    
    def __init__(self, name, content, type='other', description=None):
        """
        初始化配置实例
        
        Args:
            name: 配置名称
            content: 配置内容
            type: 配置类型
            description: 配置描述
        """
        self.name = name
        self.description = description
        self.type = type if type in CONFIG_TYPES else 'other'
        
        # 如果内容是字典，转换为JSON字符串
        if isinstance(content, dict):
            self.content = json.dumps(content)
        else:
            self.content = content
            
        self.is_active = True
    
    def get_content(self):
        """获取配置内容（解析JSON）"""
        if self.content:
            try:
                return json.loads(self.content)
            except:
                return {}
        return {}
    
    def set_content(self, content):
        """设置配置内容（转换为JSON）"""
        if isinstance(content, dict):
            self.content = json.dumps(content)
        else:
            self.content = content
    
    def to_dict(self):
        """转换为字典（包括解析的内容）"""
        config_dict = super().to_dict()
        # 将内容JSON字符串转换为Python字典
        config_dict['content'] = self.get_content()
        return config_dict 