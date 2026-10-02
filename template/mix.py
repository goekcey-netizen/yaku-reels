#!/usr/bin/env python3
"""
YAKÜ Erklärvideo – finaler Audio-Mix & Export

  python3 mix.py preview <projektordner>  → Vorschau OHNE Sprecher (mit Hinweis-Badge), NICHT zur Veröffentlichung
  python3 mix.py final <projektordner>    → finaler Spot; bricht ab, wenn keine echte Sprecherspur vorhanden ist

Sprecheraufnahmen (echte menschliche Stimme) ablegen als:
  voice/VO01.wav … voice/VO09.wav   (je ein Satz, beliebiges Format/Samplerate – wav/mp3/m4a)
  ODER voice/voiceover_full.wav     (komplette Spur, bereits auf 0:00 des Videos angelegt)

Mix-Ziele (laut Briefing):
  Stimme ≈ -14 LUFS · Musik ≈ -35 LUFS unter Sprache (zusätzlich gedeckt) · SFX deutlich unter Sprache
  Gesamt ≈ -13 LUFS integrated · True Peak ≤ -1 dBTP · AAC 320 kbit/s · H.264
"""
import json, os, subprocess, sys, glob
import numpy as np
import soundfile as sf

ROOT = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.getcwd()   # Projektordner
SR = 48000
DUR = 60.0
VIDEO = os.path.join(ROOT, "out", "video_clean.mp4")
OUTDIR = os.path.join(ROOT, "out")
TMP = os.path.join(ROOT, "out", "tmp")
os.makedirs(TMP, exist_ok=True)

# Sprecher-Slots: (Datei, Start s, max. Länge s, Text)
CUES = [
    ("VO01", 1.45, 4.75, "Unfall gehabt – und jetzt kommt ein Gutachter. Aber was macht der eigentlich?"),
    ("VO02", 7.20, 5.50, "Zuerst schaut er sich dein Fahrzeug und den Schaden ganz genau an."),
    ("VO03", 14.30, 6.10, "Beschädigte Teile werden fotografiert, vermessen – und genau dokumentiert."),
    ("VO04", 22.30, 7.10, "Auch Fahrzeugdaten und Laufleistung, Ausstattung und Zustand spielen bei der Bewertung eine Rolle."),
    ("VO05", 30.90, 5.30, "Dann wird berechnet: Welche Reparaturen sind nötig? Welche Kosten entstehen?"),
    ("VO06", 36.50, 4.80, "Je nach Schaden zählen auch weitere Werte fürs Gutachten."),
    ("VO07", 42.50, 7.60, "Am Ende kommt alles zusammen: Fotos, Fahrzeugdaten, Schadenbeschreibung und Kalkulation – in einem vollständigen Gutachten."),
    ("VO08", 50.60, 4.40, "Sauber dokumentiert. Nachvollziehbar bewertet. Verständlich erklärt."),
    ("VO09", 55.40, 4.20, "YAKÜ Gutachten. Ihr Schaden. Klar bewertet."),
]
if os.path.exists(os.path.join(ROOT, "cues.json")):
    CUES = [(c["take"], c["start"], c["maxlen"], c["text"]) for c in json.load(open(os.path.join(ROOT, "cues.json")))["takes"]]
FAIL_MSG = "Human Voice-over konnte nicht eingefügt werden – finaler Export ausstehend."


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        raise SystemExit(f"Befehl fehlgeschlagen: {' '.join(cmd[:4])} …")
    return r


def load(path):
    """Beliebige Audiodatei → mono float 48 kHz (über ffmpeg)."""
    tmp = os.path.join(TMP, "dec_" + os.path.basename(path) + ".wav")
    run(["ffmpeg", "-y", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-c:a", "pcm_f32le", tmp])
    x, _ = sf.read(tmp, dtype="float64")
    return x


def loudness(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    txt = r.stderr
    I = float(txt.split("Integrated loudness:")[1].split("I:")[1].split("LUFS")[0])
    tp = float(txt.split("True peak:")[1].split("Peak:")[1].split("dBFS")[0])
    return I, tp


def normalize(src, dst, target, tp=-1.5):
    """Zweistufige EBU-R128-Normalisierung (linear)."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", f"loudnorm=I={target}:TP={tp}:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    af = (f"loudnorm=I={target}:TP={tp}:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true,aresample={SR}")
    run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", af, "-ar", str(SR), "-c:a", "pcm_f32le", dst])


def gain_to(src, dst, target):
    I, _ = loudness(src)
    g = target - I
    run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", f"volume={g:.2f}dB", "-c:a", "pcm_f32le", dst])


def trim(x):
    a = np.abs(x)
    idx = np.where(a > 10 ** (-45 / 20))[0]
    if len(idx):
        x = x[max(0, idx[0] - int(.03 * SR)): idx[-1] + int(.12 * SR)]
    return x


def fit(x, maxlen, name, rmax=1.08):
    """Passt einen Take bei Bedarf dezent (max. 8 %) an die Slot-Länge an."""
    L = len(x) / SR
    if L <= maxlen + .05:
        return x, ""
    r = L / maxlen
    if r > rmax:
        r = rmax
    tin = os.path.join(TMP, f"fit_{name}_in.wav"); tout = os.path.join(TMP, f"fit_{name}_out.wav")
    sf.write(tin, x.astype(np.float32), SR, subtype="FLOAT")
    run(["ffmpeg", "-y", "-v", "error", "-i", tin, "-af", f"atempo={r:.4f}", "-c:a", "pcm_f32le", tout])
    y, _ = sf.read(tout, dtype="float64")
    note = f"  ↺ um {100 * (r - 1):.1f} % gestrafft"
    if len(y) / SR > maxlen + .15:
        note += f"  ⚠ noch {len(y) / SR - maxlen:.2f} s zu lang"
    return y, note


def split_read(x, n):
    """Teilt eine durchgehende Lesung an den n-1 längsten Pausen."""
    w = int(.02 * SR)
    env_ = np.sqrt(np.convolve(x ** 2, np.ones(w) / w, "same"))
    silent = env_ < 10 ** (-42 / 20)
    gaps, i = [], 0
    while i < len(silent):
        if silent[i]:
            j = i
            while j < len(silent) and silent[j]:
                j += 1
            gaps.append((j - i, i, j))
            i = j
        else:
            i += 1
    first = np.argmax(~silent); last = len(silent) - np.argmax(~silent[::-1])
    inner = [g for g in gaps if g[1] > first and g[2] < last]
    cuts = sorted(sorted(inner, reverse=True)[: n - 1], key=lambda g: g[1])
    if len(cuts) < n - 1:
        return None
    bounds = [first] + [ (c[1] + c[2]) // 2 for c in cuts ] + [last]
    return [trim(x[bounds[k]:bounds[k + 1]]) for k in range(n)]


def place_takes(track, segs, early=.25, gap=.22, end_limit=59.6):
    """Setzt Takes an ihre Cue-Zeit; ist ein Take länger als sein Fenster, rücken
    Einsätze minimal (früher/später) statt die Stimme zu verzerren."""
    prev_end = 0.0
    timing = []
    for k, ((name, cue, maxlen, _), x) in enumerate(zip(CUES, segs)):
        x, tnote = fit(x, maxlen + .35, name, rmax=1.06)
        L = len(x) / SR
        start = max(cue, prev_end + gap)
        nxt = CUES[k + 1][1] if k + 1 < len(CUES) else end_limit
        if start + L > nxt - gap and k > 0:     # reicht nicht: etwas früher beginnen (nie vor dem Crash)
            start = max(prev_end + gap, cue - early, min(start, nxt - gap - L))
        note = ""
        if k == len(CUES) - 1 and start + L > end_limit:
            x, note = fit(x, end_limit - start, name)
            L = len(x) / SR
        shift = start - cue
        print(f"  {name}: {L:4.2f} s, Einsatz {start:5.2f} s ({shift:+.2f} s){tnote}{note}")
        timing.append({"take": name, "cue": cue, "start": round(start, 3), "end": round(start + L, 3)})
        i = int(start * SR); x = x[: len(track) - i]
        track[i:i + len(x)] += x
        prev_end = start + L
    with open(os.path.join(OUTDIR, "voice_timing.json"), "w") as fh:
        json.dump(timing, fh, indent=1)


def build_voice():
    """Setzt die Sprecher-Takes an ihre Cue-Zeiten. Gibt Pfad oder None zurück."""
    full = sorted(glob.glob(os.path.join(ROOT, "voice", "voiceover_full.*")))
    vo = set(glob.glob(os.path.join(ROOT, "voice", "VO0*.*")))
    reads = [f for f in sorted(glob.glob(os.path.join(ROOT, "voice", "*.*"))) if f not in vo and f not in full]
    track = np.zeros(int(SR * DUR))
    if not full and not vo and reads:
        print(f"✓ Durchgehende Lesung gefunden: {os.path.basename(reads[0])} → wird in {len(CUES)} Takes geschnitten")
        segs = split_read(load(reads[0]), len(CUES))
        if segs is None:
            print("✗ Konnte die Lesung nicht eindeutig in Takes teilen.")
            return None
        place_takes(track, segs)
    elif full:
        x = load(full[0])[: len(track)]
        track[: len(x)] = x
        print(f"✓ Komplette Sprecherspur gefunden: {os.path.basename(full[0])}")
    else:
        missing = []
        for name, start, maxlen, text in CUES:
            f = sorted(glob.glob(os.path.join(ROOT, "voice", name + ".*")))
            if not f:
                missing.append(name)
                continue
            x, flag = fit(trim(load(f[0])), maxlen, name)
            print(f"  {name}: {len(x) / SR:4.2f} s (Slot {maxlen:.2f} s){flag}")
            i = int(start * SR)
            x = x[: len(track) - i]
            track[i:i + len(x)] += x
        if missing:
            print("✗ Fehlende Takes:", ", ".join(missing))
            return None
    out = os.path.join(TMP, "voice_raw.wav")
    sf.write(out, track.astype(np.float32), SR, subtype="FLOAT")
    return out


def voice_present(path):
    """Prüft, ob in jedem Sprecher-Slot hörbare Sprache liegt."""
    x, _ = sf.read(path)
    ok = 0
    for name, start, maxlen, _ in CUES:
        seg = x[int(start * SR): int((start + maxlen) * SR)]
        rms = 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-12)
        good = rms > -40
        ok += good
        print(f"  {name}: Pegel {rms:6.1f} dBFS {'✓' if good else '✗ keine hörbare Sprache'}")
    return ok == len(CUES)


def mux(audio, out, badge=False):
    vf = []
    if badge:
        vf = ["-vf", "drawbox=x=40:y=70:w=620:h=64:color=0x0A1B38@0.85:t=fill,"
              "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='VORSCHAU · OHNE SPRECHER':x=62:y=88:fontsize=30:fontcolor=0xE9C46A"]
    run(["ffmpeg", "-y", "-v", "error", "-i", VIDEO, "-i", audio, *vf,
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264" if badge else "copy",
         *(["-preset", "slow", "-crf", "12", "-tune", "animation", "-pix_fmt", "yuv420p"] if badge else []),
         "-c:a", "aac", "-b:a", "320k", "-ar", str(SR), "-ac", "2", "-movflags", "+faststart", "-shortest", out])


def main(mode):
    music = os.path.join(ROOT, "audio", "music.wav")
    sfx = os.path.join(ROOT, "audio", "sfx.wav")
    if not os.path.exists(VIDEO):
        raise SystemExit("Video fehlt: zuerst `npx hyperframes render --quality delivery --fps 30 --output out/video_clean.mp4`")

    if mode == "preview":
        gain_to(music, os.path.join(TMP, "m.wav"), -21)
        gain_to(sfx, os.path.join(TMP, "s.wav"), -25)
        run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(TMP, "m.wav"), "-i", os.path.join(TMP, "s.wav"),
             "-filter_complex", "amix=inputs=2:normalize=0", "-c:a", "pcm_f32le", os.path.join(TMP, "bed.wav")])
        normalize(os.path.join(TMP, "bed.wav"), os.path.join(TMP, "preview_mix.wav"), -16)
        out = os.path.join(OUTDIR, "YAKU_Erklaervideo_VORSCHAU_ohne_Sprecher.mp4")
        mux(os.path.join(TMP, "preview_mix.wav"), out, badge=True)
        I, tp = loudness(out)
        print(f"Vorschau: {out}\n  {I} LUFS, TP {tp} dBTP\n  ⚠ NICHT veröffentlichen – Sprecherspur fehlt.")
        return

    # ---------- FINAL ----------
    print("Sprecherspur prüfen …")
    v = build_voice()
    if v is None or not voice_present(v):
        print("\n" + FAIL_MSG)
        sys.exit(2)
    normalize(v, os.path.join(TMP, "voice.wav"), -14, -1.5)
    gain_to(music, os.path.join(TMP, "music_35.wav"), -35)
    gain_to(sfx, os.path.join(TMP, "sfx_28.wav"), -28)
    # Musik unter Stimme zusätzlich ducken (Sidechain)
    run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(TMP, "music_35.wav"), "-i", os.path.join(TMP, "voice.wav"),
         "-filter_complex", "[1:a]aformat=channel_layouts=stereo[sc];"
         "[0:a][sc]sidechaincompress=threshold=0.03:ratio=4:attack=25:release=350:makeup=1[mo]", "-map", "[mo]", "-c:a", "pcm_f32le", os.path.join(TMP, "music_duck.wav")])
    run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(TMP, "voice.wav"), "-i", os.path.join(TMP, "music_duck.wav"), "-i", os.path.join(TMP, "sfx_28.wav"),
         "-filter_complex", "[0:a]aformat=channel_layouts=stereo[v];[v][1:a][2:a]amix=inputs=3:normalize=0[m]", "-map", "[m]",
         "-c:a", "pcm_f32le", os.path.join(TMP, "mix_raw.wav")])
    normalize(os.path.join(TMP, "mix_raw.wav"), os.path.join(TMP, "mix.wav"), -13, -2.0)
    out = os.path.join(OUTDIR, "YAKU_Erklaervideo_FINAL.mp4")
    mux(os.path.join(TMP, "mix.wav"), out)
    ig = os.path.join(OUTDIR, "reel_instagram.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-i", out, "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-tune", "animation",
         "-maxrate", "9M", "-bufsize", "18M", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1", "-c:a", "copy", "-movflags", "+faststart", ig])
    I, tp = loudness(out)
    print(f"\nFINAL: {out}\nINSTAGRAM: {ig}\n  Gesamt {I} LUFS integrated · True Peak {tp} dBTP")
    if tp > -1.0:
        print("  ⚠ True Peak über -1 dBTP – bitte melden.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "final")
