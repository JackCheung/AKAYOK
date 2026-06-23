import pandas as pd
import openpyxl

# 读取 Excel 文件
excel_path = r'd:\project\0718网站\网站管理.xlsx'

# 获取所有 sheet 名称
xl = pd.ExcelFile(excel_path)
print("Sheet 名称：")
for sheet_name in xl.sheet_names:
    print(f"  - {sheet_name}")

print("\n" + "="*80 + "\n")

# 遍历每个 sheet，查看其结构和前几行数据
for sheet_name in xl.sheet_names:
    print(f"Sheet: {sheet_name}")
    print("-"*80)
    
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        print(f"行数: {len(df)}, 列数: {len(df.columns)}")
        print(f"\n列名:")
        for col in df.columns:
            print(f"  - {col}")
        
        print(f"\n前 3 行数据:")
        print(df.head(3).to_string())
        
    except Exception as e:
        print(f"读取失败: {e}")
    
    print("\n" + "="*80 + "\n")
