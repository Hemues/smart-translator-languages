#!/usr/bin/env bash
# fetch_voices.sh — download the chosen Piper voices (one medium voice per European language that has one, three for
# Hungarian, two for English) and the Omnilingual ASR pack from the sherpa-onnx releases into dist/, describe them
# (add_components.py), rebuild packs.json, commit, push, and publish the files as release assets. Run as root on .2:
#   sudo -n bash /storage/Samba/Temp/git/mobile-applications/smart-translator-languages/fetch_voices.sh
# Re-runnable: existing files with the right size are kept, uploads use --clobber.
set -euo pipefail
cd "$(dirname "$0")"
TTS=https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models
ASR=https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models
VOICES="ca_ES-upc_ona-medium cs_CZ-jirka-medium cy_GB-gwryw_gogleddol-medium da_DK-talesyntese-medium de_DE-thorsten-medium
el_GR-rapunzelina-low en_US-lessac-medium en_GB-alan-medium es_ES-davefx-medium eu_ES-antton-medium fi_FI-harri-medium
fr_FR-siwis-medium hu_HU-anna-medium hu_HU-imre-medium hu_HU-berta-medium is_IS-bui-medium it_IT-paola-medium lv_LV-aivars-medium
nl_NL-alex-medium no_NO-talesyntese-medium pl_PL-gosia-medium pt_PT-tugao-medium ro_RO-mihai-medium ru_RU-irina-medium
sk_SK-lili-medium sl_SI-artur-medium sq_AL-edon-medium sr_RS-serbski_institut-medium sv_SE-nst-medium tr_TR-dfki-medium
uk_UA-ukrainian_tts-medium"
OMNI=sherpa-onnx-omnilingual-asr-1600-languages-300M-ctc-v2-int8-2026-02-05.tar.bz2
mkdir -p dist
echo "$(date '+%F %T') downloading…"
fetch() {  # fetch URL NAME — skip when the local size equals the remote Content-Length
  local url="$1" name="$2" remote local
  remote=$(curl -sIL "$url" | grep -i '^content-length' | tail -1 | tr -dc '0-9')
  local=$(stat -c %s "dist/$name" 2>/dev/null || echo 0)
  if [ -n "$remote" ] && [ "$local" = "$remote" ]; then echo "  have $name ($local)"; return; fi
  curl -sL --retry 3 -o "dist/$name.part" "$url" && mv "dist/$name.part" "dist/$name"
  echo "  got  $name ($(stat -c %s "dist/$name"))"
}
for v in $VOICES; do fetch "$TTS/vits-piper-$v.tar.bz2" "vits-piper-$v.tar.bz2"; done
fetch "$ASR/$OMNI" "$OMNI"
echo "$(date '+%F %T') describing + indexing…"
python3 add_components.py
python3 make_index.py
python3 make_index.py --check
git add -A
git commit -q -m "Voices for 28 European languages (Piper, medium) and Omnilingual ASR 300M for the languages Parakeet lacks" \
  -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" || echo "nothing to commit"
git push -q origin main
echo "$(date '+%F %T') uploading…"
gh release view voices-v1 >/dev/null 2>&1 || gh release create voices-v1 --title "Voices v1 — Piper, 28 European languages" \
  --notes "One medium-quality Piper (VITS) voice per European language that has one — three for Hungarian (anna, imre, berta), two for English (US lessac, GB alan) — byte-identical to the sherpa-onnx tts-models assets. Per-voice licences: the MODEL_CARD inside each pack, summarised in packs.json. Greek has only a low-quality voice; Bulgarian, Estonian, Irish, Croatian, Lithuanian, Maltese, Belarusian, Macedonian, Bosnian and Galician have no Piper voice — the phone's own text-to-speech serves them."
gh release upload voices-v1 dist/vits-piper-*.tar.bz2 --clobber
gh release upload packs-v1 "dist/$OMNI" --clobber
echo "$(date '+%F %T') assets:"
gh release view voices-v1 --json assets -q '.assets[] | "\(.name) \(.size)"' | wc -l
gh release view packs-v1 --json assets -q '.assets[] | "\(.name) \(.size)"'
echo "$(date '+%F %T') done"
