#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 初始化SQLAlchemy
db = SQLAlchemy()

# 基础模型，提供公共字段
class BaseModel:
    """所有模型的基类，提供公共字段和方法"""
    # 创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # 更新时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """将模型转换为字典"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def save(self):
        """保存模型到数据库"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """从数据库删除模型"""
        db.session.delete(self)
        db.session.commit()
        return self 