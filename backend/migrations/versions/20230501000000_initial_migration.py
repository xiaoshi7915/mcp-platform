#!/usr/bin/env python
# -*- coding: utf-8 -*-

def upgrade(db):
    """
    升级数据库结构
    
    Args:
        db: SQLAlchemy实例
    """
    # 检查表是否存在
    tables = db.engine.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    tables = [table[0] for table in tables]
    
    # 创建工具表
    if 'tools' not in tables:
        db.engine.execute("""
        CREATE TABLE tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            type VARCHAR(50) NOT NULL,
            status VARCHAR(20) DEFAULT 'inactive',
            command VARCHAR(200),
            config TEXT,
            last_invoked_at DATETIME,
            invoke_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
    
    # 创建配置表
    if 'configs' not in tables:
        db.engine.execute("""
        CREATE TABLE configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            type VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
    
    # 创建日志表
    if 'logs' not in tables:
        db.engine.execute("""
        CREATE TABLE logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool_id INTEGER,
            level VARCHAR(20) NOT NULL DEFAULT 'info',
            message TEXT NOT NULL,
            params TEXT,
            result TEXT,
            duration INTEGER,
            caller VARCHAR(100),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(tool_id) REFERENCES tools(id)
        )
        """)
    
    # 创建模板表
    if 'templates' not in tables:
        db.engine.execute("""
        CREATE TABLE templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            type VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            scenarios VARCHAR(200),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
    
    # 创建用户表
    if 'users' not in tables:
        db.engine.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(200) NOT NULL,
            email VARCHAR(100),
            is_admin BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            last_login_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

def downgrade(db):
    """
    回滚数据库结构
    
    Args:
        db: SQLAlchemy实例
    """
    # 删除所有表
    db.engine.execute("DROP TABLE IF EXISTS users")
    db.engine.execute("DROP TABLE IF EXISTS templates")
    db.engine.execute("DROP TABLE IF EXISTS logs")
    db.engine.execute("DROP TABLE IF EXISTS configs")
    db.engine.execute("DROP TABLE IF EXISTS tools")
