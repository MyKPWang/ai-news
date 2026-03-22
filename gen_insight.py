#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 洞察生成器
通过 OpenClaw 子代理调用 MiniMax API 生成今日洞察

使用方法：
  python3 gen_insight.py          # 直接运行（会启动子代理）
  python3 gen_insight.py --wait   # 等待子代理完成

注意：
  此脚本需要通过 OpenClaw 运行才能使用子代理功能
  在终端直接运行需要配置 API Key
"""
import re
import sys
from pathlib import Path
import subprocess

NEWS_FILE = Path("/Users/wangkaipeng/.openclaw/workspace/ai-news/news.md")


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
            title = line.replace('**', '')
            title = re.sub(r'^\d+\.\s*', '', title)
            title = re.sub(r'（来自.*?）', '', title)
            items.append(title.strip())
    return items


def generate_insight_via_subagent():
    """通过 OpenClaw 子代理生成洞察"""
    # 读取新闻
    with open(NEWS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    hot_items = extract_hot_items(content)
    
    if not hot_items:
        print("❌ 未找到今日热点，请先编辑 news.md")
        return False
    
    hot_text = '\n'.join([f"{i+1}. {item}" for i, item in enumerate(hot_items[:6])])
    
    prompt = f"""你是一个科技行业分析师。请根据以下今日热点新闻，生成一段 150-200 字的今日洞察。

要求：
1. 总结 3-4 个核心趋势
2. 观点客观、有见解
3. 语言简洁有力
4. 只输出洞察内容，不要标题
5. 段落之间要空一行（用两个换行符分隔段落）

今日热点：
{hot_text}

请直接输出洞察内容，不要添加任何前缀或说明。"""
    
    # 调用 OpenClaw 子代理
    cmd = [
        'openclaw', 'session', 'spawn',
        '--task', prompt,
        '--model', 'minimax-portal/MiniMax-M2.5',
        '--timeout', '60',
        '--label', 'insight-gen'
    ]
    
    print("🤔 正在调用 AI 生成洞察...")
    print("   这会启动一个子代理，请稍候...")
    
    try:
        result = subprocess.run(cmd, cwd=str(NEWS_FILE.parent), timeout=120)
        
        if result.returncode == 0:
            print("   ✅ 子代理已启动")
            print("   💡 洞察生成后会自动更新 news.md")
            return True
        else:
            print(f"   ⚠️ 子代理启动失败: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⚠️ 超时")
        return False
    except FileNotFoundError:
        print("   ⚠️ 未找到 openclaw 命令，请确保已安装 OpenClaw")
        return False


def update_insight(insight):
    """更新 news.md 中的洞察"""
    with open(NEWS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 确保洞察段落之间有空行
    insight = insight.strip()
    
    # 检查是否已有洞察
    if '## 今日洞察' in content:
        # 替换现有洞察
        pattern = r'## 今日洞察\n.*?(?=\n\*\s*来源：|\Z)'
        content = re.sub(pattern, f'## 今日洞察\n{insight}\n', content, flags=re.DOTALL)
    else:
        # 添加洞察
        content = content.strip() + f"\n\n## 今日洞察\n{insight}\n"
    
    with open(NEWS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已更新洞察 ({len(insight)} 字)")
    return True


def main():
    print("🤖 AI 洞察生成器")
    print("=" * 50)
    
    # 检查参数
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        return
    
    # 直接运行模式
    if len(sys.argv) > 1 and sys.argv[1] == '--direct':
        # 尝试直接调用 API（需要配置 API Key）
        print("❌ 直接模式需要配置 API Key，请使用子代理模式")
        return
    
    # 默认使用子代理模式
    generate_insight_via_subagent()


if __name__ == "__main__":
    main()
