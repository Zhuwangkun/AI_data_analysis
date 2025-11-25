import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager as fm
import numpy as np
from datetime import datetime

# 连接数据库
conn = sqlite3.connect('chinook.db')

# 查询数据
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

# 设置中文字体
font_path = "C:/Windows/Fonts/simhei.ttf"  # 黑体
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams["font.sans-serif"] = [font_prop.get_name()]
plt.rcParams["axes.unicode_minus"] = False

# 转换日期格式
df['EndDate'] = pd.to_datetime(df['EndDate'])

# 设置图表样式
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# 1. 利率指数时间序列趋势图
fig, axes = plt.subplots(3, 3, figsize=(20, 15))
fig.suptitle('人民币利率指数历史趋势分析 (1998-2025)', fontsize=16, fontproperties=font_prop)

indices = ['IndexDD', 'IndexTD3M', 'IndexTD6M', 'IndexTD1Y', 'IndexTD2Y', 'IndexTD3Y', 'IndexTD5Y', 'IndexND7D']
chinese_names = ['活期存款', '三个月定存', '半年定存', '一年定存', '二年定存', '三年定存', '五年定存', '七天通知存款']

for idx, (col, name) in enumerate(zip(indices, chinese_names)):
    row = idx // 3
    col_pos = idx % 3
    if row < 3 and col_pos < 3:
        axes[row, col_pos].plot(df['EndDate'], df[col], linewidth=1)
        axes[row, col_pos].set_title(f'{name}指数', fontproperties=font_prop)
        axes[row, col_pos].axhline(y=1000, color='r', linestyle='--', alpha=0.5)
        axes[row, col_pos].grid(True, alpha=0.3)

# 隐藏最后一个空子图
axes[2, 2].set_visible(False)

plt.tight_layout()
plt.savefig('output/QT_InterestRateIndex_20251120164944/rate_indices_trend.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. 各指数收益率分布对比图
fig, ax = plt.subplots(figsize=(15, 8))

returns_data = []
for col, name in zip(indices, chinese_names):
    returns_data.append(df[col] - 1000)

# 创建箱线图
box_data = [df[col] - 1000 for col in indices]
ax.boxplot(box_data, labels=chinese_names)
ax.set_title('各期限利率指数收益率分布对比', fontsize=14, fontproperties=font_prop)
ax.set_ylabel('收益率点数（相对于1000点基期）', fontproperties=font_prop)
ax.grid(True, alpha=0.3)
ax.axhline(y=0, color='r', linestyle='--', alpha=0.5)

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('output/QT_InterestRateIndex_20251120164944/returns_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. 指数相关性热力图
fig, ax = plt.subplots(figsize=(12, 10))

correlation_data = df[indices].corr()
sns.heatmap(correlation_data,
            annot=True,
            fmt='.3f',
            cmap='coolwarm',
            center=0,
            xticklabels=chinese_names,
            yticklabels=chinese_names,
            ax=ax)

ax.set_title('利率指数相关性矩阵', fontsize=14, fontproperties=font_prop)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig('output/QT_InterestRateIndex_20251120164944/correlation_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()

# 4. 收益率随时间变化的热力图
fig, ax = plt.subplots(figsize=(15, 8))

# 按年份计算平均收益率
yearly_data = df.copy()
yearly_data['Year'] = yearly_data['EndDate'].dt.year

yearly_returns = pd.DataFrame()
for col, name in zip(indices, chinese_names):
    yearly_returns[name] = yearly_data.groupby('Year')[col].mean() - 1000

# 创建热力图
sns.heatmap(yearly_returns.T,
            cmap='RdYlGn',
            center=0,
            annot=True,
            fmt='.1f',
            ax=ax)

ax.set_title('各期限利率指数年度平均收益率热力图', fontsize=14, fontproperties=font_prop)
ax.set_xlabel('年份', fontproperties=font_prop)
ax.set_ylabel('存款类型', fontproperties=font_prop)
plt.tight_layout()
plt.savefig('output/QT_InterestRateIndex_20251120164944/yearly_returns_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()

# 5. 长期趋势对比图（移动平均线）
fig, ax = plt.subplots(figsize=(16, 8))

# 计算250日移动平均线
window = 250
for col, name in zip(indices, chinese_names):
    moving_avg = df[col].rolling(window=window).mean()
    ax.plot(df['EndDate'], moving_avg, label=name, linewidth=2)

ax.set_title(f'人民币利率指数{window}日移动平均线对比', fontsize=14, fontproperties=font_prop)
ax.set_xlabel('时间', fontproperties=font_prop)
ax.set_ylabel('指数值', fontproperties=font_prop)
ax.legend(prop=font_prop)
ax.grid(True, alpha=0.3)
ax.axhline(y=1000, color='k', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('output/QT_InterestRateIndex_20251120164944/moving_average_trend.png', dpi=300, bbox_inches='tight')
plt.close()

# 6. 统计摘要图表
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('利率指数统计特征分析', fontsize=16, fontproperties=font_prop)

# 各指数描述性统计
stats_data = []
for col, name in zip(indices, chinese_names):
    stats = {
        '存款类型': name,
        '最小值': df[col].min(),
        '最大值': df[col].max(),
        '均值': df[col].mean(),
        '标准差': df[col].std(),
        '波动幅度': df[col].max() - df[col].min()
    }
    stats_data.append(stats)

stats_df = pd.DataFrame(stats_data)

# 波动幅度对比
axes[0, 0].bar(stats_df['存款类型'], stats_df['波动幅度'])
axes[0, 0].set_title('各指数波动幅度对比', fontproperties=font_prop)
axes[0, 0].set_ylabel('波动幅度（点）', fontproperties=font_prop)
plt.setp(axes[0, 0].get_xticklabels(), rotation=45, ha='right')

# 均值对比
axes[0, 1].bar(stats_df['存款类型'], stats_df['均值'])
axes[0, 1].axhline(y=1000, color='r', linestyle='--', alpha=0.5)
axes[0, 1].set_title('各指数均值对比', fontproperties=font_prop)
axes[0, 1].set_ylabel('均值', fontproperties=font_prop)
plt.setp(axes[0, 1].get_xticklabels(), rotation=45, ha='right')

# 标准差对比
axes[1, 0].bar(stats_df['存款类型'], stats_df['标准差'])
axes[1, 0].set_title('各指数波动率（标准差）对比', fontproperties=font_prop)
axes[1, 0].set_ylabel('标准差', fontproperties=font_prop)
plt.setp(axes[1, 0].get_xticklabels(), rotation=45, ha='right')

# 收益率时间序列
axes[1, 1].plot(df['EndDate'], df['IndexTD5Y'] - 1000, label='五年定存', alpha=0.7)
axes[1, 1].plot(df['EndDate'], df['IndexDD'] - 1000, label='活期存款', alpha=0.7)
axes[1, 1].set_title('五年定存 vs 活期存款收益率对比', fontproperties=font_prop)
axes[1, 1].set_ylabel('收益率点数', fontproperties=font_prop)
axes[1, 1].legend(prop=font_prop)
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('output/QT_InterestRateIndex_20251120164944/statistical_summary.png', dpi=300, bbox_inches='tight')
plt.close()

# 关闭数据库连接
conn.close()

print("所有图表已生成完成！")
print(f"图表保存在: output/QT_InterestRateIndex_20251120164944/")
print("生成的图表包括：")
print("1. rate_indices_trend.png - 利率指数历史趋势")
print("2. returns_distribution.png - 收益率分布对比")
print("3. correlation_heatmap.png - 相关性矩阵")
print("4. yearly_returns_heatmap.png - 年度收益率热力图")
print("5. moving_average_trend.png - 移动平均线趋势")
print("6. statistical_summary.png - 统计特征分析")