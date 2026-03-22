#!/usr/bin/env python3
"""
AI 资讯早报 - 分类校验脚本
自动检查并修正新闻分类错误
"""
import re
import sys

NEWS_FILE = "/Users/wangkaipeng/.openclaw/workspace/ai-news/news.md"

# 公司分类表：关键字 -> 正确板块
# 只用于检测可能分类错误的新闻
COMPANY_CORRECTIONS = {
    # 国外公司（应该放国外AI）
    "软银": "国外AI",
    "苹果": "国外AI",
    "亚马逊": "国外AI",
    "Meta": "国外AI",
    "Google": "国外AI",
    "Nvidia": "国外AI",
    "NVIDIA": "国外AI",
    "微软": "国外AI",
    "Microsoft": "国外AI",
    "OpenAI": "国外AI",
    "Anthropic": "国外AI",
    "Samsung": "国外AI",
    "三星": "国外AI",
    "Apple": "国外AI",
    "Amazon": "国外AI",
    "Signal": "国外AI",
    "Palantir": "国外AI",
    "Perplexity": "国外AI",
    "WordPress": "国外AI",
    
    # 国内公司（应该放国内AI）
    "腾讯": "国内AI",
    "阿里": "国内AI",
    "华为": "国内AI",
    "百度": "国内AI",
    "小米": "国内AI",
    "字节": "国内AI",
    "MiniMax": "国内AI",
    "月之暗面": "国内AI",
    "智谱": "国内AI",
    "飞书": "国内AI",
    "鸿蒙": "国内AI",
}


def check_classification(content):
    """检查分类是否有问题"""
    issues = []
    
    # 提取各个板块的内容
    domestic_section = re.search(r'## 国内AI资讯.*?\n(.*?)(?=## |\Z)', content, re.DOTALL)
    foreign_section = re.search(r'## 国外AI资讯.*?\n(.*?)(?=## |\Z)', content, re.DOTALL)
    
    if not domestic_section or not foreign_section:
        return issues
    
    domestic_content = domestic_section.group(1)
    foreign_content = foreign_section.group(1)
    
    # 检查国内板块是否有国外公司
    for company, correct_section in COMPANY_CORRECTIONS.items():
        if correct_section == "国外AI":
            if company in domestic_content:
                issues.append(f"⚠️ {company} 出现在国内AI板块，应归入国外AI")
    
    # 检查国外板块是否有国内公司
    for company, correct_section in COMPANY_CORRECTIONS.items():
        if correct_section == "国内AI":
            if company in foreign_content:
                issues.append(f"⚠️ {company} 出现在国外AI板块，应归入国内AI")
    
    return issues


def main():
    print("🔍 AI 资讯早报 - 分类校验")
    print("=" * 50)
    
    # 读取文件
    with open(NEWS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查分类
    issues = check_classification(content)
    
    if issues:
        print("\n发现分类问题：")
        for issue in issues:
            print(f"  {issue}")
        print("\n⚠️ 请手动修正以上分类错误")
        return 1
    else:
        print("\n✅ 分类检查通过！")
        return 0


if __name__ == "__main__":
    sys.exit(main())
