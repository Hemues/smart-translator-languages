# smart-translator-languages

Language packs for the **Smart Translator** Android app ([Hemues/smart-translator-mobileapplication](https://github.com/Hemues/smart-translator-mobileapplication)),
separated from the app so that new languages and better models can ship without an app update.

- **`packs.json`** — the index the app reads (Settings › Speech packs › Pack server; the default points here:
  `https://raw.githubusercontent.com/Hemues/smart-translator-languages/main/packs.json`). Format: the app's `docs/04-language-packs.md` §3.
- **Releases** — the pack files themselves, as release assets (GitHub allows 2 GB per asset). The app downloads them
  straight into its private storage, checks the SHA-256 from the index over the whole stream, and installs only on a match.
- `components.json` + `make_index.py` — how `packs.json` is produced (sizes and hashes are computed, never typed).

## What is in the packs, and how big they are

| Pack (release `packs-v1`) | Download | On the phone | Covers |
| --- | ---: | ---: | --- |
| `sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2` — Parakeet-TDT-0.6B-v3, int8 | **487 MB** | 671 MB | speech recognition for **25 European languages in one model**: Bulgarian, Czech, Danish, German, Greek, English, Spanish, Estonian, Finnish, French, Croatian, Hungarian, Italian, Lithuanian, Latvian, Maltese, Dutch, Polish, Portuguese, Romanian, Russian, Slovak, Slovenian, Swedish, Ukrainian |
| `silero_vad.onnx` — Silero VAD v5 | 0.6 MB | 0.6 MB | sentence boundaries for hands-free listening (language-independent) |
| `sherpa-onnx-omnilingual-asr-1600-languages-300M-ctc-v2-int8-2026-02-05.tar.bz2` — Meta Omnilingual ASR 300M, int8 | 292 MB | 366 MB | speech recognition for the European languages Parakeet lacks: Albanian, Basque, Belarusian, Bosnian, Catalan, Galician, Georgian, Icelandic, Irish, Luxembourgish, Macedonian, Norwegian, Serbian, Turkish, Welsh (1,600 languages in total) |

| Voices (release `voices-v1`, Piper/VITS, fp32) | Download each | Languages |
| --- | ---: | --- |
| 31 voices — one medium voice per language, three Hungarian (anna, imre, berta), two English (US lessac, GB alan); Greek only low quality | 67–80 MB (≈ 2.1 GB together) | ca cs cy da de el en es eu fi fr hu is it lv nl no pl pt ro ru sk sl sq sr sv tr uk |

No Piper voice exists for Bulgarian, Estonian, Irish, Croatian, Lithuanian, Maltese, Belarusian, Macedonian, Bosnian or Galician — the phone's
own text-to-speech serves those. Per-voice dataset licences (CC0, CC-BY, CC-BY-SA …) are read from each MODEL_CARD into `packs.json`.

Translation models are **not** here (yet): the app uses ML Kit's on-device translation, whose ~30 MB per-language models
are downloaded by Google Play services (app › Languages screen). Voices: the `voices-v1` packs above, or the phone's TTS engine.

Recognition beyond Parakeet's 25 languages comes from the Omnilingual pack above (app 0.3.0 picks the pack per language); Whisper
would cover them too but does not run usefully on a phone (app FINDINGS F76/F78).

## Planned additions (each one = a release asset + an entry in `components.json`)

1. ~~Voices~~ — done 2026-09-29 (`voices-v1`). ~~Omnilingual ASR~~ — done (`packs-v1`).
2. **Parakeet with the corrected int8 recipe** (~898 MB) — the official pack loses ~20 pp WER on long utterances to the
   int8 quantisation of its convolutions; the re-export with MatMul-only int8 fixes it (app `tools/asr-finetune/export.sh`).
2. **Hungarian fine-tune of Parakeet** (`parakeet-hu-0.6b-int8`, app `docs/12`) — a second speech pack chosen per language.
3. Tier B translation (OPUS-MT, ~90 MB per direction) and voices (Piper, ~60 MB per voice) once the app has those engines;
   the index format already has `mt` and `tts` kinds for them.

## Adding or updating a pack

```bash
# 1. put the file in dist/ (never committed), 2. describe it in components.json, 3. regenerate the index
python make_index.py
# 4. upload the asset to the release the index names, 5. commit + push packs.json
gh release upload packs-v1 dist/<asset> --repo Hemues/smart-translator-languages
git add packs.json components.json && git commit -m "packs: add <id>" && git push
```

`python make_index.py --check` verifies that every entry in `packs.json` matches the file in `dist/` byte for byte.
A new release tag (e.g. `packs-v2`) is only needed when an asset with the same name changes; then `release_tag` in
`components.json` moves with it so old app versions keep working from the old tag.

## Licences

See [NOTICE.md](NOTICE.md): Parakeet-TDT-0.6B-v3 is CC-BY-4.0 (NVIDIA) and requires attribution; the sherpa-onnx export
and runtime are Apache-2.0; Silero VAD is MIT. Nothing non-commercial is or will be distributed here.
