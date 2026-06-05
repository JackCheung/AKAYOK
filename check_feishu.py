#!/usr/bin/env python3
"""
飞书配置诊断工具
用于测试飞书API配置是否正确
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from src.config import FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_APP_TOKEN, FEISHU_BASE_URL
from src.feishu_api import FeishuAPI

def check_config():
    """检查配置"""
    print("=" * 60)
    print("飞书配置诊断工具")
    print("=" * 60)
    
    print("\n📋 当前配置检查：")
    print(f"   FEISHU_APP_ID:     {FEISHU_APP_ID[:10]}..." if FEISHU_APP_ID else "   FEISHU_APP_ID:     ❌ 未设置")
    print(f"   FEISHU_APP_SECRET: {FEISHU_APP_SECRET[:10]}..." if FEISHU_APP_SECRET else "   FEISHU_APP_SECRET: ❌ 未设置")
    print(f"   FEISHU_APP_TOKEN:  {FEISHU_APP_TOKEN[:10]}..." if FEISHU_APP_TOKEN else "   FEISHU_APP_TOKEN:  ❌ 未设置")
    
    if not FEISHU_APP_ID or not FEISHU_APP_SECRET:
        print("\n❌ 配置错误：")
        print("   请先设置环境变量：")
        print("   - FEISHU_APP_ID")
        print("   - FEISHU_APP_SECRET")
        print("   - FEISHU_APP_TOKEN (可选，用于读取表格)")
        return False
    
    if not FEISHU_APP_TOKEN:
        print("\n⚠️  警告：未设置 FEISHU_APP_TOKEN")
        print("   无法读取多维表格数据")
    
    print("\n✅ 基本配置检查完成")
    return True

def test_auth():
    """测试获取访问令牌"""
    print("\n" + "=" * 60)
    print("🔑 测试身份认证")
    print("=" * 60)
    
    try:
        api = FeishuAPI()
        token = api.get_tenant_access_token()
        print(f"\n✅ 获取访问令牌成功！")
        print(f"   Token: {token[:20]}...")
        return True
    except Exception as e:
        print(f"\n❌ 获取访问令牌失败：")
        print(f"   错误: {e}")
        print("\n💡 可能的原因：")
        print("   1. FEISHU_APP_ID 或 FEISHU_APP_SECRET 错误")
        print("   2. 应用没有启用相关权限")
        print("   3. 应用被停用或删除")
        return False

def test_tables():
    """测试读取表格列表"""
    if not FEISHU_APP_TOKEN:
        return False
    
    print("\n" + "=" * 60)
    print("📊 测试读取多维表格")
    print("=" * 60)
    
    try:
        api = FeishuAPI()
        tables = api.list_tables(FEISHU_APP_TOKEN)
        
        print(f"\n✅ 成功读取表格列表！")
        print(f"   找到 {len(tables)} 个数据表：")
        for i, table in enumerate(tables, 1):
            print(f"   {i}. {table.get('name')} (ID: {table.get('table_id')})")
        return True
    except Exception as e:
        print(f"\n❌ 读取表格失败：")
        print(f"   错误: {e}")
        print("\n💡 可能的原因：")
        print("   1. FEISHU_APP_TOKEN 错误")
        print("   2. 应用没有添加为该多维表格的协作者")
        print("   3. 应用没有多维表格读取权限")
        return False

def main():
    if not check_config():
        print("\n💡 请设置环境变量后再运行：")
        print("   Windows (PowerShell):")
        print('   $env:FEISHU_APP_ID="你的AppID"')
        print('   $env:FEISHU_APP_SECRET="你的AppSecret"')
        print('   $env:FEISHU_APP_TOKEN="你的BaseToken"')
        print("\n   或者创建 .env 文件：")
        print('   FEISHU_APP_ID=你的AppID')
        print('   FEISHU_APP_SECRET=你的AppSecret')
        print('   FEISHU_APP_TOKEN=你的BaseToken')
        return
    
    if test_auth():
        test_tables()
    
    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
