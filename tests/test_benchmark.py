"""파이프라인 스모크 테스트."""
import tempfile
from pathlib import Path

from tts_bmt.benchmark import run_benchmark
from tts_bmt.engines import all_engines


def test_engines_count():
    assert len(all_engines()) == 4


def test_no_chinese_origin():
    # '중국 제외' 기준 검증
    for e in all_engines():
        assert "중국" not in e.meta.origin


def test_run_produces_outputs():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        report = run_benchmark(root)
        assert len(report["engines"]) == 4
        assert (root / "results" / "benchmark.json").exists()
        # 엔진별 5문장 * 4엔진 = 20 wav
        wavs = list((root / "audio").rglob("*.wav"))
        assert len(wavs) == 20
        # 각 엔진 요약에 rtf 존재
        for b in report["engines"]:
            assert "rtf_mean" in b["summary"]
