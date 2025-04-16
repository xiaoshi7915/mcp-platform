#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from backend.models.log import Log, LOG_LEVELS
from backend.models.tool import Tool
from backend.models.db import db
from datetime import datetime, timedelta

# 创建日志蓝图
log_bp = Blueprint('log', __name__)

@log_bp.route('/', methods=['GET'])
def get_logs():
    """获取日志列表，支持过滤和分页"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    level = request.args.get('level')
    tool_id = request.args.get('tool_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    search = request.args.get('search')
    
    # 构建查询
    query = Log.query
    
    # 按级别过滤
    if level and level in LOG_LEVELS:
        query = query.filter(Log.level == level)
    
    # 按工具ID过滤
    if tool_id:
        query = query.filter(Log.tool_id == tool_id)
    
    # 按日期范围过滤
    if start_date:
        try:
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Log.created_at >= start_datetime)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Log.created_at <= end_datetime)
        except ValueError:
            pass
    
    # 按消息内容搜索
    if search:
        search_term = f"%{search}%"
        query = query.filter(Log.message.like(search_term))
    
    # 分页
    pagination = query.order_by(Log.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # 准备响应数据
    logs = [log.to_dict() for log in pagination.items]
    
    return jsonify({
        'logs': logs,
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })

@log_bp.route('/<int:log_id>', methods=['GET'])
def get_log(log_id):
    """获取单个日志详情"""
    log = Log.query.get_or_404(log_id)
    return jsonify(log.to_dict())

@log_bp.route('/', methods=['POST'])
def create_log():
    """创建新日志"""
    # 获取请求数据
    data = request.json
    
    # 验证必需字段
    if not data or not data.get('message'):
        return jsonify({'error': '日志消息是必需的'}), 400
    
    # 验证工具ID是否存在
    tool_id = data.get('tool_id')
    if tool_id and not Tool.query.get(tool_id):
        return jsonify({'error': f"工具ID {tool_id} 不存在"}), 400
    
    # 创建新日志
    log = Log(
        message=data.get('message'),
        tool_id=tool_id,
        level=data.get('level', 'info'),
        params=data.get('params'),
        result=data.get('result'),
        duration=data.get('duration'),
        caller=data.get('caller')
    )
    
    # 保存到数据库
    db.session.add(log)
    db.session.commit()
    
    return jsonify(log.to_dict()), 201

@log_bp.route('/<int:log_id>', methods=['DELETE'])
def delete_log(log_id):
    """删除日志"""
    log = Log.query.get_or_404(log_id)
    
    # 删除日志
    db.session.delete(log)
    db.session.commit()
    
    return jsonify({'message': f"日志ID {log_id} 已删除"}), 200

@log_bp.route('/clear', methods=['POST'])
def clear_logs():
    """清除日志，支持条件过滤"""
    # 获取请求数据
    data = request.json or {}
    
    # 构建查询
    query = Log.query
    
    # 按级别过滤
    if data.get('level') and data.get('level') in LOG_LEVELS:
        query = query.filter(Log.level == data.get('level'))
    
    # 按工具ID过滤
    if data.get('tool_id'):
        query = query.filter(Log.tool_id == data.get('tool_id'))
    
    # 按日期范围过滤
    if data.get('days_before'):
        cutoff_date = datetime.utcnow() - timedelta(days=int(data.get('days_before')))
        query = query.filter(Log.created_at < cutoff_date)
    
    # 获取要删除的日志数量
    count = query.count()
    
    # 执行删除
    query.delete()
    db.session.commit()
    
    return jsonify({'message': f"已清除 {count} 条日志记录"})

@log_bp.route('/tool/<int:tool_id>', methods=['GET'])
def get_tool_logs(tool_id):
    """获取指定工具的日志"""
    # 验证工具是否存在
    tool = Tool.query.get_or_404(tool_id)
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    level = request.args.get('level')
    
    # 构建查询
    query = Log.query.filter(Log.tool_id == tool_id)
    
    # 按级别过滤
    if level and level in LOG_LEVELS:
        query = query.filter(Log.level == level)
    
    # 分页
    pagination = query.order_by(Log.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # 准备响应数据
    logs = [log.to_dict() for log in pagination.items]
    
    return jsonify({
        'tool': tool.name,
        'logs': logs,
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    }) 