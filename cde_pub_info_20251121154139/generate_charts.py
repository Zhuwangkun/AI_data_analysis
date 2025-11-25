import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager as fm
import os
from datetime import datetime

# Set up Chinese font support
font_path = "./font/MiSans-Regular.ttf"
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)
font_name = font_prop.get_name()

plt.rcParams["font.sans-serif"] = [font_name]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["svg.fonttype"] = "none"

# Connect to database
conn = sqlite3.connect('./db/jy.db')

# Create output directory
output_dir = f"./output/cde_pub_info_{datetime.now().strftime('%Y%m%d%H%M%S')}"
os.makedirs(output_dir, exist_ok=True)

print(f"Output directory: {output_dir}")

# 1. Source Type Distribution Chart
print("Generating source type distribution chart...")
df_source = pd.read_sql("""
    SELECT source_type, COUNT(*) as count
    FROM cde_pub_info
    GROUP BY source_type
    ORDER BY count DESC
    LIMIT 10
""", conn)

plt.figure(figsize=(12, 8))
plt.barh(df_source['source_type'], df_source['count'])
plt.title('数据来源类型分布', fontproperties=font_prop, fontsize=14)
plt.xlabel('记录数量', fontproperties=font_prop)
plt.ylabel('数据来源类型', fontproperties=font_prop)
plt.tight_layout()
plt.savefig(f"{output_dir}/cde_pub_info_source_type_distribution.png", dpi=300, bbox_inches='tight')
plt.close()

# 2. Classification Distribution Chart
print("Generating classification distribution chart...")
df_classify = pd.read_sql("""
    SELECT classify, COUNT(*) as count
    FROM cde_pub_info
    GROUP BY classify
    ORDER BY count DESC
    LIMIT 10
""", conn)

plt.figure(figsize=(12, 8))
plt.barh(df_classify['classify'], df_classify['count'])
plt.title('分类情况分布', fontproperties=font_prop, fontsize=14)
plt.xlabel('记录数量', fontproperties=font_prop)
plt.ylabel('分类', fontproperties=font_prop)
plt.tight_layout()
plt.savefig(f"{output_dir}/cde_pub_info_classify_distribution.png", dpi=300, bbox_inches='tight')
plt.close()

# 3. Apply Type Distribution Chart
print("Generating apply type distribution chart...")
df_apply_type = pd.read_sql("""
    SELECT apply_type, COUNT(*) as count
    FROM cde_pub_info
    WHERE apply_type IS NOT NULL
    GROUP BY apply_type
    ORDER BY count DESC
    LIMIT 10
""", conn)

plt.figure(figsize=(10, 6))
plt.bar(df_apply_type['apply_type'], df_apply_type['count'])
plt.title('申请类型分布', fontproperties=font_prop, fontsize=14)
plt.xlabel('申请类型', fontproperties=font_prop)
plt.ylabel('记录数量', fontproperties=font_prop)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(f"{output_dir}/cde_pub_info_apply_type_distribution.png", dpi=300, bbox_inches='tight')
plt.close()

# 4. Missing Values Chart
print("Generating missing values chart...")
missing_data = [
    ('source_type', 0.0), ('source_desc', 0.0), ('classify', 0.0), ('code_id', 0.0),
    ('accept_id', 0.31), ('drug_name', 9.3), ('drug_typ', 30.22), ('register_kind', 55.75),
    ('company_name', 3.66), ('pub_date', 99.06), ('adapt_symptom', 94.79), ('problem_info', 99.91),
    ('answer_info', 99.91), ('apply_date', 99.54), ('end_date', 99.51), ('rare_disease_drug', 99.94),
    ('reason_info', 99.54), ('specs_info', 91.76), ('undertake_date', 23.92), ('status_info', 96.09),
    ('year_info', 28.25), ('apply_type', 34.9), ('review_type', 96.49), ('pub_type', 96.51),
    ('entry_time', 96.54), ('drug_name_en', 97.17), ('approval_num', 97.17), ('approval_date', 97.14),
    ('business_address', 83.79)
]

df_missing = pd.DataFrame(missing_data, columns=['field', 'missing_rate'])
df_missing = df_missing.sort_values('missing_rate', ascending=True)

plt.figure(figsize=(12, 10))
plt.barh(df_missing['field'], df_missing['missing_rate'])
plt.title('字段缺失率分析', fontproperties=font_prop, fontsize=14)
plt.xlabel('缺失率 (%)', fontproperties=font_prop)
plt.ylabel('字段名称', fontproperties=font_prop)
plt.axvline(x=50, color='red', linestyle='--', alpha=0.7, label='50%阈值')
plt.legend(prop=font_prop)
plt.tight_layout()
plt.savefig(f"{output_dir}/cde_pub_info_missing_values.png", dpi=300, bbox_inches='tight')
plt.close()

# 5. Publication Date Trend
print("Generating publication date trend chart...")
df_pub_date = pd.read_sql("""
    SELECT strftime('%Y', pub_date) as year, COUNT(*) as count
    FROM cde_pub_info
    WHERE pub_date IS NOT NULL
    GROUP BY year
    ORDER BY year
""", conn)

plt.figure(figsize=(12, 6))
plt.plot(df_pub_date['year'], df_pub_date['count'], marker='o')
plt.title('发布日期年度趋势', fontproperties=font_prop, fontsize=14)
plt.xlabel('年份', fontproperties=font_prop)
plt.ylabel('记录数量', fontproperties=font_prop)
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f"{output_dir}/cde_pub_info_pub_date_trend.png", dpi=300, bbox_inches='tight')
plt.close()

# 6. Rare Disease Drug Distribution
print("Generating rare disease drug distribution chart...")
df_rare = pd.read_sql("""
    SELECT
        CASE
            WHEN rare_disease_drug = 1 THEN '罕见病药物'
            WHEN rare_disease_drug = 0 THEN '非罕见病药物'
            ELSE '未知'
        END as drug_type,
        COUNT(*) as count
    FROM cde_pub_info
    WHERE rare_disease_drug IS NOT NULL
    GROUP BY rare_disease_drug
""", conn)

plt.figure(figsize=(8, 6))
plt.pie(df_rare['count'], labels=df_rare['drug_type'], autopct='%1.1f%%', startangle=90)
plt.title('罕见病药物分布', fontproperties=font_prop, fontsize=14)
plt.axis('equal')
plt.tight_layout()
plt.savefig(f"{output_dir}/cde_pub_info_rare_disease_distribution.png", dpi=300, bbox_inches='tight')
plt.close()

print(f"All charts have been generated in: {output_dir}")
conn.close()