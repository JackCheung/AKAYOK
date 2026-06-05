import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 尝试从 .env 文件读取配置
env_file = BASE_DIR / ".env"
if env_file.exists():
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# 模板文件目录
TEMPLATE_DIR = BASE_DIR / "模板文件" / "template"

# 输出目录
OUTPUT_DIR = BASE_DIR / "output"

# Excel 文件路径
EXCEL_FILE = BASE_DIR / "网站管理.xlsx"

# 飞书 API 配置（用于飞书多维表格 API）
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
FEISHU_APP_TOKEN = os.getenv("FEISHU_APP_TOKEN", "")
FEISHU_BASE_URL = "https://open.feishu.cn"

# 网站配置
WEBSITE_CONFIG = {
    "brand_name": "Godery",
    "default_title": "Godery Office Website"
}
