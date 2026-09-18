#!/usr/bin/env bash
# Chạy site ở máy với đủ font và tìm kiếm:
#   1. subset font cho toàn bộ nội dung hiện có
#   2. build một lần rồi để Pagefind lập chỉ mục (hugo server không tự làm)
#   3. mở hugo server, kèm cả bài draft
#
#   tools/dev.sh
set -euo pipefail
cd "$(dirname "$0")/.."

echo "① Font"
./.venv/bin/python tools/fonts/build.py --dev

echo "② Chỉ mục tìm kiếm"
build_dir="$(mktemp -d)"
hugo --quiet --buildDrafts --destination "$build_dir"
npx --yes pagefind@1.5.2 --site "$build_dir" --output-path static/pagefind > /dev/null
rm -rf "$build_dir"

echo "③ hugo server — mở http://localhost:1313"
exec hugo server --buildDrafts
