"""벤치마크 실행기.

테스트 문장 세트를 각 엔진에 합성시키고, 측정 지표를 모아
docs/results/benchmark.json 으로 저장한다. (GitHub Pages가 docs/를 서빙)
오디오는 docs/audio/<engine>/<id>.wav 로 저장한다.
"""

from __future__ import annotations

import json
import platform
import statistics
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .engines import Engine, Synthesis, all_engines


# 카드사 FDS 상담사 맥락의 한국어 테스트 문장 (억양 다양화 포함)
TEST_SENTENCES: list[dict] = [
    {"id": "s1", "type": "normal",
     "text": "안녕하세요. 고객님, OO카드입니다."},
    {"id": "s2", "type": "question",
     "text": "방금 오만 원 거래가 감지되었는데, 본인 거래가 맞으신가요?"},
    {"id": "s3", "type": "urgent",
     "text": "긴급 알림입니다! 의심 거래가 감지되어 즉시 확인이 필요합니다!"},
    {"id": "s4", "type": "calm",
     "text": "안전을 위해 해당 거래를 차단했습니다. 카드를 일시 정지하였습니다."},
    {"id": "s5", "type": "mixed",
     "text": "Amazon 가맹점에서 USD 120 결제가 시도되었습니다."},
]


def run_benchmark(
    out_root: Path,
    engines: list[Engine] | None = None,
    sentences: list[dict] | None = None,
) -> dict:
    engines = engines or all_engines()
    sentences = sentences or TEST_SENTENCES

    audio_root = out_root / "audio"
    results_dir = out_root / "results"
    audio_root.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    engine_blocks = []

    for eng in engines:
        is_real = eng.available()
        syntheses: list[Synthesis] = []

        for s in sentences:
            wav_path = audio_root / eng.meta.key / f"{s['id']}.wav"
            syn = eng.synthesize(s["text"], wav_path)
            syntheses.append(syn)

        rtfs = [s.rtf for s in syntheses]
        cps = [s.chars_per_sec for s in syntheses]

        engine_blocks.append({
            "meta": asdict(eng.meta),
            "mode": "real" if is_real else "simulated",
            "summary": {
                "rtf_mean": round(statistics.mean(rtfs), 4),
                "rtf_median": round(statistics.median(rtfs), 4),
                "chars_per_sec_mean": round(statistics.mean(cps), 2),
                "total_audio_sec": round(sum(s.duration_sec for s in syntheses), 2),
                "total_synth_sec": round(sum(s.synth_sec for s in syntheses), 4),
            },
            "samples": [
                {
                    "id": sent["id"],
                    "type": sent["type"],
                    "text": sent["text"],
                    # docs 기준 상대경로 (Pages에서 그대로 접근 가능)
                    "audio": f"audio/{eng.meta.key}/{sent['id']}.wav",
                    "duration_sec": round(syn.duration_sec, 3),
                    "synth_sec": round(syn.synth_sec, 4),
                    "rtf": round(syn.rtf, 4),
                }
                for sent, syn in zip(sentences, syntheses)
            ],
        })

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python": platform.python_version(),
            "system": platform.system(),
            "machine": platform.machine(),
        },
        "disclaimer": (
            "RTF/속도는 측정 환경에 따라 달라집니다. 'simulated' 모드는 "
            "엔진 미설치 시 파이프라인 검증용 합성 신호이며 실제 음질이 아닙니다. "
            "실제 음질 비교는 각 엔진 설치 후 'real' 모드로 재실행하세요."
        ),
        "criteria": {
            "exclude": "중국 개발 엔진 제외",
            "license": "상업용 무료 (MIT 계열)",
            "language": "한국어 지원",
        },
        "engines": engine_blocks,
    }

    out_file = results_dir / "benchmark.json"
    out_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
