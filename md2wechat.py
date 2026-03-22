#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI资讯早报生成器
同时生成：
1. GitHub Pages HTML
2. 公众号 HTML
使用模板文件
"""
import re
import json
import requests
from datetime import datetime
from pathlib import Path

# 配置
WORK_DIR = Path("/Users/wangkaipeng/.openclaw/workspace/ai-news")
NEWS_FILE = WORK_DIR / "news.md"
COVER_FILE = WORK_DIR / "cover.jpg"
COVER_MEDIA_ID_FILE = WORK_DIR / "cover_media_id.txt"
TEMPLATE_WECHAT = WORK_DIR / "template_wechat.html"
TEMPLATE_GITHUB = WORK_DIR / "template_github.html"
OUTPUT_HTML = WORK_DIR / "index.html"
OUTPUT_WECHAT_HTML = WORK_DIR / "wechat_article.html"

# 公众号配置
APP_ID = "wxdef888862e3ecca1"
APP_SECRET = "1483a2e68153e9cf6a5f1580e223e660"

def read_news_md():
    """读取 news.md 文件"""
    with open(NEWS_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def read_template(path):
    """读取模板文件"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_date(content):
    """提取日期"""
    match = re.search(r'#\s*AI行业资讯\s*\|\s*(\d+年\d+月\d+日)', content)
    return match.group(1) if match else datetime.now().strftime("%Y年%m月%d日")

def extract_section(content, section_name):
    """提取板块内容"""
    # 支持标题后有括号内容，如 国内AI资讯（15条）
    pattern = rf'## {section_name}.*?\n+(.*?)(?=## |\Z)'
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else ""

def extract_hot_items(content):
    """提取今日热点"""
    pattern = r'## 今日热点.*?\n(.*?)(?=##\s|$)'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return []
    
    items = []
    for line in match.group(1).split('\n'):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith('-')):
            # 去掉 ** 序号 括号类别
            title = line.replace('**', '')
            title = re.sub(r'^\d+\.\s*', '', title)
            title = re.sub(r'（来自.*?）', '', title)
            items.append(title.strip())
    return items


def extract_all_sources(content):
    """提取所有来源并去重"""
    sources = set()
    # 匹配 "来源：xxx" 格式，支持空格（用于 "The Verge" 这种）
    for match in re.finditer(r'来源：([a-zA-Z0-9\u4e00-\u9fa5][a-zA-Z0-9\u4e00-\u9fa5\s]*)', content):
        source = match.group(1).strip()
        # 清理末尾的标点
        source = re.sub(r'[，。,.\s]+$', '', source)
        # 过滤掉一些无关的词和太短的
        if source and len(source) >= 2 and source not in ['链接', '原文', '来源']:
            sources.add(source)
    # 排序返回
    return '、'.join(sorted(sources))

def generate_github_html(content, date):
    """生成 GitHub Pages HTML"""
    template = read_template(TEMPLATE_GITHUB)
    title = f"AI行业资讯 | {date}"
    
    # 今日热点
    hot_items = extract_hot_items(content)
    hot_html = ""
    for item in hot_items:
        # 去掉 **
        item = item.replace('**', '')
        hot_html += f"                <li>{item}</li>\n"
    
    # 各板块
    sections_html = ""
    for sec_name in ['国内AI资讯', '国外AI资讯', '智能硬件资讯', '其它科技资讯']:
        sec_content = extract_section(content, sec_name)
        if not sec_content:
            continue
            
        items_html = ""
        for line in sec_content.split('\n'):
            line = line.strip()
            if line.startswith('- **'):
                title_match = re.search(r'\*\*(.+?)\*\*', line)
                title = title_match.group(1).replace('**', '') if title_match else ""
                desc_match = re.search(r'\*\*.*?\*\*\s*—\s*(.+?)(?:来源：|$)', line)
                desc = desc_match.group(1).strip() if desc_match else ""
                link_match = re.search(r'\[链接\]\((.+?)\)', line)
                link = link_match.group(1) if link_match else ""
                source_match = re.search(r'来源：([^|\[]+)', line)
                source = source_match.group(1).strip() if source_match else ""
                
                items_html += f'''
        <div class="item">
            <h3>{title}</h3>
            <p class="desc">{desc}</p>
            <p class="meta">来源：{source}'''
                if link:
                    items_html += f''' | <a href="{link}" target="_blank">原文链接</a>'''
                items_html += '''</p>
        </div>
'''
        
        if items_html:
            sections_html += f'''
        <div class="section">
            <h2>{sec_name}</h2>
{items_html}
        </div>
'''
    
    # 今日洞察
    insight = extract_section(content, '今日洞察')
    insight_html = ""
    if insight:
        insight_html = f'''
        <div class="insight">
            <h2>💡 今日洞察</h2>
            <p>{insight}</p>
        </div>
'''
    
    # 替换模板占位符
    html = template.replace('{{title}}', title)
    html = html.replace('{{hot_items}}', hot_html)
    html = html.replace('{{sections}}', sections_html)
    html = html.replace('{{insight}}', insight_html)
    
    return html

def generate_wechat_html(content, date):
    """生成公众号 HTML"""
    template = read_template(TEMPLATE_WECHAT)
    
    # 今日热点
    hot_items = extract_hot_items(content)
    hot_html = ""
    for item in hot_items:
        hot_html += f'        <li style="margin:0;font-size:16px;line-height:1.0;"><em>• {item}</em></li>\n'
    
    # 各板块
    sections_html = ""
    for sec_name, emoji in [('国内AI资讯', '🏷️'), ('国外AI资讯', '🌍'), 
                            ('智能硬件资讯', '📱'), ('其它科技资讯', '💻')]:
        sec_content = extract_section(content, sec_name)
        if not sec_content:
            continue
            
        items_html = ""
        # 把整个板块内容按资讯条目分割（每个条目以 **数字. 开头）
        items = [item for item in re.split(r'\n(?=\*\*)', sec_content) if item.strip()]
        
        for item in items:
            if not item.strip():
                continue
                
            # 标题匹配
            title_match = re.search(r'\*\*(.+?)\*\*', item)
            title = title_match.group(1) if title_match else ""
            
            # 描述匹配：从标题后到来源前
            desc_match = re.search(r'\*\*.*?\*\*\n(.*?)\n来源：', item, re.DOTALL)
            desc = desc_match.group(1).strip() if desc_match else ""
            
            # 如果没匹配到描述，尝试其他格式
            if not desc:
                desc_match = re.search(r'\*\*.*?\*\*\s*—\s*(.+?)(?:来源：|$)', item)
                desc = desc_match.group(1).strip() if desc_match else ""
            
            # 来源匹配
            source_match = re.search(r'来源：([^|\[]+)', item)
            source = source_match.group(1).strip() if source_match else ""
            
            if title:
                items_html += f'''
    <h3 style="color:#1890ff;font-weight:bold;font-size:17px;">{title}</h3>
    <p style="color:#666;font-size:15px;">{desc}</p>
'''
                if source:
                    items_html += f'    <p style="color:#1890ff;font-size:13px;">来源：{source}</p>\n'
        
        if items_html:
            sections_html += f'''
    <h2 style="color:#000000;font-weight:bold;font-size:19px;margin-top:25px;">{emoji} {sec_name}</h2>
{items_html}
'''
    
    # 今日洞察
    insight = extract_section(content, '今日洞察')
    insight_html = ""
    if insight:
        insight_html = f'''
    <h2 style="color:#000000;font-weight:bold;font-size:19px;margin-top:25px;">💡 今日洞察</h2>
    <div style="background:#f6ffed;padding:15px;border-radius:8px;line-height:1.8;font-size:15px;">
        <p>{insight}</p>
    </div>
'''
    
    # 提取来源
    sources = extract_all_sources(content)
    
    # 替换模板占位符
    html = template.replace('{{hot_items}}', hot_html)
    html = html.replace('{{sections}}', sections_html)
    html = html.replace('{{insight}}', insight_html)
    html = html.replace('{{sources}}', sources)
    
    return html

def upload_cover():
    """上传封面图到微信素材库"""
    if not COVER_FILE.exists():
        print("❌ 封面图不存在")
        return None
    
    # 读取保存的 media_id
    if COVER_MEDIA_ID_FILE.exists():
        with open(COVER_MEDIA_ID_FILE, 'r') as f:
            saved_id = f.read().strip()
        if saved_id:
            return saved_id
    
    # 获取 token
    resp = requests.get(
        f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
    ).json()
    access_token = resp.get("access_token")
    
    # 上传封面
    with open(COVER_FILE, 'rb') as f:
        files = {'media': ('cover.jpg', f, 'image/jpeg')}
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image"
        r = requests.post(url, files=files).json()
    
    if "media_id" in r:
        media_id = r["media_id"]
        with open(COVER_MEDIA_ID_FILE, 'w') as f:
            f.write(media_id)
        print(f"✅ 封面上传成功: {media_id[:30]}...")
        return media_id
    else:
        print(f"❌ 封面上传失败: {r}")
        return None

def post_to_wechat(html, date):
    """上传到公众号草稿箱"""
    resp = requests.get(
        f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
    ).json()
    access_token = resp.get("access_token")
    
    thumb_media_id = upload_cover()
    article_title = f"AI资讯早报（{date}）"
    
    draft = {
        "articles": [{
            "title": article_title,
            "author": "卧龙",
            "content": html,
            "thumb_media_id": thumb_media_id,
            "digest": "每日AI行业资讯速览"
        }]
    }
    
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
    post_data = json.dumps(draft, ensure_ascii=False).encode('utf-8')
    resp = requests.post(url, data=post_data, headers={'Content-Type': 'application/json; charset=utf-8'}).json()
    
    if "media_id" in resp:
        print(f"✅ 成功上传到公众号草稿箱!")
        print(f"📝 草稿ID: {resp['media_id'][:30]}...")
        return True
    else:
        print(f"❌ 上传失败: {resp}")
        return False

def main():
    print("🤖 AI资讯早报生成器")
    print("=" * 50)
    
    # 读取 news.md
    print("📖 读取 news.md...")
    content = read_news_md()
    date = extract_date(content)
    print(f"   日期: {date}")
    
    # 生成 GitHub Pages HTML
    print("🌐 生成 GitHub Pages HTML...")
    github_html = generate_github_html(content, date)
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(github_html)
    print(f"   ✅ 已保存到: {OUTPUT_HTML}")
    
    # 生成公众号 HTML
    print("📱 生成公众号 HTML...")
    wechat_html = generate_wechat_html(content, date)
    with open(OUTPUT_WECHAT_HTML, 'w', encoding='utf-8') as f:
        f.write(wechat_html)
    print(f"   ✅ 已保存到: {OUTPUT_WECHAT_HTML}")
    
    # 上传到公众号
    print("\n📤 上传到公众号...")
    post_to_wechat(wechat_html, date)
    
    print("\n✅ 完成!")

if __name__ == "__main__":
    main()
