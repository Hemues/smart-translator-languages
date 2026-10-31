# Storyline: smart-translator-languages

Written 2026-10-31 (CET). Sources: the four commits on `main` (`git log --date=short --reverse --format='%ad %h %s'`), the release
records (`gh release list`, 2026-10-31), the release log `_release-scripts/fetch_voices.log` and `mk_languages_repo.log`, the
file dates in `dist/` and `packs.json`, the app's AGENTS.md and STORYLINE of the app (its phase 6 and 7), and the commit
`9867546` of the app repository. Times are CET unless marked UTC. Dates are file or commit dates, or dates written in a document.

## Summary

This repository exists because the Smart Translator app needs speech packs and voices that can be updated without an app release. It
holds a public index (`packs.json`) and the metadata that generates it (`components.json`), plus the scripts that describe and check
the files. The files themselves are GitHub release assets. The repository was created on 2026-09-29, in one afternoon, with the speech
pack (Parakeet), the voice-activity file, the Omnilingual pack and 31 Piper voices. It has been public since 2026-10-01. Nothing has
been committed since 2026-09-29 (four commits in total). The app 0.6.0 reads this index at every start (design, not yet run on a phone).

## Timeline at a glance

| Phase | Dates (CET) | What | Outcome |
| --- | --- | --- | --- |
| 1. Speech pack and index | 2026-09-29, 15:34 to 15:38 | Parakeet and Silero files downloaded; repository created private; `packs-v1` release | index and tooling committed (`c0e4f25`) |
| 2. Voices and Omnilingual | 2026-09-29, 16:03 to 16:13 | `fetch_voices.sh` downloads 31 voices and the Omnilingual pack; `voices-v1` release | commit `5fb99f8` (1,521 lines added) |
| 3. Index corrections | 2026-09-29, 16:21 to 16:27 | voices point at `voices-v1`; gender hints; README table | commits `e57f97b`, `7885bf4` |
| 4. Public repository | 2026-10-01 | visibility changed to public by the owner | the app's default index answers without a login |
| 5. Quiet period | 2026-10-01 to 2026-10-31 | no commit in this repository | index unchanged |
| 6. Documentation pass | 2026-10-31 | this documentation | README, AGENTS, LESSONS, STORYLINE, HOWTO-USE |

## Phase 1 - Speech pack and index (2026-09-29, afternoon)

**The goal.** The app's speech recognition for Hungarian and the other 24 European languages of the Parakeet model had to come from a file the
app downloads, not from the APK. The later wave-11 decision D1 (2026-10-28, `docs/LANES-ST-W11-2026-10-28.md`) keeps the same rule: the
Parakeet pack is not bundled, because 487 MB would be re-shipped with every app update.

**What was built.** The Parakeet-TDT-0.6B-v3 int8 export of sherpa-onnx (487,170,055 bytes, sha256 `5793d0fd…`, CC-BY-4.0) and the Silero VAD v5.1.2
file (643,854 bytes, MIT). `components.json` describes them; `make_index.py` computes the sizes and checksums; the first `packs.json` was
generated at 14:21 UTC (16:21 CET) and is the index that every later version builds on. `NOTICE.md` records the licences.
`mk_languages_repo.sh` (run as root on 11.1.0.2) created the repository and the release `packs-v1` (13:37 UTC, 15:37 CET) and uploaded
the two files. The log records the repository as PRIVATE.

**What went wrong.** The repository was created private by the script's default. The app's default index needs a public repository,
so the visibility had to change before the default download point worked without a login (phase 4). No failure was recorded for the
first run.

**Decisions.** The pack files are release assets and never git objects, because GitHub caps git files at 100 MB. Licences travel
with the files. The repository name follows the app's name (`smart-translator-…`).

## Phase 2 - Voices and Omnilingual (2026-09-29, late afternoon)

**The goal.** Speech output in the app's languages: the phone's own text-to-speech is missing for several languages and of poor quality
for others. Piper (VITS) voices from the sherpa-onnx `tts-models` release cover 28 European languages.

**What was built.** `fetch_voices.sh` downloads one medium voice per language (three for Hungarian: anna, imre, berta; two for
English: US lessac, GB alan) and the Omnilingual CTC 300M int8 pack for the 15 languages that Parakeet lacks (292,313,120 bytes).
It skips a file when the local size equals the remote Content-Length, then runs `add_components.py`, `make_index.py` and
`make_index.py --check`, commits, pushes and uploads the assets. Its log ends at 16:13 with 31 voice assets and three packs listed.

**What went wrong.** The script uploads with `--clobber`, so a re-run would replace an asset under its name (LESSONS-LEARNED.md, 2026-10-31).
The Piper catalogue (`_release-scripts/piper-assets.txt`, 536 names) is larger than the 31 voices chosen; the choice was made by hand.

**Decisions.** One voice per language, one of quality "medium" where it exists. Greek has only a low-quality voice, and the index says so.
Ten European languages have no Piper voice (Bulgarian, Estonian, Irish, Croatian, Lithuanian, Maltese, Belarusian, Macedonian, Bosnian,
Galician); the phone's text-to-speech serves them.

## Phase 3 - Index corrections (2026-09-29, late afternoon)

**What was built.** Commit `e57f97b` moved the voice entries to the `voices-v1` release (`release_tag` per component), and added a
`gender` field to 26 voices (`add_components.py`, `GENDER` table). Commit `7885bf4` put the voices and the Omnilingual pack into the
README's pack table.

**What went wrong.** The gender field was added from a name table, which the app's own rules forbid for a voice's speaker (LESSONS-LEARNED.md,
2026-10-31, OPEN). It is the only field in the index that the app presents as a fact about a person.

**Decisions.** None recorded for the gender field. It is an open owner decision.

## Phase 4 - Public repository (2026-10-01)

**What happened.** The owner made the repository public. The app's commit `9867546` (2026-10-01) records the check: the raw `packs.json`
answers 200 with 34 entries, which is finding F102 of the app's `docs/FINDINGS.md`. The app's 0.3.1 build (versionCode 4, the Play upload
build) followed the same day, and on the emulator it read the index: "34 of 34 entries usable". The Hungarian voice pack installed from
the project's own release in 22 seconds.

**Why it mattered.** Until then the app's default index could not be read without a login (LESSONS-LEARNED.md, 2026-10-01). The app
falls back to its built-in list in that case, so no install broke, but no install got the packs from this repository either.

**Decisions.** The owner decided on public packs. The app's code repository stayed private (`Hemues/smart-translator-mobileapplication`).

## Phase 5 - Quiet period (2026-10-01 to 2026-10-31)

No commit was made to this repository in 32 days. The index on `main` stayed as `packs.json` generated at 14:21 UTC on 2026-09-29.
No change in this repository is recorded for the app's 0.4.0, 0.5.0 or 0.6.0 work (own voices, device enrolment, start without asking).
The wave-11 pack defaults of 0.6.0 read the same index according to the app's AGENTS.md. The Parakeet re-export (about 898 MB) and the
Hungarian fine-tune stayed as planned candidates in the README. Their status: parked on 2026-09-29, not measured here.

## Phase 6 - Documentation pass (2026-10-31)

The owner asked for documentation that a local model could continue from. This pass added README (rewritten, CRLF kept), AGENTS.md,
LESSONS-LEARNED.md, STORYLINE.md and docs/HOWTO-USE.md. It checked on 2026-10-31: the visibility (PUBLIC), the release list (`packs-v1`,
`voices-v1`), the raw index URL (HTTP 200, 32,672 bytes), the index entry count (34), the gender count (26), and that the working tree is
clean. Nothing was committed, pushed, published or changed on the host.

## Where it stands now (2026-10-31)

- Index: 34 entries (1 Parakeet, 1 Silero, 1 Omnilingual, 31 voices), generated 2026-09-29 14:21 UTC.
- Public, releases `packs-v1` and `voices-v1`, working tree clean, last commit `7885bf4` (2026-09-29).
- Open owner decisions: the gender labels; the `--clobber` in `fetch_voices.sh`; the creation script's `--private` line; the Parakeet
  re-export and the Hungarian fine-tune (candidates only).
- Next planned additions (README): corrected Parakeet int8 export, Hungarian fine-tune, Tier B translation packs.
