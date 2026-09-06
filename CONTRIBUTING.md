# Contributing

IssueやPull Requestを歓迎します。

## 変更時の確認事項

1. `SKILL.md`の`name`と、`.claude-plugin/plugin.json`の`name`を一致させたまま変更しない。
2. 翻訳と独立解説を明確に分離する方針を維持する。
3. 原著PDF、翻訳本文、抽出画像など、再配布権限のない資料をコミットしない。
4. スクリプトを変更した場合は次を実行する。
   - `bash -n skills/rinkou-handout-builder/scripts/build_and_check.sh`
   - `python3 -m py_compile skills/rinkou-handout-builder/scripts/extract_annotations.py`
5. マニフェストを変更した場合は、`.claude-plugin/marketplace.json`と`.claude-plugin/plugin.json`がJSONとして妥当か確認する。
6. 個人の絶対パス、認証情報、APIキーを含めない。
7. 作業手順の本文を変えた場合は、Codex版（[rinkou-handout-builder](https://github.com/HR0101/rinkou-handout-builder)）と内容が食い違っていないか確認する。

改善内容と、その変更が必要な理由をPull Requestに記載してください。
