# YAKÜ Reels – Playbook für die wöchentliche Routine

Dieses Dokument ist die verbindliche Arbeitsanweisung für die automatische Tagesroutine.
Einmal pro Woche entsteht **ein neues, ca. 60 s langes animiertes Erklärvideo (9:16) zu einem neuen Thema**,
das für **Samstag, 18:00 Uhr (Europe/Berlin)** über Metricool auf Instagram (@yaku.gutachten) **und zeitgleich auf TikTok** (YAKÜ Gutachten) eingeplant und **automatisch veröffentlicht** wird (autoPublish true, keine Freigabe nötig – Gökce, 04.10.2026).

Referenzprojekt (Qualitätsmaßstab): `beispiel-2026-10-02/` + `template/index.html`
(„Was macht ein Kfz-Gutachter eigentlich?“).

---

## 0. Feste Eckdaten

| Was | Wert |
|---|---|
| Format | 1080 × 1920, 30 fps, ~60 s, H.264 + AAC |
| Marke | YAKÜ Gutachten – Kfz-Sachverständige, München & Umgebung, Vor-Ort-Service, Website yaku-gutachten.de |
| Farben | Navy `#07306E`, Logo-Navy `#07214D`, Deep `#0A1B38`, Gold `#D8A42C` / `#E9C46A`, Papier `#F4F1EA` |
| Schriften | Fraunces (Headlines), Inter (Text), JetBrains Mono (Labels) – liegen in `template/assets/fonts` |
| Logo | `template/assets/logo.svg` (Original, nie verändern) |
| Claim | „Ihr Schaden. Klar bewertet.“ |
| Stimme | ElevenLabs, Voice „Lennard – Warm & Trustworthy“ `HNYELfQMgCeL9N0RGyxo`, Modell `eleven_multilingual_v2` |
| Metricool | Brand `yaku.gutachten`, blogId `7155086`, Zeitzone Europe/Berlin, **Instagram + TikTok im selben Post** |
| GitHub | `goekcey-netizen/yaku-reels` (öffentlich) – `main`: Vorlage, Projekte, Themenplan · `media`: fertige Videos (öffentliche raw-URLs, letzte 14 Tage) |
| Safe Area | Text nur in y 250–1480 px, x 60–960 px (Instagram-UI oben/unten/rechts) |

## 1. Inhaltliche Regeln (nicht verhandelbar)

- **90 % Mehrwert, 10 % Werbung.** Erklären, nicht anpreisen. YAKÜ erst am Ende (Endcard + Claim).
- **Nur belegbare Aussagen.** Vor dem Schreiben 2–4 seriöse deutsche Quellen öffnen (ADAC, TÜV, DEKRA, GDV,
  Verbraucherzentrale, BGH-Pressemitteilungen, yaku-gutachten.de für YAKÜ-Abläufe). Quellen in `quellen.md` notieren.
- **Keine Rechtsberatung, keine Versprechen.** Nie „die Versicherung zahlt immer“, „Gutachten ist immer kostenlos“,
  keine Euro-Beträge als Zusage, keine erfundenen Urteile. Formulierungen wie „in der Regel“, „je nach Fall“.
  Bei Rechtsthemen am Ende eines Satzes ggf. „Im Zweifel: fachlich beraten lassen.“
- Beispielwerte (km, mm, Baujahr) im Bild als **„Beispielhafte Darstellung“** kennzeichnen.
- Ansprache: **du** im Erklärteil, Claim bleibt „Ihr Schaden. Klar bewertet.“
- Nie ein Thema doppelt; nie identische Bildfolge wie an den Vortagen (letzte 3 Projekte ansehen).

## 2. Ablauf Schritt für Schritt

**Zeitplan:** Die Routine läuft einmal pro Woche (samstags früh). Veröffentlichungstermin ist immer ein **Samstag um 18:00 Uhr
(Europe/Berlin)** – und zwar der **nächste Samstag ab heute, an dem um 18:00 noch kein Reel eingeplant ist**
(Datum mit `TZ=Europe/Berlin date +%F` bestimmen). Dazu vorher `getScheduledPosts` (blogId 7155086, heute bis +5 Wochen)
abfragen. Pro Samstag höchstens ein Reel, an anderen Tagen nie. Ist der gewählte Termin weniger als 30 Minuten entfernt,
den nächsten freien Samstag nehmen.

### 2.1 Setup
```bash
# Repo ist per add_repo (owner goekcey-netizen, repo yaku-reels, access push) angebunden
git clone https://github.com/goekcey-netizen/yaku-reels.git && cd yaku-reels
cd template && npm i && cd ..
export PRODUCER_HEADLESS_SHELL_PATH=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell
pip install --break-system-packages -q soundfile scipy numpy   # falls fehlend
# HyperFrames-Regeln (Skills) zum Nachlesen:
git clone -q --depth 1 https://github.com/heygen-com/hyperframes.git /tmp/hf
#   → /tmp/hf/skills/hyperframes-core/SKILL.md, hyperframes-animation, hyperframes-cli lesen
# Falls der Headless-Shell-Pfad abweicht: ls /opt/pw-browsers
```

### 2.2 Thema wählen
`themen.json` → erstes Thema mit `status: "offen"`. Projektordner anlegen:
`projekte/<YYYY-MM-DD>-<id>/` mit Kopie von `template/` (index.html, assets, package.json-Link reicht: `cp -r template/assets`).

### 2.3 Recherche → `quellen.md`
Kernaussagen + Link + Datum. Nur was dort steht, darf in Sprechertext/Untertitel.

### 2.4 Sprechertext → `cues.json`
- 8–9 Sätze (Takes), zusammen **max. 46 s Sprechzeit**, ~2,3 Wörter/s.
- **Hook in den ersten 3 s** (Frage oder Problem aus Sicht des Autofahrers).
- Struktur: Hook → 4–5 Erklärschritte (je ein Schritt = eine Szene, Headline „Schritt n von N“ oder passende Kapitel) → Fazit → Claim.
- Letzter Take immer: `Jakü Gutachten. Ihr Schaden. Klar bewertet.` (Schreibweise „Jakü“ für die TTS!)
- `cues.json`: `takes[]` mit `take`, `start`, `maxlen`, `text`, `captions` (Indizes in `CAPS` der index.html).
  Startzeiten so planen, dass zwischen den Takes 0,3–0,8 s Luft bleibt und der letzte Take vor 59,5 s endet.

### 2.5 Komposition (HyperFrames) → `index.html`
- Ausgangspunkt `template/index.html`. Wiederverwenden: Auto (`carSVG`, inkl. Blueprint-Variante), Figuren
  (`personSVG` + Rig-Helfer `walk`, `R`, `mouth`, `blink`, `look`, `brows`, `idle`, `holdTool`), Headlines (`hdIn/hdOut`),
  Untertitel-System (`CAPS`, `capShow`), Karten (`.card .dc`), Kalkulationsblatt, Dokument mit Seiten, Endcard (unverändert lassen),
  Kamera-Helfer `camTo` (Proxy-Matrix, NICHT svgOrigin auf #cam).
- **Pro Thema neue Szenen bauen**, passend zum Inhalt (z. B. Checkliste mit abhakenden Punkten, Vergleich zweier Spalten,
  Zeitstrahl, Waage Haftpflicht/Kasko, Kalender für Nutzungsausfall, Hagelkörner, Wildwechsel-Schild …).
  Echte Character Animation (Gesten, Blicke, Walk Cycles), Elemente aus Szene A erzeugen Szene B (Match-Transitions).
- Pflichtregeln aus `/hyperframes-core`: ein pausierter GSAP-Timeline-Export `window.__timelines["main"]`,
  `defaults: {immediateRender:false}`, keine left/top-Tweens (x/y nutzen), keine Zufallswerte ohne Seed.
- Prüfen: `npx hyperframes lint` (0 Errors) → `npx hyperframes snapshot --at <10 Zeitpunkte>` → Contact-Sheet ansehen,
  Überlappungen/Safe-Area/Lesbarkeit fixen. Erst dann rendern.

### 2.6 Rendern
```bash
cd projekte/<projekt> && ln -s ../../template/node_modules node_modules
npx hyperframes render --fps 30 --video-bitrate 14M --output out/video_clean.mp4
```

### 2.7 Musik & Sound → `sound.json`
- Format wie `beispiel-2026-10-02/sound.json`. `music`: Abschnitte (intro, motif, groove, tech, riser, bright, resolve, brand)
  an die Szenen anpassen; `seed` = Datum (z. B. 20261003), `transpose` -2…+2 für Abwechslung.
- `sfx`: jedes sichtbare Ereignis vertonen (whoosh, pop, tick, ding, paper, shutter, steps, impact …), dezent.
- `out_dir`: `<projekt>/audio`. Ausführen: `python3 ../../template/sound_engine.py sound.json`

### 2.8 Stimme (ElevenLabs)
1. `creative_create_flow` (Name „YAKÜ Reel <Datum>“).
2. `creative_generate_speech` mit voice_id `HNYELfQMgCeL9N0RGyxo`, model `eleven_multilingual_v2`, **generations_count 1**,
   Prompt = alle Takes hintereinander, getrennt durch `<break time="1.5s" />`.
3. Pollen bis fertig → `media[0].url` (signierte URL, 2 h gültig).
4. Datei holen (die Cloud-Umgebung erreicht ElevenLabs-Speicher nicht direkt):
   ```bash
   gh api -X POST repos/goekcey-netizen/yaku-reels/actions/workflows/fetch-audio.yml/dispatches \
     -f ref=main -f "inputs[url]=<URL>" -f "inputs[name]=<datum>_voice.mp3"
   # warten bis Run fertig: gh api repos/goekcey-netizen/yaku-reels/actions/runs?event=workflow_dispatch
   # Download NUR über REST (gh release download nutzt GraphQL → in Claude-Sitzungen gesperrt):
   AID=$(gh api repos/goekcey-netizen/yaku-reels/releases/tags/audio-inbox --jq '.assets[] | select(.name=="<datum>_voice.mp3") | .id')
   mkdir -p voice && gh api -H "Accept: application/octet-stream" repos/goekcey-netizen/yaku-reels/releases/assets/$AID > voice/voiceover_full.mp3
   ```
   Getestet am 02.10.2026: Dispatch → Run (~30 s) → REST-Download funktioniert.
   Hinweis 03.10.2026: Ist `gh` nicht angemeldet, Dispatch über das GitHub-MCP-Tool `actions_run_trigger`
   (workflow fetch-audio.yml, ref main) auslösen und das Asset über die öffentliche URL laden:
   `curl -fsSL -o voice/read.mp3 https://github.com/goekcey-netizen/yaku-reels/releases/download/audio-inbox/<datum>_voice.mp3`
   (Prüfsumme mit dem `digest` aus `get_release_by_tag` vergleichen). Eine Datei wie `voice/read.mp3` wird von mix.py als durchgehende Lesung erkannt und in Takes geschnitten. Die Cloud-Umgebung selbst darf
   storage.googleapis.com nicht abrufen – keine Umwege versuchen.

### 2.9 Mischen, Untertitel anpassen, final
```bash
python3 ../../template/mix.py final .          # schneidet Lesung in Takes, prüft Stimme, mischt
python3 ../../template/retime_captions.py .    # Untertitel an echte Sprechzeiten
npx hyperframes render --fps 30 --video-bitrate 14M --output out/video_clean.mp4   # neu rendern
python3 ../../template/mix.py final .          # → out/reel_instagram.mp4
```
- Ist ein Take > 1 s zu lang für sein Fenster: Satz kürzen und nur diesen Teil neu erzeugen (max. 1 Wiederholung).
- Ziele: Stimme ≈ -14 LUFS, Musik ≈ -35 LUFS gedeckt, gesamt ≈ -13 LUFS, True Peak ≤ -1 dBTP.
- **Ohne hörbare Sprecherspur wird NICHT gepostet.**

### 2.10 Veröffentlichen
1. Video öffentlich ablegen (Releases anlegen ist aus Claude-Sitzungen gesperrt, daher Branch `media`).
   **Absolute Pfade übergeben** – das Skript wechselt in ein Temp-Verzeichnis:
   ```bash
   URL=$(bash template/publish_media.sh projekte/<projekt>/out/reel_instagram.mp4 <YYYY-MM-DD>-<id> projekte/<projekt>/cover.png | tail -1)
   ```
   → `https://raw.githubusercontent.com/goekcey-netizen/yaku-reels/media/videos/<YYYY-MM-DD>-<id>.mp4`
   (Metricool kopiert die Datei beim Einplanen auf static.metricool.com – getestet am 02.10.2026.)
2. Metricool `createScheduledPost`:
   - blogId `7155086`, `publicationDate {dateTime:"<YYYY-MM-DD>T18:00:00", timezone:"Europe/Berlin"}` (immer ein Samstag)
   - `providers [{network:"instagram"},{network:"tiktok"}]` – **Regel (Gökce, 04.10.2026): alles, was auf Instagram geht, geht zeitgleich auch auf TikTok**
   - `instagramData {type:"REEL", showReelOnFeed:true, isAiGenerated:true}`
   - `tiktokData {title:"<Hook, max. 90 Zeichen>", privacyOption:"PUBLIC_TO_EVERYONE", disableComment:false, disableDuet:false, disableStitch:false, autoAddMusic:false, commercialContentThirdParty:false, commercialContentOwnBrand:false, isAigc:true}
   - **`autoPublish: true`** – wird ohne Freigabe automatisch veröffentlicht (Vorgabe Gökce, 04.10.2026). Deshalb vor dem Einplanen Video, Ton und Caption besonders sorgfältig prüfen.
   - `media [<raw-URL aus Schritt 1>]`, `videoCoverMilliseconds` = ein starker Frame (Hook-Titel, meist 2000–4500)
   - Caption: 1. Zeile = Hook (≤ 90 Zeichen), 2–4 kurze Zeilen Mehrwert, CTA „Schaden melden? Link in der Bio 👉 yaku-gutachten.de“,
     3–5 Hashtags (#KfzGutachter #Unfallgutachten #München + themenspezifisch). Caption in Sie-Form wie der bestehende Feed.
     Kein Em-Dash-Spam, natürlich klingen. Keine Aussage, die nicht auch im Video/`quellen.md` belegt ist.
3. `themen.json`: Status `eingeplant`, `datum`, `video` (raw-URL), `plannerUrl`. Projektordner (ohne große Videos, siehe .gitignore) committen & pushen.

### 2.11 Bericht an Gökce
Per `SendUserMessage` auf Deutsch, Anrede „Gökce“: Thema, Video-Link, Metricool-Planner-Link, Hinweis „wird am Samstag um 18:00 automatisch veröffentlicht“, Quellen, Auffälligkeiten, verbrauchte ElevenLabs-Credits.
Bei Fehlern: was fehlt, ob gepostet wurde (nur mit Stimme!).
