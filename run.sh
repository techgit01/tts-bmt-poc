#!/usr/bin/env bash
# run.sh — 벤치마크 실행 + (옵션) 로컬 데모 미리보기
#
#   ./run.sh              # 벤치마크 실행 → docs/results, docs/audio 갱신
#   ./run.sh --serve      # 실행 후 로컬 웹서버로 데모 미리보기 (http://localhost:8000)
#   ./run.sh --list       # 엔진 목록/설치 상태만 출력
set -euo pipefail

cd "$(dirname "$0")"

# uv 없으면 setup 먼저 (PATH 에 없을 수 있어 보강)
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
if ! command -v uv >/dev/null 2>&1; then
  echo "✗ uv 가 없습니다. 먼저 ./setup.sh 를 실행하세요." >&2
  exit 1
fi

if [[ "${1:-}" == "--list" ]]; then
  uv run tts-bmt list
  exit 0
fi

echo "==> 벤치마크 실행"
uv run tts-bmt run

if [[ "${1:-}" == "--serve" ]]; then
  PORT="${2:-8000}"
  echo
  echo "==> 데모 미리보기: http://localhost:${PORT}  (Ctrl+C 로 종료)"
  cd docs && uv run python -m http.server "${PORT}"
fi
