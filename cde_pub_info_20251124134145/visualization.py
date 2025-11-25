import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from datetime import datetime
import os

# 设置中文字体
font_path = "C:/Windows/Fonts/simhei.ttf"
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams["font.sans-serif"] = [font_prop.get_name()]
    plt.rcParams["axes.unicode_minus"] = False

# 连接数据库
conn = sqlite3.connect('../../db/jy.db')

# 1. 药品类型分布图
df_drug_type = pd.read_sql("""
SELECT drug_typ, COUNT(*) as count
FROM cde_pub_info
WHERE drug_typ IS NOT NULL
GROUP BY drug_typ
ORDER BY count DESC
LIMIT 10
""", conn)

plt.figure(figsize=(12, 8))
plt.bar(range(len(df_drug_type)), df_drug_type['count'])
plt.xticks(range(len(df_drug_type)), df_drug_type['drug_typ'], rotation=45, ha='right')
plt.title('药品类型分布（前10类）', fontsize=16, fontproperties=font_prop)
plt.xlabel('药品类型', fontproperties=font_prop, fontsize=12)
plt.ylabel('记录数', fontproperties=font_prop, fontsize=12)
plt.tight_layout()
plt.savefig('cde_drug_type_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. 注册分类分布图
df_register_kind = pd.read_sql("""
SELECT register_kind, COUNT(*) as count
FROM cde_pub_info
WHERE register_kind IS NOT NULL
GROUP BY register_kind
ORDER BY count DESC
LIMIT 15
""", conn)

plt.figure(figsize=(12, 8))
plt.bar(range(len(df_register_kind)), df_register_kind['count'])
plt.xticks(range(len(df_register_kind)), df_register_kind['register_kind'], rotation=45, ha='right')
plt.title('注册分类分布（前15类）', fontsize=16, fontproperties=font_prop)
plt.xlabel('注册分类', fontproperties=font_prop, fontsize=12)
plt.ylabel('记录数', fontproperties=font_prop, fontsize=12)
plt.tight_layout()
plt.savefig('cde_register_kind_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. 数据来源分布图
df_source = pd.read_sql("""
SELECT source_type, COUNT(*) as count
FROM cde_pub_info
GROUP BY source_type
ORDER BY count DESC
""", conn)

plt.figure(figsize=(12, 8))
plt.pie(df_source['count'], labels=df_source['source_type'], autopct='%1.1f%%')
plt.title('数据来源分布', fontsize=16, fontproperties=font_prop)
plt.tight_layout()
plt.savefig('cde_source_type_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 4. 审批结果分布图
df_result = pd.read_sql("""
SELECT review_approval_resu, COUNT(*) as count
FROM cde_pub_info
WHERE review_approval_resu IS NOT NULL
GROUP BY review_approval_resu
""", conn)

plt.figure(figsize=(10, 6))
plt.bar(df_result['review_approval_resu'], df_result['count'])
plt.title('审评审批结果分布', fontsize=16, fontproperties=font_prop)
plt.xlabel('审批结果', fontproperties=font_prop, fontsize=12)
plt.ylabel('记录数', fontproperties=font_prop, fontsize=12)
plt.tight_layout()
plt.savefig('cde_approval_result_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 5. 时间序列分析 - 按年份统计审批数量
df_year = pd.read_sql("""
SELECT
    strftime('%Y', approval_date) as year,
    COUNT(*) as count
FROM cde_pub_info
WHERE approval_date IS NOT NULL
    AND approval_date >= '2010-01-01'
GROUP BY strftime('%Y', approval_date)
ORDER BY year
""", conn)

plt.figure(figsize=(14, 8))
plt.plot(df_year['year'], df_year['count'], marker='o', linewidth=2)
plt.title('2010-2025年药品批准数量趋势', fontsize=16, fontproperties=font_prop)
plt.xlabel('年份', fontproperties=font_prop, fontsize=12)
plt.ylabel('批准数量', fontproperties=font_prop, fontsize=12)
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('cde_approval_trend_by_year.png', dpi=300, bbox_inches='tight')
plt.close()

# 6. 字段完整性热力图
df_completeness = pd.read_sql("""
SELECT
    'accept_id' as field_name,
    ROUND(COUNT(accept_id) * 100.0 / COUNT(*), 2) as completeness_pct
FROM cde_pub_info
UNION ALL
SELECT
    'drug_name',
    ROUND(COUNT(drug_name) * 100.0 / COUNT(*), 2)
FROM cde_pub_info
UNION ALL
SELECT
    'company_name',
    ROUND(COUNT(company_name) * 100.0 / COUNT(*), 2)
FROM cde_pub_info
UNION ALL
SELECT
    'drug_typ',
    ROUND(COUNT(drug_typ) * 100.0 / COUNT(*), 2)
FROM cde_pub_info
UNION ALL
SELECT
    'register_kind',
    ROUND(COUNT(register_kind) * 100.0 / COUNT(*), 2)
FROM cde_pub_info
UNION ALL
SELECT
    'approval_date',
    ROUND(COUNT(approval_date) * 100.0 / COUNT(*), 2)
FROM cde_pub_info
UNION ALL
SELECT
    'apply_date',
    ROUND(COUNT(apply_date) * 100.0 / COUNT(*), 2)
FROM cde_pub_info
UNION ALL
SELECT
    'undertake_date',
    ROUND(COUNT(undertake_date) * 100.0 / COUNT(*), 2)
FROM cde_pub_info
""", conn)

plt.figure(figsize=(12, 8))
plt.barh(df_completeness['field_name'], df_completeness['completeness_pct'])
plt.title('关键审批字段完整性分析', fontsize=16, fontproperties=font_prop)
plt.xlabel('完整度 (%)', fontproperties=font_prop, fontsize=12)
plt.ylabel('字段名称', fontproperties=font_prop, fontsize=12)
plt.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('cde_field_completeness.png', dpi=300, bbox_inches='tight')
plt.close()

# 关闭数据库连接
conn.close()

print("所有图表已生成完成！")