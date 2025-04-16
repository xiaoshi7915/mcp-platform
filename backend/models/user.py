#!/usr/bin/env python
# -*- coding: utf-8 -*-
from backend.models.db import db, BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os

# 用户角色枚举
USER_ROLES = [
    'admin',        # 管理员
    'operator',     # 操作员
    'viewer'        # 查看者
]

class User(db.Model, BaseModel):
    """用户模型"""
    __tablename__ = 'users'
    
    # 用户ID
    id = db.Column(db.Integer, primary_key=True)
    # 用户名
    username = db.Column(db.String(50), nullable=False, unique=True)
    # 密码哈希
    password_hash = db.Column(db.String(256), nullable=False)
    # 电子邮件
    email = db.Column(db.String(100), nullable=True, unique=True)
    # 角色
    role = db.Column(db.String(20), nullable=False, default='viewer')
    # 是否激活
    is_active = db.Column(db.Boolean, default=True)
    # 最后登录时间
    last_login_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, username, password, email=None, role='viewer'):
        """
        初始化用户实例
        
        Args:
            username: 用户名
            password: 密码
            email: 电子邮件
            role: 角色
        """
        self.username = username
        self.set_password(password)
        self.email = email
        self.role = role if role in USER_ROLES else 'viewer'
        self.is_active = True
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def generate_token(self, expiration=86400):
        """
        生成JWT令牌
        
        Args:
            expiration: 有效期（秒）
        
        Returns:
            令牌字符串
        """
        payload = {
            'user_id': self.id,
            'username': self.username,
            'role': self.role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expiration)
        }
        
        return jwt.encode(
            payload,
            os.environ.get('SECRET_KEY', 'default-secret-key'),
            algorithm='HS256'
        )
    
    @staticmethod
    def verify_token(token):
        """
        验证JWT令牌
        
        Args:
            token: 令牌字符串
        
        Returns:
            用户实例或None
        """
        try:
            payload = jwt.decode(
                token,
                os.environ.get('SECRET_KEY', 'default-secret-key'),
                algorithms=['HS256']
            )
            user = User.query.get(payload['user_id'])
            if user and user.is_active:
                return user
            return None
        except:
            return None
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login_at = datetime.datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, include_token=False):
        """
        转换为字典
        
        Args:
            include_token: 是否包含令牌
        
        Returns:
            用户信息字典
        """
        user_dict = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'last_login_at': self.last_login_at,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if include_token:
            user_dict['token'] = self.generate_token()
        
        return user_dict 