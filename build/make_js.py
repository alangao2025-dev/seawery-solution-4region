"""把步进版的 tpl_6_js 改成解决方案版。
用法：python3 -I make_js.py <步进版 tpl_6> <模型 js> <配置 json> <输出 tpl_6>
配置：{"cover":2000000,"skip":["JP","KR"],"tkeys":["US",...],"use":{区域:用途},"showdesc":[高档描述,低档描述,未启用描述,高档门槛]}"""
import json, os, re, sys

SRC, MODEL, CFG, OUT = sys.argv[1:5]
here = os.path.dirname(os.path.abspath(__file__))
s = open(SRC, encoding="utf8").read()
cfg = json.load(open(CFG, encoding="utf8"))
model = open(MODEL, encoding="utf8").read()
comp = open(os.path.join(here, "js_compute.js"), encoding="utf8").read()
cross = open(os.path.join(here, "js_cross.js"), encoding="utf8").read()


def cut_between(a, b, new, incl_b=False):
    global s
    i = s.index(a)
    j = s.index(b, i) + (len(b) if incl_b else 0)
    s = s[:i] + new + s[j:]


def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:60], s.count(a))
    s = s.replace(a, b)


head = model + f'const COVER = {cfg["cover"]}, SKIPC = {json.dumps(cfg["skip"])}, TKEYS = {json.dumps(cfg["tkeys"])};\n'
cut_between("const DEFAULT_TOTAL", "let S = {", head)
cut_between("function compute(){", "function showDesc", comp)
hi, lo, off, thr = cfg["showdesc"]
cut_between("function showDesc(a){", "\n\nfunction render", f'function showDesc(a){{ return a>={thr} ? {json.dumps(hi, ensure_ascii=False)} : (a>0 ? {json.dumps(lo, ensure_ascii=False)} : {json.dumps(off, ensure_ascii=False)}); }}')
rep('set("p:winRate",pct(S.p.winRate)); set("p:cplG","$"+S.p.cplG); set("p:aov",usd(S.p.aov));',
    'set("p:winRate",pct(S.p.winRate)); set("p:devFee",usd(S.p.devFee)); set("p:volRate",pct(S.p.volRate)); set("p:batch",usd(S.p.batch));\n  set("kpi:devrev",cny(k.devrev)); set("kpi:batchrev",cny(k.batchrev)); set("kpi:partrev",cny(k.partrev));')
i = s.index("  const use={"); j = s.index("};", i) + 2
s = s[:i] + "  const use=" + json.dumps(cfg["use"], ensure_ascii=False) + ";" + s[j:]
cut_between("const TRN={", "let trCur", cross)
rep('let trCur="US";', 'let trCur=TKEYS[0];')
rep("Object.keys(CHART.trends).forEach(k=>{", "TKEYS.filter(k=>CHART.trends[k]).forEach(k=>{")
cut_between("function drawTrade(){", "function drawRegion(reg){", "")
rep("buildParams(); render(); drawTrends(); drawTrade(); drawPrice(); filterSrc();", "buildParams(); render(); drawTrends(); drawCross(); filterSrc();")
rep('n.textContent="询盘 = Σ 各科目金额 ÷ 对应 CPL + 官网内容金额 ÷ 内容 CPL + 外联与自然询盘；机动金按 Google 和 Meta 的平均 CPL 计算。";',
    'n.textContent="询盘 = Σ 各付费科目金额 ÷ 对应 CPL +（官网 + 案例 + 评估套件）÷ 自然询盘成本 + 外联与自然询盘；机动金按搜索和 Meta 的平均 CPL 计算。收入 = 签约项目 × 开发费 + 签约项目 × 批量比例 × 首年批量额 + 询盘 × 部件比例 × 部件订单额。";')
left = [w for w in ("cplG", "aov", "drawPrice", "drawTrade", "amt.google", "amt.amazon") if w in s]
assert not left, left
open(OUT, "w", encoding="utf8").write(s)
print("ok", len(s))
