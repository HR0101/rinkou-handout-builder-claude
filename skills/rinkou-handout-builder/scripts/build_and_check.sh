#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 path/to/handout.tex [path/to/output.pdf]" >&2
  exit 2
}

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage
fi

for command_name in platex dvipdfmx pdfinfo pdfimages; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Required command not found: $command_name" >&2
    exit 1
  fi
done

input_arg=$1
if [[ ! -f "$input_arg" ]]; then
  echo "TeX file not found: $input_arg" >&2
  exit 1
fi

tex_dir=$(cd "$(dirname "$input_arg")" && pwd -P)
tex_name=$(basename "$input_arg")
tex_stem=${tex_name%.tex}
tex_path="$tex_dir/$tex_name"

if [[ $# -eq 2 ]]; then
  output_arg=$2
  output_dir=$(cd "$(dirname "$output_arg")" && pwd -P)
  output_pdf="$output_dir/$(basename "$output_arg")"
else
  output_pdf="$tex_dir/$tex_stem.pdf"
fi

build_dir=$(mktemp -d "/tmp/rinkou-build.XXXXXX")
cleanup() {
  rm -rf "$build_dir"
}
trap cleanup EXIT

cd "$tex_dir"

platex -interaction=nonstopmode -halt-on-error \
  -output-directory="$build_dir" "$tex_name" \
  >"$build_dir/platex-pass1.log" 2>&1

platex -interaction=nonstopmode -halt-on-error \
  -output-directory="$build_dir" "$tex_name" \
  >"$build_dir/platex-pass2.log" 2>&1

dvipdfmx -o "$output_pdf" "$build_dir/$tex_stem.dvi" \
  >"$build_dir/dvipdfmx.log" 2>&1

if grep -q "Unparsed material at end of special" "$build_dir/dvipdfmx.log"; then
  echo "PDF build contains an unparsed image special. Check dvipdfmx driver settings." >&2
  sed -n '1,160p' "$build_dir/dvipdfmx.log" >&2
  exit 1
fi

if grep -Eq "undefined references|Reference .* undefined" "$build_dir/platex-pass2.log"; then
  echo "LaTeX references remain undefined after the second pass." >&2
  grep -E "undefined references|Reference .* undefined" "$build_dir/platex-pass2.log" >&2
  exit 1
fi

expected_images=$(awk '
  /^[[:space:]]*%/ { next }
  /\\includegraphics/ { count++ }
  END { print count + 0 }
' "$tex_path")

embedded_images=$(pdfimages -list "$output_pdf" | awk '
  $3 == "image" { count++ }
  END { print count + 0 }
')

if (( embedded_images < expected_images )); then
  echo "Embedded image check failed: expected at least $expected_images, found $embedded_images." >&2
  exit 1
fi

page_count=$(pdfinfo "$output_pdf" | awk -F: '/^Pages:/ { gsub(/[[:space:]]/, "", $2); print $2 }')

echo "Built: $output_pdf"
echo "Pages: $page_count"
echo "TeX image references: $expected_images"
echo "Embedded raster images: $embedded_images"
echo "Next: render every PDF page and inspect it visually."
