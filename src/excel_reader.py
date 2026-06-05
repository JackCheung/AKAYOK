import pandas as pd
from typing import Dict, List, Any
from pathlib import Path
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import EXCEL_FILE


class ExcelDataReader:
    """读取 Excel 文件中的所有数据"""
    
    def __init__(self, file_path: Path = EXCEL_FILE):
        self.file_path = file_path
        self.data = {}
        self._load_all_sheets()
    
    def _load_all_sheets(self):
        """加载所有 sheet 的数据"""
        xl = pd.ExcelFile(self.file_path)
        
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(self.file_path, sheet_name=sheet_name)
            # 清理 NaN 值
            df = df.where(pd.notnull(df), None)
            self.data[sheet_name] = df
    
    def get_website_settings(self) -> Dict[str, Any]:
        """获取网站设置"""
        df = self.data.get("网站设置")
        if df is None or len(df) == 0:
            return {}
        
        # 将第一行转换为字典
        settings = df.iloc[0].to_dict()
        # 清理 NaN 值
        return {k: v for k, v in settings.items() if v is not None}
    
    def get_carousels(self) -> List[Dict[str, Any]]:
        """获取轮播图数据"""
        df = self.data.get("轮播图")
        if df is None:
            return []
        
        # 转换为字典列表
        carousels = df.to_dict("records")
        # 过滤掉无效数据
        return [c for c in carousels if c.get("轮播图片") is not None]
    
    def get_social_media(self) -> List[Dict[str, Any]]:
        """获取社交媒体数据"""
        df = self.data.get("关注我们")
        if df is None:
            return []
        
        return df.to_dict("records")
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """获取产品分类"""
        df = self.data.get("产品分类")
        if df is None:
            return []
        
        return df.to_dict("records")
    
    def get_products(self) -> List[Dict[str, Any]]:
        """获取全部产品"""
        df = self.data.get("全部产品")
        if df is None:
            return []
        
        products = df.to_dict("records")
        # 过滤掉没有产品标题的记录
        return [p for p in products if p.get("产品title") is not None]
    
    def get_custom_pages(self) -> List[Dict[str, Any]]:
        """获取通用页面"""
        df = self.data.get("通用页面")
        if df is None:
            return []
        
        return df.to_dict("records")
    
    def get_all_data(self) -> Dict[str, Any]:
        """获取所有数据"""
        return {
            "website_settings": self.get_website_settings(),
            "carousels": self.get_carousels(),
            "social_media": self.get_social_media(),
            "categories": self.get_categories(),
            "products": self.get_products(),
            "custom_pages": self.get_custom_pages()
        }


if __name__ == "__main__":
    # 测试
    reader = ExcelDataReader()
    data = reader.get_all_data()
    print("Excel 数据加载成功！")
    print(f"产品数量: {len(data['products'])}")
    print(f"分类数量: {len(data['categories'])}")
