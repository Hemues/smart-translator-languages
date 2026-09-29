"""add_components.py — describe the pack files in dist/ that components.json does not know yet.

Piper voices (vits-piper-<locale>-<voice>-<quality>.tar.bz2): language, voice and quality come from the file name, the licence
from the MODEL_CARD inside the tarball; released under `voices-v1`, upstream = the sherpa-onnx tts-models release.
Omnilingual ASR (sherpa-onnx-omnilingual-asr-*.tar.bz2): kind asr, engine omnilingual_ctc, the languages Parakeet lacks.

    python add_components.py            # updates components.json in place (idempotent by id), then run make_index.py
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
UP_TTS = "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/"
UP_ASR = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/"

LANG_NAMES = {
    "bg": "Bulgarian", "ca": "Catalan", "cs": "Czech", "cy": "Welsh", "da": "Danish", "de": "German", "el": "Greek", "en": "English",
    "es": "Spanish", "et": "Estonian", "eu": "Basque", "fi": "Finnish", "fr": "French", "ga": "Irish", "hr": "Croatian", "hu": "Hungarian",
    "is": "Icelandic", "it": "Italian", "lt": "Lithuanian", "lv": "Latvian", "mt": "Maltese", "nl": "Dutch", "no": "Norwegian", "pl": "Polish",
    "pt": "Portuguese", "ro": "Romanian", "ru": "Russian", "sk": "Slovak", "sl": "Slovenian", "sq": "Albanian", "sr": "Serbian",
    "sv": "Swedish", "tr": "Turkish", "uk": "Ukrainian",
}
# European languages the Parakeet pack does not cover; Omnilingual ASR (1,600 languages) serves them
OMNI_LANGS = ["sq", "be", "bs", "ca", "cy", "eu", "ga", "gl", "is", "ka", "lb", "mk", "no", "sr", "tr"]
# voice gender where the voice's name or card makes it clear (shown in the app's voice picker; left out when unsure)
GENDER = {
    "anna": "f", "berta": "f", "imre": "m", "lessac": "f", "alan": "m", "thorsten": "m", "siwis": "f", "davefx": "m", "paola": "f",
    "gosia": "f", "irina": "f", "alex": "m", "jirka": "m", "lili": "f", "artur": "m", "mihai": "m", "harri": "m", "rapunzelina": "f",
    "bui": "m", "aivars": "m", "edon": "m", "gwryw_gogleddol": "m", "upc_ona": "f", "antton": "m", "tugao": "m", "dfki": "f",
}


def card_field(tar: Path, field: str) -> str:
    """One `* Field: value` line of the MODEL_CARD inside a Piper tarball ('' when absent)."""
    try:
        out = subprocess.run(["tar", "-xOjf", str(tar), "--wildcards", "*/MODEL_CARD"], capture_output=True, text=True, timeout=600).stdout
    except Exception:
        return ""
    m = re.search(r"^\*\s*" + field + r"\s*:\s*(.+)$", out, re.I | re.M)
    return m.group(1).strip() if m else ""


def piper_entry(tar: Path) -> dict:
    m = re.match(r"vits-piper-([a-z]{2})_([A-Z]{2})-(.+)-(x_low|low|medium|high)\.tar\.bz2$", tar.name)
    if not m:
        raise SystemExit(f"unexpected piper name {tar.name}")
    lang, region, voice, quality = m.groups()
    lid = tar.name[:-len(".tar.bz2")]
    licence = card_field(tar, "License") or "see MODEL_CARD in the pack"
    url = card_field(tar, "URL")
    name = LANG_NAMES.get(lang, lang)
    return {
        "id": lid, "kind": "tts", "engine": "piper_vits",
        "title": f"{name} voice — {voice.replace('_', ' ')} ({quality.replace('_', '-')}, {lang}_{region})",
        "language": lang, "voice": voice, "quality": quality, "languages": [lang], **({"gender": GENDER[voice]} if voice in GENDER else {}),
        "asset": tar.name, "upstream": UP_TTS + tar.name, "release_tag": "voices-v1",
        "licence": f"voice: {licence} · Piper/sherpa-onnx: MIT/Apache-2.0", "licence_url": url or "https://github.com/rhasspy/piper",
        "archive": True, "keep": [], "dir": f"packs/tts/{lid}",
    }


def omni_entry(tar: Path) -> dict:
    lid = "omnilingual-asr-300m-int8"
    return {
        "id": lid, "kind": "asr", "engine": "omnilingual_ctc",
        "title": "Omnilingual ASR 300M (Meta) — speech recognition for the European languages the Parakeet pack lacks",
        "languages": OMNI_LANGS,
        "asset": tar.name, "upstream": UP_ASR + tar.name, "release_tag": "packs-v1",
        "licence": "model Apache-2.0 (Meta, omnilingual-asr) · export Apache-2.0 (sherpa-onnx)",
        "licence_url": "https://github.com/facebookresearch/omnilingual-asr",
        "archive": True, "keep": ["model.int8.onnx", "tokens.txt"], "dir": f"packs/asr/{lid}",
    }


def main():
    meta = json.loads((ROOT / "components.json").read_text(encoding="utf-8"))
    known = {c["id"] for c in meta["components"]}
    added = 0
    for tar in sorted(DIST.glob("*.tar.bz2")):
        if tar.name.startswith("vits-piper-"):
            e = piper_entry(tar)
        elif "omnilingual-asr" in tar.name:
            e = omni_entry(tar)
        else:
            continue
        if e["id"] in known:
            # already described: refresh the derived fields (gender, release tag) without touching hand-edited ones
            old = next(c for c in meta["components"] if c["id"] == e["id"])
            for k in ("gender", "release_tag", "engine"):
                if k in e and old.get(k) != e[k]:
                    old[k] = e[k]; print(f"~ {e['id']}: {k} = {e[k]}")
            continue
        meta["components"].append(e); known.add(e["id"]); added += 1
        print(f"+ {e['id']}: {e['title']}  [{e['licence']}]")
    (ROOT / "components.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"components.json: {added} added, {len(meta['components'])} total")


if __name__ == "__main__":
    main()
