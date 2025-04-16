#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import random
from datetime import datetime, timedelta

# 确保可以导入后端模块
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from backend.app import create_app
from backend.models.db import db
from backend.models.tool import Tool
from backend.models.config import Config
from backend.models.log import Log
from backend.models.template import Template

# 创建Flask应用实例
app = create_app()

# 工具类型列表
TOOL_TYPES = ['filesystem', 'network', 'data_analysis', 'media', 'system', 'puppeteer', 'other']

# 配置类型列表
CONFIG_TYPES = ['tool', 'environment', 'system', 'user', 'other']

# 模板类型列表
TEMPLATE_TYPES = ['tool', 'config', 'workflow', 'other']

# 日志级别列表
LOG_LEVELS = ['info', 'warning', 'error', 'debug']

# 工具模拟数据
TOOLS_DATA = [
    {
        'name': '文件浏览器',
        'description': '浏览服务器上的文件和目录',
        'type': 'filesystem',
        'command': 'ls -la {path}',
        'config': {
            'allowed_paths': ['/data', '/tmp', '/opt'],
            'max_depth': 5,
            'show_hidden': False
        },
        'status': 'active'
    },
    {
        'name': '网络扫描器',
        'description': '扫描网络中的主机和开放端口',
        'type': 'network',
        'command': 'nmap -sT {host}',
        'config': {
            'timeout': 30,
            'scan_types': ['SYN', 'TCP', 'UDP'],
            'port_range': '1-1024'
        },
        'status': 'active'
    },
    {
        'name': '数据可视化',
        'description': '将数据转换为可视化图表',
        'type': 'data_analysis',
        'command': 'python visualize.py {data_file} {chart_type}',
        'config': {
            'supported_formats': ['csv', 'json', 'excel'],
            'chart_types': ['bar', 'line', 'pie', 'scatter'],
            'max_data_size': '10MB'
        },
        'status': 'active'
    },
    {
        'name': '图像压缩',
        'description': '压缩图像文件以减小体积',
        'type': 'media',
        'command': 'convert {input} -quality {quality} {output}',
        'config': {
            'quality_range': [50, 90],
            'supported_formats': ['jpg', 'png', 'gif'],
            'max_file_size': '20MB'
        },
        'status': 'inactive'
    },
    {
        'name': '系统监控',
        'description': '监控服务器CPU、内存和磁盘使用情况',
        'type': 'system',
        'command': 'top -bn1',
        'config': {
            'interval': 60,
            'thresholds': {
                'cpu': 80,
                'memory': 90,
                'disk': 95
            },
            'alert': True
        },
        'status': 'active'
    },
    {
        'name': '网页截图',
        'description': '获取指定URL的网页截图',
        'type': 'puppeteer',
        'command': 'puppeteer.screenshot({url: "{url}", path: "{output_path}"})',
        'config': {
            'viewport': {
                'width': 1280,
                'height': 800
            },
            'wait_time': 2000,
            'full_page': True
        },
        'status': 'active'
    },
    {
        'name': '文本分析',
        'description': '分析文本内容，提取关键词和情感',
        'type': 'data_analysis',
        'command': 'python analyze_text.py {text_file}',
        'config': {
            'language': 'zh-CN',
            'extract_keywords': True,
            'sentiment_analysis': True,
            'max_text_length': 10000
        },
        'status': 'inactive'
    },
    {
        'name': '日志分析器',
        'description': '分析日志文件，提取异常和统计信息',
        'type': 'system',
        'command': 'python log_analyzer.py {log_file} --format={format}',
        'config': {
            'supported_formats': ['nginx', 'apache', 'system'],
            'time_range': 'last_7_days',
            'highlight_errors': True
        },
        'status': 'active'
    }
]

# 配置模拟数据
CONFIGS_DATA = [
    {
        'name': '系统全局配置',
        'description': '系统核心功能的全局配置参数',
        'type': 'system',
        'content': {
            'app_name': 'MCP管理平台',
            'debug_mode': False,
            'log_level': 'info',
            'max_upload_size': '50MB',
            'session_timeout': 3600,
            'allow_registration': True,
            'default_theme': 'light'
        }
    },
    {
        'name': '开发环境配置',
        'description': '开发环境专用配置',
        'type': 'environment',
        'content': {
            'debug_mode': True,
            'log_level': 'debug',
            'database': {
                'host': 'localhost',
                'port': 3306,
                'user': 'dev_user',
                'password': 'dev_password',
                'database': 'mcp_dev'
            },
            'redis': {
                'host': 'localhost',
                'port': 6379,
                'db': 0
            }
        }
    },
    {
        'name': '生产环境配置',
        'description': '生产环境专用配置',
        'type': 'environment',
        'content': {
            'debug_mode': False,
            'log_level': 'warning',
            'database': {
                'host': 'db.example.com',
                'port': 3306,
                'user': 'prod_user',
                'password': 'prod_password',
                'database': 'mcp_prod'
            },
            'redis': {
                'host': 'redis.example.com',
                'port': 6379,
                'db': 0,
                'password': 'redis_password'
            }
        }
    },
    {
        'name': '文件浏览器配置',
        'description': '文件浏览器工具的配置',
        'type': 'tool',
        'content': {
            'allowed_paths': ['/data', '/tmp', '/opt'],
            'max_depth': 5,
            'show_hidden': False,
            'allowed_operations': ['read', 'list', 'download'],
            'file_size_limit': '100MB'
        }
    },
    {
        'name': '用户偏好设置',
        'description': '用户界面和功能偏好配置',
        'type': 'user',
        'content': {
            'theme': 'dark',
            'language': 'zh-CN',
            'page_size': 20,
            'notifications': {
                'email': True,
                'web': True,
                'mobile': False
            },
            'dashboard_widgets': ['system_status', 'recent_logs', 'tool_stats']
        }
    }
]

# 模板模拟数据
TEMPLATES_DATA = [
    {
        'name': '基础网络工具集',
        'description': '常用网络工具的模板集合',
        'type': 'tool',
        'content': {
            'tools': [
                {
                    'name': 'PING测试',
                    'description': '测试主机的网络连通性',
                    'type': 'network',
                    'command': 'ping -c 4 {host}',
                    'config': {
                        'timeout': 5,
                        'count': 4
                    }
                },
                {
                    'name': 'DNS查询',
                    'description': '查询域名的DNS记录',
                    'type': 'network',
                    'command': 'dig {domain} {record_type}',
                    'config': {
                        'record_types': ['A', 'AAAA', 'MX', 'CNAME', 'TXT']
                    }
                },
                {
                    'name': 'Traceroute',
                    'description': '跟踪网络数据包路由路径',
                    'type': 'network',
                    'command': 'traceroute {host}',
                    'config': {
                        'max_hops': 30,
                        'timeout': 5
                    }
                }
            ],
            'category_tags': ['network', 'diagnostic']
        }
    },
    {
        'name': '媒体处理工具集',
        'description': '图像和视频处理工具的模板集合',
        'type': 'tool',
        'content': {
            'tools': [
                {
                    'name': '图像压缩',
                    'description': '压缩图像文件以减小体积',
                    'type': 'media',
                    'command': 'convert {input} -quality {quality} {output}',
                    'config': {
                        'quality_range': [50, 90],
                        'supported_formats': ['jpg', 'png', 'gif']
                    }
                },
                {
                    'name': '图像裁剪',
                    'description': '裁剪图像到指定尺寸',
                    'type': 'media',
                    'command': 'convert {input} -crop {width}x{height}+{x}+{y} {output}',
                    'config': {
                        'supported_formats': ['jpg', 'png', 'gif']
                    }
                },
                {
                    'name': '视频转码',
                    'description': '将视频转换为不同格式',
                    'type': 'media',
                    'command': 'ffmpeg -i {input} -c:v {video_codec} -c:a {audio_codec} {output}',
                    'config': {
                        'supported_formats': ['mp4', 'avi', 'mkv', 'webm'],
                        'video_codecs': ['h264', 'h265', 'vp9'],
                        'audio_codecs': ['aac', 'mp3', 'opus']
                    }
                }
            ],
            'category_tags': ['media', 'image', 'video']
        }
    },
    {
        'name': '系统环境配置模板',
        'description': '不同环境的系统配置模板',
        'type': 'config',
        'content': {
            'configs': [
                {
                    'name': '开发环境',
                    'type': 'environment',
                    'content': {
                        'debug_mode': True,
                        'log_level': 'debug',
                        'database': {
                            'host': 'localhost',
                            'port': 3306
                        }
                    }
                },
                {
                    'name': '测试环境',
                    'type': 'environment',
                    'content': {
                        'debug_mode': True,
                        'log_level': 'info',
                        'database': {
                            'host': 'test-db',
                            'port': 3306
                        }
                    }
                },
                {
                    'name': '生产环境',
                    'type': 'environment',
                    'content': {
                        'debug_mode': False,
                        'log_level': 'warning',
                        'database': {
                            'host': 'prod-db',
                            'port': 3306
                        }
                    }
                }
            ]
        }
    }
]

def generate_logs(tools, count=50):
    """生成随机日志数据"""
    logs = []
    tool_ids = [tool.id for tool in tools]
    
    for _ in range(count):
        # 随机选择一个工具或者没有关联工具
        tool_id = random.choice(tool_ids + [None]) if tool_ids else None
        
        # 随机选择日志级别
        level = random.choice(LOG_LEVELS)
        
        # 创建时间在过去30天内
        days_ago = random.randint(0, 30)
        created_at = datetime.utcnow() - timedelta(days=days_ago)
        
        # 根据级别创建不同的消息
        if level == 'info':
            message = f"工具执行成功：{random.choice(['操作完成', '数据已处理', '任务已完成', '查询成功'])}"
        elif level == 'warning':
            message = f"工具执行警告：{random.choice(['参数无效', '结果不完整', '响应超时', '资源不足'])}"
        elif level == 'error':
            message = f"工具执行错误：{random.choice(['操作失败', '连接断开', '权限不足', '资源不存在'])}"
        else:  # debug
            message = f"工具执行调试：{random.choice(['开始执行', '参数解析', '中间结果', '执行完毕'])}"
        
        # 随机执行时长
        duration = random.randint(50, 5000)
        
        # 随机参数和结果
        params = {
            'param1': random.choice(['value1', 'value2', 'value3']),
            'param2': random.randint(1, 100),
            'param3': random.choice([True, False])
        }
        
        if level == 'error':
            result = {
                'status': 'error',
                'message': f"执行失败: {random.choice(['连接失败', '超时', '参数错误', '权限不足'])}"
            }
        else:
            result = {
                'status': 'success',
                'data': {
                    'field1': random.choice(['值1', '值2', '值3']),
                    'field2': random.randint(100, 999),
                    'field3': [random.randint(1, 10) for _ in range(3)]
                }
            }
        
        # 随机调用者
        caller = random.choice(['admin', 'user', 'system', 'scheduler'])
        
        # 创建日志
        log = Log(
            message=message,
            tool_id=tool_id,
            level=level,
            params=params,
            result=result,
            duration=duration,
            caller=caller
        )
        log.created_at = created_at
        log.updated_at = created_at
        logs.append(log)
    
    return logs

def main():
    """主函数，生成并存储测试数据"""
    with app.app_context():
        print("开始生成测试数据...")
        
        # 清空现有数据
        print("清空现有数据...")
        Log.query.delete()
        Tool.query.delete()
        Config.query.delete()
        Template.query.delete()
        db.session.commit()
        
        # 创建工具数据
        print("创建工具数据...")
        tools = []
        for tool_data in TOOLS_DATA:
            tool = Tool(
                name=tool_data['name'],
                description=tool_data['description'],
                type=tool_data['type'],
                command=tool_data['command'],
                config=tool_data['config']
            )
            # 设置工具状态
            tool.status = tool_data['status']
            
            # 随机设置调用次数和最后调用时间
            if random.random() > 0.3:  # 70%的工具有调用记录
                tool.invoke_count = random.randint(1, 100)
                days_ago = random.randint(0, 14)
                tool.last_invoked_at = datetime.utcnow() - timedelta(days=days_ago)
            
            db.session.add(tool)
            tools.append(tool)
        
        # 创建配置数据
        print("创建配置数据...")
        for config_data in CONFIGS_DATA:
            config = Config(
                name=config_data['name'],
                description=config_data['description'],
                type=config_data['type'],
                content=config_data['content']
            )
            config.is_active = random.random() > 0.2  # 80%的配置处于激活状态
            db.session.add(config)
        
        # 创建模板数据
        print("创建模板数据...")
        for template_data in TEMPLATES_DATA:
            template = Template(
                name=template_data['name'],
                description=template_data['description'],
                type=template_data['type'],
                content=template_data['content']
            )
            db.session.add(template)
        
        db.session.commit()
        
        # 生成日志数据
        print("生成日志数据...")
        logs = generate_logs(tools, count=100)
        db.session.add_all(logs)
        db.session.commit()
        
        print("测试数据生成完成！")
        print(f"已创建 {len(tools)} 个工具")
        print(f"已创建 {len(CONFIGS_DATA)} 个配置")
        print(f"已创建 {len(TEMPLATES_DATA)} 个模板")
        print(f"已创建 {len(logs)} 条日志")

if __name__ == "__main__":
    main() 