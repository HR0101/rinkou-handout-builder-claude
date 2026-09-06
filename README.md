# rinkou-handout-builder-claude

原著PDFの指定範囲から、次の要素を備えた日本語のLaTeX輪講資料を作成・修正・検証するためのClaude Code用スキルです。

- 指定範囲の欠落のない全文翻訳
- 翻訳本文とは独立した技術解説
- 原典から抽出した図と正確な数式
- pLaTeX／dvipdfmxによるPDF生成
- 埋め込み画像、ページ範囲、最終レイアウトの検査
- 添削済みPDFの注釈抽出と、指摘事項の反映漏れ防止

このリポジトリには、書籍・論文のPDF、翻訳成果物、抽出画像は含まれていません。利用者自身が適法に利用できる原典を用意してください。

Codex／ChatGPT向けの同名スキルは [rinkou-handout-builder-codex](https://github.com/HR0101/rinkou-handout-builder-codex) にあります。作業手順は共通で、本リポジトリはPDFの読み取りやファイル操作をClaude Codeのツールに合わせて調整したものです。

## インストール

### プラグインとして導入する（推奨）

Claude Codeで次の2つを実行します。

```text
/plugin marketplace add HR0101/rinkou-handout-builder-claude
/plugin install rinkou-handout-builder@rinkou-handout-builder-claude
```

更新するときは次を実行します。

```text
/plugin marketplace update rinkou-handout-builder-claude
```

### スキルだけを手動で置く

プラグイン管理を使わず、個人用スキルとして置くこともできます。

```bash
git clone --depth 1 https://github.com/HR0101/rinkou-handout-builder-claude.git /tmp/rinkou-claude
mkdir -p "$HOME/.claude/skills"
cp -R /tmp/rinkou-claude/skills/rinkou-handout-builder "$HOME/.claude/skills/"
rm -rf /tmp/rinkou-claude
```

プロジェクト内だけで共有する場合は、リポジトリの`.claude/skills/`へ同じディレクトリを置きます。この場合はチームの全員が同じスキルを使えます。

導入後にClaude Codeがスキルを認識しない場合は、セッションを再起動してください。

## 使い方

スキルは説明文にもとづいて自動的に読み込まれます。輪講資料の作成・修正・完成確認を依頼すると、Claudeがこのスキルを選びます。

```text
原典PDFの印刷ページ33〜42、第1.6節から第1.6.3.2節までの輪講資料を作ってください。
既存のhandout.texがあれば修正し、完成PDFを全ページ確認してください。
```

明示的に呼び出す場合は、スキル名をスラッシュコマンドとして指定します。

```text
/rinkou-handout-builder:rinkou-handout-builder
```

プラグインとして導入した場合は、次の2つの専用コマンドも使えます。

```text
/rinkou-handout-builder:build 原典.pdf 33-42 1.6-1.6.3.2
/rinkou-handout-builder:review 添削済み.pdf handout.tex
```

`build`は資料の作成・修正とPDF検証を、`review`は添削済みPDFの注釈を全件抽出したうえでの反映を行います。

対象PDF、印刷ページ範囲、開始節、終了節、出力先を明記すると安定します。添削済みPDFがある場合は、そのパスも渡してください。

## 必要な外部コマンド

LaTeXのビルドと検査には次が必要です。

- `platex`
- `dvipdfmx`
- `pdfinfo`
- `pdfimages`
- `pdftoppm`（図の細部を高解像度で確認するとき）

macOSでは、TeX Live系ディストリビューションとPopplerを用意してください。環境によってインストール方法が異なるため、それぞれの公式手順を確認してください。

添削済みPDFの注釈を抽出する場合のみ、Python 3と`pypdf`が必要です。

```bash
pip install pypdf
```

## 同梱スクリプト

### ビルドと検査

```bash
skills/rinkou-handout-builder/scripts/build_and_check.sh path/to/handout.tex
```

出力先を指定する場合：

```bash
skills/rinkou-handout-builder/scripts/build_and_check.sh path/to/handout.tex path/to/output.pdf
```

pLaTeXを2回実行してからPDFを生成し、未定義参照、画像ドライバの問題、埋め込み画像数、ページ数を検査します。最終的な全ページの目視確認は、スキルの指示に従って別途行います。

### 添削PDFの注釈抽出

```bash
skills/rinkou-handout-builder/scripts/extract_annotations.py path/to/reviewed.pdf
```

ページ番号、注釈種別、コメント本文、作成者を一覧にし、総数を表示します。添削のコメントは注釈レイヤーにあるため、ページを画像として見ても`pdftotext`で抽出しても本文には現れません。反映漏れを防ぐために使います。

## リポジトリ構成

```text
.
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── .github/
│   └── workflows/
│       └── validate.yml
├── commands/
│   ├── build.md
│   └── review.md
├── skills/
│   └── rinkou-handout-builder/
│       ├── SKILL.md
│       ├── references/
│       │   ├── quality-checklist.md
│       │   └── review-informed-style-guide.md
│       └── scripts/
│           ├── build_and_check.sh
│           └── extract_annotations.py
├── tools/
│   └── validate.py
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
└── SECURITY.md
```

## 開発者向け

変更を加えたら、公開前に定義ファイルを検証してください。

```bash
python3 tools/validate.py
```

plugin.jsonとmarketplace.jsonのJSON妥当性、必須フィールド、プラグイン名の一致、SKILL.mdのフロントマター、スキル名とディレクトリ名の一致、SKILL.mdが参照するファイルの実在、同梱スクリプトの実行権限と構文を確認します。同じ検証がpushとプルリクエストのたびにGitHub Actionsでも実行されます。

## 著作権上の注意

本スキルは作業手順を提供するものであり、第三者の原著・図・翻訳を再配布する権利を与えるものではありません。原典の利用、翻訳、引用、図の掲載、成果物の共有については、著作権法、所属機関の規程、ライセンス、引用要件を確認してください。

## ライセンス

スキル本体と付属スクリプトは[MIT License](LICENSE)で公開します。
