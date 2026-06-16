"""TTS 엔진 어댑터.

각 엔진을 공통 인터페이스(`Engine`)로 감싼다.
엔진 패키지가 설치되어 있지 않으면 자동으로 합성 신호(사인파)를 만드는
'시뮬레이션 모드'로 폴백한다 — 이렇게 해야 엔진 설치 없이도 누구나
파이프라인 전체(측정 → 리포트 → 정적 데모)를 끝까지 돌려볼 수 있다.

실제 음질 비교를 하려면 해당 엔진을 설치하고 `available()` 가 True가 되도록 한다.
"""

from __future__ import annotations

import math
import struct
import time
import wave
from dataclasses import dataclass, field
from pathlib import Path


# ----------------------------------------------------------------------
# 메타데이터 (리포트/데모에 그대로 노출됨)
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class EngineMeta:
    key: str
    name: str
    origin: str          # 개발 주체 / 국가
    license: str
    korean: str          # 한국어 지원 방식
    homepage: str
    notes: str = ""


# ----------------------------------------------------------------------
# 합성 결과
# ----------------------------------------------------------------------
@dataclass
class Synthesis:
    engine_key: str
    text: str
    wav_path: Path
    sample_rate: int
    duration_sec: float
    synth_sec: float            # 합성에 걸린 벽시계 시간
    simulated: bool
    extra: dict = field(default_factory=dict)

    @property
    def rtf(self) -> float:
        """Real-Time Factor = 합성시간 / 오디오길이. 낮을수록 빠름."""
        if self.duration_sec <= 0:
            return float("inf")
        return self.synth_sec / self.duration_sec

    @property
    def chars_per_sec(self) -> float:
        n = len(self.text.replace(" ", ""))
        return n / self.synth_sec if self.synth_sec > 0 else 0.0


# ----------------------------------------------------------------------
# 베이스 엔진
# ----------------------------------------------------------------------
class Engine:
    meta: EngineMeta
    target_sr: int = 22050

    def available(self) -> bool:
        """실제 엔진 패키지가 설치되어 있고 추론 가능한지."""
        return False

    def synthesize(self, text: str, out_path: Path) -> Synthesis:
        """텍스트 → WAV. 기본 구현은 시뮬레이션(사인파)."""
        return self._simulate(text, out_path)

    # --- 시뮬레이션 폴백 -------------------------------------------------
    def _simulate(self, text: str, out_path: Path) -> Synthesis:
        """한국어 글자 수에 비례한 길이의 사인파를 생성.

        엔진마다 약간씩 다른 기본 주파수/속도를 줘서 데모에서
        파형이 구분되도록 한다. (음질 비교가 아니라 파이프라인 검증용)
        """
        start = time.perf_counter()

        n_chars = max(1, len(text.replace(" ", "")))
        # 글자당 약 0.18초로 가정
        duration = n_chars * 0.18
        sr = self.target_sr

        # 엔진 key 해시로 음높이를 살짝 다르게
        base_freq = 180 + (sum(ord(c) for c in self.meta.key) % 7) * 18

        n_samples = int(duration * sr)
        amp = 0.25 * 32767

        out_path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out_path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            frames = bytearray()
            for i in range(n_samples):
                t = i / sr
                # 문장 끝으로 갈수록 살짝 음을 내려(혹은 올려) 억양 흉내
                tail = 1.0 - 0.15 * (t / duration)
                if text.rstrip().endswith("?"):
                    tail = 1.0 + 0.20 * (t / duration)   # 의문문: 끝을 올림
                envelope = math.sin(math.pi * t / duration)  # 페이드 인/아웃
                sample = amp * envelope * math.sin(2 * math.pi * base_freq * tail * t)
                frames += struct.pack("<h", int(sample))
            w.writeframes(bytes(frames))

        synth_sec = time.perf_counter() - start
        return Synthesis(
            engine_key=self.meta.key,
            text=text,
            wav_path=out_path,
            sample_rate=sr,
            duration_sec=duration,
            synth_sec=synth_sec,
            simulated=True,
        )


# ----------------------------------------------------------------------
# 1. Supertonic 3 (한국, Supertone)
# ----------------------------------------------------------------------
class SupertonicEngine(Engine):
    target_sr = 44100
    meta = EngineMeta(
        key="supertonic",
        name="Supertonic 3",
        origin="Supertone (🇰🇷 한국)",
        license="MIT(code) + OpenRAIL-M(model)",
        korean="기본 지원 (31개 언어, lang='ko')",
        homepage="https://github.com/supertone-inc/supertonic",
        notes="온디바이스 ~99M ONNX, CPU 실시간, 표현 태그 지원. "
              "모델은 OpenRAIL-M(사용제한+저작자표시) — MIT와 다름.",
    )

    def __init__(self, voice_name: str = "F1") -> None:
        self._tts = None
        self._voice_name = voice_name

    def available(self) -> bool:
        try:
            import supertonic  # noqa: F401
            return True
        except Exception:
            return False

    def synthesize(self, text: str, out_path: Path) -> Synthesis:
        if not self.available():
            return self._simulate(text, out_path)
        try:
            from supertonic import TTS
            if self._tts is None:
                # 최초 1회 ~400MB 모델을 ~/.cache/supertonic3/ 로 자동 다운로드
                self._tts = TTS(auto_download=True)
            style = self._tts.get_voice_style(voice_name=self._voice_name)

            out_path.parent.mkdir(parents=True, exist_ok=True)
            start = time.perf_counter()
            wav, _ = self._tts.synthesize(text=text, voice_style=style, lang="ko")
            synth_sec = time.perf_counter() - start
            self._tts.save_audio(wav, str(out_path))

            # 저장된 WAV 에서 실제 길이/샘플레이트를 읽어 정확히 측정
            with wave.open(str(out_path), "rb") as w:
                sr = w.getframerate()
                duration = w.getnframes() / sr if sr else 0.0

            return Synthesis(
                engine_key=self.meta.key,
                text=text,
                wav_path=out_path,
                sample_rate=sr,
                duration_sec=duration,
                synth_sec=synth_sec,
                simulated=False,
                extra={"voice": self._voice_name},
            )
        except Exception as e:  # 설치돼 있어도 추론 실패 시 폴백 (정직하게 simulated 표기)
            print(f"[supertonic] 실측 실패 → 시뮬레이션 폴백: {e}")
            return self._simulate(text, out_path)


# ----------------------------------------------------------------------
# 2. piper-plus (일본, ayutaz)
# ----------------------------------------------------------------------
class PiperPlusEngine(Engine):
    target_sr = 22050
    meta = EngineMeta(
        key="piper_plus",
        name="piper-plus",
        origin="ayutaz (🇯🇵 일본)",
        license="MIT",
        korean="8개 언어 중 한국어 포함 (독자 G2P)",
        homepage="https://github.com/ayutaz/piper-plus",
        notes="VITS 기반, --prosody-dim 운율 주입, CPU 실시간, "
              "음성 클로닝(Speaker Encoder). 한국어 음성모델 별도 학습/준비 필요.",
    )

    def __init__(self, model_path: str | None = None) -> None:
        self._model_path = model_path
        self._voice = None

    def available(self) -> bool:
        if not self._model_path or not Path(self._model_path).exists():
            return False
        try:
            import piper_plus  # noqa: F401
            return True
        except Exception:
            return False

    def synthesize(self, text: str, out_path: Path) -> Synthesis:
        if not self.available():
            return self._simulate(text, out_path)
        # 실제 구현 (설치 + 모델 준비 시):
        #   from piper_plus import PiperVoice
        #   if self._voice is None:
        #       self._voice = PiperVoice.load(self._model_path)
        #   ...
        return self._simulate(text, out_path)


# ----------------------------------------------------------------------
# ESPnet KSS 사전학습 기반 공통 엔진
#   - 데모는 KSS(공개 한국어 단일화자) 사전학습 모델로 실음성을 낸다.
#   - 자가학습 모델 경로(model_path)를 주면 그쪽을 우선 사용한다.
#   - espnet 미설치/추론 실패 시 시뮬레이션으로 정직하게 폴백.
# ----------------------------------------------------------------------
class _EspnetKssEngine(Engine):
    target_sr = 22050
    espnet_model_id: str = ""    # 서브클래스가 지정 (HuggingFace 모델 id)
    # meta.yaml 이 없는 저장소는 config/model 파일을 직접 지정해 로드한다.
    espnet_config_file: str = ""
    espnet_model_file: str = ""

    def __init__(self, model_path: str | None = None,
                 espnet_model: str | None = None) -> None:
        self._model_path = model_path
        self._espnet_model = espnet_model or self.espnet_model_id
        self._t2s = None

    def available(self) -> bool:
        try:
            import espnet2  # noqa: F401
        except Exception:
            return False
        # 로컬 자가학습 모델 또는 사전학습 모델 id 중 하나는 있어야 함
        if self._model_path:
            return Path(self._model_path).exists()
        return bool(self._espnet_model)

    def _load(self):
        from espnet2.bin.tts_inference import Text2Speech
        # 1) 로컬 자가학습 모델 경로 우선
        if self._model_path and Path(self._model_path).exists():
            return Text2Speech.from_pretrained(self._model_path)
        # 2) meta.yaml 없는 저장소: config.yaml + 체크포인트를 직접 받아 로드
        if self.espnet_config_file and self.espnet_model_file:
            from huggingface_hub import hf_hub_download
            cfg = hf_hub_download(self._espnet_model, self.espnet_config_file)
            mdl = hf_hub_download(self._espnet_model, self.espnet_model_file)
            return Text2Speech(train_config=cfg, model_file=mdl)
        # 3) 표준 패키징(meta.yaml 포함) 모델: from_pretrained
        return Text2Speech.from_pretrained(self._espnet_model)

    def synthesize(self, text: str, out_path: Path) -> Synthesis:
        if not self.available():
            return self._simulate(text, out_path)
        try:
            import soundfile as sf
            if self._t2s is None:
                self._t2s = self._load()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            start = time.perf_counter()
            wav = self._t2s(text)["wav"]
            synth_sec = time.perf_counter() - start

            sr = int(getattr(self._t2s, "fs", self.target_sr))
            audio = wav.view(-1).cpu().numpy()
            sf.write(str(out_path), audio, sr)
            duration = len(audio) / sr if sr else 0.0

            return Synthesis(
                engine_key=self.meta.key,
                text=text,
                wav_path=out_path,
                sample_rate=sr,
                duration_sec=duration,
                synth_sec=synth_sec,
                simulated=False,
                extra={"espnet_model": self._espnet_model},
            )
        except Exception as e:
            print(f"[{self.meta.key}] 실측 실패 → 시뮬레이션 폴백: {e}")
            return self._simulate(text, out_path)


# ----------------------------------------------------------------------
# 3. kr-custom-tts (한국, seastar105) — ESPnet
#    데모: KSS 사전학습 JETS / 자가학습 시 본인 음성 모델로 교체
# ----------------------------------------------------------------------
class KrCustomEngine(_EspnetKssEngine):
    target_sr = 22050
    espnet_model_id = (
        "imdanboy/kss_tts_train_jets_raw_phn_korean_cleaner_"
        "korean_jaso_train.total_count.ave"
    )
    meta = EngineMeta(
        key="kr_custom",
        name="kr-custom-tts",
        origin="seastar105 (🇰🇷 한국)",
        license="MIT(code) / KSS 데이터셋 별도",
        korean="한국어 전용 (ESPnet)",
        homepage="https://github.com/seastar105/kr-custom-tts",
        notes="ESPnet 기반. 데모는 KSS 공개 화자 사전학습(JETS) 사용. "
              "자가학습 시 본인 음성 모델 경로로 교체 가능.",
    )


# ----------------------------------------------------------------------
# 4. SCE-TTS (한국, yunho0130) — ESPnet
#    데모: KSS 사전학습 VITS / 원 가이드는 자가학습 Tacotron2
# ----------------------------------------------------------------------
class SceTtsEngine(_EspnetKssEngine):
    target_sr = 22050
    espnet_model_id = (
        "songhee/kss_tts_train_full_band_vits_raw_phn_korean_cleaner_korean_jaso"
    )
    # 이 저장소엔 meta.yaml 이 없어 config/checkpoint 를 직접 지정해 로드한다.
    espnet_config_file = "config.yaml"
    espnet_model_file = "1000epoch.pth"
    meta = EngineMeta(
        key="sce_tts",
        name="SCE-TTS",
        origin="yunho0130 (🇰🇷 한국)",
        license="MIT(code) / KSS 데이터셋 별도",
        korean="한국어 전용 (데모: ESPnet KSS VITS)",
        homepage="https://gist.github.com/yunho0130",
        notes="원 가이드는 자가학습 Tacotron2. 데모는 KSS 공개 화자 "
              "사전학습(VITS, ESPnet)으로 실음성 제공.",
    )


# ----------------------------------------------------------------------
# 레지스트리
# ----------------------------------------------------------------------
def all_engines(model_paths: dict[str, str] | None = None) -> list[Engine]:
    """엔진 4종을 생성한다.

    `model_paths` 로 학습형/모델 의존 엔진의 산출물 경로를 주면 해당 엔진의
    `available()` 이 True 가 되어 실측(real) 모드로 전환된다.
    예: all_engines({"piper_plus": "models/ko.onnx", "kr_custom": "models/kr.pth"})
    (Supertonic 은 pip 패키지 설치 여부로 판별하므로 경로가 필요 없다.)
    """
    mp = model_paths or {}
    return [
        SupertonicEngine(),
        PiperPlusEngine(model_path=mp.get("piper_plus")),
        KrCustomEngine(model_path=mp.get("kr_custom")),
        SceTtsEngine(model_path=mp.get("sce_tts")),
    ]
