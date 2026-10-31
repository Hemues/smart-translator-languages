# Using smart-translator-languages (step by step)

Written 2026-10-31 (CET). Kind: data repository with an index generator and download scripts (no app code). It is used by the
Smart Translator app (its code is `mobile-applications/smart-translator`) and by the people who publish packs.
Current state: public repository, releases `packs-v1` and `voices-v1`, index of 34 entries, last commit 2026-09-29 (`7885bf4`).
Verified on 2026-10-31 from the workstation (`git`, `gh`, `curl`); the publish steps were not run.

Contents:

1. What a person can do with this repository
2. Requirements
3. Check the index (read-only)
4. How the app consumes the index and the files
5. Add a new voice or pack
6. Upgrade a pack or a voice (new name or new tag)
7. Remove a pack
8. Check a downloaded file by hand
9. Licence step
10. Troubleshooting

---

## 1. What a person can do with this repository

- **Read** the index as a user: `https://raw.githubusercontent.com/Hemues/smart-translator-languages/main/packs.json`.
- **Download** a pack or a voice from the release page: `https://github.com/Hemues/smart-translator-languages/releases`.
- **Publish** a new pack or voice (owner or integrator, on 11.1.0.2 as root, sections 5 to 7).
- **Check** that the index matches the files in `dist/` (section 3).

Nothing here runs on a phone. The app is in `mobile-applications/smart-translator`, and its installation guide is in that repository's
`docs/HOWTO-USE.md`.

## 2. Requirements

| Need | Check | Expected |
| --- | --- | --- |
| Python 3 on 11.1.0.2 | `python3 --version` | a 3.x version. The scripts use only the standard library. |
| The share | `ls /storage/Samba/Temp/git/mobile-applications/smart-translator-languages` | `AGENTS.md`, `README.md`, `components.json`, `dist/` and others |
| `git` | `git --version` | any recent version |
| `gh` (GitHub CLI) logged in as the owner's account, root only | `sudo -n gh auth status` (on 11.1.0.2) | a logged-in account with write rights to `Hemues/smart-translator-languages`. Not verified on 2026-10-31. |
| Free space in `dist/` | `du -sh dist` | about 2.8 GB on 2026-10-31 |

On the Windows workstation the `python` command is a Microsoft Store stub (checked 2026-10-31: "Python was not found"). Run the tools on
11.1.0.2 with `python3`, or install Python first.

## 3. Check the index (read-only)

```bash
cd /storage/Samba/Temp/git/mobile-applications/smart-translator-languages
python3 make_index.py --check
```

Expected output: one line per component, `OK <id>  <bytes> bytes`, and exit code 0. A line that starts with `MISSING dist/<name>`
or `BAD` means the file in `dist/` differs from the index: do not publish until it is fixed. The check reads every file in `dist/`
(2.8 GB), so it takes several minutes. Not re-run on 2026-10-31.

Check the repository state:

```bash
git -c core.fileMode=false status --short     # empty output = clean
git log --date=short --format='%ad %h %s'      # the four commits of 2026-09-29
```

Check the public read, from any machine:

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://raw.githubusercontent.com/Hemues/smart-translator-languages/main/packs.json
```

Expected: `200` (checked 2026-10-31, 32,672 bytes).

Check the releases and their assets:

```bash
gh release view packs-v1 --repo Hemues/smart-translator-languages --json assets -q '.assets[] | "\(.name) \(.size)"'
gh release view voices-v1 --repo Hemues/smart-translator-languages --json assets -q '.assets[] | "\(.name) \(.size)"'
```

Expected: three assets in `packs-v1` (the Parakeet archive 487,170,055 bytes, the Omnilingual archive 292,313,120 bytes, `silero_vad.onnx`
643,854 bytes) and 31 archives in `voices-v1` (67 to 80 MB each).

## 4. How the app consumes the index and the files

1. At start the app reads `packs.json` from `main` (the default *Pack server* of the app; settings › Speech packs › Pack server).
2. For every component the app knows, the index gives the file name, `bytes`, `sha256` and a list of `urls`. The first URL is this
   repository's release asset; the second is the upstream sherpa-onnx release (for the Parakeet, Silero, Omnilingual and Piper files).
3. The app downloads the first URL that answers into `<name>.part`, checks the size and the SHA-256 over the whole download, and only then
   installs it. A mismatch is never installed. The second URL is tried if the first one fails.
4. For a pack that is already installed, the app compares the index's `sha256` with the marker it wrote at install time. When they differ
   (and the auto-update switch is on), it downloads the new file to a `.part` name, checks it, renames the old file to `*.old`, moves
   the new file in, and deletes `*.old`. If a step fails after the rename, the old file is moved back.
5. If the index cannot be read, the app logs `pack index: could not fetch … (HTTP 404) — using the built-in list` (the text the app's
   design prints) and uses its built-in list, whose entries also carry the upstream URLs.

Consequence for a publisher: a change to `packs.json` on `main` reaches every install at its next start. A change to an asset under an
existing name reaches the installs that download it next. Read section 6 before changing an asset.

## 5. Add a new voice or pack

Run these steps as root on 11.1.0.2, in the repository folder. The owner decides when to add a voice. The example is a Piper voice; for
another kind of pack, replace step 1 and use the matching `kind` in `components.json`.

1. **Get the file.** The sherpa-onnx `tts-models` release names files `vits-piper-<locale>-<voice>-<quality>.tar.bz2`. The candidates
   are listed in `_release-scripts/piper-assets.txt` (536 names with sizes; a snapshot, its date not recorded). Download the chosen
   file into `dist/`:

   ```bash
   curl -fL -o dist/vits-piper-<locale>-<voice>-<quality>.tar.bz2 \
     https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-<locale>-<voice>-<quality>.tar.bz2
   ```

   Compare the byte size with the catalogue line. Write the download to a `.part` name first if the network is unreliable.
2. **Describe it.** `python3 add_components.py` adds the new file to `components.json`: language, voice and quality from the name; the
   licence and licence URL from the `MODEL_CARD` inside the archive. Read the new entry. Do not add a `gender` value (AGENTS.md, Traps).
3. **Build the index.** `python3 make_index.py` computes `bytes` and `sha256` from `dist/` and writes `packs.json`.
4. **Verify.** `python3 make_index.py --check` must print `OK` for every component, including the new one, and exit 0.
5. **Publish the asset** under the release tag named by the component's `release_tag` (`voices-v1` for voices, `packs-v1` for the
   others):

   ```bash
   gh release upload voices-v1 dist/vits-piper-<locale>-<voice>-<quality>.tar.bz2 --repo Hemues/smart-translator-languages
   ```

   Do not add `--clobber` here: a new name needs no overwrite.
6. **Verify the upload by download.** The fleet rule (2026-10-31): an upload that finishes in about a second may have stored only the
   metadata. Download the asset from the release page and compare its size and SHA-256 with `packs.json`:

   ```bash
   curl -sL -o /tmp/check.tar.bz2 https://github.com/Hemues/smart-translator-languages/releases/download/voices-v1/<file>
   sha256sum /tmp/check.tar.bz2     # must equal the sha256 in packs.json
   rm -f /tmp/check.tar.bz2
   ```

7. **Commit the metadata**, with explicit paths:

   ```bash
   git add packs.json components.json NOTICE.md
   git commit -m "packs: add <id>" -m "Co-Authored-By: <your attribution line>"
   git push origin main
   ```

   Read `git diff --cached --stat` before the commit: only the three files should appear.
8. **The app** sees the new entry at its next start. No app release is needed. The app offers the voice in *Settings › Voices*.

## 6. Upgrade a pack or a voice (new name or new tag)

An asset that an older build downloads must not be overwritten. The repository rule (README.md) says that a changed file gets a new asset
name, or the same name under a new release tag, so that old app versions keep working from the old tag.

1. Decide the new name: for example `vits-piper-<locale>-<voice>-<quality>-v2.tar.bz2`, or a new tag `voices-v2`.
2. If the tag is new, create it once: `gh release create voices-v2 --repo Hemues/smart-translator-languages --title "Voices v2" --notes "..."`.
   Write the notes with the licence of each file.
3. In `components.json`, change the component's `asset` (new name) and/or its `release_tag` (new tag). Change nothing else in other
   components.
4. Run section 5, steps 3 to 7.
5. Keep the old asset until no supported app build needs it. Delete it only then, and say so in the release notes (`gh release delete-asset`
   with the owner's word).

## 7. Remove a pack

Removing a pack from the index is a decision with an effect on installs. An app that has the pack installed keeps it, but no longer
manages it (the open item of the app's wave-11 notes). Before removing:

1. Tell the owner which devices are affected (the owner's own phones are the usual case).
2. Remove the component from `components.json`, run `make_index.py` and `make_index.py --check`, and commit `packs.json` and `components.json`.
3. Keep the asset in the release until no supported build needs it.

## 8. Check a downloaded file by hand

On a PC or the host, after a download:

```bash
sha256sum <file>                      # Linux and Git Bash
certutil -hashfile <file> SHA256      # Windows
```

Compare the value with the `sha256` of the same file in `packs.json`. The index is the only reference; the file name alone proves nothing.

## 9. Licence step

Every new file comes with its licence in the same commit:

- The licence of a Piper voice is in its model card (inside the archive). `add_components.py` reads it into `components.json` and
  `packs.json`.
- A model other than a Piper voice needs its own paragraph in `NOTICE.md`, with the model's page and its licence name.
- Attribution required by a licence (CC-BY-4.0 for Parakeet) must appear in `NOTICE.md`.
- Non-commercial licences are not distributed here (fleet rule and the app's standing rule). If a file's licence is unclear, it does not
  go into the index.
- A repository's own LICENSE file does not settle the licence of a dataset or a model (fleet rule). Read the model card and the source page.

## 10. Troubleshooting

### `make_index.py --check` prints `MISSING dist/<name>`

Cause: the file is not in `dist/` (git-ignored; it lives only on the share).
Fix: put the file back from its source (section 5, step 1) or remove the component from `components.json`.

### `make_index.py --check` prints `BAD <id>`

Cause: the file in `dist/` differs from the index in size or checksum (a re-download, a partial file, or an edited file).
Fix: download the file again from its upstream URL and compare with the index. If the upstream file changed, follow section 6. Do not edit `packs.json`
by hand.

### The app says `pack index: could not fetch … (HTTP 404)`

Cause: the raw `packs.json` cannot be read. The repository is not public, or the branch or the file name changed.
Fix: `curl -s -o /dev/null -w '%{http_code}\n' https://raw.githubusercontent.com/Hemues/smart-translator-languages/main/packs.json` must print
`200`. Check the visibility with `gh repo view Hemues/smart-translator-languages --json visibility`. The visibility is an owner decision.

### An app build downloads a file and the checksum does not match

Cause: a file under an old name was replaced after an older build had recorded its checksum.
Fix: restore the old file under its name, or give the new file a new name and tag (section 6). Never overwrite a published asset.

### `gh release upload` answers that the asset already exists

Cause: an asset with that name exists in the release.
Fix: use a new name (section 6). Use `--clobber` only when the owner has decided that no older build depends on the asset.
