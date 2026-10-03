# YAKÜ Feed-Posts – Playbook für die Routine

Alle **2 Tage um 09:00 Uhr (Europe/Berlin)** erscheint auf Instagram (@yaku.gutachten) ein neuer Feed-Post
im festen YAKÜ-Look – **automatisch veröffentlicht über Metricool** (autoPublish true).
Die Routine läuft an geraden Kalendertagen früh morgens und plant den Post für **09:00 Uhr am selben Tag** ein.

## 0. Eckdaten

| Was | Wert |
|---|---|
| Format | 1080 × 1350 (4:5), **JPEG** (PNG scheitert bei Metricool/Instagram mit „ERROR / Unknown“) |
| Typen | `einzelbild` (Headline + Auto mit Messkreis + 3 Labels + CTA) · `karussell` (Cover · 3 Inhalts-Slides · CTA) – abwechselnd |
| Farben | Navy `#071B3A`, Gold `#D8A52C`/`#E0B64D`, Creme `#F4F1EA`, Akzentblau `#1556C0` |
| Schriften | Fraunces (variabel, opsz), Inter, JetBrains Mono – liegen in `feed/assets/fonts` |
| Logo | `feed/assets/logo.svg` = Original von yaku-gutachten.de, nie verändern |
| Claim | „Ihr Schaden. Klar bewertet.“ |
| Metricool | blogId `7155086`, Zeitzone Europe/Berlin, nur Instagram, `autoPublish: true` |
| Bilder öffentlich | `feed/publish_images.sh` → Branch `media`, Ordner `feed/` (raw-URLs, 30 Tage) |

## 1. Inhaltliche Regeln (nicht verhandelbar)

- **Nur belegte Aussagen**: was auf yaku-gutachten.de steht (Leistungen, Ablauf, FAQ, Einsatzgebiet,
  Erreichbarkeit) oder allgemein fachlich gesichert ist (ADAC, Verbraucherzentrale, GDV …).
- **Keine Rechtsberatung, keine Versprechen**, keine Euro-Beträge, keine erfundenen Fälle, Zahlen oder Urteile.
  Bei Rechts-/Kostenthemen: „grundsätzlich“, „in der Regel“, „je nach Fall“ und `"disclaimer": true`.
- **Ansprache „Sie“**, seriös, freundlich, verständlich. Keine Versicherungs-Fachsprache, kein Gen-Z-Ton.
- **Keine KI-Menschen, keine Fotos** – nur der grafische Stil aus `yaku_feed.py`.
- **Kein Thema doppelt.** Gepostete Themen stehen in `themen-feed.json` mit status `gepostet`.

## 2. Ablauf

1. **Setup**
   ```bash
   cd yaku-reels
   pip install --break-system-packages -q playwright pillow 2>/dev/null || true
   # Chromium ist vorinstalliert (PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers); nicht "playwright install" ausführen
   ```
2. **Termin prüfen**: `DATUM=$(TZ=Europe/Berlin date +%F)`. Metricool `getScheduledPosts` (blogId 7155086,
   heute 00:00 bis +2 Tage, timezone Europe/Berlin). Ist für heute 09:00 schon ein Instagram-POST (kein Reel)
   eingeplant → nichts tun, nur kurz berichten. Ist es schon nach 08:40 Uhr → für **morgen 09:00** einplanen.
3. **Thema wählen**: erstes Thema in `feed/themen-feed.json` mit `"status": "offen"`.
   Sind keine offenen Themen mehr da: ein **neues Thema** nach demselben Schema anlegen
   (Typ abwechselnd zum letzten geposteten), Inhalte nur aus yaku-gutachten.de bzw. belegbaren Quellen,
   Quellen im Bericht nennen. Headlines kurz halten (Zeile 1 eines Einzelbilds max. ~14 Zeichen).
4. **Rendern**: `python3 feed/yaku_feed.py <id>` → `feed/out/<id>/01.jpg …` + `vorschau.jpg`.
   **Jedes Bild ansehen** (Read): Text vollständig, nichts abgeschnitten, keine Überlappung, Umlaute korrekt.
   Bei Problemen Text in der JSON kürzen bzw. `fs`/`fs1`/`fs2` setzen und neu rendern.
5. **Öffentlich ablegen**:
   ```bash
   bash feed/publish_images.sh "$DATUM-<id>" feed/out/<id>/0*.jpg   # gibt die URLs in Reihenfolge aus
   ```
   Nur `01.jpg`, `02.jpg` … übergeben (nicht `vorschau.jpg`).
6. **Metricool `createScheduledPost`** (blogId `7155086`, date `<DATUM>T09:00:00+02:00` bzw. +01:00 im Winter):
   ```json
   {"autoPublish": true, "draft": false, "text": "<caption>", "media": ["<url1>", "..."],
    "mediaAltText": ["YAKÜ Gutachten – <titel>"], "providers": [{"network": "instagram"}],
    "publicationDate": {"dateTime": "<DATUM>T09:00:00", "timezone": "Europe/Berlin"},
    "instagramData": {"type": "POST", "showReelOnFeed": true, "isAiGenerated": false},
    "firstCommentText": "", "shortener": false, "smartLinkData": {"ids": []}, "descendants": [], "hasNotReadNotes": false}
   ```
   `isAiGenerated` bleibt **false**: die Grafiken sind programmatisch gesetzte Typografie/Illustration, keine KI-Bilder.
   Danach mit `getScheduledPosts` prüfen, dass der Post mit Status PENDING und allen Bildern drin ist.
   **Hinweis:** Jeder neue Feed-Post verschiebt das 6-teilige Logo-Grid im Profil um eine Position – das ist so gewollt.
7. **Plan aktualisieren**: Thema in `themen-feed.json` auf `"status": "gepostet"`, `"datum"`, `"plannerUrl"` setzen,
   committen und pushen (`main`). Vorher `git pull --rebase`, weil die Reel-Routine im selben Repo arbeitet.
8. **Bericht** an Gökce (Deutsch, Anrede „Gökce“): Thema, Termin, Vorschaubild (`vorschau.jpg` per SendUserFile),
   Metricool-Planner-Link, Auffälligkeiten. Wenn etwas scheitert: klar sagen, was fehlt und dass nichts eingeplant wurde.
