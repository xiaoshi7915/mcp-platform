# backend/migrations/migration_manager.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import importlib
import argparse
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 将项目根目录添加到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import Config
from backend.models.db import db

class MigrationManager:
    """数据库迁移管理器"""
    
    def __init__(self, app=None, db=None):
        """
        初始化迁移管理器
        
        Args:
            app: Flask应用实例
            db: SQLAlchemy实例
        """
        self.app = app
        self.db = db
        self.migrations_dir = os.path.join(os.path.dirname(__file__), 'versions')
        
        # 确保迁移目录存在
        if not os.path.exists(self.migrations_dir):
            os.makedirs(self.migrations_dir)
    
    def generate_migration(self, name):
        """
        生成新的迁移文件
        
        Args:
            name: 迁移名称
        """
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{name}.py"
        filepath = os.path.join(self.migrations_dir, filename)
        
        # 创建迁移文件模板
        with open(filepath, 'w') as f:
            f.write("""#!/usr/bin/env python
# -*- coding: utf-8 -*-

def upgrade(db):
    \"\"\"
    升级数据库结构
    
    Args:
        db: SQLAlchemy实例
    \"\"\"
    # 在此编写升级操作
    # 例如: db.engine.execute("ALTER TABLE users ADD COLUMN email VARCHAR(100)")
    pass

def downgrade(db):
    \"\"\"
    回滚数据库结构
    
    Args:
        db: SQLAlchemy实例
    \"\"\"
    # 在此编写回滚操作
    # 例如: db.engine.execute("ALTER TABLE users DROP COLUMN email")
    pass
""")
        
        print(f"迁移文件已生成: {filepath}")
    
    def run_migrations(self, direction="up"):
        """
        运行所有迁移
        
        Args:
            direction: 迁移方向，"up"表示升级，"down"表示回滚
        """
        # 获取所有迁移文件并按时间戳排序
        migrations = []
        for filename in os.listdir(self.migrations_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                migrations.append(filename)
        
        migrations.sort()
        
        # 创建迁移表（如果不存在）
        with self.app.app_context():
            self.db.engine.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version VARCHAR(100) NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # 获取已应用的迁移
            applied_migrations = []
            for row in self.db.engine.execute("SELECT version FROM migrations"):
                applied_migrations.append(row[0])
            
            if direction == "up":
                # 应用未应用的迁移
                for migration in migrations:
                    version = migration[:-3]  # 去除.py后缀
                    if version not in applied_migrations:
                        self._apply_migration(version, migration)
            else:
                # 回滚已应用的迁移（倒序）
                for migration in reversed(migrations):
                    version = migration[:-3]  # 去除.py后缀
                    if version in applied_migrations:
                        self._rollback_migration(version, migration)
    
    def _apply_migration(self, version, filename):
        """
        应用单个迁移
        
        Args:
            version: 迁移版本
            filename: 迁移文件名
        """
        try:
            # 导入迁移模块
            module_path = f"backend.migrations.versions.{filename[:-3]}"
            migration = importlib.import_module(module_path)
            
            # 执行升级
            with self.app.app_context():
                print(f"应用迁移: {version}")
                migration.upgrade(self.db)
                
                # 记录已应用的迁移
                self.db.engine.execute(
                    "INSERT INTO migrations (version) VALUES (?)",
                    (version,)
                )
                print(f"迁移应用成功: {version}")
        except Exception as e:
            print(f"迁移应用失败: {version}")
            print(f"错误: {str(e)}")
            raise
    
    def _rollback_migration(self, version, filename):
        """
        回滚单个迁移
        
        Args:
            version: 迁移版本
            filename: 迁移文件名
        """
        try:
            # 导入迁移模块
            module_path = f"backend.migrations.versions.{filename[:-3]}"
            migration = importlib.import_module(module_path)
            
            # 执行回滚
            with self.app.app_context():
                print(f"回滚迁移: {version}")
                migration.downgrade(self.db)
                
                # 删除迁移记录
                self.db.engine.execute(
                    "DELETE FROM migrations WHERE version = ?",
                    (version,)
                )
                print(f"迁移回滚成功: {version}")
        except Exception as e:
            print(f"迁移回滚失败: {version}")
            print(f"错误: {str(e)}")
            raise

def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="数据库迁移工具")
    subparsers = parser.add_subparsers(dest="command", help="迁移命令")
    
    # 生成迁移命令
    generate_parser = subparsers.add_parser("generate", help="生成新的迁移文件")
    generate_parser.add_argument("name", help="迁移名称")
    
    # 升级命令
    subparsers.add_parser("upgrade", help="应用所有迁移")
    
    # 回滚命令
    subparsers.add_parser("downgrade", help="回滚所有迁移")
    
    args = parser.parse_args()
    
    # 创建应用
    app = create_app()
    
    # 创建迁移管理器
    manager = MigrationManager(app, db)
    
    # 执行命令
    if args.command == "generate":
        manager.generate_migration(args.name)
    elif args.command == "upgrade":
        manager.run_migrations("up")
    elif args.command == "downgrade":
        manager.run_migrations("down")
    else:
        parser.print_help()