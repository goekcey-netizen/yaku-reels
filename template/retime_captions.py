"""Richtet die Untertitel-Sinnabschnitte (CAPS in index.html) an der echten Sprecherspur aus."""
import json, re, sys, os, numpy as np, soundfile as sf
os.chdir(sys.argv[1] if len(sys.argv) > 1 else ".")
SR = 48000
T = json.load(open("out/voice_timing.json"))
x, _ = sf.read("out/tmp/voice_raw.wav")
w = int(.02 * SR)
env = np.sqrt(np.convolve(x ** 2, np.ones(w) / w, "same"))
quiet = env < 10 ** (-40 / 20)
GROUPS = {c["take"]: c.get("captions", []) for c in json.load(open("cues.json"))["takes"]}
html = open("index.html").read()
block = re.search(r"const CAPS = \[\n(.*?)\n\];", html, re.S)
lines = block.group(1).split("\n")
caps = [re.match(r'\s*\[([\d.]+), ([\d.]+), (".*")\],?', l).groups() for l in lines]
texts = [c[2] for c in caps]
new = [None] * len(caps)

def snap(t, a, b):
    """nächste Sprechpause (Mitte) im Bereich ±0.45 s"""
    lo, hi = int(max(a, t - .45) * SR), int(min(b, t + .45) * SR)
    best, bd = t, 9
    i = lo
    while i < hi:
        if quiet[i]:
            j = i
            while j < hi and quiet[j]:
                j += 1
            if (j - i) / SR > .09:
                m = (i + j) / 2 / SR
                if abs(m - t) < bd:
                    best, bd = m, abs(m - t)
            i = j
        i += 1
    return best

for t in T:
    g = GROUPS.get(t["take"])
    if not g:
        continue
    s, e = t["start"], t["end"]
    lens = [len(re.sub(r"[*\"]", "", texts[i])) for i in g]
    tot = sum(lens)
    b = [s]
    acc = 0
    for L in lens[:-1]:
        acc += L
        b.append(snap(s + (e - s) * acc / tot, s, e))
    b.append(e)
    prop = [s] + [s + (e - s) * sum(lens[:k + 1]) / tot for k in range(len(lens) - 1)] + [e]
    if min(b[k + 1] - b[k] for k in range(len(b) - 1)) < .75:
        b = prop
    for k, i in enumerate(g):
        a0 = b[k] - (.12 if k == 0 else 0)
        a1 = b[k + 1] + (.35 if k == len(g) - 1 else 0)
        new[i] = (round(a0, 2), round(a1, 2))
for i in range(len(new) - 1):
    if new[i] and new[i + 1] and new[i][1] > new[i + 1][0]:
        new[i] = (new[i][0], new[i + 1][0])
out = []
for i, (a, b2, txt) in enumerate(caps):
    na, nb = new[i] if new[i] else (float(a), float(b2))
    out.append(f"  [{na}, {nb}, {txt}]")
html = html[:block.start(1)] + ",\n".join(out) + html[block.end(1):]
open("index.html", "w").write(html)
print("\n".join(out))
