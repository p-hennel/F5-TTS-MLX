import datetime
import pkgutil
from typing import Literal, Optional

import mlx.core as mx

import numpy as np

from f5_tts_mlx.cfm import F5TTS
from f5_tts_mlx.utils import convert_char_to_pinyin

import soundfile as sf

from typing import Tuple

SAMPLE_RATE = 24_000
HOP_LENGTH = 256
FRAMES_PER_SEC = SAMPLE_RATE / HOP_LENGTH
TARGET_RMS = 0.1

def get_sample_rate() -> int:
  return SAMPLE_RATE

def get_f5tts(model_name: str = "lucasnewman/f5-tts-mlx") -> F5TTS:
  return F5TTS.from_pretrained(model_name)

def get_ref_audio(
  ref_audio_path: Optional[str] = None,
  ref_audio_text: Optional[str] = None,
  debug: bool = False
) -> Tuple[mx.array, str | None]:
  if ref_audio_path is None:
    data = pkgutil.get_data("f5_tts_mlx", "tests/test_en_1_ref_short.wav")

    # write to a temp file
    tmp_ref_audio_file = "/tmp/ref.wav"
    with open(tmp_ref_audio_file, "wb") as f:
      f.write(data)

    if data is not None:
      audio, sr = sf.read(tmp_ref_audio_file)
      ref_audio_text = "Some call me nature, others call me mother nature."
  else:
    # load reference audio
    audio, sr = sf.read(ref_audio_path)
    if sr != SAMPLE_RATE:
      raise ValueError("Reference audio must have a sample rate of 24kHz")

  audio = mx.array(audio)

  if debug:
    ref_audio_duration = audio.shape[0] / SAMPLE_RATE
    print(f"Got reference audio with duration: {ref_audio_duration:.2f} seconds")

  rms = mx.sqrt(mx.mean(mx.square(audio)))
  if rms < TARGET_RMS:
    audio = audio * TARGET_RMS / rms

  return audio, ref_audio_text

def generate(
  f5tts: F5TTS,
  text: str,
  duration: Optional[float] = None,
  ref_audio = None,
  ref_audio_text: Optional[str] = None,
  steps: int = 32,
  method: Literal["euler", "midpoint"] = "euler",
  cfg_strength: float = 2.0,
  sway_sampling_coef: float = -1.0,
  speed: float = 1.0,  # used when duration is None as part of the duration heuristic
  seed: Optional[int] = None,
  debug: bool = False
):
  if ref_audio is None and ref_audio_text is None:
    ref_audio, ref_audio_text = get_ref_audio(debug=debug)

  # generate the audio for the given text
  text = convert_char_to_pinyin([ref_audio_text + " " + text])

  start_date = datetime.datetime.now()

  if duration is not None:
    duration = int(duration * FRAMES_PER_SEC)

  wave, _ = f5tts.sample(
    mx.expand_dims(ref_audio, axis=0),
    text=text,
    duration=duration,
    steps=steps,
    method=method,
    speed=speed,
    cfg_strength=cfg_strength,
    sway_sampling_coef=sway_sampling_coef,
    seed=seed,
  )

  # trim the reference audio
  wave = wave[ref_audio.shape[0] :]
  
  if debug:
    generated_duration = wave.shape[0] / SAMPLE_RATE
    elapsed_time = datetime.datetime.now() - start_date
    print(f"Generated {generated_duration:.2f} seconds of audio in {elapsed_time}.")

  return np.array(wave)