#!/usr/bin/env PYTHONPATH=/tmp/fpdf2test /usr/local/bin/python3
import sys
from fpdf import FPDF

# 读取HTML内容
with open('/Users/wangkaipeng/.openclaw/workspace/ai-news/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 简单解析 - 提取标题和内容
pdf = FPDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

# 标题
pdf.set_font('Arial', 'B', 16)
pdf.cell(0, 10, 'AI行业资讯 2026年3月19日', ln=True, align='C')
pdf.ln(5)

# 提取今日热点
import re

# 提取新闻标题和内容
def extract_text(html):
    texts = []
    # 提取标题
    titles = re.findall(r'<h3 class="news-title">(.*?)</h3>', html)
    for t in titles:
        texts.append(('title', t))
    # 提取卡片内容
    contents = re.findall(r'<div class="news-content">(.*?)</div>', html, re.DOTALL)
    for c in contents:
        # 清理HTML标签
        c = re.sub(r'<[^>]+>', '', c)
        c = c.strip()
        if c:
            texts.append(('content', c))
    return texts

# 提取洞察
insights = re.findall(r'<div class="insight">(.*?)</div>', html, re.DOTALL)

pdf.set_font('Arial', '', 10)

# 添加标题
pdf.set_font('Arial', 'B', 12)
pdf.cell(0, 8, '今日热点', ln=True)
pdf.set_font('Arial', '', 10)
pdf.multi_cell(0, 5, '1. 黄仁勋：Token是新的大宗商品\n2. 百度智能云发布产品调价公告\n3. 网易回应AI清退外包\n4. 罗福莉自曝小米新模型\n5. 特斯拉要甩掉宁德时代？\n6. AI正在吞噬所有软件')
pdf.ln(3)

# 添加国内AI咨询
pdf.set_font('Arial', 'B', 12)
pdf.cell(0, 8, '国内AI咨询', ln=True)
pdf.set_font('Arial', '', 10)

# 添加内容
pdf.multi_cell(0, 5, '百度智能云发布产品调价公告\n来源：虎嗅\n百度智能云发布产品调价公告，这是继阿里云之后又一家涨价的云服务商。')
pdf.ln(2)

pdf.multi_cell(0, 5, '网易回应"使用AI清退全部外包"传闻\n来源：虎嗅\n有传闻称网易使用AI清退全部外包人员，网易对此作出回应。')
pdf.ln(2)

pdf.multi_cell(0, 5, '罗福莉自曝小米新模型训练过程\n来源：虎嗅\n小米AI领域重要人物罗福莉自曝新模型训练过程，引发业内关注。')
pdf.ln(2)

pdf.multi_cell(0, 5, 'AI Coding实战：10年祖传系统，54万行代码，2周重构结束\n来源：虎嗅\n展示AI在编程领域的巨大潜力。')
pdf.ln(3)

# 添加国外AI咨询
pdf.set_font('Arial', 'B', 12)
pdf.cell(0, 8, '国外AI咨询', ln=True)
pdf.set_font('Arial', '', 10)

pdf.multi_cell(0, 5, '黄仁勋：Token是新的大宗商品\n来源：虎嗅\n"过去因为相信所以看见的那个token，现在不用相信就能看见"。')
pdf.ln(2)

pdf.multi_cell(0, 5, 'AI正在吞噬所有软件\n来源：虎嗅\nAI正在吞噬所有软件，传统软件行业面临前所未有的变革。')
pdf.ln(3)

# 添加其他科技资讯
pdf.set_font('Arial', 'B', 12)
pdf.cell(0, 8, '其他科技资讯', ln=True)
pdf.set_font('Arial', '', 10)

pdf.multi_cell(0, 5, '特斯拉要甩掉宁德时代？\n来源：虎嗅\n特斯拉与宁德时代的合作关系传出新动向。')
pdf.ln(2)

pdf.multi_cell(0, 5, '吉利猛追，能否撼动比亚迪王者地位？\n来源：虎嗅\n自主品牌车企竞争激烈。')
pdf.ln(3)

# 添加洞察
pdf.set_font('Arial', 'B', 12)
pdf.cell(0, 8, '今日洞察', ln=True)
pdf.set_font('Arial', '', 10)
pdf.multi_cell(0, 5, 'AI行业继续火热，黄仁勋提出"Token是新大宗商品"观点引发热议。\n\n国内云厂商纷纷涨价，AI算力成本持续上升。\n\nAI应用正在加速落地，AI Coding、Agent成为热门赛道。\n\n汽车行业变革加速。')

# 保存
output_path = '/Users/wangkaipeng/.openclaw/workspace/ai-news/ai-news-2026-03-19.pdf'
pdf.output(output_path)
print(f'PDF已生成: {output_path}')
