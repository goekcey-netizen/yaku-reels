#!/usr/bin/env bash
# Legt ein fertiges Reel (und optional das Cover) öffentlich im Branch "media" ab
# und gibt die öffentliche raw-URL aus. Behält nur die letzten 14 Tage, Branch bleibt
# ein einzelner Commit (Repo wächst nicht).
#   bash template/publish_media.sh <video.mp4> <zielname-ohne-endung> [cover.png]
set -euo pipefail
VID="$1"; NAME="$2"; COVER="${3:-}"
REPO=https://github.com/goekcey-netizen/yaku-reels.git
W=$(mktemp -d)
cd "$W"
if git clone -q --depth 1 -b media "$REPO" m 2>/dev/null; then :; else
  mkdir m && cd m && git init -q -b media && git remote add origin "$REPO" && cd ..
fi
cd m
mkdir -p videos
cp "$VID" "videos/$NAME.mp4"
[ -n "$COVER" ] && cp "$COVER" "videos/$NAME.png"
# alles älter als 14 Tage entfernen (Dateinamen beginnen mit YYYY-MM-DD)
CUT=$(TZ=Europe/Berlin date -d '14 days ago' +%F)
for f in videos/*; do d=$(basename "$f" | cut -c1-10); [[ "$d" < "$CUT" ]] && rm -f "$f"; done
touch .nojekyll
[ -f index.html ] || echo "YAKÜ Reels – öffentliche Video-Ablage für Metricool" > index.html
rm -rf .git/shallow 2>/dev/null || true
git checkout -q --orphan tmp
git add -A
git -c user.name="YAKÜ Reels Bot" -c user.email=goekcey@gmail.com commit -qm "Media $(TZ=Europe/Berlin date +%F)"
git push -q -f origin tmp:media
URL="https://raw.githubusercontent.com/goekcey-netizen/yaku-reels/media/videos/$NAME.mp4"
# warten bis öffentlich abrufbar
for i in $(seq 1 30); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -I "$URL")
  [ "$code" = 200 ] && break; sleep 5
done
echo "$URL"
