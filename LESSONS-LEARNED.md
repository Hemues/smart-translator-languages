# Lessons learned: smart-translator-languages

Written 2026-10-31 (CET) by the documentation lane, from the git history (4 commits, 2026-09-29), `fetch_voices.sh`, the release
log in `_release-scripts/`, the app's AGENTS.md and the fact checks of 2026-10-31. Newest first. Each entry has symptom, root cause,
fix and rule. Entries marked **OPEN** are not fixed.

Index:

- 2026-10-31 OPEN: voice gender labels come from a hand-written name table
- 2026-10-31 OPEN: `fetch_voices.sh` re-uploads with `--clobber`
- 2026-10-31: the repository is public, the creation script says private
- 2026-10-01: the default index answered 404 while the repository was private
- 2026-09-29: the Piper list has 536 names, the app uses 31 voices (a catalogue, not a list of decisions)
- 2026-09-29: the release tag and the asset name are part of the compatibility of old builds

---

## 2026-10-31 OPEN - voice gender labels come from a hand-written name table

- **Version / commit:** `e57f97b` (2026-09-29, "packs.json: voices point at the voices-v1 release; gender hints").
- **Symptom:** 26 voices carry a `gender` value in `packs.json` (11 `"f"`, 15 `"m"`, counted 2026-10-31). The app's voice picker
  shows "· female" or "· male" after the voice name.
- **Root cause:** `add_components.py` holds a `GENDER` dictionary keyed by voice name, filled "where the voice's name or card makes it
  clear". A name is a proxy for a person's sex. The app's own standing rules say a voice must never be labelled male or female from its
  name, and that a label of that kind about a person is a high-risk matter under the EU AI Act if distributed (smart-translator
  AGENTS.md, trap table).
- **Fix:** none yet. Owner decision: remove the field and the picker suffix, or replace it with a measured label that the user chooses.
- **Rule:** no table of names may write a label that the app presents as a fact about a voice's speaker.
- **Detection gap:** nothing reads the index's `gender` field against the rule. The two repositories are not tested together.

## 2026-10-31 OPEN - `fetch_voices.sh` re-uploads with `--clobber`

- **Version / commit:** `5fb99f8` (2026-09-29, the voices commit) and the script as it stands.
- **Symptom:** the script runs `gh release upload voices-v1 dist/vits-piper-*.tar.bz2 --clobber` and
  `gh release upload packs-v1 "dist/$OMNI" --clobber`. A re-run replaces an asset under the same name without any warning.
- **Root cause:** the script was written for the first upload, when no build depended on the assets. Its re-run path does not ask
  whether an older build still reads that asset.
- **Fix:** none yet. Proposed: upload a changed file under a new name or a new tag, and remove `--clobber` from the script. The rule
  is in README.md (*Adding or updating a pack*) and in docs/HOWTO-USE.md section 11.
- **Rule:** a published asset is immutable. A change is a new name or a new tag, never an overwrite.
- **Detection gap:** the release log shows the upload, not the old size or checksum.

## 2026-10-31 - the repository is public, the creation script says private

- **Version / commit:** `_release-scripts/mk_languages_repo.sh` (created 2026-09-29 15:37 CEST); the public switch was made by hand
  on 2026-10-01.
- **Symptom:** the script's log shows `https://github.com/Hemues/smart-translator-languages PRIVATE` (2026-09-29 15:38). The
  2026-10-31 check shows PUBLIC.
- **Root cause:** the first creation was private (it was new). The owner made it public on 2026-10-01 so that the app's default
  index answers without a login. The script was not updated, so it still says `--private`.
- **Fix:** this document records the state. The script's flag should be commented, not removed, so a re-creation is a decision.
- **Rule:** repository visibility is an owner decision with a consequence (the index). Check it with `gh repo view` after any change.

## 2026-10-01 - the default index must be public, and the public switch was made before the first public read

- **Version / commit:** the app's default index URL is read at every start by 0.2.0 and later builds (design, `docs/04-language-packs.md`).
- **Symptom:** no failure is recorded. The app's design says that when the index cannot be fetched it logs
  `pack index: could not fetch … (HTTP 404) — using the built-in list` and uses the built-in list (smart-translator AGENTS.md). That line is the
  expected log text for a private or missing repository; it was not observed in a recorded run.
- **Root cause (design):** the index is read from `raw.githubusercontent.com`, which answers a login-free read only for a public repository.
  The app carries no token.
- **Fix:** the owner made the repository public on 2026-10-01. Commit `9867546` of the app repository records the check: the raw
  `packs.json` answered 200 with 34 entries (finding F102). On the emulator the app read the index: "34 of 34 entries usable", and the
  Hungarian voice pack installed from the project's own release in 22 seconds (smart-translator AGENTS.md, 2026-10-01).
- **Rule:** the app's default download point is a public address. Any change of that address or its visibility is a release-level change,
  checked from the app itself.
- **Detection gap:** the fallback is silent for the user. The user sees only the built-in list, not that the index is missing.

## 2026-09-29 - the Piper list has 536 names, the app uses 31 voices

- **Version / commit:** `_release-scripts/piper-assets.txt` (a snapshot of the sherpa-onnx `tts-models` names with sizes, 536 lines,
  file date 2026-09-29 15:59; the source date of the snapshot is not recorded).
- **Symptom:** a reader may think the 536 names are available. They are candidates: variants of quality (low, medium, high) and
  precision (fp16, int8, fp32).
- **Root cause:** the catalogue lists every variant of every voice. The repository carries one medium voice per language, chosen by
  hand (`fetch_voices.sh` lists them).
- **Fix:** none needed. The choice is recorded in `fetch_voices.sh` and in README.md.
- **Rule:** a candidate list is not a decision. Write the decision (which name, why) into `components.json` with its licence.

## 2026-09-29 - the release tag and the asset name are part of old builds' compatibility

- **Version / commit:** the index format (`index_version` 1, `min_app_version` 2) and the `release_tag` per component.
- **Symptom:** none. This is the rule the first index set up, written in README.md on 2026-09-29.
- **Root cause:** an installed build verifies a download against the checksum it reads. A new file under an old name means the
  checksum the old build expects no longer matches the file a new download brings.
- **Fix:** the rule: a changed asset gets a new name or a new tag, and `release_tag` moves for that component only.
- **Rule:** a published asset never changes under its name. Read this entry before any upload.
- **Detection gap:** none automatic. The check is manual, and `--clobber` in `fetch_voices.sh` works against it (see the entry above).
