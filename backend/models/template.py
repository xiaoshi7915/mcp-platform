#!/usr/bin/env python
# -*- coding: utf-8 -*-
from backend.models.db import db, BaseModel
import json

class Template(db.Model, BaseModel):
    """MCP工具模板模型"""
    __tablename__ = 'templates'
    
    # 模板ID
    id = db.Column(db.Integer, primary_key=True)
    # 模板名称
    name = db.Column(db.String(100), nullable=False, unique=True)
    # 模板描述
    description = db.Column(db.Text, nullable=True)
    # 工具类型
    type = db.Column(db.String(50), nullable=False)
    # 模板内容（JSON格式）
    content = db.Column(db.Text, nullable=False)
    # 适用场景
    scenarios = db.Column(db.String(200), nullable=True)
    
    def __init__(self, name, content, type, description=None, scenarios=None):
        """
        初始化模板实例
        
        Args:
            name: 模板名称
            content: 模板内容
            type: 工具类型
            description: 模板描述
            scenarios: 适用场景
        """
        self.name = name
        self.description = description
        self.type = type
        
        # 如果内容是字典，转换为JSON字符串
        if isinstance(content, dict):
            self.content = json.dumps(content)
        else:
            self.content = content
            
        self.scenarios = scenarios
    
    def get_content(self):
        """获取模板内容（解析JSON）"""
        if self.content:
            try:
                return json.loads(self.content)
            except:
                return {}
        return {}
    
    def to_dict(self):
        """转换为字典（包括解析的内容）"""
        template_dict = super().to_dict()
        # 将内容JSON字符串转换为Python字典
        template_dict['content'] = self.get_content()
        return template_dict 