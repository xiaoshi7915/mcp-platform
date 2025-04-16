#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify, g
from functools import wraps
from backend.models.user import User, USER_ROLES
from backend.models.db import db
import datetime
import re

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)

def extract_token(request):
    """从请求中提取令牌"""
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            auth_type, token = auth_header.split(' ')
            if auth_type == 'Bearer':
                return token
        except ValueError:
            return None
    return None

def token_required(f):
    """JWT令牌认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = extract_token(request)
        
        if not token:
            return jsonify({'error': '请提供认证令牌'}), 401
        
        user = User.verify_token(token)
        if not user:
            return jsonify({'error': '无效或已过期的令牌'}), 401
        
        g.current_user = user
        return f(*args, **kwargs)
    
    return decorated

def roles_required(roles):
    """角色验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not g.current_user:
                return jsonify({'error': '请先登录'}), 401
            
            if g.current_user.role not in roles:
                return jsonify({'error': '权限不足'}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

@auth_bp.route('/register', methods=['POST'])
@token_required
@roles_required(['admin'])
def register():
    """
    注册新用户 (仅管理员可操作)
    ---
    tags:
      - 用户认证
    description: 创建新用户账号，仅管理员可以执行此操作
    parameters:
      - in: body
        name: user
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: 用户名(3-20个字符)
            password:
              type: string
              description: 密码(6-30个字符)
            email:
              type: string
              description: 电子邮箱地址
            role:
              type: string
              enum: ['admin', 'operator', 'viewer']
              description: 用户角色
    responses:
      201:
        description: 创建成功
      400:
        description: 参数错误或用户已存在
      401:
        description: 认证失败
      403:
        description: 权限不足
    """
    # 获取请求数据
    data = request.json
    
    # 验证必需字段
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': '请提供用户名和密码'}), 400
    
    # 验证用户名格式
    username = data.get('username')
    if len(username) < 3 or len(username) > 20:
        return jsonify({'error': '用户名长度应为3-20个字符'}), 400
        
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return jsonify({'error': '用户名只能包含字母、数字和下划线'}), 400
    
    # 验证密码强度
    password = data.get('password')
    if len(password) < 6 or len(password) > 30:
        return jsonify({'error': '密码长度应为6-30个字符'}), 400
    
    # 验证邮箱格式（如果提供）
    email = data.get('email')
    if email:
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            return jsonify({'error': '邮箱格式无效'}), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'error': f"用户名 '{username}' 已存在"}), 400
    
    # 检查邮箱是否已存在（如果提供）
    if email and User.query.filter_by(email=email).first():
        return jsonify({'error': f"邮箱 '{email}' 已被使用"}), 400
    
    # 确定角色
    role = 'viewer'  # 默认为viewer角色
    if data.get('role') and data.get('role') in USER_ROLES:
        role = data.get('role')
    
    # 创建新用户
    user = User(
        username=username,
        password=password,
        email=email,
        role=role
    )
    
    # 保存到数据库
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': '用户创建成功',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    ---
    tags:
      - 用户认证
    description: 用户登录获取认证令牌
    parameters:
      - in: body
        name: credentials
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: 用户名
            password:
              type: string
              description: 密码
    responses:
      200:
        description: 登录成功
      400:
        description: 参数错误
      401:
        description: 认证失败
      403:
        description: 账号被停用
    """
    # 获取请求数据
    data = request.json
    
    # 验证必需字段
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': '请提供用户名和密码'}), 400
    
    # 检查用户名是否存在
    user = User.query.filter_by(username=data.get('username')).first()
    if not user:
        return jsonify({'error': '用户名或密码错误'}), 401
    
    # 验证密码
    if not user.check_password(data.get('password')):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    # 验证用户是否被激活
    if not user.is_active:
        return jsonify({'error': '此账户已被停用'}), 403
    
    # 更新最后登录时间
    user.update_last_login()
    
    # 生成认证令牌
    token = user.generate_token()
    
    return jsonify({
        'message': '登录成功',
        'user': user.to_dict(),
        'token': token
    }), 200

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_user_info():
    """获取当前用户信息"""
    return jsonify(g.current_user.to_dict()), 200

@auth_bp.route('/users', methods=['GET'])
@token_required
@roles_required(['admin'])
def get_users():
    """获取用户列表（仅限管理员）"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
@roles_required(['admin'])
def get_user(user_id):
    """获取单个用户信息（仅限管理员）"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
@roles_required(['admin'])
def update_user(user_id):
    """更新用户信息（仅限管理员）"""
    user = User.query.get_or_404(user_id)
    data = request.json
    
    # 更新用户信息
    if data.get('email'):
        # 检查新邮箱是否已存在
        existing = User.query.filter_by(email=data.get('email')).first()
        if existing and existing.id != user_id:
            return jsonify({'error': f"邮箱 '{data.get('email')}' 已被使用"}), 400
        user.email = data.get('email')
    
    if data.get('role') and data.get('role') in USER_ROLES:
        user.role = data.get('role')
    
    if 'is_active' in data:
        user.is_active = bool(data.get('is_active'))
    
    # 如果提供了新密码，则更新密码
    if data.get('password'):
        if len(data.get('password')) < 6 or len(data.get('password')) > 30:
            return jsonify({'error': '密码长度应为6-30个字符'}), 400
        user.set_password(data.get('password'))
    
    # 保存更新
    db.session.commit()
    
    return jsonify({
        'message': '用户信息已更新',
        'user': user.to_dict()
    }), 200

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """用户修改自己的密码"""
    data = request.json
    
    # 验证必需字段
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({'error': '请提供当前密码和新密码'}), 400
    
    # 验证当前密码
    if not g.current_user.check_password(data.get('old_password')):
        return jsonify({'error': '当前密码错误'}), 401
    
    # 验证新密码强度
    if len(data.get('new_password')) < 6 or len(data.get('new_password')) > 30:
        return jsonify({'error': '新密码长度应为6-30个字符'}), 400
    
    # 更新密码
    g.current_user.set_password(data.get('new_password'))
    db.session.commit()
    
    return jsonify({'message': '密码已更新'}), 200 