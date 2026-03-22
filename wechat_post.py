#!/usr/bin/env python3
"""
公众号自动发布脚本
将 AI 资讯早报自动发布到公众号草稿箱
"""
import requests
import json
import os
import re

# 配置
APP_ID = "wxdef888862e3ecca1"
APP_SECRET = "1483a2e68153e9cf6a5f1580e223e660"

# 文件路径
NEWS_FILE = "/Users/wangkaipeng/.openclaw/workspace/ai-news/news.md"
OUTPUT_FILE = "/Users/wangkaipeng/.openclaw/workspace/ai-news/wechat_draft.md"

def get_access_token():
    """获取公众号 access_token"""
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
    resp = requests.get(url).json()
    if "access_token" in resp:
        return resp["access_token"]
    else:
        print(f"获取token失败: {resp}")
        return None

def get_mp_list(access_token):
    """获取公众号列表"""
    url = f"https://api.weixin.qq.com/cgi-bin/freepublish/getappinfo?access_token={access_token}"
    resp = requests.get(url).json()
    return resp

def convert_md_to_wechat(md_file, output_file):
    """将 MD 转换为公众号格式"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析日期
    date_match = re.search(r'#\s*AI行业资讯\s*\|\s*(\d+年\d+月\d+日)', content)
    title_date = date_match.group(1) if date_match else ""
    
    # 提取板块内容
    sections = []
    
    # 今日热点
    hot_match = re.search(r'## 今日热点[^#]*\n(.*?)(?=##|$)', content, re.DOTALL)
    if hot_match:
        hot_lines = hot_match.group(1).strip().split('\n')
        hot_items = []
        for line in hot_lines:
            line = line.strip()
            if line:
                hot_items.append(line.replace('**', '').replace('（来自', ' - ').replace('）', ''))
        if hot_items:
            sections.append(("今日热点", hot_items))
    
    # 其它板块
    section_names = ['国内AI资讯', '国外AI资讯', '智能硬件资讯', '其它科技资讯', '今日洞察']
    for sec_name in section_names:
        sec_match = re.search(rf'## {sec_name}\s*\n(.*?)(?=##|$)', content, re.DOTALL)
        if sec_match:
            sec_content = sec_match.group(1).strip()
            # 提取标题和链接
            items = []
            # 匹配 - **标题** — 描述... 来源：xxx | [链接](url)
            for line in sec_content.split('\n'):
                line = line.strip()
                if line.startswith('- **'):
                    # 提取标题
                    title_match = re.match(r'-\s*\*\*(.+?)\*\*', line)
                    if title_match:
                        title = title_match.group(1)
                        # 检查是否有链接
                        link_match = re.search(r'\[链接\]\((.+?)\)', line)
                        link = link_match.group(1) if link_match else ""
                        items.append((title, link))
            if items:
                sections.append((sec_name, items))
    
    # 生成公众号格式
    output = f"# AI行业资讯 {title_date}\n\n"
    
    for sec_name, items in sections:
        output += f"## {sec_name}\n\n"
        
        if sec_name == "今日热点":
            for item in items:
                output += f"{item}\n"
        elif sec_name == "今日洞察":
            # 今日洞察是纯文字
            output += f"{items[0] if items else ''}\n"
        else:
            for title, link in items:
                output += f"• {title}"
                if link:
                    output += f"\n  原文: {link}"
                output += "\n"
        output += "\n"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)
    
    return output

def main():
    print("🤖 AI资讯早报 - 公众号发布工具\n")
    
    # 1. 获取 access_token
    print("1. 获取 access_token...")
    access_token = get_access_token()
    if not access_token:
        print("❌ 获取失败")
        return
    print(f"   ✅ Token获取成功")
    
    # 2. 转换格式
    print("2. 转换格式...")
    if not os.path.exists(NEWS_FILE):
        print(f"   ❌ 文件不存在: {NEWS_FILE}")
        return
    content = convert_md_to_wechat(NEWS_FILE, OUTPUT_FILE)
    print(f"   ✅ 已生成: {OUTPUT_FILE}")
    
    # 3. 显示预览
    print("\n📝 预览内容：")
    print("="*50)
    print(content[:1500])
    print("="*50)
    
    # 4. 提示用户
    print("\n⚠️  请登录公众号后台手动发布：")
    print("   https://mp.weixin.qq.com/")
    print(f"\n📄 内容已保存到: {OUTPUT_FILE}")
    print("   你可以直接复制里面的内容到公众号编辑器")

if __name__ == "__main__":
    main()
