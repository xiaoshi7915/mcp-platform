#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import subprocess
import threading
import time
from datetime import datetime
from backend.models.tool import Tool
from backend.models.log import Log
from backend.models.db import db

class ToolService:
    """MCP工具服务类，负责工具的启动、停止和调用"""
    
    @staticmethod
    def start_tool(tool_id):
        """
        启动工具服务
        
        Args:
            tool_id: 工具ID
            
        Returns:
            成功返回True，失败返回False
        """
        tool = Tool.query.get(tool_id)
        if not tool:
            return False
        
        # 如果工具已经是活跃状态，直接返回成功
        if tool.status == 'active':
            return True
        
        try:
            # 获取工具配置
            config = tool.get_config()
            
            # TODO: 实现实际的工具启动逻辑
            # 这里仅作为示例，模拟工具启动
            
            # 更新工具状态
            tool.status = 'active'
            db.session.commit()
            
            # 记录日志
            log = Log(
                message=f"工具 '{tool.name}' 已启动",
                tool_id=tool.id,
                level='info'
            )
            db.session.add(log)
            db.session.commit()
            
            return True
        except Exception as e:
            # 更新工具状态为错误
            tool.status = 'error'
            db.session.commit()
            
            # 记录错误日志
            log = Log(
                message=f"工具 '{tool.name}' 启动失败: {str(e)}",
                tool_id=tool.id,
                level='error'
            )
            db.session.add(log)
            db.session.commit()
            
            return False
    
    @staticmethod
    def stop_tool(tool_id):
        """
        停止工具服务
        
        Args:
            tool_id: 工具ID
            
        Returns:
            成功返回True，失败返回False
        """
        tool = Tool.query.get(tool_id)
        if not tool:
            return False
        
        # 如果工具已经是非活跃状态，直接返回成功
        if tool.status == 'inactive':
            return True
        
        try:
            # 获取工具配置
            config = tool.get_config()
            
            # TODO: 实现实际的工具停止逻辑
            # 这里仅作为示例，模拟工具停止
            
            # 更新工具状态
            tool.status = 'inactive'
            db.session.commit()
            
            # 记录日志
            log = Log(
                message=f"工具 '{tool.name}' 已停止",
                tool_id=tool.id,
                level='info'
            )
            db.session.add(log)
            db.session.commit()
            
            return True
        except Exception as e:
            # 记录错误日志
            log = Log(
                message=f"工具 '{tool.name}' 停止失败: {str(e)}",
                tool_id=tool.id,
                level='error'
            )
            db.session.add(log)
            db.session.commit()
            
            return False
    
    @staticmethod
    def invoke_tool(tool_id, params=None):
        """
        调用工具
        
        Args:
            tool_id: 工具ID
            params: 调用参数
            
        Returns:
            调用结果字典
        """
        tool = Tool.query.get(tool_id)
        if not tool:
            return {'success': False, 'error': '工具不存在'}
        
        # 检查工具状态
        if tool.status != 'active':
            return {'success': False, 'error': '工具未激活'}
        
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 获取工具配置
            config = tool.get_config()
            
            # TODO: 实现实际的工具调用逻辑
            # 这里仅作为示例，模拟工具调用
            result = {'status': 'success', 'data': {}}
            
            # 计算执行时间（毫秒）
            duration = int((time.time() - start_time) * 1000)
            
            # 更新工具调用信息
            tool.last_invoked_at = datetime.utcnow()
            tool.invoke_count += 1
            db.session.commit()
            
            # 记录日志
            log = Log(
                message=f"工具 '{tool.name}' 调用成功",
                tool_id=tool.id,
                level='info',
                params=params,
                result=result,
                duration=duration
            )
            db.session.add(log)
            db.session.commit()
            
            return {'success': True, 'result': result, 'duration': duration}
        except Exception as e:
            # 计算执行时间（毫秒）
            duration = int((time.time() - start_time) * 1000)
            
            # 记录错误日志
            log = Log(
                message=f"工具 '{tool.name}' 调用失败: {str(e)}",
                tool_id=tool.id,
                level='error',
                params=params,
                duration=duration
            )
            db.session.add(log)
            db.session.commit()
            
            return {'success': False, 'error': str(e), 'duration': duration}
    
    @staticmethod
    def check_tool_status(tool_id):
        """
        检查工具状态
        
        Args:
            tool_id: 工具ID
            
        Returns:
            工具状态信息字典
        """
        tool = Tool.query.get(tool_id)
        if not tool:
            return {'success': False, 'error': '工具不存在'}
        
        # TODO: 实现实际的工具状态检查逻辑
        # 这里仅作为示例，返回数据库中的状态
        
        return {
            'success': True,
            'status': tool.status,
            'last_invoked_at': tool.last_invoked_at.isoformat() if tool.last_invoked_at else None,
            'invoke_count': tool.invoke_count
        } 