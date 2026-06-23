import requests
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_BASE_URL, FEISHU_APP_TOKEN


class FeishuAPI:
    """飞书多维表格 API 封装"""
    
    def __init__(self, app_id: str = FEISHU_APP_ID, app_secret: str = FEISHU_APP_SECRET):
        self.app_id = app_id
        self.app_secret = app_secret
        self.tenant_access_token = None
        self.base_url = FEISHU_BASE_URL
    
    def get_tenant_access_token(self) -> str:
        """获取租户访问令牌"""
        url = f"{self.base_url}/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        
        if data.get("code") != 0:
            raise Exception(f"获取飞书访问令牌失败: {data}")
        
        self.tenant_access_token = data["tenant_access_token"]
        return self.tenant_access_token
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        if not self.tenant_access_token:
            self.get_tenant_access_token()
        
        return {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
    
    def list_records(self, app_token: str, table_id: str, page_size: int = 100) -> List[Dict[str, Any]]:
        """获取多维表格记录"""
        all_records = []
        page_token = ""
        
        while True:
            url = f"{self.base_url}/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
            params = {"page_size": page_size}
            if page_token:
                params["page_token"] = page_token
            
            response = requests.get(url, headers=self._get_headers(), params=params)
            data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"获取飞书表格记录失败: {data}")
            
            items = data.get("data", {}).get("items", [])
            # 提取记录的 fields 数据
            records = [item.get("fields", {}) for item in items]
            all_records.extend(records)
            
            page_token = data.get("data", {}).get("page_token", "")
            if not page_token:
                break
        
        return all_records
    
    def list_tables(self, app_token: str) -> List[Dict[str, Any]]:
        """获取多维表格中的所有数据表"""
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{app_token}/tables"
        response = requests.get(url, headers=self._get_headers())
        data = response.json()
        
        if data.get("code") != 0:
            raise Exception(f"获取飞书表格列表失败: {data}")
        
        return data.get("data", {}).get("items", [])


class FeishuDataReader:
    """从飞书多维表格读取数据"""
    
    # 默认的表名映射（与Excel中的sheet对应）
    DEFAULT_TABLE_MAPPING = {
        "网站设置": "网站设置",
        "产品分类": "产品分类",
        "全部产品": "全部产品",
        "通用页面": "通用页面",
        "轮播图": "轮播图",
        "关注我们": "关注我们"
    }
    
    def __init__(self, app_token: str = FEISHU_APP_TOKEN, table_mapping: Optional[Dict[str, str]] = None):
        self.api = FeishuAPI()
        self.app_token = app_token
        self.table_mapping = table_mapping or self.DEFAULT_TABLE_MAPPING
        self.data = {}
    
    def _convert_field_value(self, value: Any) -> Any:
        """转换飞书字段值为标准格式"""
        if isinstance(value, dict):
            # 处理图片等复杂类型
            if value.get("type") == "image" and value.get("image_list"):
                # 取第一张图片的URL
                images = value.get("image_list", [])
                if images:
                    return images[0].get("url", "")
            # 处理多选/关联等
            elif isinstance(value, list):
                return ",".join(str(item) for item in value)
        elif isinstance(value, list):
            return ",".join(str(item) for item in value)
        return value
    
    def get_table_data(self, table_name: str) -> List[Dict[str, Any]]:
        """获取指定表的数据"""
        try:
            # 首先获取所有表，找到对应table_id
            tables = self.api.list_tables(self.app_token)
            table_id = None
            
            for table in tables:
                if table.get("name") == table_name:
                    table_id = table.get("table_id")
                    break
            
            if not table_id:
                print(f"警告: 未找到表 '{table_name}'")
                return []
            
            # 获取记录
            records = self.api.list_records(self.app_token, table_id)
            
            # 转换字段值
            converted_records = []
            for record in records:
                converted = {}
                for key, value in record.items():
                    converted[key] = self._convert_field_value(value)
                converted_records.append(converted)
            
            return converted_records
        except Exception as e:
            print(f"读取表 '{table_name}' 失败: {e}")
            return []
    
    def get_website_settings(self) -> Dict[str, Any]:
        """获取网站设置"""
        table_name = self.table_mapping.get("网站设置", "网站设置")
        records = self.get_table_data(table_name)
        if records:
            return records[0]
        return {}
    
    def get_carousels(self) -> List[Dict[str, Any]]:
        """获取轮播图数据"""
        table_name = self.table_mapping.get("轮播图", "轮播图")
        return self.get_table_data(table_name)
    
    def get_social_media(self) -> List[Dict[str, Any]]:
        """获取社交媒体数据"""
        table_name = self.table_mapping.get("关注我们", "关注我们")
        return self.get_table_data(table_name)
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """获取产品分类"""
        table_name = self.table_mapping.get("产品分类", "产品分类")
        return self.get_table_data(table_name)
    
    def get_products(self) -> List[Dict[str, Any]]:
        """获取全部产品"""
        table_name = self.table_mapping.get("全部产品", "全部产品")
        return self.get_table_data(table_name)
    
    def get_custom_pages(self) -> List[Dict[str, Any]]:
        """获取通用页面"""
        table_name = self.table_mapping.get("通用页面", "通用页面")
        return self.get_table_data(table_name)
    
    def get_all_data(self) -> Dict[str, Any]:
        """获取所有数据"""
        print("从飞书多维表格读取数据...")
        return {
            "website_settings": self.get_website_settings(),
            "carousels": self.get_carousels(),
            "social_media": self.get_social_media(),
            "categories": self.get_categories(),
            "products": self.get_products(),
            "custom_pages": self.get_custom_pages()
        }


if __name__ == "__main__":
    print("飞书 API 模块已准备好")
    print("\n使用说明:")
    print("1. 配置环境变量:")
    print("   - FEISHU_APP_ID: 飞书应用 ID")
    print("   - FEISHU_APP_SECRET: 飞书应用密钥")
    print("   - FEISHU_APP_TOKEN: 飞书多维表格 App Token")
    print("\n2. 在飞书开放平台创建应用并获取上述信息")
    print("3. 将应用添加到多维表格的协作者中")
