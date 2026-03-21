#!/usr/bin/env python3
"""
Markdown 转 HTML 转换脚本
将 ai-news 的 markdown 格式转换为 HTML 页面
支持6个板块：今日热点、国内AI、国外AI、智能硬件、其它科技、今日洞察
"""
import re
from datetime import datetime

# 配置路径
MD_FILE = '/Users/wangkaipeng/.openclaw/workspace/ai-news/news.md'
TEMPLATE_FILE = '/Users/wangkaipeng/.openclaw/workspace/ai-news/template.html'
OUTPUT_FILE = '/Users/wangkaipeng/.openclaw/workspace/ai-news/index.html'

# 板块颜色配置
SECTION_COLORS = {
    '国内AI': 'default',      # 红色竖条
    '国外AI': 'blue',         # 蓝色竖条
    '智能硬件': 'green',      # 绿色竖条
    '其它科技': 'purple',     # 紫色竖条
}

SECTION_EMOJI = {
    '国内AI': '🏷️',
    '国外AI': '🌍',
    '智能硬件': '📱',
    '其它科技': '💻',
}

# 域名映射 - 用于拼接相对路径
DOMAIN_MAP = {
    '36kr': 'https://www.36kr.com',
    'huxiu': 'https://www.huxiu.com',
    'jiemian': 'https://www.jiemian.com',
    'infoq': 'https://www.infoq.cn',
    'theverge': 'https://www.theverge.com',
    'wired': 'https://www.wired.com',
    'venturebeat': 'https://venturebeat.com',
    'reuters': 'https://www.reuters.com',
    'bbc': 'https://www.bbc.com',
    'wsj': 'https://www.wsj.com',
}


def fix_link(link):
    """修复链接：相对路径拼接域名，绝对路径直接返回"""
    if not link:
        return ''
    
    link = link.strip()
    
    # 如果是相对路径（以/开头，不是http）
    if link.startswith('/'):
        # 尝试识别域名
        for domain, base_url in DOMAIN_MAP.items():
            # 这里简化处理：如果是 /newsflashes/xxx 或 /article/xxx，拼接36kr或虎嗅
            if '/newsflashes/' in link or '/p/' in link:
                return 'https://www.36kr.com' + link
            elif '/article/' in link:
                return 'https://www.huxiu.com' + link
            elif '/news/' in link:
                return 'https://www.jiemian.com' + link
        # 默认返回原链接（可能是正确的相对路径）
        return link
    
    # 如果已经是完整链接，直接返回
    if link.startswith('http://') or link.startswith('https://'):
        return link
    
    return link


def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def parse_markdown(md_content):
    """解析 markdown 内容"""
    data = {
        'title': '',
        'date': '',
        'hot_items': [],
        'sections': [],  # [(title, items, color_class), ...]
        'insight': '',
        'footer': ''
    }
    
    lines = md_content.strip().split('\n')
    
    # 解析标题日期
    title_match = re.search(r'#\s*(.+?)\s*\|\s*(\d+年\d+月\d+日)', md_content)
    if title_match:
        data['title'] = title_match.group(1).strip()
        data['date'] = title_match.group(2).strip()
        
        # 获取星期
        date_str = title_match.group(2)
        try:
            year, month, day = re.findall(r'\d+', date_str)
            weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            weekday_name = weekday[datetime(int(year), int(month), int(day)).weekday()]
            data['date'] = f"{date_str} {weekday_name}"
        except:
            pass
    
    # 解析今日热点
    # 找到 ## 今日热点 这一行，然后找下一个 ## 之间的内容
    hot_match = re.search(r'##\s+今日热点', md_content)
    if hot_match:
        # 找到这一行的结束位置
        start_pos = hot_match.end()
        # 往回找到行尾
        line_end = md_content.find('\n', hot_match.start())
        if line_end != -1:
            start_pos = line_end + 1
        
        # 找到下一个 ##
        next_section = re.search(r'\n##\s+', md_content[start_pos:])
        if next_section:
            end_pos = start_pos + next_section.start()
        else:
            end_pos = len(md_content)
        hot_content = md_content[start_pos:end_pos]
        
        # 匹配 1. **标题** — 描述 或 1. **标题**
        for line in hot_content.split('\n'):
            line = line.strip()
            if line:
                match = re.match(r'^\d+\.\s*\*\*(.+?)\*\*\s*(?:—|-)?\s*(.*)$', line)
                if match:
                    title = match.group(1).strip()
                    desc = match.group(2).strip() if match.group(2) else ''
                    if title:
                        data['hot_items'].append({'title': title, 'desc': desc})
    
    # 解析各个资讯板块
    section_names = ['国内AI资讯', '国外AI资讯', '智能硬件资讯', '其它科技资讯']
    
    for section_name in section_names:
        # 匹配 ## 板块名 和下一个 ## 之间的内容
        pattern = rf'##\s*{section_name}\s*\n(.*?)(?=##\s|$)'
        match = re.search(pattern, md_content, re.DOTALL)
        
        if match:
            section_content = match.group(1)
            items = []
            
            # 匹配 - **标题** — 描述 来源：xxx | [链接](url)
            item_pattern = re.compile(
                r'-\s*\*\*([^*]+)\*\*\s*(?:—|-)\s*(.+?)\s*来源：([^|\n]+)(?:\s*\|\s*\[链接\]\(([^)]+)\))?',
                re.DOTALL
            )
            for item_match in item_pattern.finditer(section_content):
                title = item_match.group(1).strip()
                desc = item_match.group(2).strip()
                source = item_match.group(3).strip() if item_match.group(3) else ''
                link = item_match.group(4).strip() if item_match.group(4) else ''
                items.append({'title': title, 'desc': desc, 'source': source, 'link': link})
            
            # 如果没匹配到标准格式，尝试简单格式
            if not items:
                simple_pattern = re.compile(r'-\s*(.+?)(?:—|-)\s*(.+?)$', re.MULTILINE)
                for item_match in simple_pattern.finditer(section_content):
                    title = item_match.group(1).strip()
                    desc = item_match.group(2).strip()
                    items.append({'title': title, 'desc': desc, 'source': '', 'link': ''})
            
            if items:
                # 获取颜色
                key_name = section_name.replace('资讯', '')
                color = SECTION_COLORS.get(key_name, 'default')
                emoji = SECTION_EMOJI.get(key_name, '📰')
                
                data['sections'].append({
                    'title': section_name,
                    'items': items,
                    'color': color,
                    'emoji': emoji
                })
    
    # 解析今日洞察
    insight_match = re.search(r'##\s*今日洞察\s*\n(.*?)(?:\n\*\s*来源：|$)', md_content, re.DOTALL)
    if insight_match:
        data['insight'] = insight_match.group(1).strip()
    
    # 解析底部来源
    source_match = re.search(r'\*来源：(.+?)\*', md_content)
    if source_match:
        data['footer'] = f"来源：{source_match.group(1).strip()}"
    
    return data


def render_hot_items(items):
    """渲染今日热点"""
    if not items:
        return ''
    
    html = '<div class="hot-box">\n      <div class="title">📌 今日热点</div>\n'
    for i, item in enumerate(items, 1):
        title = item['title'].replace('**', '')
        desc = item['desc'].replace('**', '')
        if desc:
            html += f'      <div class="item">{i}. {title} — {desc}</div>\n'
        else:
            html += f'      <div class="item">{i}. {title}</div>\n'
    html += '    </div>'
    return html


def render_sections(sections):
    """渲染资讯板块"""
    if not sections:
        return ''
    
    html = ''
    for section in sections:
        title = section['title']
        items = section['items']
        color = section['color']
        emoji = section['emoji']
        
        title_class = f'sec-title {color}'
        
        html += f'''
    <div class="sec">
      <div class="{title_class}">{emoji} {title}</div>
      <div class="sec-list">
'''
        for item in items:
            html += f'        <div class="item">\n'
            html += f'          <div class="title">{item["title"]}</div>\n'
            if item['desc']:
                html += f'          <div class="desc">{item["desc"]}</div>\n'
            if item['source']:
                html += f'          <div class="meta">来源：{item["source"]}</div>\n'
            if item['link']:
                fixed_link = fix_link(item['link'])
                html += f'          <div class="link"><a href="{fixed_link}">查看原文 →</a></div>\n'
            html += f'        </div>\n'
        
        html += '      </div>\n    </div>'
    
    return html


def render_insight(content):
    """渲染今日洞察"""
    if not content:
        return ''
    
    html = f'''
    <div class="insight">
      <div class="title">💡 今日洞察</div>
      <div class="content">{content}</div>
    </div>'''
    return html


def generate_html(data, template):
    """生成最终 HTML"""
    html = template
    
    # 替换变量
    html = html.replace('{{title}}', data['title'])
    html = html.replace('{{date}}', data['date'])
    html = html.replace('{{hot_items}}', render_hot_items(data['hot_items']))
    html = html.replace('{{sections}}', render_sections(data['sections']))
    html = html.replace('{{insight}}', render_insight(data['insight']))
    html = html.replace('{{footer}}', data['footer'])
    
    return html


def main():
    print("📝 读取 Markdown 文件...")
    md_content = read_file(MD_FILE)
    
    print("🔄 解析 Markdown 内容...")
    data = parse_markdown(md_content)
    print(f"   标题: {data['title']}")
    print(f"   日期: {data['date']}")
    print(f"   热点: {len(data['hot_items'])} 条")
    for sec in data['sections']:
        print(f"   {sec['title']}: {len(sec['items'])} 条")
    
    print("📄 读取模板文件...")
    template = read_file(TEMPLATE_FILE)
    
    print("🎨 生成 HTML...")
    html = generate_html(data, template)
    
    print("💾 写入输出文件...")
    write_file(OUTPUT_FILE, html)
    
    print(f"✅ 完成! 已生成: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
