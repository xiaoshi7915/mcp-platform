#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from backend.models.tool import Tool, TOOL_TYPES, TOOL_STATUS
from backend.models.db import db
from datetime import datetime

# 创建工具蓝图
tool_bp = Blueprint('tool', __name__)

@tool_bp.route('/', methods=['GET'])
def get_tools():
    """获取工具列表，支持过滤和分页"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    tool_type = request.args.get('type')
    status = request.args.get('status')
    search = request.args.get('search')
    
    # 构建查询
    query = Tool.query
    
    # 按类型过滤
    if tool_type and tool_type in TOOL_TYPES:
        query = query.filter(Tool.type == tool_type)
    
    # 按状态过滤
    if status and status in TOOL_STATUS:
        query = query.filter(Tool.status == status)
    
    # 按名称或描述搜索
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Tool.name.like(search_term)) | 
            (Tool.description.like(search_term))
        )
    
    # 分页
    pagination = query.order_by(Tool.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # 准备响应数据
    tools = [tool.to_dict() for tool in pagination.items]
    
    return jsonify({
        'tools': tools,
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })

@tool_bp.route('/<int:tool_id>', methods=['GET'])
def get_tool(tool_id):
    """获取单个工具详情"""
    tool = Tool.query.get_or_404(tool_id)
    return jsonify(tool.to_dict())

@tool_bp.route('/', methods=['POST'])
def create_tool():
    """创建新工具"""
    # 获取请求数据
    data = request.json
    
    # 验证必需字段
    if not data or not data.get('name'):
        return jsonify({'error': '工具名称是必需的'}), 400
    
    # 检查工具名称是否已存在
    if Tool.query.filter_by(name=data.get('name')).first():
        return jsonify({'error': f"工具名称 '{data.get('name')}' 已存在"}), 400
    
    # 创建新工具
    tool = Tool(
        name=data.get('name'),
        description=data.get('description'),
        type=data.get('type', 'other'),
        command=data.get('command'),
        config=data.get('config', {})
    )
    
    # 保存到数据库
    db.session.add(tool)
    db.session.commit()
    
    return jsonify(tool.to_dict()), 201

@tool_bp.route('/<int:tool_id>', methods=['PUT'])
def update_tool(tool_id):
    """更新工具信息"""
    # 获取工具
    tool = Tool.query.get_or_404(tool_id)
    
    # 获取请求数据
    data = request.json
    
    # 更新工具信息
    if data.get('name'):
        # 检查名称是否已存在
        existing = Tool.query.filter_by(name=data.get('name')).first()
        if existing and existing.id != tool_id:
            return jsonify({'error': f"工具名称 '{data.get('name')}' 已存在"}), 400
        tool.name = data.get('name')
    
    if 'description' in data:
        tool.description = data.get('description')
    
    if 'type' in data and data.get('type') in TOOL_TYPES:
        tool.type = data.get('type')
    
    if 'command' in data:
        tool.command = data.get('command')
    
    if 'config' in data:
        tool.set_config(data.get('config', {}))
    
    if 'status' in data and data.get('status') in TOOL_STATUS:
        tool.status = data.get('status')
    
    # 保存更新
    db.session.commit()
    
    return jsonify(tool.to_dict())

@tool_bp.route('/<int:tool_id>', methods=['DELETE'])
def delete_tool(tool_id):
    """删除工具"""
    tool = Tool.query.get_or_404(tool_id)
    
    # 删除工具
    db.session.delete(tool)
    db.session.commit()
    
    return jsonify({'message': f"工具 '{tool.name}' 已删除"}), 200

@tool_bp.route('/<int:tool_id>/activate', methods=['POST'])
def activate_tool(tool_id):
    """激活工具"""
    tool = Tool.query.get_or_404(tool_id)
    
    # 更新状态
    tool.status = 'active'
    db.session.commit()
    
    return jsonify({'message': f"工具 '{tool.name}' 已激活", 'tool': tool.to_dict()})

@tool_bp.route('/<int:tool_id>/deactivate', methods=['POST'])
def deactivate_tool(tool_id):
    """停用工具"""
    tool = Tool.query.get_or_404(tool_id)
    
    # 更新状态
    tool.status = 'inactive'
    db.session.commit()
    
    return jsonify({'message': f"工具 '{tool.name}' 已停用", 'tool': tool.to_dict()})

@tool_bp.route('/<int:tool_id>/invoke', methods=['POST'])
def invoke_tool(tool_id):
    """调用工具"""
    tool = Tool.query.get_or_404(tool_id)
    
    # 检查工具状态
    if tool.status != 'active':
        return jsonify({'error': f"工具 '{tool.name}' 未激活"}), 400
    
    # 更新调用信息
    tool.last_invoked_at = datetime.utcnow()
    tool.invoke_count += 1
    db.session.commit()
    
    # TODO: 实现实际的工具调用逻辑
    # 这里仅作为示例，返回模拟的调用结果
    return jsonify({
        'message': f"工具 '{tool.name}' 调用成功",
        'tool': tool.to_dict(),
        'result': {'status': 'success', 'data': {}}
    }) 