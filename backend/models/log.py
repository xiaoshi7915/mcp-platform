#!/usr/bin/env python
# -*- coding: utf-8 -*-
from backend.models.db import db, BaseModel
import json

# 日志级别枚举
LOG_LEVELS = [
    'info',      # 信息
    'warning',   # 警告
    'error',     # 错误
    'debug'      # 调试
]

class Log(db.Model, BaseModel):
    """MCP工具日志模型"""
    __tablename__ = 'logs'
    
    # 日志ID
    id = db.Column(db.Integer, primary_key=True)
    # 工具ID
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=True)
    # 日志级别
    level = db.Column(db.String(20), nullable=False, default='info')
    # 日志消息
    message = db.Column(db.Text, nullable=False)
    # 调用参数（JSON格式）
    params = db.Column(db.Text, nullable=True)
    # 调用结果（JSON格式）
    result = db.Column(db.Text, nullable=True)
    # 执行时长（毫秒）
    duration = db.Column(db.Integer, nullable=True)
    # 调用者信息
    caller = db.Column(db.String(100), nullable=True)
    
    def __init__(self, message, tool_id=None, level='info', params=None, result=None, duration=None, caller=None):
        """
        初始化日志实例
        
        Args:
            message: 日志消息
            tool_id: 工具ID
            level: 日志级别
            params: 调用参数
            result: 调用结果
            duration: 执行时长
            caller: 调用者信息
        """
        self.message = message
        self.tool_id = tool_id
        self.level = level if level in LOG_LEVELS else 'info'
        
        # 参数和结果转JSON
        if isinstance(params, dict):
            self.params = json.dumps(params)
        else:
            self.params = params
            
        if isinstance(result, dict):
            self.result = json.dumps(result)
        else:
            self.result = result
            
        self.duration = duration
        self.caller = caller
    
    def get_params(self):
        """获取调用参数（解析JSON）"""
        if self.params:
            try:
                return json.loads(self.params)
            except:
                return {}
        return {}
    
    def get_result(self):
        """获取调用结果（解析JSON）"""
        if self.result:
            try:
                return json.loads(self.result)
            except:
                return {}
        return {}
    
    def to_dict(self):
        """转换为字典（包括解析的参数和结果）"""
        log_dict = super().to_dict()
        # 将JSON字符串转换为Python字典
        log_dict['params'] = self.get_params()
        log_dict['result'] = self.get_result()
        return log_dict 