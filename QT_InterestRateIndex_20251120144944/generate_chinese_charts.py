import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np
from datetime import datetime

# 设置中文字体
font_path = "../../font/MiSans-Regular.ttf"
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams["font.sans-serif"] = [font_prop.get_name()]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 12

# 连接数据库
conn = sqlite3.connect('D:/AgentWork/Sqlite/work001/db/jy.db')

# 读取数据
df = pd.read_sql_query("""
    SELECT
        EndDate,
        IndexDD,
        IndexTD3M,
        IndexTD6M,
        IndexTD1Y,
        IndexTD2Y,
        IndexTD3Y,
        IndexTD5Y,
        IndexND7D
    FROM QT_InterestRateIndex
    ORDER BY EndDate
""", conn)

df['EndDate'] = pd.to_datetime(df['EndDate'])
df['Year'] = df['EndDate'].dt.year

# 中文标签
titles = {
    'IndexDD': '活期存款指数',
    'IndexTD3M': '三个月定存指数',
    'IndexTD6M': '半年定存指数',
    'IndexTD1Y': '一年定存指数',
    'IndexTD2Y': '二年定存指数',
    'IndexTD3Y': '三年定存指数',
    'IndexTD5Y': '五年定存指数',
    'IndexND7D': '七天通知存款指数'
}

terms = ['IndexDD', 'IndexTD3M', 'IndexTD6M', 'IndexTD1Y', 'IndexTD2Y', 'IndexTD3Y', 'IndexTD5Y', 'IndexND7D']
labels = ['活期存款', '三个月', '半年', '一年', '二年', '三年', '五年', '七天通知']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']

print("开始生成中文图表...")

# 1. 主要指数趋势图（短期vs长期）
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 12))

# 短期vs长期对比
ax1.plot(df['EndDate'], df['IndexDD'], linewidth=2, color=colors[0], label='活期存款')
ax1.plot(df['EndDate'], df['IndexTD1Y'], linewidth=2, color=colors[3], label='一年定存')
ax1.plot(df['EndDate'], df['IndexTD5Y'], linewidth=2, color=colors[6], label='五年定存')
ax1.set_title('利率指数时间序列趋势图 (1998-2025)', fontproperties=font_prop, fontsize=16, fontweight='bold')
ax1.set_xlabel('时间', fontproperties=font_prop, fontsize=14)
ax1.set_ylabel('指数值（基点=1000）', fontproperties=font_prop, fontsize=14)
ax1.legend(prop=font_prop)
ax1.grid(True, alpha=0.3)

# 所有期限对比
for idx, label, color in zip(terms, labels, colors):
    ax2.plot(df['EndDate'], df[idx], label=label, linewidth=1, color=color)

ax2.set_title('所有期限利率指数对比', fontproperties=font_prop, fontsize=16, fontweight='bold')
ax2.set_xlabel('时间', fontproperties=font_prop, fontsize=14)
ax2.set_ylabel('指数值（基点=1000）', fontproperties=font_prop, fontsize=14)
ax2.legend(prop=font_prop, ncol=4)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('chinese_trends.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ 主要趋势图已生成")

# 2. 年度均值趋势图
annual_means = df.groupby('Year')[terms].mean()

fig, ax = plt.subplots(figsize=(16, 10))
for idx, label, color in zip(terms, labels, colors):
    ax.plot(annual_means.index, annual_means[idx],
            marker='o', markersize=6, label=label, linewidth=2, color=color)

ax.set_title('年度平均利率指数趋势图', fontproperties=font_prop, fontsize=16, fontweight='bold')
ax.set_xlabel('年份', fontproperties=font_prop, fontsize=14)
ax.set_ylabel('年度平均指数值', fontproperties=font_prop, fontsize=14)
ax.legend(prop=font_prop)
ax.grid(True, alpha=0.3)
ax.set_xticks(range(1998, 2026, 2))

plt.tight_layout()
plt.savefig('output/QT_InterestRateIndex_20251120144944/chinese_annual_averages.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ 年度均值图已生成")

# 3. 分布箱线图
fig, ax = plt.subplots(figsize=(14, 8))
data_to_plot = [df[col].dropna() for col in terms]

box_plot = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
for patch, color in zip(box_plot['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.8)
    patch.set_edgecolor('black')
    patch.set_linewidth(1)

ax.set_title('各期限利率指数分布箱线图', fontproperties=font_prop, fontsize=16, fontweight='bold')
ax.set_xlabel('存款期限', fontproperties=font_prop, fontsize=14)
ax.set_ylabel('指数值', fontproperties=font_prop, fontsize=14)
ax.grid(True, alpha=0.3)

# 添加统计值
for i, (col, label) in enumerate(zip(terms, labels)):
    median = df[col].median()
    ax.text(i+1, median, f'{median:.0f}',
            ha='center', va='bottom', fontproperties=font_prop,
            fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('output/QT_InterestRateIndex_20251120144944/chinese_distribution_boxplot.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ 分布箱线图已生成")

# 4. 相关性热力图
correlation_data = df[terms].corr()

fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(correlation_data, annot=True, fmt='.3f', cmap='RdYlBu_r',
            center=0.9, square=True, linewidths=0.5,
            xticklabels=labels, yticklabels=labels, ax=ax)

ax.set_title('利率指数相关性热力图', fontproperties=font_prop, fontsize=16, fontweight='bold')
ax.set_xlabel('存款期限', fontproperties=font_prop, fontsize=14)
ax.set_ylabel('存款期限', fontproperties=font_prop, fontsize=14)

plt.tight_layout()
plt.savefig('output/QT_InterestRateIndex_20251120144944/chinese_correlation_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ 相关性热力图已生成")

# 5. 期限结构演化图
key_dates = ['2000-12-31', '2008-12-31', '2014-12-31', '2020-12-31', '2025-11-20']
key_data = []

for date_str in key_dates:
    row = df[df['EndDate'] <= date_str].iloc[-1]
    key_data.append({
        '年份': date_str[:4],
        '活期': row['IndexDD'],
        '三个月': row['IndexTD3M'],
        '半年': row['IndexTD6M'],
        '一年': row['IndexTD1Y'],
        '二年': row['IndexTD2Y'],
        '三年': row['IndexTD3Y'],
        '五年': row['IndexTD5Y']
    })

term_structure = pd.DataFrame(key_data)
terms_chinese = ['活期', '三个月', '半年', '一年', '二年', '三年', '五年']

fig, ax = plt.subplots(figsize=(14, 9))
plot_colors = ['#2E8B57', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']

for i, (date, color) in enumerate(zip(key_dates, plot_colors)):
    year = date[:4]
    ax.plot(terms_chinese, term_structure.iloc[i][terms_chinese],
            marker='o', markersize=8, label=f'{year}年',
            linewidth=3, color=color)

ax.set_title('利率期限结构演化图', fontproperties=font_prop, fontsize=16, fontweight='bold')
ax.set_xlabel('存款期限', fontproperties=font_prop, fontsize=14)
ax.set_ylabel('指数值', fontproperties=font_prop, fontsize=14)
ax.legend(prop=font_prop)
ax.grid(True, alpha=0.3)
ax.set_xticklabels(terms_chinese, fontproperties=font_prop)

plt.tight_layout()
plt.savefig('output/QT_InterestRateIndex_20251120144944/chinese_term_structure_evolution.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ 期限结构演化图已生成")

# 6. 数据质量可视化
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

# 缺失值分析
missing_counts = [df[col].isna().sum() for col in terms]
missing_labels = ['活期', '三个月', '半年', '一年', '二年', '三年', '五年']
colors_missing = colors[:7]

bars = ax1.bar(missing_labels, missing_counts, color=colors_missing, alpha=0.8)
ax1.set_title('各期限指数缺失值统计', fontproperties=font_prop, fontsize=14, fontweight='bold')
ax1.set_ylabel('缺失值数量', fontproperties=font_prop, fontsize=12)
ax1.tick_params(axis='x', rotation=45)

# 添加数值标签
for bar, count in zip(bars, missing_counts):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
             f'{count}', ha='center', va='bottom', fontproperties=font_prop)

# 月度数据完整性
monthly_counts = df.groupby(['Year', 'Month']).size().reset_index(name='count')
monthly_counts['Date'] = pd.to_datetime(monthly_counts[['Year', 'Month']].assign(day=1))

ax2.plot(monthly_counts['Date'], monthly_counts['count'], linewidth=2, color='blue')
ax2.set_title('月度数据完整性检查', fontproperties=font_prop, fontsize=14, fontweight='bold')
ax2.set_xlabel('时间', fontproperties=font_prop, fontsize=12)
ax2.set_ylabel('月度记录数', fontproperties=font_prop, fontsize=12)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('output/QT_InterestRateIndex_20251120144944/chinese_data_quality.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ 数据质量可视化图已生成")

conn.close()
print("🎉 所有中文图表生成完成！")

# 生成图表统计信息
print("\n=== 图表生成统计 ===")
print("1. 主要趋势图: chinese_trends.png")
print("2. 年度均值图: chinese_annual_averages.png")
print("3. 分布箱线图: chinese_distribution_boxplot.png")
print("4. 相关性热力图: chinese_correlation_heatmap.png")
print("5. 期限结构演化: chinese_term_structure_evolution.png")
print("6. 数据质量图: chinese_data_quality.png")