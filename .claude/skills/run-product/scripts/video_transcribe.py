#!/usr/bin/env python3
"""Local transcript with word timestamps (faster-whisper, CPU int8, free), plus a sync check.

Writes --out as a flat list of words: [[start, end, "word"], ...] (seconds, absolute in the file,
--offset added). Prints one line per segment with its timing, which is the beat table for the script.

Usage:
  python -I video_transcribe.py SRC.mp4 --out orig_words.json --lang en
  python -I video_transcribe.py vo.wav --out words.json --lang es --model small
  python -I video_transcribe.py final.mp4 --out final_words.json --lang es --against words.json --tol 0.15
Options: --start/--end to cut a window (e.g. the narrator part only), --offset to shift times,
--prompt "Krino, Grip-Lock" to bias spelling of brand words.
--against REF.json: independent check. Matches words in order (accents and punctuation ignored),
reports the share matched and the worst start offset; exits 1 if an offset is over --tol.
Videos are read through ffmpeg ($FFMPEG, PATH or imageio-ffmpeg); 16 kHz mono is extracted to a temp file.
"""
import argparse, difflib, json, os, re, shutil, subprocess, sys, tempfile, unicodedata


def ffmpeg():
    p = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if p:
        return p
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def norm(w):
    w = unicodedata.normalize("NFKD", w.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9%]", "", w)


def transcribe(path, model, lang, start, end, prompt):
    from faster_whisper import WhisperModel
    fd, wav = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    cmd = [ffmpeg(), "-v", "error", "-y"] + (["-ss", str(start)] if start else []) + ["-i", path]
    cmd += (["-t", str(end - (start or 0))] if end else []) + ["-vn", "-ac", "1", "-ar", "16000", wav]
    subprocess.run(cmd, check=True)
    m = WhisperModel(model, device="cpu", compute_type="int8")
    segs, info = m.transcribe(wav, word_timestamps=True, language=lang, initial_prompt=prompt)
    out, base = [], start or 0.0
    for s in segs:
        print(f"{s.start + base:7.2f}-{s.end + base:7.2f} {s.text.strip()}")
        out += [[round(w.start + base, 3), round(w.end + base, 3), w.word.strip()] for w in s.words]
    os.remove(wav)
    print(f"language {info.language} ({info.language_probability:.2f}), {len(out)} words")
    return out


def check(words, ref, tol):
    a, b = [norm(w[2]) for w in words], [norm(w[2]) for w in ref]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    pairs = [(words[m.a + k], ref[m.b + k]) for m in sm.get_matching_blocks() for k in range(m.size)]
    offs = sorted(((abs(x[0] - y[0]), x, y) for x, y in pairs), key=lambda t: -t[0])
    print(f"matched {len(pairs)}/{len(ref)} reference words ({100 * len(pairs) / max(1, len(ref)):.0f}%)")
    for d, x, y in offs[:5]:
        print(f"  offset {d:.2f}s  '{x[2]}' at {x[0]:.2f} vs ref {y[0]:.2f}")
    worst = offs[0][0] if offs else 0
    print("SYNC OK" if worst <= tol else f"SYNC FAIL: worst offset {worst:.2f}s > {tol}s")
    return worst <= tol


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("--out", required=True)
    ap.add_argument("--lang", default=None, help="en, es, fr ... (auto-detect if omitted)")
    ap.add_argument("--model", default="small")
    ap.add_argument("--start", type=float)
    ap.add_argument("--end", type=float)
    ap.add_argument("--offset", type=float, default=0.0)
    ap.add_argument("--prompt")
    ap.add_argument("--against")
    ap.add_argument("--tol", type=float, default=0.15)
    a = ap.parse_args()
    words = transcribe(a.src, a.model, a.lang, a.start, a.end, a.prompt)
    for w in words:
        w[0], w[1] = round(w[0] + a.offset, 3), round(w[1] + a.offset, 3)
    json.dump(words, open(a.out, "w", encoding="utf-8"), ensure_ascii=False)
    print("words", a.out)
    if a.against:
        return 0 if check(words, json.load(open(a.against, encoding="utf-8")), a.tol) else 1


if __name__ == "__main__":
    sys.exit(main())
