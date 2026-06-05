#!/usr/bin/env python3
"""
网站生成器主入口脚本

使用方法:
    python generate.py [--source excel|feishu] [--template jinja2|legacy]

默认从 飞书多维表格 读取数据，默认使用 Jinja2 模板
"""

import sys
import argparse
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from src.excel_reader import ExcelDataReader
from src.feishu_api import FeishuDataReader
from src.generator import WebsiteGenerator
from src.generator_j2 import Jinja2WebsiteGenerator


def main():
    parser = argparse.ArgumentParser(description="生成静态网站")
    parser.add_argument(
        "--source",
        type=str,
        default="feishu",
        choices=["excel", "feishu"],
        help="数据源类型: excel 或 feishu (默认: feishu)"
    )
    parser.add_argument(
        "--template",
        type=str,
        default="jinja2",
        choices=["jinja2", "legacy"],
        help="模板引擎: jinja2 (新) 或 legacy (旧) (默认: jinja2)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("网站生成器")
    print("=" * 60)
    
    # 1. 读取数据
    print(f"\n1. 从 {args.source} 读取数据...")
    if args.source == "excel":
        reader = ExcelDataReader()
        data = reader.get_all_data()
        print(f"   数据加载成功:")
        print(f"   - 产品数量: {len(data['products'])}")
        print(f"   - 分类数量: {len(data['categories'])}")
        print(f"   - 自定义页面数量: {len(data['custom_pages'])}")
    else:
        try:
            reader = FeishuDataReader()
            data = reader.get_all_data()
            print(f"   数据加载成功:")
            print(f"   - 产品数量: {len(data['products'])}")
            print(f"   - 分类数量: {len(data['categories'])}")
            print(f"   - 自定义页面数量: {len(data['custom_pages'])}")
        except Exception as e:
            print(f"   从飞书读取数据失败: {e}")
            print("   回退到 Excel 数据源")
            reader = ExcelDataReader()
            data = reader.get_all_data()
    
    # 2. 生成网站
    print(f"\n2. 使用 {args.template} 模板引擎生成网站...")
    if args.template == "jinja2":
        generator = Jinja2WebsiteGenerator(data)
    else:
        generator = WebsiteGenerator(data)
    generator.generate_all()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
    print("\n下一步:")
    print("   1. 检查 output 目录下的生成文件")
    print("   2. 将 output 目录的内容部署到 GitHub Pages")
    print("\n使用Excel数据源:")
    print("   1. 准备好 网站管理.xlsx 文件")
    print("   2. 运行: python generate.py --source excel")
    print("\n使用旧模板引擎:")
    print("   python generate.py --template legacy")


if __name__ == "__main__":
    main()
