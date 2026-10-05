#!/usr/bin/env python3
"""Build the local Chinese reading editions. Requires pandoc on PATH."""
from pathlib import Path
import html
import json
import re
import subprocess
import sys
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
BOOKS = {'beyond-feelings': ('超越感觉', '批判性思维指南', 26),
         'the-craft-of-research': ('研究的艺术', '第五版 · 研究、论证与表达', 37)}
CSS = '''
:root{color-scheme:light;--paper:#fbfaf6;--ink:#263333;--muted:#657471;--line:#dbe2dc;--accent:#1a625a;--size:19px}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:28px}body{margin:0;background:var(--paper);color:var(--ink);font-family:"Songti SC","Noto Serif CJK SC","STSong",serif;font-size:var(--size);line-height:1.95}
a{color:var(--accent);text-decoration-thickness:1px;text-underline-offset:4px}a:hover{color:#a65531}a:focus-visible,button:focus-visible,input:focus-visible,summary:focus-visible{outline:3px solid #bc784b;outline-offset:3px}
.layout{max-width:1480px;margin:auto;display:grid;grid-template-columns:285px minmax(0,1fr);gap:68px;padding:0 48px 80px 24px}
.sidebar{position:sticky;top:0;height:100vh;overflow:auto;border-right:1px solid var(--line);padding:34px 25px 40px 4px;font:14px/1.65 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}
.brand{display:block;font-size:19px;font-weight:650;text-decoration:none;margin-bottom:5px}.sidebar small{color:var(--muted)}.sidebar summary{cursor:pointer;font-weight:650;padding:24px 0 10px}.search-label{display:block;color:var(--muted);font-size:12px;margin-top:10px}.sidebar input{width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:6px;background:white;font:inherit;margin:5px 0 16px}.sidebar ol{list-style:none;padding:0;margin:0}.sidebar li{margin:2px 0}.sidebar li a{display:block;padding:8px 10px;border-radius:5px;text-decoration:none;color:#40534f}.sidebar li a:hover{background:#e9efea}.sidebar li a.current{background:#e4ede7;color:#12534a;font-weight:600}.nav-number{font-size:11px;color:#7c8d87;display:inline-block;min-width:24px;font-variant-numeric:tabular-nums}.extras{border-top:1px solid var(--line);margin-top:24px;padding-top:18px}.extras a{display:block;margin:10px 0}
main{max-width:820px;min-width:0;padding-top:64px}.book-header{padding:0 0 50px;border-bottom:1px solid var(--line);margin-bottom:50px}.eyebrow{font:12px/1.5 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;letter-spacing:.2em;color:var(--muted)}.book-header h1{font-size:52px;line-height:1.25;letter-spacing:.03em;margin:17px 0}.subtitle{font-size:20px;color:#536862;margin:0}.edition-meta{font:13px/1.7 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;color:var(--muted);margin-top:24px}.controls{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:25px;font:13px/1.6 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}.controls button{font:inherit;border:1px solid var(--line);border-radius:5px;background:transparent;padding:7px 12px;cursor:pointer;color:var(--ink)}.controls button[aria-pressed=true]{background:var(--accent);border-color:var(--accent);color:white}
.chapter{padding-bottom:65px;margin-bottom:64px;border-bottom:1px solid var(--line);overflow-wrap:anywhere}.chapter-label{font:11px/1.6 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;letter-spacing:.13em;color:var(--muted);margin-bottom:12px}.chapter h1{font-size:31px;line-height:1.5;margin:0 0 28px}.chapter h2{font-size:24px;line-height:1.6;margin:44px 0 20px;color:#164d47}.chapter h3{font-size:21px;line-height:1.6;margin:30px 0 15px}.chapter h4{font-size:19px;margin:25px 0 12px}.chapter p{margin:0 0 1.05em}.chapter strong{font-weight:700}.chapter ul,.chapter ol{padding-left:1.5em;margin:1em 0}.chapter li{padding-left:.12em;margin:.45em 0}.chapter blockquote{margin:25px 0;padding:19px 25px;border-left:3px solid #77a092;background:#eff3ed;font-size:.96em}.chapter blockquote>:last-child{margin-bottom:0}.table-wrap{overflow-x:auto;margin:28px 0;border:1px solid var(--line);border-radius:5px}table{border-collapse:collapse;width:100%;font:16px/1.8 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}th,td{text-align:left;vertical-align:top;padding:12px 15px;border-bottom:1px solid var(--line);min-width:110px}th{background:#edf1eb;font-weight:650}tbody tr:last-child td{border-bottom:0}.chapter img{max-width:100%;height:auto;display:block;margin:30px auto;background:white}.chapter figure{margin:28px 0}.chapter figcaption{font-size:14px;line-height:1.7;text-align:center;color:var(--muted)}code{font-size:.86em;background:#eaf0e9;border-radius:3px;padding:2px 5px;overflow-wrap:anywhere}pre{white-space:pre-wrap;font-size:15px;background:#eef2eb;padding:18px;border-radius:5px}pre code{padding:0;background:transparent}.footnotes{font-size:14px;line-height:1.8;color:#596a63;margin-top:36px}.footnote-ref{text-decoration:none;font-family:system-ui}.back-top{font:13px/1.7 system-ui;display:inline-block;margin-top:24px}.read-footer{font:13px/1.8 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;color:var(--muted)}
@media(max-width:1000px){.layout{grid-template-columns:235px minmax(0,1fr);gap:35px;padding-right:30px}.sidebar{padding-right:18px}main{padding-top:45px}}
@media(max-width:720px){body{font-size:var(--size)}.layout{display:block;padding:0 22px 50px}.sidebar{position:relative;height:auto;border:0;border-bottom:1px solid var(--line);padding:20px 0}.sidebar details[open] ol{max-height:48vh;overflow:auto}.sidebar summary{padding:10px 0}.extras{display:flex;gap:18px;flex-wrap:wrap}.extras a{margin:0}main{padding-top:35px}.book-header h1{font-size:39px}.book-header{padding-bottom:30px;margin-bottom:32px}.chapter h1{font-size:27px}.chapter h2{font-size:22px}.chapter{padding-bottom:36px;margin-bottom:38px}.chapter blockquote{padding:15px 18px}th,td{padding:10px}.controls button{min-height:40px}}
@media print{.table-wrap{overflow:visible}body{background:white;font-size:11pt;line-height:1.7}.layout{display:block;padding:0;max-width:none}.sidebar,.controls,.back-top{display:none}main{max-width:none;padding:0}.book-header{page-break-after:always;border:0}.chapter{page-break-before:always;padding:0;border:0}.chapter h1{font-size:24pt}.chapter h2{font-size:17pt;break-after:avoid}table{font-size:9pt}a{color:inherit}blockquote,figure,tr{break-inside:avoid}}
'''
JS = '''
const search=document.getElementById('chapter-search');
search.addEventListener('input',()=>{const q=search.value.trim().toLowerCase();document.querySelectorAll('.chapter-link').forEach(a=>{a.parentElement.hidden=!a.textContent.toLowerCase().includes(q)})});
document.querySelectorAll('[data-size]').forEach(button=>button.addEventListener('click',()=>{document.documentElement.style.setProperty('--size',button.dataset.size+'px');document.querySelectorAll('[data-size]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)))}));
if(window.matchMedia('(max-width:720px)').matches)document.getElementById('outline').open=false;
const chapters=[...document.querySelectorAll('.chapter')];
function updateCurrent(){let current=chapters[0];for(const chapter of chapters){if(chapter.getBoundingClientRect().top<=100)current=chapter;else break;}document.querySelectorAll('.chapter-link').forEach(a=>{const active=current&&a.hash==='#'+current.id;a.classList.toggle('current',active);if(active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});}
let pending=false;window.addEventListener('scroll',()=>{if(!pending){pending=true;requestAnimationFrame(()=>{updateCurrent();pending=false;});}},{passive:true});
window.addEventListener('load',updateCurrent);window.addEventListener('hashchange',updateCurrent);window.addEventListener('resize',updateCurrent);updateCurrent();
'''

def title_of(s):
    return next(line[2:].strip() for line in s.splitlines() if line.startswith('# '))

def namespace_md(s, prefix):
    return re.sub(r'\[\^([^]]+)\]',lambda m:'[^'+prefix+'-'+m.group(1)+']',s)

def render(s, ident, chapter_map, prefix=''):
    out=subprocess.run(['pandoc','-f','markdown+footnotes','-t','html5','--id-prefix='+ident+'-','--wrap=none'],input=s,text=True,capture_output=True,check=True).stdout
    for name,ref in chapter_map.items():
        out=out.replace('href="'+name+'"','href="#'+ref+'"')
        out=out.replace('href="'+quote(name)+'"','href="#'+ref+'"')
    if prefix:
        out=re.sub(r'src="(?!https?:|data:)([^"]+)"',lambda m:'src="'+prefix+m.group(1)+'"',out)
    return re.sub(r'(<table(?:\s[^>]*)?>[\s\S]*?</table>)',r'<div class="table-wrap">\1</div>',out)

def shell(title, subtitle, links, articles, extra_links):
    return '<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+' · 中文阅读版</title><style>'+CSS+'</style></head><body id="top"><div class="layout"><aside class="sidebar"><a class="brand" href="#top">'+html.escape(title)+'</a><small>中文译本 · 离线阅读</small><details id="outline" open><summary>阅读目录</summary><label class="search-label" for="chapter-search">查找章节</label><input id="chapter-search" type="search" placeholder="输入章节关键词"><nav aria-label="章节目录"><ol>'+''.join(links)+'</ol></nav></details><div class="extras">'+extra_links+'</div></aside><main><header class="book-header"><div class="eyebrow">THINK FRAMEWORK · 中文书架</div><h1>'+html.escape(title)+'</h1><p class="subtitle">'+html.escape(subtitle)+'</p><p class="edition-meta">依据项目现有文本翻译 · 保留案例、练习与注释</p><div class="controls"><span>正文字号</span><button type="button" data-size="17" aria-pressed="false">小</button><button type="button" data-size="19" aria-pressed="true">标准</button><button type="button" data-size="22" aria-pressed="false">大</button></div></header>'+''.join(articles)+'<footer class="read-footer">中文译本依据项目底本整理。原文缺损与编辑处理见审校说明。</footer></main></div><script>'+JS+'</script></body></html>\n'

def build(book):
    title,subtitle,total=BOOKS[book]; dest=ROOT/(book+'-zh-CN')
    parts=sorted(dest.glob('[0-9][0-9][0-9]_*.md'))
    source_parts=sorted((ROOT/book).glob('[0-9][0-9][0-9]_*.md'))
    if len(parts)!=total or [p.name for p in parts]!=[p.name for p in source_parts]:
        raise SystemExit(f'{book}: expected {total} exact counterpart files; found {len(parts)}')
    cn={'零':0,'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9}
    def normalize_heading(m):
        n=m[1]
        if '十' in n:
            a,b=n.split('十'); num=10*(cn.get(a,1) if a else 1)+cn.get(b,0)
        else:num=cn[n]
        return f'# 第 {num} 章　'
    for p in parts:
        s=p.read_text(); s=re.sub(r'^# 第([一二三四五六七八九十]+)章[ 　]*',normalize_heading,s,count=1)
        p.write_text(s)
    mapping={p.name:'chapter-'+p.name[:3] for p in parts}
    merged=[f'# {title}\n\n> 中文合并阅读版。分章文件、图片、提炼笔记与审校说明见本目录 README。\n']
    links=[]; articles=[]; md_links=[]
    for p in parts:
        s=p.read_text(); t=title_of(s); ident=mapping[p.name]
        links.append('<li><a class="chapter-link" href="#'+ident+'"><span class="nav-number">'+p.name[:3]+'</span>'+html.escape(t)+'</a></li>')
        md_links.append(f'- [{t}]({quote(p.name)})')
        merged.append('\n---\n\n'+re.sub(r'^(#{1,5}) ',r'#\1 ',namespace_md(s,p.name[:3]),flags=re.M))
        articles.append('<article class="chapter" id="'+ident+'"><div class="chapter-label">'+p.name[:3]+' / '+str(total).zfill(3)+'</div>'+render(s,ident,mapping)+'<a class="back-top" href="#top">返回书首 ↑</a></article>')
    (dest/(book+'.md')).write_text('\n'.join(merged))
    extra='<a href="notes.html">中文提炼笔记 ↗</a><a href="translation-review.html">翻译与审校说明 ↗</a>'
    (dest/'阅读版.html').write_text(shell(title,subtitle,links,articles,extra))
    # A separate, equally styled reading edition of the already-existing derived notes.
    links=[]; articles=[]
    for i,p in enumerate(sorted((dest/'derived').rglob('*.md')),1):
        s=p.read_text(); t=title_of(s); ident='note-'+str(i)
        links.append('<li><a class="chapter-link" href="#'+ident+'">'+html.escape(t)+'</a></li>')
        articles.append('<article class="chapter" id="'+ident+'">'+render(s,ident,{})+'</article>')
    (dest/'notes.html').write_text(shell(title+' · 提炼笔记','可执行原则、章节台账与补充笔记',links,articles,'<a href="阅读版.html">返回正文 ↗</a>'))
    readme=f'''# 《{title}》中文译本

[打开排版阅读版](阅读版.html) · [中文合并版]({book}.md) · [提炼笔记](notes.html) · [翻译与审校说明](translation-review.md)

本目录与 `../{book}/` 一一对应，正文完整翻译，保留原文件名，便于对照。共 {total} 个分章／前后附属文件，另有合并版、`derived/` 提炼笔记及 `images/` 原图。

直接用浏览器打开 `阅读版.html` 即可离线阅读，支持目录筛选、章节跳转、调整字号和打印；图片应与 HTML 保持在同一目录结构中。原图中的英文标签已在正文附近给出中文说明；封面和标识的文字见 [图片文字说明](images/图片文字说明.md)。

译文按现有底本保留作者观点与案例的时代背景。明确的导出重复、错误标题和断词已整理；无法可靠恢复的缺文在原位标明。英文例句只在语言教学需要时保留，书目信息保留英文以便检索。

## 分章阅读

'''+ '\n'.join(md_links)+'''

## 提炼笔记

- [可执行原则手册](derived/actionable-principles.md)
- [逐章原则提取台账](derived/chapter-principles.md)

提炼笔记原本以中文为主，本版保留其结构、原则编号和来源线索，翻译剩余英文说明并统一术语。笔记中的原文路径与行号仍指向英文底本，以保留可追溯性。

Owner: 中文翻译协作组  
Purpose: 提供完整、自然、便于阅读与核对的中文译本  
Assumptions: 以项目现有 Markdown 和图片为底本；不擅自更新作者的历史案例  
Open questions: 底本缺损及编辑处理见审校说明  
Handoff: 从阅读版开始；需核对具体内容时，按保留的文件名查阅原文
'''
    if (dest/'derived/partials').exists():readme=readme.replace('\n提炼笔记原本','\n- [第十四、十五章补充台账](derived/partials/part-3b-problems-b.md)\n\n提炼笔记原本')
    (dest/'README.md').write_text(readme)
    review=dest/'translation-review.md'
    if review.exists():
        content=render(review.read_text(),'review',{})
        (dest/'translation-review.html').write_text(shell(title+' · 翻译与审校说明','完整性、文字与排版检查',[],['<article class="chapter" id="review">'+content+'</article>'],'<a href="阅读版.html">返回正文 ↗</a>'))
    print(f'{book}: built {total} source counterparts, combined Markdown, HTML reading editions and README')

if __name__=='__main__':
    for book in (sys.argv[1:] or BOOKS):build(book)
