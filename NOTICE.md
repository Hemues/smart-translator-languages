# Notices and attributions

This repository redistributes third-party model files unchanged, as release assets. Their licences apply to the files;
nothing here alters them.

## Parakeet-TDT-0.6B-v3 (int8 ONNX export)

- Model: **NVIDIA Parakeet-TDT-0.6B-v3**, https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3
- Licence: **Creative Commons Attribution 4.0 International (CC-BY-4.0)** — https://creativecommons.org/licenses/by/4.0/
- Attribution: "Parakeet-TDT-0.6B-v3 © NVIDIA Corporation, licensed under CC-BY-4.0." The model was trained on the Granary
  dataset (CC-BY-4.0) and NVIDIA's own data; see the model card.
- Export/packaging: **sherpa-onnx** (k2-fsa), Apache License 2.0 — https://github.com/k2-fsa/sherpa-onnx. The asset
  `sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2` is the file published in the sherpa-onnx `asr-models` release,
  byte for byte (sha256 `5793d0fd397c5778d2cf2126994d58e9d56b1be7c04d13c7a15bb1b4eafb16bf`).

## Silero VAD

- Model: **Silero VAD v5.1.2** (`silero_vad.onnx`), https://github.com/snakers4/silero-vad
- Licence: **MIT** — Copyright (c) 2020-present Silero Team. The asset is the copy published in the sherpa-onnx
  `asr-models` release (sha256 `9e2449e1087496d8d4caba907f23e0bd3f78d91fa552479bb9c23ac09cbb1fd6`).

## The index and scripts in this repository

`packs.json`, `components.json` and `make_index.py` are © Hemues and released under the MIT licence.
