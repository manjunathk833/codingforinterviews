#!/usr/bin/env python3
"""
Walkthrough Audio & Visual Sync Engine (`hub/tts_walkthrough_engine.py`)

Adapted from the reference architecture in `manjunathk833/stock-analysis`:
- `app/services/content/tts_engine.py` (`_clean_script`, `_tts_edge`, `_run_gtts`)
- `app/services/content/script_generator.py` (`parse_script_sections`, `_extract_visual_cues`)
- `app/services/content/video_renderer.py` (`_audio_duration`, `_normalize_section_durations`,
  `_stamp_visual_cue_on_frame`)

Provides:
1. `clean_script_for_tts(text)`: Strips Markdown syntax, backticks, and emojis and expands
   code operators (`->`, `!=`, `==`, `p^N`) so TTS reads like a natural human instructor.
2. `generate_walkthrough_audio(slug, slides)`: Synthesizes voiceover audio into
   `media/walkthroughs/` using `edge-tts` (`en-IN-NeerjaNeural`) -> `gtts` (`en-in`) ->
   offline macOS CoreAudio (`/usr/bin/say` + `/usr/bin/afconvert`) -> deterministic WAV fallback.
3. `normalize_section_durations(slides, audio_dur)`: Measures exact audio duration and scales
   each slide's word-count duration (`scale = audio_dur / total`) into exact `[t_start, t_end]`
   windows and timed on-screen `visual_cues` (`[{t_start, text, duration}]`).
"""

from __future__ import annotations

import asyncio
import hashlib
import math
import pathlib
import re
import shutil
import struct
import subprocess
import tempfile
import wave
from typing import Any, Dict, List

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
WALKTHROUGH_MEDIA_DIR = REPO_ROOT / "media" / "walkthroughs"
DEFAULT_VOICE = "en-IN-NeerjaNeural"


def clean_script_for_tts(text: str) -> str:
    """Strip Markdown formatting, backticks, and code symbols for clean TTS consumption."""
    text = text or ""
    # Remove horizontal rules (--- or ***)
    text = re.sub(r"^\s*[-*]{3,}\s*$", "", text, flags=re.MULTILINE)
    # Remove [SECTION: ...] or **[HOOK]** labels
    text = re.sub(r"^\s*\*{0,3}\[[\w\s/:]+\]\*{0,3}\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\[SECTION:.*?\]", "", text)
    # Remove bold/italic markers and backticks (keep inner text)
    text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # Remove ATX heading lines
    text = re.sub(r"#{1,6}\s+[^\n]*\n?", "", text)
    # Expand common code & math operators into natural spoken English
    text = (
        text.replace("->", " to ")
        .replace("=>", " leads to ")
        .replace("!=", " does not equal ")
        .replace("==", " equals ")
        .replace(">=", " at least ")
        .replace("<=", " at most ")
        .replace("p^N", "p to the power of N")
        .replace("0.99 ^ 100", "0.99 to the power of 100")
    )
    # Strip emoji / non-ASCII symbols outside standard Latin/Devanagari ranges
    text = re.sub(r"[^\x00-\x7F\u0900-\u097F\u0A00-\u0A7F]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _default_scene_nodes(idx: int, slide: Dict[str, Any]) -> List[str]:
    """Provide a 3-node state diagram flow for every walkthrough scene."""
    existing = slide.get("nodes")
    if isinstance(existing, list) and len(existing) >= 3:
        return [str(x)[:42] for x in existing[:3]]

    badge = str(slide.get("badge") or f"Scene {idx + 1}")
    code_lines = [
        ln.strip().lstrip("#/ ").strip()
        for ln in str(slide.get("code") or "").splitlines()
        if ln.strip()
    ]
    n1 = badge.split("·")[-1].strip()[:38] if "·" in badge else badge[:38]
    n2 = (code_lines[0][:38] if code_lines else "Execute Core Step")
    n3 = (
        code_lines[-1][:38]
        if len(code_lines) > 1
        else ["1. Build Intuition", "2. Run Starter Code", "3. Spot Scaling Limit", "4. Apply Staff Invariant"][idx % 4]
    )
    return [n1 or "1. Input State", n2 or "2. Transform", n3 or "3. Verified Output"]


def get_audio_duration(audio_path: pathlib.Path) -> float:
    """
    Measure exact audio duration in seconds:
    1. macOS built-in `/usr/bin/afinfo` (fast, zero external dylib dependency)
    2. `wave` stdlib module (for `.wav` files)
    3. `ffprobe` (`/opt/homebrew/bin/ffprobe` or `PATH`)
    4. `pydub.AudioSegment`
    5. Bitrate fallback (8,000 bytes/sec for 64kbps mono MP3/M4A)
    """
    if not audio_path.exists():
        return 12.0

    if audio_path.suffix.lower() == ".wav":
        try:
            with wave.open(str(audio_path), "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                if rate > 0:
                    return round(max(1.0, frames / float(rate)), 2)
        except Exception:
            pass

    if pathlib.Path("/usr/bin/afinfo").exists():
        try:
            res = subprocess.run(
                ["/usr/bin/afinfo", str(audio_path)],
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
            )
            m = re.search(r"estimated duration:\s*([0-9.]+)\s*sec", res.stdout)
            if m:
                return round(max(1.0, float(m.group(1))), 2)
        except Exception:
            pass

    for ffprobe_cand in ("/opt/homebrew/bin/ffprobe", "/usr/local/bin/ffprobe", shutil.which("ffprobe")):
        if ffprobe_cand and pathlib.Path(ffprobe_cand).exists():
            try:
                res = subprocess.run(
                    [
                        ffprobe_cand,
                        "-v",
                        "error",
                        "-show_entries",
                        "format=duration",
                        "-of",
                        "default=noprint_wrappers=1:nokey=1",
                        str(audio_path),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=True,
                )
                return round(max(1.0, float(res.stdout.strip())), 2)
            except Exception:
                pass

    try:
        from pydub import AudioSegment

        seg = AudioSegment.from_file(str(audio_path))
        return round(max(1.0, len(seg) / 1000.0), 2)
    except Exception:
        pass

    return round(max(4.0, audio_path.stat().st_size / 8000.0), 2)


def normalize_section_durations(
    slides: List[Dict[str, Any]],
    audio_dur: float,
    wpm: float = 160.0,
    min_dur: float = 3.0,
) -> List[Dict[str, Any]]:
    """
    Scale each slide's word-count duration proportionally so they sum to `audio_dur`
    (adapted from `stock-analysis/app/services/content/video_renderer.py`), and extract
    timed on-screen `visual_cues` (`{t_start, text, duration}`).
    """
    if not slides:
        return []

    step_names = [
        "Step 1: Plain-English Story",
        "Step 2: First Lines of Code",
        "Step 3: Where It Breaks",
        "Step 4: Staff Deep-Dive",
    ]

    prepared: List[Dict[str, Any]] = []
    for idx, s in enumerate(slides):
        clean_tts = clean_script_for_tts(str(s.get("caption", "")))
        words = max(1, len(clean_tts.split()))
        raw_dur = max(min_dur, round((words / wpm) * 60.0, 2))
        prepared.append(
            {
                **s,
                "sceneIndex": idx,
                "stepName": s.get("stepName") or step_names[min(idx, len(step_names) - 1)],
                "nodes": _default_scene_nodes(idx, s),
                "activeNode": int(s.get("activeNode", min(idx, 2))),
                "cleanTts": clean_tts,
                "wordCount": words,
                "duration_s": raw_dur,
            }
        )

    total_est = sum(item["duration_s"] for item in prepared)
    target_total = audio_dur if audio_dur and audio_dur > 0 else total_est
    scale = (target_total / total_est) if total_est > 0 else 1.0

    cursor = 0.0
    out: List[Dict[str, Any]] = []
    for idx, item in enumerate(prepared):
        if idx < len(prepared) - 1:
            dur = round(max(1.5, item["duration_s"] * scale), 2)
        else:
            dur = round(max(1.5, target_total - cursor), 2)

        t_start = round(cursor, 2)
        t_end = round(cursor + dur, 2)
        cursor = t_end

        # Extract timed visual cues from inline code tokens, $ numbers, or percentages
        raw_caption = str(item.get("caption", ""))
        cue_tokens = re.findall(
            r"(?:`[^`]+`|\$[0-9]+(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?%)",
            raw_caption,
        )
        visual_cues: List[Dict[str, Any]] = []
        for c_idx, tok in enumerate(cue_tokens[:3]):
            cue_t = round(t_start + (dur * (c_idx + 1) / (len(cue_tokens[:3]) + 1)), 2)
            visual_cues.append(
                {
                    "t_start": cue_t,
                    "text": tok.strip("`")[:18],
                    "duration": round(min(2.4, dur * 0.45), 2),
                }
            )

        out.append(
            {
                **item,
                "duration_s": dur,
                "t_start": t_start,
                "t_end": t_end,
                "time": f"{int(t_start // 60)}:{int(t_start % 60):02d}",
                "visual_cues": visual_cues,
            }
        )
    return out


async def _run_edge_tts(text: str, out_path: pathlib.Path, timeout: int = 18) -> None:
    import edge_tts

    comm = edge_tts.Communicate(text, voice=DEFAULT_VOICE)
    await asyncio.wait_for(comm.save(str(out_path)), timeout=timeout)


def _write_deterministic_tone_wav(out_path: pathlib.Path, duration_s: float) -> None:
    """Fallback deterministic soft chime/pulse WAV when running in headless CI without TTS."""
    sample_rate = 16000
    n_samples = int(max(3.0, min(duration_s, 60.0)) * sample_rate)
    with wave.open(str(out_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        buf = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            env = 0.15 * math.exp(-((t % 4.0) * 1.8))
            val = int(32767 * env * math.sin(2.0 * math.pi * 440.0 * t))
            buf.extend(struct.pack("<h", val))
        wf.writeframes(bytes(buf))


def generate_walkthrough_audio(
    slug: str,
    slides: List[Dict[str, Any]],
    force_offline: bool = False,
) -> Dict[str, Any]:
    """
    Generate (or serve cached) walkthrough voiceover audio for `slug` and return
    exact `[t_start, t_end]` normalized slide timings + `visual_cues`.
    """
    WALKTHROUGH_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    safe_slug = re.sub(r"[^a-zA-Z0-9_-]", "-", slug or "chapter").strip("-")

    cleaned_segments = [clean_script_for_tts(str(s.get("caption", ""))) for s in slides if s.get("caption")]
    full_script = " . ".join(seg for seg in cleaned_segments if seg) or "Welcome to this interactive chapter walkthrough."
    script_hash = hashlib.md5(full_script.encode("utf-8")).hexdigest()[:8]

    # Check if we already have a cached audio file for this exact script hash
    for ext, backend_label in ((".mp3", "cached-mp3"), (".m4a", "cached-coreaudio-m4a"), (".wav", "cached-wav")):
        cand = WALKTHROUGH_MEDIA_DIR / f"{safe_slug}-{script_hash}{ext}"
        if cand.exists() and cand.stat().st_size > 400 and not force_offline:
            dur = get_audio_duration(cand)
            synced = normalize_section_durations(slides, dur)
            return {
                "status": "ok",
                "slug": slug,
                "audioUrl": f"/media/walkthroughs/{cand.name}",
                "audioDuration": dur,
                "backend": backend_label,
                "slides": synced,
            }

    mp3_target = WALKTHROUGH_MEDIA_DIR / f"{safe_slug}-{script_hash}.mp3"
    backend_used = ""

    if not force_offline:
        # Tier 1: edge-tts (`en-IN-NeerjaNeural` from stock-analysis `tts_engine.py`)
        try:
            asyncio.run(_run_edge_tts(full_script, mp3_target))
            if mp3_target.exists() and mp3_target.stat().st_size > 500:
                backend_used = f"edge-tts ({DEFAULT_VOICE})"
        except Exception:
            mp3_target.unlink(missing_ok=True)

        # Tier 2: gtts (`en-in` fallback from stock-analysis `tts_engine.py`)
        if not backend_used:
            try:
                from gtts import gTTS

                tts = gTTS(text=full_script, lang="en-in", slow=False)
                tts.save(str(mp3_target))
                if mp3_target.exists() and mp3_target.stat().st_size > 500:
                    backend_used = "gtts (en-in)"
            except Exception:
                mp3_target.unlink(missing_ok=True)

    # Tier 3: 100% Offline macOS CoreAudio (`/usr/bin/say` + `/usr/bin/afconvert`)
    final_path = mp3_target
    if not backend_used:
        say_bin = "/usr/bin/say" if pathlib.Path("/usr/bin/say").exists() else shutil.which("say")
        afconvert_bin = "/usr/bin/afconvert" if pathlib.Path("/usr/bin/afconvert").exists() else shutil.which("afconvert")
        if say_bin and afconvert_bin:
            m4a_target = WALKTHROUGH_MEDIA_DIR / f"{safe_slug}-{script_hash}.m4a"
            try:
                with tempfile.TemporaryDirectory() as td:
                    aiff_path = pathlib.Path(td) / "speech.aiff"
                    subprocess.run([say_bin, "-r", "185", "-o", str(aiff_path), full_script], check=True, timeout=25)
                    subprocess.run(
                        [afconvert_bin, "-f", "m4af", "-d", "aac", str(aiff_path), str(m4a_target)],
                        check=True,
                        capture_output=True,
                        timeout=20,
                    )
                if m4a_target.exists() and m4a_target.stat().st_size > 400:
                    final_path = m4a_target
                    backend_used = "coreaudio-say-m4a"
            except Exception:
                m4a_target.unlink(missing_ok=True)

    # Tier 4: Deterministic WAV fallback (for Linux CI containers without TTS binaries)
    if not backend_used:
        wav_target = WALKTHROUGH_MEDIA_DIR / f"{safe_slug}-{script_hash}.wav"
        est_words = max(8, len(full_script.split()))
        est_dur = round(max(12.0, (est_words / 160.0) * 60.0), 2)
        _write_deterministic_tone_wav(wav_target, est_dur)
        final_path = wav_target
        backend_used = "deterministic-wav"

    dur = get_audio_duration(final_path)
    synced = normalize_section_durations(slides, dur)
    return {
        "status": "ok",
        "slug": slug,
        "audioUrl": f"/media/walkthroughs/{final_path.name}",
        "audioDuration": dur,
        "backend": backend_used,
        "slides": synced,
    }
