#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify
from backend.models.tool import Tool
from backend.models.log import Log
from backend.models.config import Config
from backend.models.db import db
from datetime import datetime, timedelta
import psutil

# 创建仪表盘蓝图
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/overview', methods=['GET'])
def get_overview():
    """获取仪表盘概览数据"""
    # 获取工具统计信息
    total_tools = Tool.query.count()
    active_tools = Tool.query.filter_by(status='active').count()
    inactive_tools = Tool.query.filter_by(status='inactive').count()
    error_tools = Tool.query.filter_by(status='error').count()
    
    # 获取日志统计信息
    total_logs = Log.query.count()
    info_logs = Log.query.filter_by(level='info').count()
    warning_logs = Log.query.filter_by(level='warning').count()
    error_logs = Log.query.filter_by(level='error').count()
    
    # 获取最近的日志
    recent_logs = Log.query.order_by(Log.created_at.desc()).limit(5).all()
    recent_logs_data = [log.to_dict() for log in recent_logs]
    
    # 获取最活跃的工具（按调用次数）
    active_tools_data = Tool.query.order_by(Tool.invoke_count.desc()).limit(5).all()
    active_tools_list = [tool.to_dict() for tool in active_tools_data]
    
    # 获取系统资源使用情况
    try:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        memory_info = psutil.virtual_memory()
        memory_usage = memory_info.percent
        disk_info = psutil.disk_usage('/')
        disk_usage = disk_info.percent
    except:
        # 如果psutil不可用，使用默认值
        cpu_usage = 0
        memory_usage = 0
        disk_usage = 0
    
    return jsonify({
        'tools': {
            'total': total_tools,
            'active': active_tools,
            'inactive': inactive_tools,
            'error': error_tools
        },
        'logs': {
            'total': total_logs,
            'info': info_logs,
            'warning': warning_logs,
            'error': error_logs,
            'recent': recent_logs_data
        },
        'active_tools': active_tools_list,
        'system': {
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'disk_usage': disk_usage
        }
    })

@dashboard_bp.route('/stats/daily', methods=['GET'])
def get_daily_stats():
    """获取每日统计数据"""
    # 获取过去30天的日期
    today = datetime.utcnow().date()
    dates = [(today - timedelta(days=i)) for i in range(30)]
    dates.reverse()  # 从最早到最近排序
    
    # 初始化结果数据
    daily_stats = []
    
    for date in dates:
        # 日期的开始和结束时间
        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())
        
        # 获取当天的调用次数
        calls_count = Log.query.filter(
            Log.created_at >= start_date,
            Log.created_at <= end_date
        ).count()
        
        # 获取当天的错误次数
        error_count = Log.query.filter(
            Log.created_at >= start_date,
            Log.created_at <= end_date,
            Log.level == 'error'
        ).count()
        
        # 添加到结果中
        daily_stats.append({
            'date': date.isoformat(),
            'calls': calls_count,
            'errors': error_count
        })
    
    return jsonify(daily_stats)

@dashboard_bp.route('/tool_types', methods=['GET'])
def get_tool_types():
    """获取工具类型分布"""
    # 获取所有支持的工具类型
    from backend.models.tool import TOOL_TYPES
    
    # 初始化结果数据
    type_stats = []
    
    for tool_type in TOOL_TYPES:
        # 获取该类型的工具数量
        count = Tool.query.filter_by(type=tool_type).count()
        
        # 添加到结果中
        type_stats.append({
            'type': tool_type,
            'count': count
        })
    
    return jsonify(type_stats)

@dashboard_bp.route('/recent_activities', methods=['GET'])
def get_recent_activities():
    """获取最近活动"""
    # 获取最近的日志
    recent_logs = Log.query.order_by(Log.created_at.desc()).limit(10).all()
    
    # 转换为活动数据
    activities = []
    
    for log in recent_logs:
        # 获取关联的工具名称
        tool_name = 'Unknown'
        if log.tool_id:
            tool = Tool.query.get(log.tool_id)
            if tool:
                tool_name = tool.name
        
        # 构建活动数据
        activity = {
            'id': log.id,
            'timestamp': log.created_at.isoformat(),
            'tool': tool_name,
            'level': log.level,
            'message': log.message
        }
        
        activities.append(activity)
    
    return jsonify(activities) 