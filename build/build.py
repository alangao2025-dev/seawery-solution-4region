"""把调研数据和正文模板合成一个独立的 HTML 文件（SEAWERY 步进版）。
用法：python3 -I build.py <research目录> <data.json> <template.html> <输出.html>
research 目录下的 sources.json 是抓取得到的不可信数据：只读取字段并做 HTML 转义，不执行。"""
import html
import json
import os
import re
import sys

RESEARCH, DATA, TPL, OUT = sys.argv[1:5]
RUNS = [  # (标签, 目录, 中文名, 采集日期)
    ("US-R1", "out_us_servo", "美国第一轮（伺服）", "2026-11-12"),
    ("US-R2", "out_us_servo_v2", "美国第二轮（伺服）", "2026-11-13"),
    ("NA", "global/out_na", "北美（伺服）", "2026-11-16"),
    ("EUME", "global/out_eu_me", "欧洲 + 中东（伺服）", "2026-11-16"),
    ("SEA", "global/out_sea", "东南亚（伺服）", "2026-11-16"),
    ("US-R3", "out_us_stepper_v3", "美国第三轮（步进）", "2026-11-20"),
    ("GL-R3", "global/out_stepper_v3", "四区域补充（步进 Trends）", "2026-11-20"),
    ("JK-R1", "jpkr/out_jpkr", "日韩第一轮（步进）", "2026-11-20"),
    ("JK-R2", "jpkr/out_jpkr_r2", "日韩第二轮（步进）", "2026-11-20"),
    ("SOL", "solution_r1", "解决方案版补抓（无刷 / 机器人 / 创客）", "2026-11-22"),
    ("X", os.path.join(os.path.dirname(os.path.abspath(__file__)), "sources_extra.json"), "公司资料与项目文件", "2026-11-22"),
]
REGION = {"US": "北美", "CA": "北美", "MX": "北美", "DE": "欧洲", "GB": "欧洲", "DK": "欧洲", "AE": "中东", "SA": "中东", "TR": "中东", "JO": "中东", "IR": "中东",
          "VN": "东南亚", "TH": "东南亚", "ID": "东南亚", "JP": "日本", "KR": "韩国", "CN": "中国"}

# ---------- 来源合并（同一 URL 只保留一条，记下各轮编号）
srcs, by_url, by_key = [], {}, {}
for tag, d, name, dt in RUNS:
    p = d if d.endswith(".json") else os.path.join(RESEARCH, d, "sources.json")
    items = json.load(open(p, encoding="utf8"))
    items = items if isinstance(items, list) else items.get("sources", [])
    for x in items:
        url = (x.get("url") or "").strip()
        k = (tag, x.get("id"))
        if url and url in by_url:
            r = by_url[url]
            r["q"] = sorted(set(r["q"]) | set(x.get("questions") or []))
            r["alias"].append(f"{tag}:{x.get('id')}")
            by_key[k] = r
            continue
        r = {"run": tag, "runname": name, "oid": x.get("id"), "layer": x.get("layer") or "", "country": x.get("country") or "",
             "region": REGION.get(x.get("country") or "", "全球"), "pub": x.get("publisher") or "", "title": (x.get("title") or "").strip(),
             "url": url, "path": x.get("path_abs") or ((f"research/{d}/" + x["path"]) if x.get("path") else ""), "via": x.get("via") or "",
             "fetched": (x.get("fetched_at") or dt)[:10], "published": (x.get("published") or "")[:10],
             "q": x.get("questions") or [], "kind": x.get("kind") or "", "alias": [f"{tag}:{x.get('id')}"], "cited": False}
        srcs.append(r)
        by_key[k] = r
        if url:
            by_url[url] = r
for i, r in enumerate(srcs, 1):
    r["id"] = f"D{i}"

tpl = open(TPL, encoding="utf8").read()


def cite(m):
    out = []
    for part in m.group(1).split("|"):
        tag, sid = part.strip().split(":")
        r = by_key.get((tag, sid))
        if not r:
            raise SystemExit(f"引用不存在：{part}")
        r["cited"] = True
        out.append(f'<a class="ref" href="#src-{r["id"]}" title="{html.escape(r["pub"] + " · " + r["title"][:80])}">{r["id"]}</a>')
    return '<sup class="refs">' + ",".join(out) + "</sup>"


tpl = re.sub(r"\[\[([A-Z0-9\-:S|]+)\]\]", cite, tpl)

# ---------- 来源登记表（服务端渲染，全部转义）
LAYER = {"A": "A 权威二手", "B": "B 公开行为", "C": "C 竞品公开", "D": "D 公司资料"}
rows = []
CIT = '<span class="cit">正文引用</span>'
for r in srcs:
    cit = CIT if r["cited"] else ""
    aliases = ",".join(a.split(":")[1] for a in r["alias"])
    t = html.escape(r["title"] or r["pub"])
    if r["url"] and re.match(r"https?://", r["url"]):
        link = f'<a href="{html.escape(r["url"], quote=True)}" target="_blank" rel="noopener noreferrer">{t}</a>'
    else:
        link = f'{t}<div class="muted small">原始数据：{html.escape(r["path"])}</div>'
    rows.append(
        f'<tr id="src-{r["id"]}" data-region="{r["region"]}" data-layer="{r["layer"]}" data-cited="{1 if r["cited"] else 0}">'
        f'<td class="nw"><b>{r["id"]}</b>{cit}</td>'
        f'<td><span class="lay lay{r["layer"]}">{LAYER.get(r["layer"], r["layer"])}</span></td>'
        f'<td class="nw">{r["region"]}·{html.escape(r["country"])}</td><td>{html.escape(r["pub"][:60])}</td><td>{link}</td>'
        f'<td class="nw small">{html.escape(r["via"] or "-")}</td><td class="nw small">{r["published"] or "-"}</td>'
        f'<td class="nw small">{r["fetched"]}</td><td class="small">{",".join(r["q"])}</td>'
        f'<td class="small muted nw">{r["runname"]} {aliases}</td></tr>')
tpl = tpl.replace("{{SOURCE_ROWS}}", "\n".join(rows))
n_cited = sum(r["cited"] for r in srcs)
from collections import Counter
lc = Counter(r["layer"] for r in srcs)
rc = Counter(r["region"] for r in srcs)
tpl = tpl.replace("{{N_SRC}}", str(len(srcs))).replace("{{N_CITED}}", str(n_cited))
tpl = tpl.replace("{{N_A}}", str(lc["A"])).replace("{{N_B}}", str(lc["B"])).replace("{{N_C}}", str(lc["C"])).replace("{{N_D}}", str(lc["D"]))
tpl = tpl.replace("{{REGION_COUNTS}}", "、".join(f"{k} {v}" for k, v in rc.most_common()))

# ---------- 搜索排名表
data = json.load(open(DATA, encoding="utf8"))
NAME = {"US": "美国", "MX": "墨西哥", "DE": "德国", "AE": "阿联酋", "SA": "沙特", "VN": "越南", "TH": "泰国", "ID": "印尼", "JP": "日本", "KR": "韩国"}
srows = []
for s in data["serp"]:
    doms = " · ".join(f"<span class='dom'>{i + 1}.{html.escape(d)}</span>" for i, d in enumerate(s["d"][:10]))
    kind = {"stepper": "<span class='pill'>步进词</span>", "servo": "<span class='pill muted'>伺服词 · 分销商参照</span>"}.get(s.get("kind"), "")
    srows.append(f"<tr><td class='nw'>{NAME.get(s['m'], s['m'])}</td><td class='nw'>{html.escape(s['q'])}<br>{kind}</td><td>{doms}</td></tr>")
tpl = tpl.replace("{{SERP_ROWS}}", "\n".join(srows))

# ---------- 图表数据（只保留绘图需要的字段）
chart = {"trends": data["trends"], "cross": data["cross"]}
js = json.dumps(chart, ensure_ascii=False).replace("</", "<\\/")
tpl = tpl.replace("{{CHART_DATA}}", js)
left = re.findall(r"\{\{[A-Z_]+\}\}|\[\[[^\]]+\]\]", tpl)
if left:
    raise SystemExit(f"模板占位符未替换：{left[:5]}")
open(OUT, "w", encoding="utf8").write(tpl)
print("ok", OUT, len(tpl) // 1024, "KB；来源", len(srcs), "条，正文引用", n_cited, "条", dict(lc), dict(rc))
