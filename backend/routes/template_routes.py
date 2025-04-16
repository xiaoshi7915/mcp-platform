#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from backend.models.template import Template
from backend.models.tool import Tool, TOOL_TYPES
from backend.models.db import db

# 创建模板蓝图
template_bp = Blueprint('template', __name__)

@template_bp.route('/', methods=['GET'])
def get_templates():
    """获取模板列表，支持过滤和分页"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    template_type = request.args.get('type')
    search = request.args.get('search')
    
    # 构建查询
    query = Template.query
    
    # 按类型过滤
    if template_type and template_type in TOOL_TYPES:
        query = query.filter(Template.type == template_type)
    
    # 按名称或描述搜索
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Template.name.like(search_term)) | 
            (Template.description.like(search_term)) |
            (Template.scenarios.like(search_term))
        )
    
    # 分页
    pagination = query.order_by(Template.name).paginate(page=page, per_page=per_page)
    
    # 准备响应数据
    templates = [template.to_dict() for template in pagination.items]
    
    return jsonify({
        'templates': templates,
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })

@template_bp.route('/<int:template_id>', methods=['GET'])
def get_template(template_id):
    """获取单个模板详情"""
    template = Template.query.get_or_404(template_id)
    return jsonify(template.to_dict())

@template_bp.route('/', methods=['POST'])
def create_template():
    """创建新模板"""
    # 获取请求数据
    data = request.json
    
    # 验证必需字段
    if not data or not data.get('name') or not data.get('content') or not data.get('type'):
        return jsonify({'error': '模板名称、内容和类型是必需的'}), 400
    
    # 检查模板名称是否已存在
    if Template.query.filter_by(name=data.get('name')).first():
        return jsonify({'error': f"模板名称 '{data.get('name')}' 已存在"}), 400
    
    # 验证类型是否有效
    if data.get('type') not in TOOL_TYPES:
        return jsonify({'error': f"无效的工具类型: '{data.get('type')}'"}), 400
    
    # 创建新模板
    template = Template(
        name=data.get('name'),
        content=data.get('content'),
        type=data.get('type'),
        description=data.get('description'),
        scenarios=data.get('scenarios')
    )
    
    # 保存到数据库
    db.session.add(template)
    db.session.commit()
    
    return jsonify(template.to_dict()), 201

@template_bp.route('/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """更新模板信息"""
    # 获取模板
    template = Template.query.get_or_404(template_id)
    
    # 获取请求数据
    data = request.json
    
    # 更新模板信息
    if data.get('name'):
        # 检查名称是否已存在
        existing = Template.query.filter_by(name=data.get('name')).first()
        if existing and existing.id != template_id:
            return jsonify({'error': f"模板名称 '{data.get('name')}' 已存在"}), 400
        template.name = data.get('name')
    
    if 'description' in data:
        template.description = data.get('description')
    
    if 'scenarios' in data:
        template.scenarios = data.get('scenarios')
    
    if 'type' in data:
        # 验证类型是否有效
        if data.get('type') not in TOOL_TYPES:
            return jsonify({'error': f"无效的工具类型: '{data.get('type')}'"}), 400
        template.type = data.get('type')
    
    if 'content' in data:
        template.content = data.get('content')
    
    # 保存更新
    db.session.commit()
    
    return jsonify(template.to_dict())

@template_bp.route('/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    """删除模板"""
    template = Template.query.get_or_404(template_id)
    
    # 删除模板
    db.session.delete(template)
    db.session.commit()
    
    return jsonify({'message': f"模板 '{template.name}' 已删除"}), 200

@template_bp.route('/<int:template_id>/import', methods=['POST'])
def import_template(template_id):
    """从模板导入创建工具"""
    # 获取模板
    template = Template.query.get_or_404(template_id)
    
    # 获取请求数据（可选的自定义参数）
    data = request.json or {}
    
    # 从模板获取内容
    content = template.get_content()
    
    # 创建工具名称（可自定义或使用默认值）
    tool_name = data.get('name', f"{template.name}_tool_{template.id}")
    
    # 检查工具名称是否已存在
    if Tool.query.filter_by(name=tool_name).first():
        return jsonify({'error': f"工具名称 '{tool_name}' 已存在"}), 400
    
    # 创建新工具
    tool = Tool(
        name=tool_name,
        description=data.get('description', template.description),
        type=template.type,
        command=data.get('command'),
        config=content
    )
    
    # 保存到数据库
    db.session.add(tool)
    db.session.commit()
    
    return jsonify({
        'message': f"已从模板 '{template.name}' 导入创建新工具",
        'tool': tool.to_dict()
    }), 201 