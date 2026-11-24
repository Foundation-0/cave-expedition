#!/bin/bash
# Compares the published files with PUBLISH_MANIFEST.tsv (sha256 and size), written when the amendment was published. Run from this folder.
cd "$(dirname "$0")"
ok=0; bad=0
while IFS=$'\t' read -r p h s; do
  [ "$p" = "path" ] && continue
  f="../../$p"
  a=$(shasum -a 256 "$f" 2>/dev/null | cut -d' ' -f1); b=$(wc -c < "$f" 2>/dev/null | tr -d ' ')
  if [ "$a" = "$h" ] && [ "$b" = "$s" ]; then ok=$((ok+1)); else bad=$((bad+1)); echo "MISMATCH $p"; fi
done < PUBLISH_MANIFEST.tsv
echo "published files equal to the manifest: $ok of $((ok+bad))"
