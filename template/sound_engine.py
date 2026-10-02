"""YAKÜ Reels – Sound-Engine: Musik & Sounddesign komplett synthetisiert (lizenzfrei), gesteuert über sound.json.
Aufruf: python3 sound_engine.py sound.json
"""
import numpy as np
from scipy.signal import butter, sosfilt
import soundfile as sf
import os

SR = 48000
DUR = 60.0
N = int(SR * DUR)
rng = np.random.default_rng(42)
OUT = os.path.dirname(os.path.abspath(__file__))


def t_(d):
    return np.arange(int(SR * d)) / SR


def lp(x, f, o=2):
    return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, o=2):
    return sosfilt(butter(o, [lo, hi], "band", fs=SR, output="sos"), x)


def place(buf, sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= buf.shape[0]:
        return
    sig = np.array(sig[: buf.shape[0] - i], dtype=float)
    k = min(len(sig) // 4, int(.006 * SR))
    if k > 1:
        sig[-k:] *= np.linspace(1, 0, k)
        sig[: k // 6 + 1] *= np.linspace(0, 1, k // 6 + 1)
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    buf[i : i + len(sig), 0] += sig * gain * l * 1.414
    buf[i : i + len(sig), 1] += sig * gain * r * 1.414


def env(n, a, d, curve=4.0):
    a_n = max(1, int(a * SR))
    e = np.ones(n)
    e[:a_n] = np.linspace(0, 1, a_n)
    rest = n - a_n
    if rest > 0:
        e[a_n:] = np.exp(-curve * np.arange(rest) / (d * SR))
    return e


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# =====================================================================
# MUSIC  — D-Dur, 100 BPM, Mallet/Pluck + warmes Pad + weicher Bass
# =====================================================================
BPM = 100
BEAT = 60 / BPM
BAR = 4 * BEAT
music = np.zeros((N, 2))



def mallet(freq, dur=1.1, bright=1.0):
    t = t_(dur)
    s = np.sin(2 * np.pi * freq * t) * env(len(t), .004, dur * .55, 4)
    s += .35 * bright * np.sin(2 * np.pi * freq * 4.0 * t) * env(len(t), .002, .09, 4)
    s += .18 * np.sin(2 * np.pi * freq * 2.0 * t) * env(len(t), .003, .3, 4)
    return s * .5


def pad(freqs, dur, att=.6, rel=.8):
    t = t_(dur)
    s = np.zeros(len(t))
    for f in freqs:
        for det in (-0.12, 0.0, 0.13):
            ph = rng.uniform(0, 1)
            saw = 2 * ((f * (1 + det / 100) * t + ph) % 1) - 1
            s += saw
    s = lp(s, 1400, 2) / (len(freqs) * 3)
    e = np.ones(len(t))
    a = int(att * SR)
    r = int(rel * SR)
    e[:a] = np.linspace(0, 1, a)
    e[-r:] *= np.linspace(1, 0, r)
    return s * e


def bass(freq, dur):
    t = t_(dur)
    s = np.sin(2 * np.pi * freq * t) + .25 * np.sin(2 * np.pi * freq * 2 * t)
    s = np.tanh(1.4 * s) * env(len(t), .01, dur * .9, 2.2)
    return s * .55


def kick():
    t = t_(.35)
    f = 50 + 70 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(len(t), .002, .3, 5) * .9


def snap():
    t = t_(.18)
    n = bp(rng.standard_normal(len(t)), 1200, 5000)
    return n * env(len(t), .001, .1, 6) * .35


def hat(open_=False):
    d = .12 if open_ else .05
    t = t_(d)
    n = hp(rng.standard_normal(len(t)), 7000)
    return n * env(len(t), .001, d, 5) * .18


# chords (MIDI) per bar
D, Bm, G, A, Em, F_ = [62, 66, 69], [59, 62, 66], [55, 59, 62], [57, 61, 64], [52, 55, 59], [54, 57, 61]
PROG_A = [D, Bm, G, A]
PROG_B = [Bm, G, D, A]  # scene 5: nachdenklicher
roots = {tuple(D): 38, tuple(Bm): 35, tuple(G): 31, tuple(A): 33}

# section map (seconds)
def bars_between(t0, t1):
    out = []
    t = t0
    while t < t1 - 1e-6:
        out.append(t)
        t += BAR
    return out

def noise(d):
    return rng.standard_normal(int(SR * d))


def sweep_noise(d, centers):
    """Rauschen, dessen Bandmitte zeitlich gleitet (Crossfade über feste Bänder, keine Klicks)."""
    n = len(t_(d))
    src = noise(d)
    bands = np.geomspace(150, 9000, 12)
    outs = [bp(src, b * .7, min(20000, b * 1.4), 2) for b in bands]
    lc = np.log(np.clip(centers, 150, 9000))
    lb = np.log(bands)
    out = np.zeros(n)
    for i, o in enumerate(outs):
        w = np.exp(-((lc - lb[i]) ** 2) / (2 * .35 ** 2))
        out += o * w
    return out


def whoosh(d=.45, lo=300, hi=4000, up=True):
    n = len(t_(d))
    p = np.linspace(0, 1, n)
    p = p if up else 1 - p
    c = lo * (hi / lo) ** p if hi > lo else hi * (lo / hi) ** p
    if not up:
        c = c[::-1] if hi > lo else c
    out = sweep_noise(d, np.geomspace(lo, hi, n))
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.6
    return out * e * .5


def pop(f=900, d=.12):
    t = t_(d)
    fr = f * (1.6 - .6 * np.exp(-t * 40))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * env(len(t), .002, d * .5, 5) * .5


def tick(f=2400, d=.03):
    t = t_(d)
    return np.sin(2 * np.pi * f * t) * env(len(t), .0005, d, 6) * .4


def step(soft=1.0):
    t = t_(.09)
    n = lp(noise(.09), 900) * env(len(t), .002, .07, 5)
    th = np.sin(2 * np.pi * 90 * t) * env(len(t), .001, .05, 5) * .5
    return (n * .9 + th) * .5 * soft


def ding(f=1320, d=.6):
    t = t_(d)
    s = np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 12)
    return s * env(len(t), .002, d * .6, 4) * .35


def shutter(big=True):
    t = t_(.16)
    c1 = hp(noise(.02), 2000) * env(int(.02 * SR), .0005, .015, 5)
    c2 = bp(noise(.04), 1500, 7000) * env(int(.04 * SR), .0005, .03, 5)
    out = np.zeros(len(t))
    out[: len(c1)] += c1
    o = int(.07 * SR)
    out[o : o + len(c2)] += c2 * .9
    if big:
        wt = t_(.35)
        whine = np.sin(2 * np.pi * np.cumsum(3000 + 3000 * wt / .35) / SR) * env(len(wt), .02, .3, 3) * .05
        out2 = np.zeros(len(wt))
        out2[: len(out)] += out
        return (out2 + whine) * .8
    return out * .6


def paper(d=.25):
    t = t_(d)
    n = bp(noise(d), 1500, 8000)
    crackle = (rng.random(len(t)) > .995) * rng.standard_normal(len(t)) * 2
    return (n * .5 + hp(crackle, 2000)) * np.sin(np.pi * np.linspace(0, 1, len(t))) * .4


def marker(d=.5):
    t = t_(d)
    n = bp(noise(d), 2500, 6000)
    am = .6 + .4 * np.sin(2 * np.pi * 23 * t)
    e = np.minimum(1, t / .03) * np.minimum(1, (d - t) / .05)
    return n * am * e * .22


def impact():
    t = t_(.9)
    f = 45 + 80 * np.exp(-t * 18)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), .001, .5, 4)
    crunch = bp(noise(.25), 400, 3500) * env(int(.25 * SR), .001, .15, 5)
    crack = hp(noise(.05), 3000) * env(int(.05 * SR), .0005, .03, 6)
    out = boom * .9
    out[: len(crunch)] += crunch * .7
    out[: len(crack)] += crack * .5
    return np.tanh(out * 1.3) * .8


def glass():
    out = np.zeros(int(.8 * SR))
    for k in range(7):
        f = rng.uniform(2800, 6500)
        d = rng.uniform(.15, .35)
        tt = t_(d)
        s = np.sin(2 * np.pi * f * tt) * env(len(tt), .001, d, 6) * rng.uniform(.08, .16)
        o = int(rng.uniform(.02, .45) * SR)
        out[o : o + len(s)] += s
    return out


def thunk():
    t = t_(.3)
    s = np.sin(2 * np.pi * np.cumsum(70 + 60 * np.exp(-t * 30)) / SR) * env(len(t), .001, .2, 5)
    s[: int(.03 * SR)] += lp(noise(.03), 1500) * .5
    return s * .7


def engine(d=1.0):
    t = t_(d)
    f = 70 - 25 * (t / d)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) + .5 * np.sin(2 * np.pi * np.cumsum(f * 2) / SR)
    s = lp(np.tanh(s * 1.5), 600)
    road = lp(noise(d), 1200) * .4
    e = np.minimum(1, t / .05) * np.exp(-2.2 * t / d)
    return (s * .5 + road) * e * .5


def squeak(d=.35):
    t = t_(d)
    f = 1900 - 400 * t / d
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 + .3 * np.sin(2 * np.pi * 37 * t))
    return s * env(len(t), .02, d, 3) * .06


def brandhit():
    t = t_(3.0)
    f = 40 + 30 * np.exp(-t * 6)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), .002, 1.6, 4) * .8
    shimmer = np.zeros(len(t))
    for fr in [1175, 1480, 1760, 2350]:
        shimmer += np.sin(2 * np.pi * fr * t) * env(len(t), .01, 1.8, 3) * .06
    rev = hp(noise(3.0), 3000) * env(len(t), .01, 1.0, 4) * .05
    return boom + shimmer + rev


def scan_sweep(d=1.6):
    t = t_(d)
    c = 1200 + 5000 * (1 - np.abs(2 * np.linspace(0, 1, len(t)) - 1))
    out = sweep_noise(d, c)
    tone = np.sin(2 * np.pi * 880 * t) * .15 + np.sin(2 * np.pi * 1320 * t) * .08
    e = np.sin(np.pi * np.linspace(0, 1, len(t)))
    return (out * .35 + tone) * e * .35



# =====================================================================
# DRIVER – liest sound.json (Zeitplan des jeweiligen Videos)
# =====================================================================
import json, sys
CFG = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUT, "sound.json")))
DUR = float(CFG.get("duration", 60.0)); N = int(SR * DUR)
rng = np.random.default_rng(int(CFG.get("seed", 42)))
TR = int(CFG.get("transpose", 0))                      # Tonart-Variation pro Video (Halbtöne, -3..+3)
BPM = float(CFG.get("bpm", 100)); BEAT = 60 / BPM; BAR = 4 * BEAT
music = np.zeros((N, 2)); sfx = np.zeros((N, 2))
D, Bm, G, A = [62, 66, 69], [59, 62, 66], [55, 59, 62], [57, 61, 64]
ROOTS = {tuple(D): 38, tuple(Bm): 35, tuple(G): 31, tuple(A): 33}
PROG = {"A": [D, Bm, G, A], "B": [Bm, G, D, A], "C": [G, A, D, Bm]}
tp = lambda m: m + TR
def bars(t0, t1):
    out, t = [], t0
    while t < t1 - 1e-6: out.append(t); t += BAR
    return out

def sec_intro(s):
    for i, m in enumerate([74, 76, 78, 81]): place(music, mallet(mtof(tp(m)), .7), s["t"] + .05 + i * BEAT / 2, .55, -.2 + .13 * i)
    place(music, pad([mtof(tp(n)) for n in D], s.get("until", s["t"] + 1.2) - s["t"] + .3, .1, .4), s["t"], .25)
def sec_motif(s):
    for i, m in enumerate([69, 71, 73, 76]): place(music, mallet(mtof(tp(m)), .9, .7), s["t"] + i * BEAT * .5, .4, .2 - .1 * i)
    place(music, pad([mtof(tp(n)) for n in A], 3.4, 1.2, 1.0), s["t"], .22)
def sec_groove(s):
    prog = PROG[s.get("prog", "A")]; dfrom = s.get("drums_from", s["t"])
    for bi, b in enumerate(bars(s["t"], s["until"])):
        ch = prog[bi % 4]
        place(music, pad([mtof(tp(n)) for n in ch], BAR + .3, .4, .5), b, .24)
        place(music, bass(mtof(tp(ROOTS[tuple(ch)])), BEAT * 1.8), b, .5)
        place(music, bass(mtof(tp(ROOTS[tuple(ch)])), BEAT * 1.6), b + 2 * BEAT, .42)
        for k, idx in enumerate([0, None, 2, 1, None, 2, 0, 1]):
            if idx is not None: place(music, mallet(mtof(tp(ch[idx] + 12)), .6, .8), b + k * BEAT / 2, .30, (-.35, .35)[k % 2])
        for k in range(4):
            if k in (0, 2): place(music, kick(), b + k * BEAT, .55)
            if b >= dfrom and k in (1, 3): place(music, snap(), b + k * BEAT, .5)
        if b >= dfrom:
            for k in range(8): place(music, hat(k % 4 == 3), b + k * BEAT / 2, .9, .3)
def sec_tech(s):
    prog = PROG[s.get("prog", "B")]
    for bi, b in enumerate(bars(s["t"], s["until"])):
        ch = prog[bi % 4]
        place(music, pad([mtof(tp(n - 12)) for n in ch] + [mtof(tp(ch[1]))], BAR + .3, .6, .6), b, .22)
        place(music, bass(mtof(tp(ROOTS[tuple(ch)])), BEAT * 3.6), b, .45)
        arp = [ch[0], ch[1], ch[2], ch[1] + 12, ch[2], ch[1], ch[0] + 12, ch[2]]
        for k in range(16): place(music, mallet(mtof(tp(arp[k % 8] + 12)), .35, 1.2), b + k * BEAT / 4, .16, np.sin(k) * .5)
        for k in range(4):
            if k in (0, 2): place(music, kick(), b + k * BEAT, .38)
            place(music, hat(), b + k * BEAT + BEAT / 2, .8, -.3)
def sec_riser(s):
    d = s.get("dur", 1.4); rt = t_(d)
    r = bp(rng.standard_normal(len(rt)), 800, 9000) * np.linspace(0, 1, len(rt)) ** 2.2
    r += .3 * np.sin(2 * np.pi * np.cumsum(300 + 900 * (rt / d) ** 2) / SR) * np.linspace(0, 1, len(rt)) ** 2
    place(music, r * .35, s["t"], 1.0)
def sec_bright(s):
    prog = PROG[s.get("prog", "A")]
    for bi, b in enumerate(bars(s["t"], s["until"])):
        ch = prog[bi % 4]
        place(music, pad([mtof(tp(n)) for n in ch] + [mtof(tp(ch[0] + 12))], BAR + .3, .2, .5), b, .26)
        place(music, bass(mtof(tp(ROOTS[tuple(ch)])), BEAT * 1.8), b, .5)
        place(music, bass(mtof(tp(ROOTS[tuple(ch)])), BEAT * 1.6), b + 2 * BEAT, .42)
        for k in range(8): place(music, mallet(mtof(tp(ch[(k * 2) % 3] + 12 + (12 if k == 7 else 0))), .6, .9), b + k * BEAT / 2, .28, (-.4, .4)[k % 2])
        for k in range(4): place(music, kick() if k in (0, 2) else snap(), b + k * BEAT, .55 if k in (0, 2) else .45)
        for k in range(8): place(music, hat(k % 4 == 3), b + k * BEAT / 2, .9, .3)
def sec_resolve(s):
    for bi, b in enumerate(bars(s["t"], s["until"])):
        ch = [G, A][bi % 2]
        place(music, pad([mtof(tp(n)) for n in ch], BAR + .4, .3, .6), b, .26)
        place(music, bass(mtof(tp(ROOTS[tuple(ch)])), BEAT * 3.5), b, .45)
        for k in range(4):
            place(music, mallet(mtof(tp(ch[k % 3] + 12)), .8, .7), b + k * BEAT, .3, (-.3, .3)[k % 2])
            if k % 2 == 0: place(music, kick(), b + k * BEAT, .3)
def sec_brand(s):
    t = s["t"]
    place(music, pad([mtof(tp(n)) for n in [50, 57, 62, 66, 69]], DUR - t + .2, .05, 2.2), t, .34)
    place(music, bass(mtof(tp(38)), 3.5), t, .6)
    for i, m in enumerate([74, 78, 81, 86]): place(music, mallet(mtof(tp(m)), 1.6, .9), t + i * .09, .32, -.3 + .2 * i)
    if "cta" in s:
        for i, m in enumerate([81, 86]): place(music, mallet(mtof(tp(m)), 1.4, .6), s["cta"] + i * .12, .22)
SECTIONS = dict(intro=sec_intro, motif=sec_motif, groove=sec_groove, tech=sec_tech, riser=sec_riser, bright=sec_bright, resolve=sec_resolve, brand=sec_brand)
for s in CFG["music"]: SECTIONS[s["type"]](s)
fade = np.ones(N); fs_ = int(1.2 * SR); fade[-fs_:] = np.linspace(1, 0, fs_) ** 1.5
music *= fade[:, None]
dl = int(.012 * SR); music[dl:, 1] = .85 * music[dl:, 1] + .15 * music[:-dl, 0]

# ---- SFX-Katalog (Name → Generator)
def orbit_tone(d=3.6):
    t = t_(d); e = np.sin(np.pi * t / d)
    return np.sin(2 * np.pi * 523 * t) * .03 * e + np.sin(2 * np.pi * 784 * t) * .02 * e
def blip_up(d=.5):
    t = t_(d); return np.sin(2 * np.pi * np.cumsum(500 + 700 * t / d) / SR) * env(len(t), .02, d, 3) * .08
def drone(d=2.0):
    t = t_(d); return (lp(noise(d), 300) * .2 + np.sin(2 * np.pi * 55 * t) * .15) * np.sin(np.pi * t / d)
def exhale(d=.5):
    return lp(noise(d), 1200) * np.sin(np.pi * np.linspace(0, 1, int(d * SR))) * .12
SFX = {
  "impact": lambda e: impact(), "glass": lambda e: glass(), "thunk": lambda e: thunk(),
  "engine": lambda e: engine(e.get("d", 1.0)), "squeak": lambda e: squeak(e.get("d", .35)),
  "whoosh": lambda e: whoosh(e.get("d", .45), e.get("lo", 300), e.get("hi", 3000), e.get("up", True)),
  "pop": lambda e: pop(e.get("f", 900), e.get("d", .12)), "tick": lambda e: tick(e.get("f", 2000), e.get("d", .04)),
  "step": lambda e: step(e.get("soft", 1.0)), "ding": lambda e: ding(e.get("f", 1568), e.get("d", .5)),
  "shutter": lambda e: shutter(e.get("big", True)), "paper": lambda e: paper(e.get("d", .3)),
  "marker": lambda e: marker(e.get("d", .5)), "brandhit": lambda e: brandhit(), "scan": lambda e: scan_sweep(e.get("d", 1.6)),
  "orbit": lambda e: orbit_tone(e.get("d", 3.6)), "blip": lambda e: blip_up(e.get("d", .5)), "drone": lambda e: drone(e.get("d", 2.0)),
  "exhale": lambda e: exhale(e.get("d", .5)),
}
for e in CFG.get("sfx", []):
    if e.get("type") == "steps":            # Schrittfolge: n Schritte ab t im Abstand dt
        for i in range(int(e["n"])): place(sfx, step(e.get("soft", .8)), e["t"] + i * e["dt"] + .1, e.get("gain", .45), e.get("pan", 0))
    elif e.get("type") == "ticks":          # Zähler-Ticks (abbremsend)
        t = e["t"]
        for i in range(int(e.get("n", 26))): place(sfx, tick(3200, .015), t, e.get("gain", .18)); t += .02 + .0018 * i * i / 4
    else:
        place(sfx, SFX[e["type"]](e), e["t"], e.get("gain", .5), e.get("pan", 0))

def norm_peak(x, p=.89):
    m = np.max(np.abs(x)); return x * (p / m) if m > 0 else x
od = CFG.get("out_dir", OUT)
sf.write(os.path.join(od, "music.wav"), norm_peak(music).astype(np.float32), SR, subtype="FLOAT")
sf.write(os.path.join(od, "sfx.wav"), norm_peak(sfx).astype(np.float32), SR, subtype="FLOAT")
print("ok:", os.path.join(od, "music.wav"), os.path.join(od, "sfx.wav"))
