#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from backend.models.config import Config, CONFIG_TYPES
from backend.models.db import db

# 创建配置蓝图
config_bp = Blueprint('config', __name__)

@config_bp.route('/', methods=['GET'])
def get_configs():
    """获取配置列表，支持过滤和分页"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    config_type = request.args.get('type')
    is_active = request.args.get('is_active')
    search = request.args.get('search')
    
    # 构建查询
    query = Config.query
    
    # 按类型过滤
    if config_type and config_type in CONFIG_TYPES:
        query = query.filter(Config.type == config_type)
    
    # 按状态过滤
    if is_active is not None:
        is_active_bool = (is_active.lower() == 'true')
        query = query.filter(Config.is_active == is_active_bool)
    
    # 按名称或描述搜索
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Config.name.like(search_term)) | 
            (Config.description.like(search_term))
        )
    
    # 分页
    pagination = query.order_by(Config.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # 准备响应数据
    configs = [config.to_dict() for config in pagination.items]
    
    return jsonify({
        'configs': configs,
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })

@config_bp.route('/<int:config_id>', methods=['GET'])
def get_config(config_id):
    """获取单个配置详情"""
    config = Config.query.get_or_404(config_id)
    return jsonify(config.to_dict())

@config_bp.route('/', methods=['POST'])
def create_config():
    """创建新配置"""
    # 获取请求数据
    data = request.json
    
    # 验证必需字段
    if not data or not data.get('name') or 'content' not in data:
        return jsonify({'error': '配置名称和内容是必需的'}), 400
    
    # 检查配置名称是否已存在
    if Config.query.filter_by(name=data.get('name')).first():
        return jsonify({'error': f"配置名称 '{data.get('name')}' 已存在"}), 400
    
    # 创建新配置
    config = Config(
        name=data.get('name'),
        content=data.get('content'),
        type=data.get('type', 'other'),
        description=data.get('description')
    )
    
    # 设置激活状态
    if 'is_active' in data:
        config.is_active = bool(data.get('is_active'))
    
    # 保存到数据库
    db.session.add(config)
    db.session.commit()
    
    return jsonify(config.to_dict()), 201

@config_bp.route('/<int:config_id>', methods=['PUT'])
def update_config(config_id):
    """更新配置信息"""
    # 获取配置
    config = Config.query.get_or_404(config_id)
    
    # 获取请求数据
    data = request.json
    
    # 更新配置信息
    if data.get('name'):
        # 检查名称是否已存在
        existing = Config.query.filter_by(name=data.get('name')).first()
        if existing and existing.id != config_id:
            return jsonify({'error': f"配置名称 '{data.get('name')}' 已存在"}), 400
        config.name = data.get('name')
    
    if 'description' in data:
        config.description = data.get('description')
    
    if 'type' in data and data.get('type') in CONFIG_TYPES:
        config.type = data.get('type')
    
    if 'content' in data:
        config.set_content(data.get('content'))
    
    if 'is_active' in data:
        config.is_active = bool(data.get('is_active'))
    
    # 保存更新
    db.session.commit()
    
    return jsonify(config.to_dict())

@config_bp.route('/<int:config_id>', methods=['DELETE'])
def delete_config(config_id):
    """删除配置"""
    config = Config.query.get_or_404(config_id)
    
    # 删除配置
    db.session.delete(config)
    db.session.commit()
    
    return jsonify({'message': f"配置 '{config.name}' 已删除"}), 200

@config_bp.route('/<int:config_id>/activate', methods=['POST'])
def activate_config(config_id):
    """激活配置"""
    config = Config.query.get_or_404(config_id)
    
    # 更新状态
    config.is_active = True
    db.session.commit()
    
    return jsonify({'message': f"配置 '{config.name}' 已激活", 'config': config.to_dict()})

@config_bp.route('/<int:config_id>/deactivate', methods=['POST'])
def deactivate_config(config_id):
    """停用配置"""
    config = Config.query.get_or_404(config_id)
    
    # 更新状态
    config.is_active = False
    db.session.commit()
    
    return jsonify({'message': f"配置 '{config.name}' 已停用", 'config': config.to_dict()}) 