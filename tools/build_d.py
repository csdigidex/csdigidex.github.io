# 디지몬별 정적 페이지(d/NNN.html)를 본 도감 화면 스냅샷(snap.json)으로 다시 만든다.
# 순서: (1) 로컬 서버 띄우고 snap.js 실행 → snap.json  (2) 이 스크립트 실행
import json, re, html, hashlib, base64, os, datetime
R='/home/claude/csdigidex.github.io'
TODAY=datetime.date.today().isoformat()
snap=json.load(open('/home/claude/dex/static/snap.json'))
s=open(R+'/index.html',encoding='utf-8').read()
D=json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>',s,re.S).group(1))
NO={d['name']:d['no'] for d in D['digimon'] if d.get('no')}
css=re.search(r'<style[^>]*>(.*?)</style>',s,re.S).group(1)
EXTRA="""
.sp{max-width:900px;margin:0 auto;padding:16px 16px 40px}
.sp .crumb{color:var(--muted);font-size:14px;margin:4px 0 8px}.sp .crumb a{color:var(--accent);display:inline-flex;align-items:center;gap:6px}
.sp .alias{color:var(--muted);font-size:14px;margin:0 0 10px}
.sp .openapp{display:inline-block;margin:0 0 14px;padding:9px 16px;border-radius:10px;background:var(--accent);color:#fff;text-decoration:none;font-weight:600}
.file.sfile{position:static!important;max-height:none!important;overflow:visible!important;inset:auto!important;z-index:auto!important;border-radius:14px!important;border:1px solid var(--line)!important;padding:20px!important;display:block!important}
.sfile a.chip,.sfile a.tn,.sfile a.rt-go{text-decoration:none;color:inherit}.sfile [data-href]{cursor:pointer}
.sp .faq{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px 20px;margin:14px 0}.sp .faq h2{font-size:18px;margin:0 0 6px}.sp .faq h3{font-size:15px;margin:12px 0 2px}.sp .faq p{margin:2px 0}
.sp footer{font-size:12px;color:var(--muted);margin-top:24px;line-height:1.6}
@media (max-width:760px){.file.sfile{padding:16px!important}}
"""
open(R+'/app.css','w',encoding='utf-8').write(css+EXTRA)
os.makedirs(R+'/img/h',exist_ok=True)
seen={}
def img(m):
    uri=m.group(0)
    if uri in seen: return seen[uri]
    head,b64=uri.split(',',1); ext={'image/png':'png','image/jpeg':'jpg','image/webp':'webp','image/gif':'gif','image/svg+xml':'svg'}[head[5:].split(';')[0]]
    raw=base64.b64decode(b64); h=hashlib.sha1(raw).hexdigest()[:12]
    p=f'img/h/{h}.{ext}'
    if not os.path.exists(R+'/'+p): open(R+'/'+p,'wb').write(raw)
    seen[uri]='../'+p; return seen[uri]
def url(n):
    n=html.unescape(n); return f'{int(NO[n]):03d}.html' if n in NO else '../'
SCRIPT="""<script>
(function(){var t=document.querySelector('.tree');function draw(){if(!t)return;var svg=t.querySelector('.tree-svg'),E=JSON.parse(t.dataset.edges),tb=t.getBoundingClientRect();svg.setAttribute('width',t.scrollWidth);svg.setAttribute('height',t.scrollHeight);var P={};t.querySelectorAll('[data-tn]').forEach(function(b){var r=b.getBoundingClientRect();P[b.dataset.tn]={l:r.left-tb.left+t.scrollLeft,r:r.right-tb.left+t.scrollLeft,y:r.top-tb.top+r.height/2}});svg.innerHTML=E.map(function(e){var a=P[e[0]],b=P[e[1]];if(!a||!b)return'';var x1=a.r,x2=b.l,m=(x1+x2)/2;return'<path style="stroke:var(--t'+e[2]+')" d="M'+x1+','+a.y+' C'+m+','+a.y+' '+m+','+b.y+' '+x2+','+b.y+'"/>'}).join('')}
draw();addEventListener('resize',draw);addEventListener('load',draw);if(document.fonts)document.fonts.ready.then(draw);
document.addEventListener('click',function(e){var c=e.target.closest('[data-href]');if(!c||e.target.closest('a,button'))return;location.href=c.dataset.href});})();
</script>"""
cnt=0
for no,raw in snap.items():
    f=f'{R}/d/{int(no):03d}.html'
    if not os.path.exists(f): print('missing page',no); continue
    old=open(f,encoding='utf-8').read()
    head=old[:old.find('</head>')]
    head=re.sub(r'<style>.*?</style>','',head,count=1,flags=re.S)
    if 'app.css' not in head:
        head+='<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Do+Hyeon&family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap"><link rel="stylesheet" href="../app.css">'
    body=old[old.find('<body'):]
    crumb=re.search(r'<p class="(?:meta|crumb)"><a href="\.\./".*?</p>',body,re.S).group(0).replace('class="meta"','class="crumb"',1)
    alias=re.search(r'<p class="(?:meta" style="margin-top:-6px|alias)">(.*?)</p>',body,re.S)
    faq=re.search(r'<(?:div class="card"|section class="faq") id="faq">(.*?)</(?:div|section)>',body,re.S)
    name=html.unescape(re.search(r'<h2>(.*?)</h2>',raw).group(1))
    h=raw
    h=re.sub(r'<button class="back" id="back">.*?</button>','',h)
    h=re.sub(r'<div class="scope".*?</div>','',h,count=1,flags=re.S)
    # 세대 탭 → 고정 라벨
    m=re.search(r'<div class="foetabs" role="tablist">(.*?)</div>',h,re.S)
    if m:
        cur=re.search(r'aria-selected="true"[^>]*>(.*?)</button>',m.group(1),re.S)
        lab=re.sub(r'<[^>]+>','',cur.group(1)).strip() if cur else ''
        h=h.replace(m.group(0),f'<p class="lvnote" style="margin:4px 0"><b>{lab}</b> · 다른 세대 상대는 도감에서 볼 수 있어요.</p>')
        h=h.replace(' · 세대를 누르면 그 세대 목록이 보여요','')
    h=re.sub(r'<button ([^>]*?)data-go="([^"]*)"([^>]*)>(.*?)</button>',lambda m:f'<a {m.group(1)}href="{url(m.group(2))}"{m.group(3)}>{m.group(4)}</a>',h,flags=re.S)
    h=re.sub(r'<button ([^>]*?)data-tgo="([^"]*)"([^>]*)>(.*?)</button>',lambda m:f'<a {m.group(1)}href="{url(m.group(2))}"{m.group(3)}>{m.group(4)}</a>',h,flags=re.S)
    h=re.sub(r'data-evgo="([^"]*)"',lambda m:f'data-evgo="{m.group(1)}" data-href="{url(m.group(1))}"',h)
    h=re.sub(r'<button class="rt-go" data-rtto="[^"]*">.*?</button>',f'<a class="rt-go" href="../#d/{no}">🧭 도감에서 {html.escape(name)} 진화 루트 찾기</a>',h,flags=re.S)
    h=re.sub(r'<svg class="tree-svg"[^>]*>.*?</svg>',lambda m:re.sub(r'>.*?</svg>$','></svg>',m.group(0),flags=re.S),h,flags=re.S)
    h=re.sub(r'data:image/[a-z+]+;base64,[A-Za-z0-9+/=]+',img,h)
    h=h.replace('<img class="ico big" src=','<img class="ico big" alt="'+html.escape(name)+' 아이콘" src=',1).replace('alt="" width="56"','width="56"',1)
    out=head+'</head><body><main class="sp">\n'+crumb+'\n'
    if alias: out+=f'<p class="alias">{alias.group(1)}</p>\n'
    out+=f'<a class="openapp" href="../#d/{no}">도감 앱에서 열기 (검색·비교·파트너 테스트)</a>\n'
    out+=f'<article class="file sfile" id="file" data-open="true">{h}</article>\n'
    if faq: out+=f'<section class="faq" id="faq">{faq.group(1)}</section>\n'
    out+=f'<footer>비영리 팬 사이트입니다. 게임 화면에서 옮겨 적은 정보이며, 디지몬 관련 이미지·명칭의 저작권은 ©Akiyoshi Hongo, Toei Animation, ©BANDAI NAMCO Entertainment Inc.에 있습니다. 이 사이트의 정리 내용을 옮길 때는 출처(csdigidex.github.io)를 밝혀 주세요. 마지막 업데이트 {TODAY}.</footer>\n</main>{SCRIPT}</body></html>'
    open(f,'w',encoding='utf-8').write(out); cnt+=1
print('pages',cnt,'images',len(seen))
