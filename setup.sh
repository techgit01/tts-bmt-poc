#!/usr/bin/env bash
# setup.sh — 새 PC에서 한 번만 실행하는 환경 준비 스크립트
#
#   ./setup.sh            # 코어 의존성만 (가벼움, 시뮬레이션 모드까지 가능)
#   ./setup.sh --full     # 실측 엔진(supertonic, piper)까지 설치
#
# 하는 일:
#   1) uv 설치 (없으면 자동)
#   2) Python 3.12 고정
#   3) uv sync 로 의존성 설치
#   4) VS Code GitHub Actions 확장 설치 ('code' CLI 있을 때)
set -euo pipefail

# 스크립트 위치를 기준으로 동작 (어디서 호출하든 OK)
cd "$(dirname "$0")"

echo "==> [1/4] uv 확인"
if ! command -v uv >/dev/null 2>&1; then
  echo "    uv 미설치 → 설치합니다."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # 설치 직후 PATH 반영 (현재 셸용)
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi
if ! command -v uv >/dev/null 2>&1; then
  echo "    ✗ uv 를 PATH 에서 찾지 못했습니다. 새 터미널을 열고 다시 실행하세요." >&2
  exit 1
fi
echo "    uv $(uv --version)"

echo "==> [2/4] Python 3.12 고정"
uv python pin 3.12

echo "==> [3/4] 의존성 설치"
if [[ "${1:-}" == "--full" ]]; then
  echo "    --full: 실측 엔진(supertonic, piper) 포함"
  uv sync --extra supertonic --extra piper --extra audio
else
  echo "    코어만 설치 (실측 엔진은 './setup.sh --full' 또는 'uv sync --extra <엔진>')"
  uv sync
fi

echo "==> [4/4] VS Code 확장 (GitHub Actions) 설치"
if command -v code >/dev/null 2>&1; then
  # 워크플로(.github/workflows/*.yml) 편집/실행 모니터링용 공식 확장
  code --install-extension github.vscode-github-actions --force
  echo "    github.vscode-github-actions 설치 완료"
else
  echo "    'code' CLI 미발견 → 건너뜀."
  echo "    VS Code 에서 Command Palette > 'Shell Command: Install code command in PATH' 실행 후"
  echo "    다시 './setup.sh' 하거나, 확장 탭에서 'GitHub Actions'(github.vscode-github-actions) 설치하세요."
fi

echo
echo "✓ 준비 완료. 이제 ./run.sh 로 벤치마크를 실행하세요."
