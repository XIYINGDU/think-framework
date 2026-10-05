#!/usr/bin/env python3
"""Structural checks only; semantic translation quality requires source review."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
from collections import Counter
import hashlib
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
BOOKS={'beyond-feelings':26,'the-craft-of-research':37}
class Document(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.links=[]; self.images=[]; self.articles=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        if tag=='a' and 'href' in attrs:self.links.append(attrs['href'])
        if tag=='img' and 'src' in attrs:self.images.append(attrs['src'])
        if tag=='article' and attrs.get('id','').startswith('chapter-'):self.articles+=1

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(book):
    source=ROOT/book; dest=ROOT/(book+'-zh-CN'); errors=[]; records=[]
    files=sorted(source.rglob('*')); originals=[p for p in files if p.is_file()]
    for p in originals:
        q=dest/p.relative_to(source)
        if not q.exists():errors.append('Missing counterpart: '+str(q.relative_to(ROOT)));continue
        records.append({'source':str(p.relative_to(ROOT)),'source_sha256':digest(p),'translation':str(q.relative_to(ROOT)),'translation_sha256':digest(q)})
        if p.suffix.lower() in {'.jpg','.jpeg','.png'} and digest(p)!=digest(q):errors.append('Original image changed: '+str(q))
    parts=sorted(dest.glob('[0-9][0-9][0-9]_*.md'))
    if len(parts)!=BOOKS[book]:errors.append(f'Expected {BOOKS[book]} sections; got {len(parts)}')
    footnotes=0; figures=0
    for p in parts:
        s=p.read_text(); original=source/p.name
        if len(re.findall(r'^# ',s,re.M))!=1:errors.append(p.name+': must have one H1')
        if not re.search(r'[\u4e00-\u9fff]',s):errors.append(p.name+': no Chinese translation')
        for marker in ['\u00ad','\ufffd']:
            if marker in s:errors.append(p.name+': invalid character '+repr(marker))
        if re.search(r'^P\d+-C\d+-\d+\s*$',s,re.M):errors.append(p.name+': export page marker remains')
        refs=set(re.findall(r'\[\^([^]]+)\](?!:)',s)); defs=re.findall(r'^\[\^([^]]+)\]:',s,re.M)
        if refs!=set(defs):errors.append(p.name+': footnote references and definitions differ')
        if len(defs)!=len(set(defs)):errors.append(p.name+': duplicate footnote IDs')
        footnotes+=len(defs)
        images=re.findall(r'!\[[^]]*\]\(([^)]+)\)',s); figures+=len(images)
        if original.exists():
            original_images=re.findall(r'!\[[^]]*\]\(([^)]+)\)',original.read_text())
            if Counter(images)!=Counter(original_images):errors.append(p.name+': image references differ from source')
        for link in images:
            if not (p.parent/unquote(link)).is_file():errors.append(p.name+': missing image '+link)
        for block in re.findall(r'(?:^\|.*\|\s*$\n?){2,}',s,re.M):
            rows=block.strip().splitlines(); widths=[len(re.split(r'(?<!\\)\|',row)) for row in rows]
            if len(set(widths))>1:errors.append(p.name+': malformed table column count')
    combined=dest/(book+'.md')
    if combined.exists():
        s=combined.read_text(); defs=re.findall(r'^\[\^([^]]+)\]:',s,re.M)
        refs=set(re.findall(r'\[\^([^]]+)\](?!:)',s))
        if len(defs)!=len(set(defs)) or refs!=set(defs):errors.append('Combined edition has invalid footnotes')
        if len(defs)!=footnotes:errors.append('Combined edition loses footnotes')
    for p in sorted(dest.glob('*.html')):
        doc=Document();doc.feed(p.read_text()); duplicates=[k for k,n in Counter(doc.ids).items() if n>1]
        if duplicates:errors.append(p.name+': duplicate HTML IDs '+str(duplicates[:5]))
        for href in doc.links+doc.images:
            url=urlsplit(href)
            if url.scheme or href.startswith('//'):continue
            if not url.path:
                if url.fragment and unquote(url.fragment) not in doc.ids:errors.append(p.name+': missing anchor '+url.fragment)
            elif not (p.parent/unquote(url.path)).exists():errors.append(p.name+': broken local link '+href)
        if p.name=='阅读版.html' and doc.articles!=BOOKS[book]:errors.append('HTML chapter count mismatch')
    source_aps=set(re.findall(r'^### (AP-\d+)',(source/'derived/actionable-principles.md').read_text(),re.M))
    target_aps=set(re.findall(r'^### (AP-\d+)',(dest/'derived/actionable-principles.md').read_text(),re.M))
    if source_aps!=target_aps:errors.append('Derived AP IDs differ')
    report={'book':book,'sections':len(parts),'source_counterparts':len(records),'images':len(list((source/'images').iterdir())),
            'inline_figures':figures,'footnotes':footnotes,'actionable_principles':len(target_aps),
            'chinese_characters_in_sections':sum(len(re.findall(r'[\u4e00-\u9fff]',p.read_text())) for p in parts),
            'checks':'structural; source fidelity and prose reviewed separately','errors':errors,'files':records}
    (dest/'validation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='files'},ensure_ascii=False))
    return not errors
if __name__=='__main__':
    results=[check(b) for b in (sys.argv[1:] or BOOKS)]
    sys.exit(0 if all(results) else 1)
