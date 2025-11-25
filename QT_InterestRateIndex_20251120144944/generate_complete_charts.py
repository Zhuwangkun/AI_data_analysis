import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 设置matplotlib参数
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10
plt.style.use('seaborn-v0_8')

# 连接数据库
conn = sqlite3.connect('db/jy.db')

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
df['Month'] = df['EndDate'].dt.month

# 1. 主要指数时间序列图
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))

# 短期vs长期对比
ax1.plot(df['EndDate'], df['IndexDD'], label='Demand Deposit', linewidth=1.5, color='blue')
ax1.plot(df['EndDate'], df['IndexTD1Y'], label='1-Year Fixed', linewidth=1.5, color='red')
ax1.plot(df['EndDate'], df['IndexTD5Y'], label='5-Year Fixed', linewidth=1.5, color='green')
ax1.set_title('Interest Rate Index Trends (1998-2025)', fontsize=14, fontweight='bold')
ax1.set_xlabel('Time Period')
ax1.set_ylabel('Index Value (Base=1000)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 所有期限对比
terms = ['IndexDD', 'IndexTD3M', 'IndexTD6M', 'IndexTD1Y', 'IndexTD2Y', 'IndexTD3Y', 'IndexTD5Y']
labels = ['Demand', '3M', '6M', '1Y', '2Y', '3Y', '5Y']
colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink']

for idx, label, color in zip(terms, labels, colors):
    ax2.plot(df['EndDate'], df[idx], label=label, linewidth=1, color=color)

ax2.set_title('All Deposit Terms Comparison', fontsize=14, fontweight='bold')
ax2.set_xlabel('Time Period')
ax2.set_ylabel('Index Value (Base=1000)')
ax2.legend(ncol=3)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('output/QT_InterestRateIndex_20251120144944/interest_rate_trends.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. 年度均值趋势图
annual_means = df.groupby('Year')[terms].mean()

fig, ax = plt.subplots(figsize=(14, 8))
for idx, label, color in zip(terms, labels, colors):
    ax.plot(annual_means.index, annual_means[idx], marker='o', label=label, linewidth=2, markersize=4)

ax.set_title('Annual Average Interest Rate Indices', fontsize=14, fontweight='bold')
ax.set_xlabel('Year')
ax.set_ylabel('Annual Average Index Value')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xticks(range(1998, 2026, 2))

plt.tight_layout()
plt.savefig('output/QT_InterestRateIndex_20251120144944/annual_averages.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. 指数分布箱线图
fig, ax = plt.subplots(figsize=(12, 6))
data_to_plot = [df[col].dropna() for col in terms]

box_plot = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
for patch, color in zip(box_plot['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax.set_title('Distribution of Interest Rate Indices by Term', fontsize=14, fontweight='bold')
ax.set_xlabel('Deposit Term')
ax.set_ylabel('Index Value')
ax.grid(True, alpha=0.3)

# 添加统计值标签
for i, (col, label) in enumerate(zip(terms, labels)):
    median = df[col].median()
    ax.text(i+1, median, f'{median:.0f}', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('output/QT_InterestRateIndex_20251120144944/distribution_boxplot.png', dpi=300, bbox_inches='tight')
plt.close()

# 4. 相关性热力图
correlation_data = df[terms].corr()

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(correlation_data, annot=True, fmt='.3f', cmap='RdYlBu_r', center=0.8,
            xticklabels=labels, yticklabels=labels, ax=ax)
ax.set_title('Correlation Matrix of Interest Rate Indices', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('output/QT_InterestRateIndex_20251120144944/correlation_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()

# 5. 利率期限结构变化图
# 选择几个关键时间点进行分析
key_dates = ['2000-12-31', '2008-12-31', '2014-12-31', '2020-12-31', '2025-11-20']
key_data = []

for date_str in key_dates:
    row = df[df['EndDate'] <= date_str].iloc[-1]
    key_data.append({
        'Date': date_str[:4],
        'Demand': row['IndexDD'],
        '3M': row['IndexTD3M'],
        '6M': row['IndexTD6M'],
        '1Y': row['IndexTD1Y'],
        '2Y': row['IndexTD2Y'],
        '3Y': row['IndexTD3Y'],
        '5Y': row['IndexTD5Y']
    })

term_structure = pd.DataFrame(key_data)
terms_short = ['Demand', '3M', '6M', '1Y', '2Y', '3Y', '5Y']

fig, ax = plt.subplots(figsize=(12, 8))
for i, (date, color) in enumerate(zip(key_dates, ['blue', 'green', 'red', 'orange', 'purple'])):
    year = date[:4]
    ax.plot(terms_short, term_structure.iloc[i][terms_short],
            marker='o', label=year, linewidth=2, markersize=6)

ax.set_title('Term Structure Evolution of Interest Rates', fontsize=14, fontweight='bold')
ax.set_xlabel('Deposit Term')
ax.set_ylabel('Index Value')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xticklabels(terms_short, rotation=45)

plt.tight_layout()
plt.savefig('output/QT_InterestRateIndex_20251120144944/term_structure_evolution.png', dpi=300, bbox_inches='tight')
plt.close()

# 6. 缺失值分析图
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# 缺失值分布
missing_counts = [df[col].isna().sum() for col in terms + ['IndexND7D']]
missing_labels = labels + ['7D Notice']
colors_missing = colors + ['gray']

ax1.bar(missing_labels, missing_counts, color=colors_missing)
ax1.set_title('Missing Values by Deposit Term')
ax1.set_ylabel('Count of Missing Values')
ax1.tick_params(axis='x', rotation=45)

# 数据完整性时间线
completeness = pd.DataFrame({
    'Date': df['EndDate'],
    'Completeness': (~df[['IndexDD', 'IndexTD1Y', 'IndexTD5Y', 'IndexND7D']].isna().any(axis=1)).astype(int)
})

ax2.plot(completeness['Date'], completeness['Completeness'], linewidth=1, color='blue')
ax2.set_title('Data Completeness Over Time')
ax2.set_xlabel('Date')
ax2.set_ylabel('Complete Records (1=Complete, 0=Incomplete)')
ax2.set_ylim(-0.1, 1.1)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('output/QT_InterestRateIndex_20251120144944/data_quality_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

print("所有图表生成完成！")
print("生成的图表包括：")
print("1. interest_rate_trends.png - 利率指数趋势图")
print("2. annual_averages.png - 年度均值趋势图")
print("3. distribution_boxplot.png - 分布箱线图")
print("4. correlation_heatmap.png - 相关性热力图")
print("5. term_structure_evolution.png - 期限结构演化图")
print("6. data_quality_analysis.png - 数据质量分析图")

conn.close()