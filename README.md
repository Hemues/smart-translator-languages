# smart-translator-languages

Language packs for the **Smart Translator** Android app ([Hemues/smart-translator-mobileapplication](https://github.com/Hemues/smart-translator-mobileapplication), private),
separated from the app so that new languages and better models can ship without an app update. This repository is **public**
(since 2026-10-01; checked with `gh repo view` on 2026-10-31), because the app's default download point must be readable without a login.

It is not the app, it is not the builds (those are in `smart-translator-mobileapplication-images`), and it holds no personal data or
voice recordings. A personal voice pack never goes here (see AGENTS.md).

## Start here (reading order)

1. This README: what is in the packs, how big they are, how the index is built.
2. [AGENTS.md](AGENTS.md): the rules for changing the index, the traps, the verified commands.
3. [docs/HOWTO-USE.md](docs/HOWTO-USE.md): step by step, how the app consumes the index, how to add or upgrade a voice or a model.
4. [LESSONS-LEARNED.md](LESSONS-LEARNED.md): postmortems (the gender labels, the visibility change, the 404 fallback).
5. [STORYLINE.md](STORYLINE.md): how the repository came to be, from 2026-09-29.
6. [NOTICE.md](NOTICE.md): the licences of every redistributed file. Read it before you publish anything.

## Current state (2026-10-31)

| Item | State | How checked |
| --- | --- | --- |
| Visibility | **PUBLIC** | `gh repo view Hemues/smart-translator-languages --json visibility`, 2026-10-31 |
| Default index URL | `https://raw.githubusercontent.com/Hemues/smart-translator-languages/main/packs.json` | the app's default; `packs.json` `generated` = `2026-09-29T14:21:29Z` |
| Index entries | 34 components: 1 Parakeet pack, 1 VAD file, 1 Omnilingual pack, 31 voices | the index file, read 2026-10-31 |
| Releases | `packs-v1` (created 2026-09-29 13:37 UTC: Parakeet, VAD, Omnilingual), `voices-v1` (2026-09-29 14:11 UTC: 31 Piper voices) | `gh release list`, 2026-10-31 |
| Commits on `main` | 4, from `c0e4f25` (2026-09-29) to `7885bf4` (2026-09-29). Nothing changed since. | `git log`, 2026-10-31 |
| Working tree | clean (`git status` shows nothing) | `git status`, 2026-10-31 |
| Local `dist/` folder | 2.8 GB of pack files, git-ignored, kept on the share only | `ls`, 2026-10-31 |
| Languages with speech recognition | 25 (Parakeet) plus 15 more (Omnilingual) | the index's `languages` lists |
| Languages with a Piper voice | 28 (31 voices, three Hungarian) | `voices-v1` |

## What is in the packs, and how big they are

| Pack (release `packs-v1`) | Download | On the phone | Covers |
| --- | ---: | ---: | --- |
| `sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2`, Parakeet-TDT-0.6B-v3, int8 | **487 MB** | 671 MB | speech recognition for **25 European languages in one model**: Bulgarian, Czech, Danish, German, Greek, English, Spanish, Estonian, Finnish, French, Croatian, Hungarian, Italian, Lithuanian, Latvian, Maltese, Dutch, Polish, Portuguese, Romanian, Russian, Slovak, Slovenian, Swedish, Ukrainian |
| `silero_vad.onnx`, Silero VAD v5 | 0.6 MB | 0.6 MB | sentence boundaries for hands-free listening (language-independent) |
| `sherpa-onnx-omnilingual-asr-1600-languages-300M-ctc-v2-int8-2026-02-05.tar.bz2`, Meta Omnilingual ASR 300M, int8 | 292 MB | 366 MB | speech recognition for the European languages Parakeet lacks: Albanian, Basque, Belarusian, Bosnian, Catalan, Galician, Georgian, Icelandic, Irish, Luxembourgish, Macedonian, Norwegian, Serbian, Turkish, Welsh (1,600 languages in total) |

| Voices (release `voices-v1`, Piper/VITS, fp32) | Download each | Languages |
| --- | ---: | --- |
| 31 voices, one medium voice per language, three Hungarian (anna, imre, berta), two English (US lessac, GB alan); Greek only low quality | 67–80 MB (about 2.1 GB together) | ca cs cy da de el en es eu fi fr hu is it lv nl no pl pt ro ru sk sl sq sr sv tr uk |

No Piper voice exists for Bulgarian, Estonian, Irish, Croatian, Lithuanian, Maltese, Belarusian, Macedonian, Bosnian or Galician. The
phone's own text-to-speech serves those. Per-voice dataset licences (CC0, CC-BY, CC-BY-SA and others) are read from each MODEL_CARD
into `packs.json`.

Translation models are **not** here. The app uses ML Kit's on-device translation, whose models of about 30 MB per language are
downloaded by Google Play services (app › Languages screen). Voices: the `voices-v1` packs above, or the phone's TTS engine.

Recognition beyond Parakeet's 25 languages comes from the Omnilingual pack (app 0.3.0 picks the pack per language). Whisper would cover
them too but does not run usefully on a phone (app FINDINGS F76/F78).

## How the index is built

The index is generated, never typed. Three files make it:

- `components.json`: the metadata of each component (id, kind, language, asset file name, upstream URL, licence, release tag, and for
  voices a `gender` hint that `add_components.py` writes from a name table; see AGENTS.md, *voice gender labels*).
- `make_index.py`: computes `bytes` and `sha256` from the file in `dist/`, builds the URL list (our release first, the upstream URL second),
  and writes `packs.json`. `python make_index.py --check` verifies every entry against `dist/` and exits 1 on a mismatch.
- `add_components.py`: describes the new files in `dist/` that `components.json` does not know yet. Language, voice and quality come
  from the file name; the licence comes from the `MODEL_CARD` inside the archive.

The app verifies the SHA-256 of the whole download, whichever URL answered. A file that does not match is never installed.

## Adding or updating a pack (short form)

```bash
# 1. put the file in dist/ (never committed), 2. describe it in components.json, 3. regenerate the index
python make_index.py
# 4. upload the asset to the release the index names, 5. commit + push packs.json
gh release upload packs-v1 dist/<asset> --repo Hemues/smart-translator-languages
git add packs.json components.json && git commit -m "packs: add <id>" && git push
```

`python make_index.py --check` verifies that every entry in `packs.json` matches the file in `dist/` byte for byte.
A new release tag (for example `packs-v2`) is needed when an asset with the same name changes. Then `release_tag` in
`components.json` moves with it, so old app versions keep working from the old tag. The full procedure, with the upgrade rule and the
licence step, is in [docs/HOWTO-USE.md](docs/HOWTO-USE.md).

Scripts that publish: `fetch_voices.sh` (downloads the 31 voices and the Omnilingual pack from the sherpa-onnx releases, describes them,
rebuilds the index, commits, pushes and uploads the assets; run as root on 11.1.0.2) and `_release-scripts/mk_languages_repo.sh` in
`mobile-applications/_release-scripts/` (creates the repository and the release when missing).

## Planned additions (each one = a release asset + an entry in `components.json`)

1. ~~Voices~~ done 2026-09-29 (`voices-v1`). ~~Omnilingual ASR~~ done (`packs-v1`).
2. **Parakeet with the corrected int8 recipe** (about 898 MB). The README of the time says the official pack loses about 20 points of WER on
   long utterances to the int8 quantisation of its convolutions, and that a re-export with MatMul-only int8 fixes it (app
   `tools/asr-finetune/export.sh`). This is a claim from the planning documents; it was not re-measured on 2026-10-31.
3. **Hungarian fine-tune of Parakeet** (`parakeet-hu-0.6b-int8`, app `docs/12-hungarian-asr-finetune-plan.md`), a second speech pack chosen per
   language. Parked on 2026-09-29.
4. Tier B translation (OPUS-MT, about 90 MB per direction) and more voices once the app has those engines. The index format already has
   `mt` and `tts` kinds for them.

## Licences

See [NOTICE.md](NOTICE.md). Parakeet-TDT-0.6B-v3 is CC-BY-4.0 (NVIDIA) and requires attribution. The sherpa-onnx export and runtime are
Apache-2.0. Silero VAD is MIT. The Piper voices carry the licence of their dataset, read from each model card into `packs.json`.
Nothing non-commercial is or will be distributed here. The index and scripts are © Hemues under the MIT licence (NOTICE.md).

## Documentation map

| File | Purpose |
| --- | --- |
| `README.md` | this file: contents, sizes, state, how the index is built |
| `AGENTS.md` | rules, traps and verified commands for anyone who changes the index |
| `docs/HOWTO-USE.md` | step by step: consume the index, add a voice, upgrade a model, check the hashes |
| `LESSONS-LEARNED.md` | dated postmortems with their rules |
| `STORYLINE.md` | the repository's history by phase |
| `NOTICE.md` | licences and attributions of every redistributed file |
| `components.json`, `packs.json` | the metadata and the generated index (do not edit `packs.json` by hand) |
| `make_index.py`, `add_components.py`, `fetch_voices.sh` | the index tooling and the voice download script |
