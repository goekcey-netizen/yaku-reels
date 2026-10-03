# yaku-reels

Tägliche animierte Erklär-Reels für **YAKÜ Gutachten** (Kfz-Sachverständige, München & Umgebung).

- `template/` – HyperFrames-Vorlage (Animation, Figuren, Endcard), Sound-Engine, Mix- und Untertitel-Skripte
- `beispiel-2026-10-02/` – Referenzfilm „Was macht ein Kfz-Gutachter eigentlich?“
- `projekte/` – ein Ordner pro Reel (wöchentlich, Samstag 18:00)
- `themen.json` – Redaktionsplan (Status je Thema)
- `PLAYBOOK.md` – Arbeitsanweisung der Tagesroutine
- Fertige Videos liegen im Branch **`media`** (öffentliche raw-Links für Metricool, letzte 14 Tage; `template/publish_media.sh`).
- Sprecherspuren holt die Action `fetch-audio` von ElevenLabs ab (Release `audio-inbox`).

Musik und Sounddesign sind vollständig selbst synthetisiert (lizenzfrei). Schriften: SIL Open Font License.

## Feed-Posts (alle 2 Tage, 09:00)
- `feed/` – Generator `yaku_feed.py` (1080×1350, YAKÜ-Look), Themenplan `themen-feed.json`, Arbeitsanweisung `FEED_PLAYBOOK.md`
- Bilder liegen öffentlich im Branch **`media`**, Ordner `feed/` (`feed/publish_images.sh`, 30 Tage)
