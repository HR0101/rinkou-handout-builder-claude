#!/usr/bin/env python3
"""添削済みPDFの注釈をすべて列挙する。

PDFのコメントは注釈レイヤーに入っているため、ページを画像として見ても
pdftotext で抽出しても本文には現れない。反映漏れを防ぐため、ページ番号・
注釈種別・コメント本文・作成者を一覧にし、総数を最後に示す。

ハイライトや取り消し線が「どの語を選んでいるか」までは取り出さない。
選択範囲の特定は、出力されたページ番号をたよりに該当ページを目で確認する。

使い方:
    extract_annotations.py path/to/reviewed.pdf
    extract_annotations.py path/to/reviewed.pdf --format tsv
"""

import argparse
import sys
from pathlib import Path

# コメントを持ちうる注釈だけを対象にする（リンクや描画補助は除く）
COMMENT_SUBTYPES = {
    "Text",
    "FreeText",
    "Highlight",
    "Underline",
    "Squiggly",
    "StrikeOut",
    "Caret",
    "Ink",
    "Square",
    "Circle",
    "Line",
    "Polygon",
    "PolyLine",
    "Stamp",
    "FileAttachment",
    "Popup",
}


def load_pypdf():
    """pypdf を読み込む。無ければ導入方法を示して終了する。"""
    try:
        from pypdf import PdfReader
    except ImportError:
        print(
            "pypdf が必要です。次のいずれかで導入してください。\n"
            "    pip install pypdf\n"
            "    python3 -m pip install --user pypdf",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return PdfReader


def clean(value):
    """注釈の値を1行の文字列へ整える。"""
    if value is None:
        return ""
    text = str(value).replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
    return " ".join(text.split())


def collect(reader):
    """全ページの注釈を取り出す。Popup は親注釈の重複なので除く。"""
    found = []
    for page_index, page in enumerate(reader.pages, start=1):
        annotations = page.get("/Annots")
        if not annotations:
            continue
        for reference in annotations:
            try:
                annotation = reference.get_object()
            except Exception as error:  # 壊れた参照があっても他を落とさない
                print(
                    f"警告: {page_index}ページの注釈を読めませんでした: {error}",
                    file=sys.stderr,
                )
                continue

            subtype = clean(annotation.get("/Subtype")).lstrip("/")
            if subtype not in COMMENT_SUBTYPES or subtype == "Popup":
                continue

            # 本文は /Contents に入るが、リッチテキストしか持たない実装もある
            comment = clean(annotation.get("/Contents")) or clean(
                annotation.get("/RC")
            )

            found.append(
                {
                    "page": page_index,
                    "subtype": subtype,
                    "subject": clean(annotation.get("/Subj")),
                    "comment": comment,
                    "author": clean(annotation.get("/T")),
                }
            )
    return found


def main():
    parser = argparse.ArgumentParser(
        description="添削済みPDFの注釈を列挙する",
    )
    parser.add_argument("pdf", type=Path, help="添削済みPDFのパス")
    parser.add_argument(
        "--format",
        choices=("text", "tsv"),
        default="text",
        help="出力形式（既定: text）",
    )
    args = parser.parse_args()

    if not args.pdf.is_file():
        print(f"PDFが見つかりません: {args.pdf}", file=sys.stderr)
        raise SystemExit(1)

    PdfReader = load_pypdf()
    try:
        reader = PdfReader(str(args.pdf))
    except Exception as error:
        print(f"PDFを開けませんでした: {error}", file=sys.stderr)
        raise SystemExit(1)

    annotations = collect(reader)

    if args.format == "tsv":
        print("page\tsubtype\tauthor\tcomment")
        for item in annotations:
            print(
                f"{item['page']}\t{item['subtype']}\t{item['author']}\t{item['comment']}"
            )
    else:
        for index, item in enumerate(annotations, start=1):
            print(f"[{index}] p.{item['page']} {item['subtype']}", end="")
            if item["author"]:
                print(f" / {item['author']}", end="")
            print()
            if item["subject"]:
                print(f"    件名: {item['subject']}")
            if item["comment"]:
                print(f"    コメント: {item['comment']}")
            else:
                print("    コメント: （本文なし。ハイライト等の選択箇所そのものが指摘）")

    print(f"\n注釈の総数: {len(annotations)} 件 / 全 {len(reader.pages)} ページ")
    if not annotations:
        print(
            "注釈が0件でした。添削が画像として貼られている可能性があるため、"
            "全ページを目視でも確認してください。"
        )


if __name__ == "__main__":
    main()
