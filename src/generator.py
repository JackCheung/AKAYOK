import os
import shutil
import re
from pathlib import Path
from typing import Dict, List, Any
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import TEMPLATE_DIR, OUTPUT_DIR


class WebsiteGenerator:
    """网站生成器"""
    
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
        
        # 筛选畅销品和新品
        self.best_sellers = [p for p in self.products if p.get("畅销品") == "是"]
        self.new_arrivals = [p for p in self.products if p.get("新品") == "是"]
    
    def generate_robots_txt(self):
        """生成 robots.txt 文件"""
        site_url = self.website_settings.get("网站url", "https://example.com")
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
        site_url = self.website_settings.get("网站url", "https://example.com")
        if not site_url.endswith('/'):
            site_url += '/'
        
        urls = []
        
        # 首页
        urls.append((site_url, "1.0", "daily"))
        
        # 分类页面
        for cat in self.categories:
            cat_slug = cat.get("分类slug", "")
            if cat_slug and str(cat_slug).lower() != 'nan':
                urls.append((f"{site_url}{cat_slug}/", "0.8", "weekly"))
        
        # 产品页面
        for product in self.products:
            product_title = product.get("产品title", "")
            if not product_title:
                continue
            product_slug = product.get("产品slug", "")
            if not product_slug or str(product_slug).lower() == 'nan':
                product_slug = str(product_title).replace(" ", "-")
            product_category = product.get("产品分类", "")
            category_slug = str(product_category).replace(" ", "-") if product_category else "products"
            urls.append((f"{site_url}{category_slug}/{product_slug}/", "0.6", "weekly"))
        
        # 自定义页面
        for page in self.custom_pages:
            page_slug = page.get("页面slug", "")
            if page_slug and str(page_slug).lower() != 'nan':
                urls.append((f"{site_url}{page_slug}/", "0.7", "monthly"))
        
        # 生成 XML
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
        xml_content += '</urlset>'
        
        output_path = OUTPUT_DIR / "sitemap.xml"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        print(f"sitemap.xml 生成成功: {output_path}")
    
    def copy_static_files(self):
        """复制静态文件（CSS、JS 等）"""
        # 只复制静态资源，不复制HTML模板（模板用于生成新页面）
        static_extensions = [".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico"]
        for item in TEMPLATE_DIR.iterdir():
            if item.is_file() and item.suffix.lower() in static_extensions:
                shutil.copy2(item, OUTPUT_DIR / item.name)
    
    def generate_product_card_html(self, product: Dict[str, Any]) -> str:
        """生成产品卡片HTML"""
        product_title = product.get("产品title", "Product")
        product_slug = product.get("产品slug", "")
        if not product_slug:
            product_slug = str(product_title).replace(" ", "-")
        product_category = product.get("产品分类", "")
        category_slug = str(product_category).replace(" ", "-") if product_category else "products"
        product_img = product.get("产品图片", "")
        # 获取第一张图片
        if product_img and isinstance(product_img, str):
            product_img = product_img.split(",")[0].strip()
        if not product_img:
            product_img = "https://via.placeholder.com/300x300"
        product_price = product.get("单价", "$0.00")
        if not isinstance(product_price, str):
            product_price = f"${product_price}" if product_price else "$0.00"
        product_asin = product.get("asin", "")
        amazon_link = f"https://www.amazon.com/dp/{product_asin}/" if product_asin else "#"
        
        product_url = f"/{category_slug}/{product_slug}/"
        
        return f'''
        <div class="product-card">
          <a href="{product_url}">
            <img src="{product_img}" alt="{product_title}" class="product-img">
          </a>
          <div class="product-info">
            <h3 class="product-name">
              <a href="{product_url}">{product_title}</a>
            </h3>
            <p class="product-price">{product_price}</p>
            <a href="{amazon_link}" target="_blank" class="buy-btn">Buy on Amazon</a>
          </div>
        </div>
        '''
    
    def generate_carousel_slide_html(self, carousel: Dict[str, Any]) -> str:
        """生成轮播图HTML"""
        img_url = carousel.get("轮播图片", "")
        img_alt = carousel.get("图片文本alt", "Banner")
        link_url = carousel.get("图片链接", "#")
        
        return f'''
        <div class="slide">
          <a href="{link_url}" target="_blank">
            <img src="{img_url}" alt="{img_alt}">
          </a>
        </div>
        '''
    
    def generate_navigation_html(self) -> str:
        """生成导航HTML"""
        nav_items = []
        nav_items.append(f'<li><a href="/" class="active">Home</a></li>')
        
        for cat in self.categories:
            cat_title = cat.get("分类title", "Category")
            cat_slug = cat.get("分类slug", "")
            if cat_slug:
                nav_items.append(f'<li><a href="/{cat_slug}/">{cat_title}</a></li>')
        
        # 添加自定义页面
        for page in self.custom_pages:
            page_title = page.get("页面title", "Page")
            page_slug = page.get("页面slug", "")
            if page_slug:
                nav_items.append(f'<li><a href="/{page_slug}/">{page_title}</a></li>')
        
        return "\n".join(nav_items)
    
    def generate_homepage(self):
        """生成首页"""
        template_path = TEMPLATE_DIR / "index.html"
        output_path = OUTPUT_DIR / "index.html"
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换品牌名和基础信息
        content = content.replace("AKAYOK", self.brand_name)
        content = content.replace("akayok.com", self.website_settings.get("网站url", "example.com"))
        content = re.sub(r'<title>.*?</title>', f'<title>{self.site_title}</title>', content)
        
        # 替换SEO描述
        if self.site_description:
            content = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{self.site_description}">', content)
        if self.site_keywords:
            content = re.sub(r'<meta name="keywords" content="[^"]*">', f'<meta name="keywords" content="{self.site_keywords}">', content)
        
        # 替换顶部通知
        if self.top_notice:
            content = re.sub(r'HOLIDAY SALE: USE CODE <strong>XMAS20</strong> FOR 20% OFF', self.top_notice, content)
        
        # 替换版权信息
        if self.copyright_info:
            content = re.sub(r'© 2011 - 2026 The AKAYOK Company\. All rights reserved\.', self.copyright_info, content)
        
        # 替换导航
        nav_html = self.generate_navigation_html()
        content = re.sub(r'<ul class="nav-list">.*?</ul>', f'<ul class="nav-list">{nav_html}</ul>', content, flags=re.DOTALL)
        
        # 替换轮播图
        if self.carousels:
            carousel_html = "".join([self.generate_carousel_slide_html(c) for c in self.carousels])
            content = re.sub(r'<div class="slide active">.*?</div>\s*<div class="slide">.*?</div>\s*<div class="slide">.*?</div>', carousel_html, content, flags=re.DOTALL)
        
        # 替换畅销品
        if self.best_sellers:
            best_sellers_html = "".join([self.generate_product_card_html(p) for p in self.best_sellers])
            # 找到第一个产品轮播并替换
            content = re.sub(r'<div class="product-carousel" id="productCarousel1">.*?</div>\s*<button class="carousel-btn next"', 
                            f'<div class="product-carousel" id="productCarousel1">{best_sellers_html}</div><button class="carousel-btn next"', 
                            content, flags=re.DOTALL)
        
        # 替换新品
        if self.new_arrivals:
            new_arrivals_html = "".join([self.generate_product_card_html(p) for p in self.new_arrivals])
            # 找到第二个产品轮播并替换
            content = re.sub(r'<div class="product-carousel" id="productCarousel2">.*?</div>\s*<button class="carousel-btn next"', 
                            f'<div class="product-carousel" id="productCarousel2">{new_arrivals_html}</div><button class="carousel-btn next"', 
                            content, flags=re.DOTALL)
        
        # 保存文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"首页生成成功: {output_path}")
    
    def generate_category_pages(self):
        """生成分类页面"""
        template_path = TEMPLATE_DIR / "category.html"
        
        # 为每个分类创建目录和页面
        for category in self.categories:
            category_title = category.get("分类title", "Category")
            category_slug = category.get("分类slug", "")
            if not category_slug:
                continue
            
            # 创建分类目录
            category_dir = OUTPUT_DIR / category_slug
            category_dir.mkdir(exist_ok=True)
            
            # 复制模板
            output_path = category_dir / "index.html"
            shutil.copy2(template_path, output_path)
            
            # 读取并修改内容
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换品牌名和导航
            content = content.replace("AKAYOK", self.brand_name)
            
            # 替换分类标题
            content = content.replace("Office Supplies", category_title)
            
            # 替换导航
            nav_html = self.generate_navigation_html()
            content = re.sub(r'<ul class="nav-list">.*?</ul>', f'<ul class="nav-list">{nav_html}</ul>', content, flags=re.DOTALL)
            
            # 筛选该分类的产品
            category_products = [p for p in self.products if p.get("产品分类") == category_title]
            if category_products:
                products_html = "".join([self.generate_product_card_html(p) for p in category_products])
                # 替换产品展示区域
                content = re.sub(r'<div class="product-grid">.*?</div>', 
                               f'<div class="product-grid">{products_html}</div>', 
                               content, flags=re.DOTALL)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"分类页面生成成功: {output_path}")
    
    def generate_product_pages(self):
        """生成产品详情页"""
        template_path = TEMPLATE_DIR / "product.html"
        
        for product in self.products:
            product_title = product.get("产品title", "")
            if not product_title:
                continue
            
            product_slug = product.get("产品slug", "")
            product_category = product.get("产品分类", "")
            product_price = product.get("单价", "$0.00")
            product_description = product.get("产品简介", "")
            product_images = product.get("产品图片", "")
            product_asin = product.get("asin", "")
            product_keywords = product.get("产品keywords", "")
            product_desc = product.get("产品description", "")
            
            # 确保 slug 是字符串且有效
            if not product_slug or not isinstance(product_slug, str) or product_slug.lower() == 'nan':
                product_slug = str(product_title).replace(" ", "-")
            
            # 创建产品目录
            category_slug = str(product_category).replace(" ", "-") if product_category else "products"
            product_dir = OUTPUT_DIR / category_slug / product_slug
            product_dir.mkdir(parents=True, exist_ok=True)
            
            # 复制模板
            output_path = product_dir / "index.html"
            shutil.copy2(template_path, output_path)
            
            # 读取并修改内容
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换品牌名
            content = content.replace("AKAYOK", self.brand_name)
            
            # 替换页面标题和 SEO
            content = re.sub(r'<title>.*?</title>', f'<title>{product_title} | {self.brand_name}</title>', content)
            
            if product_keywords and str(product_keywords).lower() != 'nan':
                content = re.sub(r'<meta name="keywords" content="[^"]*">', f'<meta name="keywords" content="{product_keywords}">', content)
            if product_desc and str(product_desc).lower() != 'nan':
                content = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{product_desc}">', content)
            
            # 替换产品标题 - 更全面的替换
            original_title = "Melissa & Doug Finger Paint Paper Pad (2-Pack, 50-Sheets Each) - 12x18 Inch Art Paper for Kids Activities, Arts and Crafts, and Homeschool Essentials - FSC Certified"
            content = content.replace(original_title, product_title)
            
            # 替换产品价格 - 需要替换多个地方
            price_str = str(product_price) if product_price is not None else "$0.00"
            if price_str.lower() == 'nan':
                price_str = "$0.00"
            if not price_str.startswith('$'):
                price_str = f"${price_str}"
            # 替换主要价格
            content = content.replace("$49.99", price_str, 1)
            # 替换分享弹窗里的价格
            content = re.sub(r'<p class="share-product-price">\$\d+\.\d+</p>', f'<p class="share-product-price">{price_str}</p>', content)
            
            # 替换产品描述
            product_description_str = str(product_description) if product_description is not None else ""
            if product_description_str.lower() == 'nan':
                product_description_str = ""
            if product_description_str:
                original_desc = "Our Premium Cotton T-Shirt is crafted from 100% organic cotton, offering exceptional comfort and durability. The minimalist design features a classic crew neck and clean finish, making it perfect for everyday wear. Available in multiple colors and sizes."
                content = content.replace(original_desc, product_description_str)
            
            # 处理产品图片 - 确保URL完整
            image_list = []
            if product_images and str(product_images).lower() != 'nan':
                image_str = str(product_images)
                image_list = [img.strip() for img in image_str.split(',') if img.strip()]
                # 补全不完整的URL
                for i in range(len(image_list)):
                    img = image_list[i]
                    if img and not img.startswith('http'):
                        image_list[i] = f"https://m.media-amazon.com/images/I/{img}"
            
            if image_list:
                main_image = image_list[0]
                # 替换主图
                content = content.replace("https://m.media-amazon.com/images/I/71Jl-KMF9LL._SL1500_.jpg", main_image)
                # 更新其他图片
                placeholder_images = [
                    "https://m.media-amazon.com/images/I/819cd3d4eML._SL1500_.jpg",
                    "https://m.media-amazon.com/images/I/81-ektvX+tL._SL1500_.jpg",
                    "https://m.media-amazon.com/images/I/81Q0QsYZJYL._SL1500_.jpg",
                    "https://m.media-amazon.com/images/I/81CRQFxl8GL._SL1500_.jpg"
                ]
                for i, placeholder in enumerate(placeholder_images):
                    if i + 1 < len(image_list):
                        content = content.replace(placeholder, image_list[i + 1])
            
            # 替换亚马逊链接
            if product_asin and str(product_asin).lower() != 'nan':
                amazon_url = f"https://www.amazon.com/dp/{product_asin}/"
                content = content.replace("https://www.amazon.com/dp/B0DYNH1LYR/", amazon_url)
            
            # 替换面包屑导航
            breadcrumb_html = f'''
            <a href="/">Home</a>
            <span>/</span>
            <a href="/{category_slug}/">{product_category}</a>
            <span>/</span>
            <span class="current">{product_title}</span>
            '''
            # 使用更简单的替换方式
            breadcrumb_start = content.find('<div class="breadcrumb">')
            breadcrumb_end = content.find('</div>', breadcrumb_start)
            if breadcrumb_start != -1 and breadcrumb_end != -1:
                new_breadcrumb = f'<div class="breadcrumb">\n        <div class="container">\n          {breadcrumb_html}\n        </div>\n      </div>'
                content = content[:breadcrumb_start] + new_breadcrumb + content[breadcrumb_end + 6:]
            
            # 生成相关产品（同分类下的其他产品）
            related_products = [p for p in self.products if p.get("产品分类") == product_category and p.get("产品title") != product_title][:6]
            if related_products:
                related_html = ""
                for rp in related_products:
                    rp_title = rp.get("产品title", "")
                    rp_slug_val = rp.get("产品slug", "")
                    if not rp_slug_val or str(rp_slug_val).lower() == 'nan':
                        rp_slug_val = str(rp_title).replace(" ", "-")
                    rp_price = rp.get("单价", "$0.00")
                    rp_img = rp.get("产品图片", "https://via.placeholder.com/300x300")
                    rp_img_str = str(rp_img)
                    if ',' in rp_img_str:
                        rp_img_str = rp_img_str.split(',')[0].strip()
                    if not rp_img_str.startswith('http') and rp_img_str.lower() != 'nan':
                        rp_img_str = f"https://m.media-amazon.com/images/I/{rp_img_str}"
                    if rp_img_str.lower() == 'nan':
                        rp_img_str = "https://via.placeholder.com/300x300"
                    rp_asin = rp.get("asin", "")
                    rp_price_str = str(rp_price) if rp_price is not None else "$0.00"
                    if rp_price_str.lower() == 'nan':
                        rp_price_str = "$0.00"
                    if not rp_price_str.startswith('$'):
                        rp_price_str = f"${rp_price_str}"
                    rp_amazon_url = f"https://www.amazon.com/dp/{rp_asin}/" if rp_asin and str(rp_asin).lower() != 'nan' else "#"
                    
                    related_html += f'''
                    <div class="related-card">
                      <a href="/{category_slug}/{rp_slug_val}/">
                        <img src="{rp_img_str}" alt="{rp_title}" class="related-img">
                      </a>
                      <div class="related-info">
                        <h3 class="related-name">
                          <a href="/{category_slug}/{rp_slug_val}/">{rp_title}</a>
                        </h3>
                        <p class="related-price">{rp_price_str}</p>
                        <a href="{rp_amazon_url}" target="_blank" class="related-buy-btn">Buy on Amazon</a>
                      </div>
                    </div>
                    '''
                content = re.sub(r'<div class="related-grid" id="relatedGrid">.*?</div>', f'<div class="related-grid" id="relatedGrid">{related_html}</div>', content, flags=re.DOTALL)
            
            # 替换导航
            nav_html = self.generate_navigation_html()
            content = re.sub(r'<ul class="nav-list">.*?</ul>', f'<ul class="nav-list">{nav_html}</ul>', content, flags=re.DOTALL)
            
            # 更新所有链接为相对路径
            content = content.replace('href="index.html"', 'href="/"')
            content = content.replace('href="category.html?id=office-supplies"', f'href="/{category_slug}/"')
            content = content.replace('href="category.html?id=carrying-cases"', f'href="/{category_slug}/"')
            content = content.replace('href="category.html?id=clothing"', f'href="/{category_slug}/"')
            content = content.replace('href="category.html?id=shoes"', f'href="/{category_slug}/"')
            content = content.replace('href="category.html?id=accessories"', f'href="/{category_slug}/"')
            content = content.replace('href="about.html"', 'href="/About-Us/"')
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"产品页面生成成功: {output_path}")
    
    def generate_custom_pages(self):
        """生成自定义页面"""
        template_path = TEMPLATE_DIR / "custompage.html"
        
        for page in self.custom_pages:
            page_title = page.get("页面title", "")
            page_slug = page.get("页面slug", "")
            if not page_slug:
                continue
            
            # 创建页面目录
            page_dir = OUTPUT_DIR / page_slug
            page_dir.mkdir(exist_ok=True)
            
            # 复制模板
            output_path = page_dir / "index.html"
            shutil.copy2(template_path, output_path)
            
            # 读取并修改内容
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换品牌名
            content = content.replace("AKAYOK", self.brand_name)
            
            # 替换页面标题
            content = content.replace("About Us", page_title)
            
            # 替换导航
            nav_html = self.generate_navigation_html()
            content = re.sub(r'<ul class="nav-list">.*?</ul>', f'<ul class="nav-list">{nav_html}</ul>', content, flags=re.DOTALL)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"自定义页面生成成功: {output_path}")
    
    def generate_all(self):
        """生成所有页面"""
        print("开始生成网站...")
        
        # 1. 复制静态文件
        print("复制静态文件...")
        self.copy_static_files()
        
        # 2. 生成首页
        print("生成首页...")
        self.generate_homepage()
        
        # 3. 生成分类页面
        print("生成分类页面...")
        self.generate_category_pages()
        
        # 4. 生成产品页面
        print("生成产品页面...")
        self.generate_product_pages()
        
        # 5. 生成自定义页面
        print("生成自定义页面...")
        self.generate_custom_pages()
        
        # 6. 生成 robots.txt
        print("生成 robots.txt...")
        self.generate_robots_txt()
        
        # 7. 生成 sitemap.xml
        print("生成 sitemap.xml...")
        self.generate_sitemap_xml()
        
        print("\n网站生成完成！")
        print(f"输出目录: {OUTPUT_DIR}")


if __name__ == "__main__":
    # 测试用例（需要配合excel_reader使用）
    print("WebsiteGenerator 模块已准备好")
