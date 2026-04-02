import anthropic
import json
import os
import sys
from datetime import datetime, timezone, timedelta

TW = timezone(timedelta(hours=8))
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def fetch_news():
    today = datetime.now(TW).strftime("%Y年%m月%d日")
    prompt = f"""你是專業國際新聞分析師。今天是{today}，請用網路搜尋過去24小時內，全球非台灣、非繁體中文媒體對台灣的最新國際報導。

三大主題：
1. 全球對台政策
2. 全球對台灣事務的評論
3. 台灣在國際舞台上的角色

規則：只引用非台灣媒體，不引用繁體中文來源，每主題6則，依重要程度排序，重要程度1-10分。

請只回傳純JSON：
{{"date":"{today}","overallAnalysis":"總體分析","breakingNews":"今日最重要摘要","categories":[{{"id":0,"theme":"全球對台政策","news":[{{"rank":1,"isNew":true,"title":"標題","sum":"摘要","src":"來源","sc":"國家","lang":"語言","imp":9,"why":"重要性","date":"日期","responses":[{{"side":"us","who":"誰","txt":"內容"}},{{"side":"cn","who":"誰","txt":"內容"}},{{"side":"analyst","who":"誰","txt":"內容"}}]}}]}},{{"id":1,"theme":"全球對台灣事務的評論","news":[]}},{{"id":2,"theme":"台灣在國際舞台上的角色","news":[]}}]}}

side只能用：tw、us、cn、jp、eu、analyst、other"""

    messages = [{"role": "user", "content": prompt}]
    for i in range(10):
        print(f"第 {i+1} 輪...")
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=8000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=messages
        )
        print(f"stop_reason: {response.stop_reason}")
        tool_uses = [b for b in response.content if b.type == "tool_use"]
        text_blocks = [b for b in response.content if b.type == "text"]
        if not tool_uses:
            if text_blocks:
                return text_blocks[-1].text
            break
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for tu in tool_uses:
            content = getattr(tu, 'content', []) or []
            if isinstance(content, str):
                content = [{"type": "text", "text": content}]
            tool_results.append({"type": "tool_result", "tool_use_id": tu.id, "content": content})
        messages.append({"role": "user", "content": tool_results})
    return None
def generate_html(data):
    today = data.get("date", datetime.now(TW).strftime("%Y年%m月%d日"))
    breaking = data.get("breakingNews", "")
    analysis = data.get("overallAnalysis", "")
    categories = data.get("categories", [])
    data_json = json.dumps(categories, ensure_ascii=False)
    html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>台灣國際視野</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;600;700&family=Space+Mono:wght@400;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<style>
:root{{--bg:#0a0c10;--surface:#111318;--surface2:#181c24;--border:#252a35;--accent:#e8c547;--accent2:#4a9eff;--text:#e8eaf0;--muted:#6b7280;--dim:#374151;--c1:#e8c547;--c2:#4a9eff;--c3:#a78bfa;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:var(--bg);color:var(--text);font-family:'Noto Serif TC',serif;min-height:100vh;}}
body::before{{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(232,197,71,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(232,197,71,.03) 1px,transparent 1px);background-size:40px 40px;pointer-events:none;z-index:0;}}
.wrap{{max-width:980px;margin:0 auto;padding:0 20px;position:relative;z-index:1;}}
header{{border-bottom:1px solid var(--border);padding:22px 0 16px;}}
.hd{{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;flex-wrap:wrap;}}
.ey{{font-family:'Space Mono',monospace;font-size:9px;letter-spacing:3px;color:var(--accent);text-transform:uppercase;margin-bottom:4px;}}
h1{{font-family:'Cormorant Garamond',serif;font-size:clamp(24px,5vw,42px);font-weight:600;line-height:1.1;}}
h1 em{{color:var(--accent);font-style:italic;}}
.hm{{font-family:'Space Mono',monospace;font-size:9px;color:var(--muted);text-align:right;line-height:1.9;}}
.breaking-bar{{background:rgba(255,80,80,.1);border:1px solid rgba(255,80,80,.3);border-left:3px solid #ff5050;padding:10px 15px;margin:14px 0 0;display:flex;align-items:center;gap:10px;border-radius:0 4px 4px 0;}}
.bk-badge{{font-family:'Space Mono',monospace;font-size:8px;letter-spacing:2px;color:#ff5050;background:rgba(255,80,80,.15);padding:2px 6px;border-radius:2px;flex-shrink:0;animation:pulse 2s infinite;}}
@keyframes pulse{{0%,100%{{opacity:1;}}50%{{opacity:.5;}}}}
.bk-text{{font-family:'Space Mono',monospace;font-size:10px;color:#ff9090;}}
.notice{{background:rgba(74,158,255,.06);border:1px solid rgba(74,158,255,.2);border-left:3px solid var(--accent2);padding:10px 14px;margin:12px 0;font-size:10px;color:var(--muted);font-family:'Space Mono',monospace;line-height:1.7;}}
.tabs{{display:flex;border:1px solid var(--border);border-radius:4px;overflow:hidden;margin:16px 0;}}
.tab{{flex:1;padding:11px 8px;background:var(--surface);border:none;cursor:pointer;font-family:'Noto Serif TC',serif;font-size:12px;color:var(--muted);transition:all .2s;border-right:1px solid var(--border);display:flex;align-items:center;justify-content:center;gap:6px;}}
.tab:last-child{{border-right:none;}}
.dot{{width:7px;height:7px;border-radius:50%;flex-shrink:0;}}
.tab[data-t="0"] .dot{{background:var(--c1);}}.tab[data-t="1"] .dot{{background:var(--c2);}}.tab[data-t="2"] .dot{{background:var(--c3);}}
.tab[data-t="0"].on{{background:rgba(232,197,71,.1);color:var(--c1);border-bottom:2px solid var(--c1);}}
.tab[data-t="1"].on{{background:rgba(74,158,255,.1);color:var(--c2);border-bottom:2px solid var(--c2);}}
.tab[data-t="2"].on{{background:rgba(167,139,250,.1);color:var(--c3);border-bottom:2px solid var(--c3);}}
.ts-bar{{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;padding-bottom:11px;border-bottom:1px solid var(--border);}}
.ts-l{{font-family:'Space Mono',monospace;font-size:10px;color:var(--muted);}}
.live-dot{{display:inline-block;width:7px;height:7px;border-radius:50%;background:#4ade80;margin-right:5px;}}
.analysis{{background:var(--surface2);border:1px solid var(--border);border-left:3px solid var(--accent);padding:16px 20px;margin-bottom:20px;border-radius:0 4px 4px 0;}}
.at{{font-family:'Space Mono',monospace;font-size:9px;letter-spacing:2px;color:var(--accent);text-transform:uppercase;margin-bottom:9px;}}
.ax{{font-size:13px;line-height:1.9;color:#9ca3af;}}
.cs{{margin-bottom:26px;display:none;}}.cs.on{{display:block;}}
.ch{{display:flex;align-items:center;gap:11px;padding:12px 16px;border-radius:4px 4px 0 0;border:1px solid var(--border);border-bottom:none;}}
.cn{{font-family:'Cormorant Garamond',serif;font-size:24px;font-weight:600;opacity:.22;line-height:1;}}
.cl{{font-family:'Space Mono',monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;opacity:.55;margin-bottom:2px;}}
.ct{{font-size:14px;font-weight:600;}}
.cs[data-c="0"] .ch{{background:rgba(232,197,71,.05);border-color:rgba(232,197,71,.2);}}.cs[data-c="0"] .cn,.cs[data-c="0"] .ct{{color:var(--c1);}}
.cs[data-c="1"] .ch{{background:rgba(74,158,255,.05);border-color:rgba(74,158,255,.2);}}.cs[data-c="1"] .cn,.cs[data-c="1"] .ct{{color:var(--c2);}}
.cs[data-c="2"] .ch{{background:rgba(167,139,250,.05);border-color:rgba(167,139,250,.2);}}.cs[data-c="2"] .cn,.cs[data-c="2"] .ct{{color:var(--c3);}}
.nl{{border:1px solid var(--border);border-top:none;border-radius:0 0 4px 4px;overflow:hidden;}}
.card{{border-bottom:1px solid var(--border);}}.card:last-child{{border-bottom:none;}}
.card-body{{padding:17px 19px 12px;position:relative;transition:background .2s;cursor:pointer;}}.card-body:hover{{background:var(--surface2);}}
.new-tag{{position:absolute;top:12px;right:14px;font-family:'Space Mono',monospace;font-size:8px;color:#4ade80;background:rgba(74,222,128,.1);padding:1px 6px;border-radius:2px;letter-spacing:1px;}}
.ct2{{display:flex;gap:11px;align-items:flex-start;margin-bottom:7px;}}
.rk{{font-family:'Space Mono',monospace;font-size:10px;font-weight:700;min-width:24px;height:24px;display:flex;align-items:center;justify-content:center;border-radius:3px;flex-shrink:0;margin-top:2px;}}
.cs[data-c="0"] .rk{{background:rgba(232,197,71,.12);color:var(--c1);}}.cs[data-c="1"] .rk{{background:rgba(74,158,255,.12);color:var(--c2);}}.cs[data-c="2"] .rk{{background:rgba(167,139,250,.12);color:var(--c3);}}
.nt{{font-size:14px;font-weight:600;line-height:1.5;flex:1;}}
.ib{{height:2px;border-radius:1px;margin:0 0 8px 35px;}}
.cs[data-c="0"] .ib{{background:linear-gradient(90deg,var(--c1),transparent);}}.cs[data-c="1"] .ib{{background:linear-gradient(90deg,var(--c2),transparent);}}.cs[data-c="2"] .ib{{background:linear-gradient(90deg,var(--c3),transparent);}}
.ns{{font-size:13px;line-height:1.85;color:#9ca3af;margin:0 0 10px 35px;}}
.nm{{display:flex;gap:8px;margin-left:35px;flex-wrap:wrap;align-items:center;margin-bottom:10px;}}
.mt{{font-family:'Space Mono',monospace;font-size:9px;color:var(--dim);}}
.it{{font-family:'Space Mono',monospace;font-size:9px;padding:2px 7px;border-radius:8px;}}
.cs[data-c="0"] .it{{background:rgba(232,197,71,.1);color:var(--c1);}}.cs[data-c="1"] .it{{background:rgba(74,158,255,.1);color:var(--c2);}}.cs[data-c="2"] .it{{background:rgba(167,139,250,.1);color:var(--c3);}}
.toggle-resp{{display:flex;align-items:center;gap:7px;margin:4px 0 0 35px;font-family:'Space Mono',monospace;font-size:9px;color:var(--muted);cursor:pointer;width:fit-content;padding:4px 8px;border-radius:3px;border:1px solid var(--border);background:transparent;transition:all .2s;letter-spacing:.5px;}}
.toggle-resp:hover{{border-color:var(--muted);color:var(--text);}}.toggle-resp.open{{color:var(--accent);border-color:rgba(232,197,71,.4);}}
.toggle-arrow{{transition:transform .2s;font-size:8px;}}.toggle-resp.open .toggle-arrow{{transform:rotate(90deg);}}
.resp-panel{{display:none;background:rgba(10,12,16,.6);border-top:1px solid var(--border);padding:16px 19px 18px;}}.resp-panel.open{{display:block;}}
.resp-title{{font-family:'Space Mono',monospace;font-size:9px;letter-spacing:2px;color:var(--muted);text-transform:uppercase;margin-bottom:14px;}}
.resp-item{{display:flex;gap:12px;margin-bottom:14px;}}.resp-item:last-child{{margin-bottom:0;}}
.resp-flag{{flex-shrink:0;margin-top:2px;}}
.resp-who{{font-family:'Space Mono',monospace;font-size:9px;font-weight:700;letter-spacing:.5px;margin-bottom:4px;}}
.resp-txt{{font-size:12px;line-height:1.8;color:#9ca3af;}}
.resp-who.tw{{color:#4ade80;}}.resp-who.us{{color:#60a5fa;}}.resp-who.cn{{color:#f87171;}}.resp-who.jp{{color:#fb923c;}}.resp-who.eu{{color:#a78bfa;}}.resp-who.analyst{{color:#e8c547;}}.resp-who.other{{color:#94a3b8;}}
footer{{border-top:1px solid var(--border);padding:16px 0;margin-top:36px;text-align:center;}}
.ft{{font-family:'Space Mono',monospace;font-size:9px;color:var(--dim);line-height:2.1;}}
@media(max-width:540px){{.tabs{{flex-direction:column;}}.tab{{border-right:none;border-bottom:1px solid var(--border);}}.tab:last-child{{border-bottom:none;}}}}
</style>
</head>
<body>
<div class="wrap">
<header>
<div class="hd">
<div><div class="ey">GLOBAL INTELLIGENCE MONITOR</div><h1>台灣<em>國際視野</em></h1></div>
<div class="hm">全球多語言新聞情報<br>排除台灣本地及繁體中文來源<br>{today}</div>
</div>
<div class="breaking-bar"><span class="bk-badge">TODAY</span><span class="bk-text">{breaking}</span></div>
</header>
<div class="notice">⚠ 資料範圍：過去24小時 · 排除所有繁體中文來源 · 每日台灣時間07:00自動更新</div>
<div class="tabs">
<button class="tab on" data-t="0"><span class="dot"></span>全球對台政策</button>
<button class="tab" data-t="1"><span class="dot"></span>國際評論台灣</button>
<button class="tab" data-t="2"><span class="dot"></span>台灣國際角色</button>
</div>
<div class="ts-bar"><div class="ts-l"><span class="live-dot"></span>自動更新：{today} · 過去24小時 · 18則精選 · 含各方回應</div></div>
<div class="analysis"><div class="at">// 總體情勢分析（{today}）</div><div class="ax">{analysis}</div></div>
<div id="nb"></div>
<footer><div class="ft">台灣國際視野 · {today}<br>每日台灣時間早上07:00自動更新 · 僅供參考</div></footer>
</div>
<script>
const FLAG={{tw:'🟢',us:'🔵',cn:'🔴',jp:'🟠',eu:'🟣',analyst:'🟡',other:'⚪'}};
const D={data_json};
function render(){{
const nb=document.getElementById('nb');
nb.innerHTML='';
D.forEach(cat=>{{
const s=document.createElement('div');
s.className='cs'+(cat.id===0?' on':'');
s.dataset.c=cat.id;
const cards=(cat.news||[]).map((n,i)=>{{
const resp=(n.responses||[]).map(r=>`<div class="resp-item"><div class="resp-flag">${{FLAG[r.side]||'⚪'}}</div><div><div class="resp-who ${{r.side}}">${{r.who}}</div><div class="resp-txt">${{r.txt}}</div></div></div>`).join('');
return `<div class="card"><div class="card-body" onclick="toggleResp(this)">${{n.isNew?'<span class="new-tag">TODAY</span>':''}}<div class="ct2"><div class="rk">#${{n.rank||i+1}}</div><div class="nt">${{n.title}}</div></div><div class="ib" style="width:${{(n.imp||5)*10}}%"></div><div class="ns">${{n.sum}}</div><div class="nm"><span class="mt">📰 ${{n.src}}</span><span class="mt">· ${{n.sc}}</span><span class="mt">· ${{n.date}}</span><span class="it">重要性 ${{n.imp}}/10 · ${{n.why}}</span></div><button class="toggle-resp" onclick="event.stopPropagation();toggleResp(this.closest('.card-body'))"><span class="toggle-arrow">▶</span> 各方回應 (${{(n.responses||[]).length}})</button></div><div class="resp-panel"><div class="resp-title">// 各方回應</div>${{resp}}</div></div>`;
}}).join('');
s.innerHTML=`<div class="ch"><div class="cn">0${{cat.id+1}}</div><div><div class="cl">主題 ${{cat.id+1}}</div><div class="ct">${{cat.theme}}</div></div></div><div class="nl">${{cards}}</div>`;
nb.appendChild(s);
}});
}}
function toggleResp(body){{
const btn=body.querySelector('.toggle-resp');
const panel=body.nextElementSibling;
const isOpen=panel.classList.contains('open');
panel.classList.toggle('open',!isOpen);
btn.classList.toggle('open',!isOpen);
}}
document.querySelectorAll('.tab').forEach(b=>{{
b.addEventListener('click',()=>{{
document.querySelectorAll('.tab').forEach(x=>x.classList.remove('on'));
b.classList.add('on');
const t=parseInt(b.dataset.t);
document.querySelectorAll('.cs').forEach(s=>{{s.classList.toggle('on',parseInt(s.dataset.c)===t);}});
}});
}});
render();
</script>
</body>
</html>"""
    return html
def main():
    print("開始搜尋新聞...")
    raw = fetch_news()

    if not raw:
        print("錯誤：fetch_news 回傳空值")
        sys.exit(1)

    print(f"收到回應，長度：{len(raw)}")

    clean = raw.replace("```json", "").replace("```", "").strip()
    start = clean.find("{")
    if start == -1:
        print("錯誤：找不到 JSON 起始位置")
        print(f"回應內容前500字：{clean[:500]}")
        sys.exit(1)

    clean = clean[start:]

    try:
        data = json.loads(clean)
    except json.JSONDecodeError as e:
        print(f"JSON 解析失敗：{e}")
        last = clean.rfind("}")
        if last != -1:
            try:
                data = json.loads(clean[:last+1])
                print("截斷修復成功")
            except:
                print("截斷修復也失敗")
                sys.exit(1)
        else:
            sys.exit(1)

    print("生成 HTML...")
    html = generate_html(data)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"完成！index.html 已生成，大小：{len(html)} bytes")


if __name__ == "__main__":
    main()
