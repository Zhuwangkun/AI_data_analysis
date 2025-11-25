import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from datetime import datetime

# 设置中文字体
import matplotlib
font_name = matplotlib.rcParams['font.sans-serif'][0] if matplotlib.rcParams['font.sans-serif'] else 'DejaVu Sans'
font_prop = fm.FontProperties(family=font_name)

plt.rcParams["font.sans-serif"] = [font_name]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["svg.fonttype"] = "none"

# 连接数据库
conn = sqlite3.connect('../../db/jy.db')

# 1. 读取数据
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

# 2. 时间序列趋势图
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Interest Rate Index Time Series Trends', fontsize=16)

# 活期存款指数
axes[0,0].plot(df['EndDate'], df['IndexDD'], linewidth=1, color='blue')
axes[0,0].set_title('Demand Deposit Index')
axes[0,0].set_xlabel('Date')
axes[0,0].set_ylabel('Index Value')
axes[0,0].grid(True, alpha=0.3)

# 3-month time deposit index
axes[0,1].plot(df['EndDate'], df['IndexTD3M'], linewidth=1, color='green')
axes[0,1].set_title('3-Month Time Deposit Index')
axes[0,1].set_xlabel('Date')
axes[0,1].set_ylabel('Index Value')
axes[0,1].grid(True, alpha=0.3)

# 1-year time deposit index
axes[1,0].plot(df['EndDate'], df['IndexTD1Y'], linewidth=1, color='red')
axes[1,0].set_title('1-Year Time Deposit Index')
axes[1,0].set_xlabel('Date')
axes[1,0].set_ylabel('Index Value')
axes[1,0].grid(True, alpha=0.3)

# 5-year time deposit index
axes[1,1].plot(df['EndDate'], df['IndexTD5Y'], linewidth=1, color='purple')
axes[1,1].set_title('5-Year Time Deposit Index')
axes[1,1].set_xlabel('Date')
axes[1,1].set_ylabel('Index Value')
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('output/QT_InterestRateIndex_20251120144944/time_series_trend.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. 所有利率指数对比图
fig, ax = plt.subplots(figsize=(14, 8))
indices = ['IndexDD', 'IndexTD3M', 'IndexTD6M', 'IndexTD1Y', 'IndexTD2Y', 'IndexTD3Y', 'IndexTD5Y', 'IndexND7D']
colors = ['blue', 'green', 'orange', 'red', 'purple', 'brown', 'pink', 'gray']
labels = ['Demand', '3M', '6M', '1Y', '2Y', '3Y', '5Y', '7D Notice']

for idx, color, label in zip(indices, colors, labels):
    ax.plot(df['EndDate'], df[idx], label=label, linewidth=1, color=color)

ax.set_title('All Interest Rate Indices Comparison', fontsize=14)
ax.set_xlabel('Date')
ax.set_ylabel('Index Value')
ax.legend()
ax.grid(True, alpha=0.3)

plt.savefig('output/QT_InterestRateIndex_20251120144944/all_indices_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# 4. 指数分布箱线图
fig, ax = plt.subplots(figsize=(12, 6))
index_data = [df['IndexDD'], df['IndexTD3M'], df['IndexTD6M'], df['IndexTD1Y'],
              df['IndexTD2Y'], df['IndexTD3Y'], df['IndexTD5Y'], df['IndexND7D']]
labels = ['Demand', '3M', '6M', '1Y', '2Y', '3Y', '5Y', '7D Notice']

box_plot = ax.boxplot(index_data, labels=labels, patch_artist=True)
colors = plt.cm.Set3(range(len(labels)))
for patch, color in zip(box_plot['boxes'], colors):
    patch.set_facecolor(color)

ax.set_title('Interest Rate Indices Distribution', fontsize=14)
ax.set_xlabel('Deposit Type')
ax.set_ylabel('Index Value')
ax.grid(True, alpha=0.3)

plt.savefig('output/QT_InterestRateIndex_20251120144944/distribution_boxplot.png', dpi=300, bbox_inches='tight')
plt.close()

# 5. 相关性热力图
fig, ax = plt.subplots(figsize=(10, 8))
correlation_matrix = df[indices].corr()
sns.heatmap(correlation_matrix, annot=True, fmt='.3f', cmap='coolwarm', center=0, ax=ax,
            xticklabels=labels, yticklabels=labels)
ax.set_title('Interest Rate Indices Correlation Heatmap', fontsize=14)
plt.savefig('output/QT_InterestRateIndex_20251120144944/correlation_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()

# 6. 年度均值趋势图
annual_means = df.groupby(df['EndDate'].dt.year)[indices].mean()

fig, ax = plt.subplots(figsize=(14, 8))
for idx, color, label in zip(indices, colors, labels):
    ax.plot(annual_means.index, annual_means[idx], marker='o', label=label, linewidth=2)

ax.set_title('Annual Mean Trends of Interest Rate Indices', fontsize=14)
ax.set_xlabel('Year')
ax.set_ylabel('Annual Mean Index Value')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xticks(range(1998, 2026, 2))

plt.savefig('output/QT_InterestRateIndex_20251120144944/annual_means_trend.png', dpi=300, bbox_inches='tight')
plt.close()

print("图表生成完成！")
conn.close()