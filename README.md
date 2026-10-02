# yaku-reels

Tägliche animierte Erklär-Reels für **YAKÜ Gutachten** (Kfz-Sachverständige, München & Umgebung).

- `template/` – HyperFrames-Vorlage (Animation, Figuren, Endcard), Sound-Engine, Mix- und Untertitel-Skripte
- `beispiel-2026-10-02/` – Referenzfilm „Was macht ein Kfz-Gutachter eigentlich?“
- `projekte/` – ein Ordner pro Tag
- `themen.json` – Redaktionsplan (Status je Thema)
- `PLAYBOOK.md` – Arbeitsanweisung der Tagesroutine
- Fertige Videos liegen im Branch **`media`** (öffentliche raw-Links für Metricool, letzte 14 Tage; `template/publish_media.sh`).
- Sprecherspuren holt die Action `fetch-audio` von ElevenLabs ab (Release `audio-inbox`).

Musik und Sounddesign sind vollständig selbst synthetisiert (lizenzfrei). Schriften: SIL Open Font License.
