import os
import shutil
from pathlib import Path
from typing import Dict, List, Any
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import J2_TEMPLATE_DIR, OUTPUT_DIR
from jinja2 import Environment, FileSystemLoader, select_autoescape


class Jinja2WebsiteGenerator:
    """使用 Jinja2 模板的网站生成器"""

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.website_settings = data.get("website_settings", {})
        self.categories = data.get("categories", [])
        self.products = data.get("products", [])
        self.carousels = data.get("carousels", [])
        self.custom_pages = data.get("custom_pages", [])
        self.social_media = data.get("social_media", [])

        # 确保输出目录存在
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # 获取品牌信息
        self.brand_name = self.website_settings.get("品牌名称", "Godery")
        self.site_title = self.website_settings.get("网站title", f"{self.brand_name} | Office Website")
        self.site_description = self.website_settings.get("网站description", "")
        self.site_keywords = self.website_settings.get("网站keywords", "")
        self.top_notice = self.website_settings.get("顶部通知栏", "")
        self.copyright_info = self.website_settings.get("版权信息", f"© 2024 {self.brand_name}")
        self.logo_url = self.website_settings.get("Logo图片", "")
        self.site_url = self.website_settings.get("网站url", "https://example.com")

        # 筛选畅销品和新品
        self.best_sellers = [p for p in self.products if p.get("畅销品") == "是"]
        self.new_arrivals = [p for p in self.products if p.get("新品") == "是"]

        # 初始化 Jinja2 环境
        self.env = Environment(
            loader=FileSystemLoader(str(J2_TEMPLATE_DIR)),
            autoescape=select_autoescape(['html', 'xml'])
        )

        # 预处理产品数据
        self.processed_products = self._process_products()
        self.processed_categories = self._process_categories()
        self.processed_custom_pages = self._process_custom_pages()
        self.processed_carousels = self._process_carousels()

    def _process_products(self) -> List[Dict]:
        """预处理产品数据"""
        processed = []
        for product in self.products:
            product_title = product.get("产品title", "")
            if not product_title:
                continue

            product_slug = product.get("产品slug", "")
            if not product_slug or str(product_slug).lower() == 'nan':
                product_slug = str(product_title).replace(" ", "-").lower()

            product_category = product.get("产品分类", "")
            category_slug = str(product_category).replace(" ", "-").lower() if product_category else "products"

            product_image = product.get("产品图片", "")
            if not product_image or str(product_image).lower() == 'nan':
                product_image = ""

            product_price = product.get("产品价格", "")
            if not product_price or str(product_price).lower() == 'nan':
                product_price = ""

            amazon_link = product.get("亚马逊链接", "")
            if not amazon_link or str(amazon_link).lower() == 'nan':
                amazon_link = "#"

            product_description = product.get("产品描述", "")
            if not product_description or str(product_description).lower() == 'nan':
                product_description = ""

            processed.append({
                "title": product_title,
                "slug": product_slug,
                "category": product_category,
                "category_slug": category_slug,
                "image": product_image,
                "price": product_price,
                "amazon_link": amazon_link,
                "description": product_description,
                "is_best_seller": product.get("畅销品") == "是",
                "is_new_arrival": product.get("新品") == "是"
            })
        return processed

    def _process_categories(self) -> List[Dict]:
        """预处理分类数据"""
        processed = []
        for category in self.categories:
            category_title = category.get("分类title", "")
            if not category_title:
                continue

            category_slug = category.get("分类slug", "")
            if not category_slug or str(category_slug).lower() == 'nan':
                category_slug = str(category_title).replace(" ", "-").lower()

            processed.append({
                "title": category_title,
                "slug": category_slug
            })
        return processed

    def _process_custom_pages(self) -> List[Dict]:
        """预处理自定义页面数据"""
        processed = []
        for page in self.custom_pages:
            page_title = page.get("页面title", "")
            if not page_title:
                continue

            page_slug = page.get("页面slug", "")
            if not page_slug or str(page_slug).lower() == 'nan':
                page_slug = str(page_title).replace(" ", "-").lower()

            page_content = page.get("页面内容", "")
            if not page_content or str(page_content).lower() == 'nan':
                page_content = ""

            processed.append({
                "title": page_title,
                "slug": page_slug,
                "content": page_content
            })
        return processed

    def _process_carousels(self) -> List[Dict]:
        """预处理轮播图数据"""
        processed = []
        for carousel in self.carousels:
            carousel_image = carousel.get("轮播图片", "")
            if not carousel_image or str(carousel_image).lower() == 'nan':
                continue

            carousel_alt = carousel.get("轮播描述", carousel.get("轮播标题", "Banner"))
            carousel_link = carousel.get("轮播链接", "#")
            if not carousel_link or str(carousel_link).lower() == 'nan':
                carousel_link = "#"

            processed.append({
                "image": carousel_image,
                "alt": carousel_alt,
                "link": carousel_link
            })
        return processed

    def _get_common_context(self) -> Dict:
        """获取所有页面共用的上下文"""
        return {
            "brand_name": self.brand_name,
            "site_title": self.site_title,
            "site_description": self.site_description,
            "site_keywords": self.site_keywords,
            "top_notice": self.top_notice,
            "copyright_info": self.copyright_info,
            "logo_url": self.logo_url,
            "categories": self.processed_categories,
            "custom_pages": self.processed_custom_pages
        }

    def generate_robots_txt(self):
        """生成 robots.txt 文件"""
        site_url = self.site_url
        if not site_url.endswith('/'):
            site_url += '/'

        content = f"""User-agent: *
Allow: /

Sitemap: {site_url}sitemap.xml
"""
        output_path = OUTPUT_DIR / "robots.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"robots.txt 生成成功: {output_path}")

    def generate_sitemap_xml(self):
        """生成 sitemap.xml 文件"""
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        site_url = self.site_url
        if not site_url.endswith('/'):
            site_url += '/'

        urls = []
        urls.append((site_url, "1.0", "daily"))

        for cat in self.processed_categories:
            urls.append((f"{site_url}{cat['slug']}/", "0.8", "weekly"))

        for product in self.processed_products:
            urls.append((f"{site_url}{product['category_slug']}/{product['slug']}/", "0.6", "weekly"))

        for page in self.processed_custom_pages:
            urls.append((f"{site_url}{page['slug']}/", "0.7", "monthly"))

        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
        for loc, priority, changefreq in urls:
            xml_content += f'''  <url>
    <loc>{loc}</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>
'''
        xml_content += '''</urlset>'''

        output_path = OUTPUT_DIR / "sitemap.xml"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        print(f"sitemap.xml 生成成功: {output_path}")

    def generate_homepage(self):
        """生成首页"""
        template = self.env.get_template("index.html")

        context = self._get_common_context()
        context.update({
            "page_title": self.site_title,
            "carousels": self.processed_carousels,
            "best_sellers": self.processed_products[:10],
            "new_arrivals": [p for p in self.processed_products if p.get("is_new_arrival")][:10]
        })

        content = template.render(**context)

        output_path = OUTPUT_DIR / "index.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"首页生成成功: {output_path}")

    def generate_category_pages(self):
        """生成分类页面"""
        template = self.env.get_template("category.html")

        for category in self.processed_categories:
            category_title = category["title"]
            category_slug = category["slug"]

            # 创建分类目录
            category_dir = OUTPUT_DIR / category_slug
            category_dir.mkdir(exist_ok=True)

            # 筛选该分类的产品
            category_products = [p for p in self.processed_products if p.get("category") == category_title]

            context = self._get_common_context()
            context.update({
                "page_title": f"{category_title} | {self.brand_name}",
                "category_title": category_title,
                "current_category_slug": category_slug,
                "products": category_products
            })

            content = template.render(**context)

            output_path = category_dir / "index.html"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"分类页面生成成功: {output_path}")

    def generate_product_pages(self):
        """生成产品详情页面"""
        template = self.env.get_template("product.html")

        for product in self.processed_products:
            product_title = product["title"]
            product_slug = product["slug"]
            category_slug = product["category_slug"]
            category_title = product["category"]

            # 创建产品目录
            product_dir = OUTPUT_DIR / category_slug / product_slug
            product_dir.mkdir(parents=True, exist_ok=True)

            # 找出相关产品（同分类的其他产品）
            related_products = [
                p for p in self.processed_products
                if p["category"] == category_title and p["slug"] != product_slug
            ][:8]

            context = self._get_common_context()
            context.update({
                "page_title": f"{product_title} | {self.brand_name}",
                "product_title": product_title,
                "product_image": product["image"],
                "product_price": product["price"],
                "product_description": product["description"],
                "amazon_link": product["amazon_link"],
                "category_title": category_title,
                "category_slug": category_slug,
                "related_products": related_products
            })

            content = template.render(**context)

            output_path = product_dir / "index.html"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"产品详情页生成成功: {output_path}")

    def generate_custom_pages(self):
        """生成自定义页面"""
        template = self.env.get_template("custompage.html")

        for page in self.processed_custom_pages:
            page_title = page["title"]
            page_slug = page["slug"]

            # 创建页面目录
            page_dir = OUTPUT_DIR / page_slug
            page_dir.mkdir(exist_ok=True)

            context = self._get_common_context()
            context.update({
                "page_title": f"{page_title} | {self.brand_name}",
                "current_page_slug": page_slug,
                "page_content": page["content"]
            })

            content = template.render(**context)

            output_path = page_dir / "index.html"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"自定义页面生成成功: {output_path}")

    def copy_static_files(self):
        """复制静态文件（CSS、JS等）"""
        # 复制 CSS
        css_src = J2_TEMPLATE_DIR / "style.css"
        if css_src.exists():
            css_dst = OUTPUT_DIR / "style.css"
            shutil.copy2(css_src, css_dst)
            print(f"CSS 文件复制成功: {css_dst}")

        # 复制 JS
        js_src = J2_TEMPLATE_DIR / "script.js"
        if js_src.exists():
            js_dst = OUTPUT_DIR / "script.js"
            shutil.copy2(js_src, js_dst)
            print(f"JS 文件复制成功: {js_dst}")

    def generate_all(self):
        """生成所有页面"""
        print("=" * 60)
        print("开始使用 Jinja2 模板生成网站...")
        print("=" * 60)

        self.generate_robots_txt()
        self.generate_sitemap_xml()
        self.copy_static_files()
        self.generate_homepage()
        self.generate_category_pages()
        self.generate_product_pages()
        self.generate_custom_pages()

        print("=" * 60)
        print("网站生成完成！")
        print(f"输出目录: {OUTPUT_DIR.absolute()}")
        print("=" * 60)
