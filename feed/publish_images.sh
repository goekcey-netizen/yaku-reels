#!/usr/bin/env bash
# Legt fertige Feed-Bilder öffentlich im Branch "media" (Ordner feed/) ab und gibt pro Bild
# die öffentliche raw-URL aus (eine pro Zeile, in Reihenfolge). Behält 30 Tage.
# Videos der Reel-Routine (Ordner videos/) bleiben unangetastet.
#   bash feed/publish_images.sh <YYYY-MM-DD>-<thema-id> bild1.png [bild2.png ...]
set -euo pipefail
NAME="$1"; shift
REPO=https://github.com/goekcey-netizen/yaku-reels.git
W=$(mktemp -d)
for f in "$@"; do cp "$f" "$W/"; done
cd "$W"
if git clone -q --depth 1 -b media "$REPO" m 2>/dev/null; then :; else
  mkdir m && cd m && git init -q -b media && git remote add origin "$REPO" && cd ..
fi
cd m
mkdir -p feed
i=0; URLS=()
for f in "$@"; do
  i=$((i+1)); dst="feed/${NAME}-$(printf %02d $i).png"
  cp "$W/$(basename "$f")" "$dst"
  URLS+=("https://raw.githubusercontent.com/goekcey-netizen/yaku-reels/media/$dst")
done
CUT=$(TZ=Europe/Berlin date -d '30 days ago' +%F)
for f in feed/*; do d=$(basename "$f" | cut -c1-10); [[ "$d" < "$CUT" ]] && rm -f "$f"; done
touch .nojekyll
[ -f index.html ] || echo "YAKÜ – öffentliche Medien-Ablage für Metricool" > index.html
rm -rf .git/shallow 2>/dev/null || true
git checkout -q --orphan tmp
git add -A
git -c user.name="YAKÜ Feed Bot" -c user.email=goekcey@gmail.com commit -qm "Feed $NAME"
git push -q -f origin tmp:media
for u in "${URLS[@]}"; do
  for t in $(seq 1 30); do
    code=$(curl -s -o /dev/null -w '%{http_code}' -I "$u")
    [ "$code" = 200 ] && break; sleep 5
  done
  echo "$u"
done
