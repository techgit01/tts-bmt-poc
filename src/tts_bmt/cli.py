"""CLI: `tts-bmt` / `uv run tts-bmt`.

사용:
  uv run tts-bmt run          # 벤치마크 실행 → docs/results, docs/audio 생성
  uv run tts-bmt list         # 4개 엔진 메타데이터 출력
"""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .benchmark import run_benchmark
from .engines import all_engines

console = Console()

# 프로젝트 루트 기준 docs/ (GitHub Pages 서빙 디렉토리)
DOCS = Path(__file__).resolve().parents[2] / "docs"


def cmd_list(_: argparse.Namespace) -> None:
    table = Table(title="한국어 TTS 벤치마크 후보 (중국 제외 / 상업용 무료)")
    table.add_column("키", style="cyan")
    table.add_column("이름", style="bold")
    table.add_column("개발", style="green")
    table.add_column("라이선스")
    table.add_column("설치됨?")

    for eng in all_engines():
        table.add_row(
            eng.meta.key,
            eng.meta.name,
            eng.meta.origin,
            eng.meta.license,
            "✅" if eng.available() else "— (시뮬레이션)",
        )
    console.print(table)


def cmd_run(args: argparse.Namespace) -> None:
    out_root = Path(args.out).resolve()
    console.print(f"[bold]벤치마크 실행[/bold] → {out_root}")
    report = run_benchmark(out_root)

    table = Table(title="결과 요약")
    table.add_column("엔진", style="bold")
    table.add_column("모드")
    table.add_column("RTF(평균)", justify="right")
    table.add_column("문자/초", justify="right")
    for block in report["engines"]:
        table.add_row(
            block["meta"]["name"],
            block["mode"],
            f'{block["summary"]["rtf_mean"]}',
            f'{block["summary"]["chars_per_sec_mean"]}',
        )
    console.print(table)
    console.print(
        f'\n[green]✓[/green] 결과: {out_root / "results" / "benchmark.json"}'
        f'\n[green]✓[/green] 오디오: {out_root / "audio"}'
        f'\n[dim]docs/index.html 을 GitHub Pages로 배포하면 브라우저에서 확인됩니다.[/dim]'
    )


def main() -> None:
    parser = argparse.ArgumentParser(prog="tts-bmt", description="한국어 TTS 4종 벤치마크 POC")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="엔진 목록/설치상태")
    p_list.set_defaults(func=cmd_list)

    p_run = sub.add_parser("run", help="벤치마크 실행")
    p_run.add_argument("--out", default=str(DOCS), help="산출물 루트 (기본: docs/)")
    p_run.set_defaults(func=cmd_run)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
