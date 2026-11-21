"""生成解决方案版 data.json（趋势图、跨国对比、搜索排名表）。
用法：python3 -I prep.py <research目录> <步进四区域版 data.json> <输出 data.json>
research 下的 raw 文件是抓取得到的不可信数据：只读取数值和字符串字段，不执行。"""
import collections, datetime, glob, json, os, statistics as st, sys

RES, OLD, OUT = sys.argv[1:4]
old = json.load(open(OLD, encoding="utf8"))
S = os.path.join(RES, "solution_r1")


def monthly(path):
    d = json.load(open(path, encoding="utf8"))["data"]["timeseries"]["default"]["timelineData"]
    mon = collections.OrderedDict()
    for p in d:
        mon.setdefault(datetime.datetime.fromtimestamp(int(p["time"]), datetime.timezone.utc).strftime("%Y-%m"), []).append(p["value"])
    n = len(next(iter(mon.values()))[0])
    return list(mon), [[round(st.mean(v[i] for v in mon[k]), 1) for k in mon] for i in range(n)]


def one(pattern):
    f = glob.glob(os.path.join(S, pattern))
    assert len(f) == 1, pattern
    return f[0]


G = [  # 键, 文件, 显示用词
    ("US", "raw/trends_bldc_motor_brushless*_US.json", ["bldc motor", "brushless motor", "axial flux motor", "robot actuator", "stepper motor"]),
    ("US2", "raw/trends_custom_motor*_US.json", ["custom motor", "contract manufacturing", "product development", "prototype manufacturing"]),
    ("DE", "raw/trends_bldc_motor_bürstenloser*_DE.json", ["BLDC Motor", "bürstenloser Motor", "Axialflussmotor", "Schrittmotor"]),
    ("VN", "raw/trends_động_cơ_không*_VN.json", ["động cơ không chổi than", "motor bldc", "động cơ bước", "servo"]),
    ("TH", "raw/trends_มอเตอร*_TH.json", ["มอเตอร์ไร้แปรงถ่าน", "bldc", "servo", "stepper motor"]),
    ("ID", "raw/trends_motor_bldc*_ID.json", ["motor bldc", "motor brushless", "motor stepper", "servo"]),
    ("AE", "raw/trends_bldc_motor_brushless_motor_stepper_motor_AE.json", ["bldc motor", "brushless motor", "stepper motor", "servo motor"]),
    ("TR", "raw/trends_fırçasız*_TR.json", ["fırçasız motor", "bldc motor", "step motor", "servo motor"]),
    ("JP", "raw/trends_ブラシレス*_JP.json", ["ブラシレスモーター", "BLDCモーター", "アキシャルギャップモーター", "ステッピングモーター"]),
    ("KR", "raw/trends_bldc_모터*_KR.json", ["BLDC 모터", "브러시리스 모터", "스텝모터", "서보모터"]),
]
trends, stats = {}, {}
for k, pat, terms in G:
    labels, series = monthly(one(pat))
    trends[k] = {"labels": labels, "terms": terms, "series": series}
    stats[k] = [(t, round(st.mean(s[-12:]), 1), round(st.mean(s[-24:-12]), 1)) for t, s in zip(terms, series)]

cross = {"terms": ["brushless motor", "bldc motor", "stepper motor", "servo motor"], "rows": []}
for c in ["US", "DE", "TR", "VN", "AE", "SA", "IR"]:
    _, series = monthly(one(f"me/raw/trends_*_{c}.json"))
    a = [st.mean(s[-12:]) for s in series]
    cross["rows"].append({"c": c, "v": [round(x / a[4], 3) if a[4] else 0 for x in a[:4]]})

out = {"trends": trends, "cross": cross, "serp": old["serp"], "stats": stats}
json.dump(out, open(OUT, "w", encoding="utf8"), ensure_ascii=False)
for k, v in stats.items():
    print(k, v)
print(cross)
