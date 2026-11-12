"""ElevenLabs helper for video ads (new-PC replacement for demucs + faster-whisper).

Subcommands
-----------
  voices                      list voices on the account
  tts     --text/--text-file  TTS with character-level timestamps -> wav + words.json
  stt     --audio             speech-to-text with word timestamps (read-back check)
  isolate --audio             voice isolation (demucs replacement)
  delete-voice <voice_id>     free a clone slot

Design notes
------------
* One TTS call for the whole script keeps prosody consistent across beats; the
  returned character alignment is folded into word timings, and beat boundaries
  are derived from the audio instead of forcing speech into fixed slots.
* NOTE ON VOICES: this script is deliberately limited to the account's *premade*
  (licensed stock) voices and voices the operator owns. It has no `clone`
  subcommand. Cloning the voice out of a competitor's ad is not something we
  have the rights to do - see VIDEO_AD_POLICY.md next to this script.

Usage:  python -I video_eleven.py <subcommand> --help
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.elevenlabs.io"
DEFAULT_ENV = r"D:\Ecom\Products\.secrets\elevenlabs.env"

# Operator default voice settings (14-video-ads.md Step 5).
VOICE_SETTINGS = {
    "stability": 0.55,
    "similarity_boost": 0.9,
    "style": 0.15,
    "use_speaker_boost": True,
}


def load_key(env_path):
    if os.environ.get("ELEVENLABS_API_KEY"):
        return os.environ["ELEVENLABS_API_KEY"]
    with open(env_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == "ELEVENLABS_API_KEY":
                return v.strip().strip('"').strip("'")
    raise SystemExit("ELEVENLABS_API_KEY not found in " + env_path)


def call(key, path, data=None, method=None, raw_body=None, content_type=None):
    url = API + path
    headers = {"xi-api-key": key}
    body = None
    if raw_body is not None:
        body = raw_body
        headers["Content-Type"] = content_type
    elif data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers,
                                 method=method or ("POST" if body else "GET"))
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read(), resp.headers.get_content_type()
    except urllib.error.HTTPError as exc:
        sys.stderr.write("HTTP %s %s\n%s\n" % (exc.code, url, exc.read()[:2000].decode("utf-8", "replace")))
        raise


def multipart(fields, files):
    """Minimal multipart/form-data encoder (stdlib only)."""
    boundary = "----mojoBoundary7f3a91c2"
    out = []
    for name, value in fields.items():
        if value is None:
            continue
        out.append(("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n"
                    % (boundary, name, value)).encode("utf-8"))
    for name, path in files.items():
        fname = os.path.basename(path)
        with open(path, "rb") as fh:
            payload = fh.read()
        out.append(("--%s\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"%s\"\r\n"
                    "Content-Type: application/octet-stream\r\n\r\n" % (boundary, name, fname)).encode("utf-8"))
        out.append(payload)
        out.append(b"\r\n")
    out.append(("--%s--\r\n" % boundary).encode("utf-8"))
    return b"".join(out), "multipart/form-data; boundary=" + boundary


def words_from_alignment(align):
    """Fold ElevenLabs character alignment into word objects."""
    chars = align["characters"]
    starts = align["character_start_times_seconds"]
    ends = align["character_end_times_seconds"]
    words, cur, c_start, c_end = [], "", None, None
    for ch, s, e in zip(chars, starts, ends):
        if ch.isspace():
            if cur:
                words.append({"word": cur, "start": round(c_start, 3), "end": round(c_end, 3)})
                cur, c_start = "", None
            continue
        if not cur:
            c_start = s
        cur += ch
        c_end = e
    if cur:
        words.append({"word": cur, "start": round(c_start, 3), "end": round(c_end, 3)})
    return words


def cmd_voices(args, key):
    body, _ = call(key, "/v2/voices?page_size=100")
    data = json.loads(body)
    for v in data.get("voices", []):
        lbl = v.get("labels") or {}
        print("%-24s %-46s %-9s %s/%s" % (v["voice_id"], (v.get("name") or "")[:46],
                                          v.get("category"), lbl.get("accent"), lbl.get("gender")))
    sub, _ = call(key, "/v1/user/subscription")
    s = json.loads(sub)
    print("\nquota: %s / %s characters (tier %s)" % (s.get("character_count"), s.get("character_limit"), s.get("tier")))


def cmd_tts(args, key):
    text = args.text
    if args.text_file:
        with open(args.text_file, encoding="utf-8") as fh:
            text = fh.read().strip()
    if not text:
        raise SystemExit("need --text or --text-file")
    print("characters billed: %d" % len(text))
    settings = dict(VOICE_SETTINGS)
    if args.speed:
        settings["speed"] = args.speed          # ElevenLabs range 0.7-1.2; rule: <= 1.08
    payload = {
        "text": text,
        "model_id": args.model,
        "voice_settings": settings,
    }
    if args.language:
        payload["language_code"] = args.language
    path = "/v1/text-to-speech/%s/with-timestamps?output_format=%s" % (args.voice, args.output_format)
    body, _ = call(key, path, data=payload)
    data = json.loads(body)
    audio = base64.b64decode(data["audio_base64"])
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out, "wb") as fh:
        fh.write(audio)
    align = data.get("normalized_alignment") or data.get("alignment")
    words = words_from_alignment(align)
    wpath = args.words or (os.path.splitext(args.out)[0] + "-words.json")
    with open(wpath, "w", encoding="utf-8") as fh:
        json.dump({"voice_id": args.voice, "model_id": args.model,
                   "voice_settings": settings, "text": text, "words": words},
                  fh, ensure_ascii=False, indent=1)
    print("audio -> %s" % args.out)
    print("words -> %s  (%d words, %.2fs)" % (wpath, len(words), words[-1]["end"] if words else 0))


def cmd_stt(args, key):
    fields = {"model_id": args.model, "timestamps_granularity": "word",
              "diarize": "false", "language_code": args.language}
    body_bytes, ctype = multipart(fields, {"file": args.audio})
    body, _ = call(key, "/v1/speech-to-text", raw_body=body_bytes, content_type=ctype)
    data = json.loads(body)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    print(data.get("text", "")[:4000])
    print("\n-> %s" % args.out)


def cmd_isolate(args, key):
    body_bytes, ctype = multipart({}, {"audio": args.audio})
    body, _ = call(key, "/v1/audio-isolation", raw_body=body_bytes, content_type=ctype)
    with open(args.out, "wb") as fh:
        fh.write(body)
    print("-> %s" % args.out)


def cmd_design_voice(args, key):
    """Voice Design: description -> N previews (mp3 + STT/pace check) in --out-dir."""
    text = args.text
    if args.text_file:
        with open(args.text_file, encoding="utf-8") as fh:
            text = fh.read().strip()
    os.makedirs(args.out_dir, exist_ok=True)
    payload = {"voice_description": args.description, "model_id": args.model,
               "text": text, "auto_generate_text": False}
    if args.guidance is not None:
        payload["guidance_scale"] = args.guidance
    try:
        body, _ = call(key, "/v1/text-to-voice/design?output_format=mp3_44100_128", data=payload)
    except urllib.error.HTTPError:
        payload.pop("model_id", None)
        body, _ = call(key, "/v1/text-to-voice/create-previews?output_format=mp3_44100_128", data=payload)
    data = json.loads(body)
    n_words = len(text.split())
    report = []
    for i, p in enumerate(data.get("previews", [])):
        mp3 = os.path.join(args.out_dir, "preview_%d.mp3" % i)
        with open(mp3, "wb") as fh:
            fh.write(base64.b64decode(p["audio_base_64"]))
        row = {"i": i, "generated_voice_id": p["generated_voice_id"], "file": mp3,
               "duration": p.get("duration_secs")}
        if not args.no_check:
            fields = {"model_id": "scribe_v1", "language_code": args.language}
            bb, ct = multipart(fields, {"file": mp3})
            sb, _ = call(key, "/v1/speech-to-text", raw_body=bb, content_type=ct)
            heard = json.loads(sb).get("text", "")
            norm = lambda s: [w.strip(".,!?;:\"'").lower() for w in s.split()]
            a, b = norm(text), norm(heard)
            match = sum(1 for w in a if w in set(b)) / max(len(a), 1)
            row.update(heard=heard, word_match=round(match, 3),
                       wpm=round(n_words / (row["duration"] or 1) * 60, 1) if row["duration"] else None)
        report.append(row)
        print("preview %d  %s  %.1fs  wpm=%s  match=%s" % (i, row["generated_voice_id"], row["duration"] or 0,
                                                         row.get("wpm"), row.get("word_match")))
    with open(os.path.join(args.out_dir, "previews.json"), "w", encoding="utf-8") as fh:
        json.dump({"description": args.description, "text": text, "previews": report}, fh, indent=1, ensure_ascii=False)
    print("-> %s" % os.path.join(args.out_dir, "previews.json"))


def cmd_save_voice(args, key):
    """Save a Voice Design preview as a permanent voice on the account."""
    payload = {"voice_name": args.name, "voice_description": args.description,
               "generated_voice_id": args.generated_id}
    body, _ = call(key, "/v1/text-to-voice", data=payload)
    data = json.loads(body)
    print("saved %s -> voice_id %s" % (args.name, data.get("voice_id")))


def cmd_tighten(args, key):
    """Cap pauses between words at --max-gap s (lead-in at --lead s); re-times words.json. No API call."""
    import wave
    import av
    import numpy as np
    data = json.load(open(args.words, encoding="utf-8"))
    words = data["words"]
    c = av.open(args.audio)
    rs = av.AudioResampler(format="s16", layout="mono", rate=44100)
    x = np.concatenate([f.to_ndarray().ravel() for fr in c.decode(c.streams.audio[0]) for f in rs.resample(fr)])
    sr = 44100
    pad = 0.04                      # keep a little breath around each cut
    segs, new_words, t_out = [], [], 0.0
    prev_end = max(words[0]["start"] - args.lead, 0.0)
    for i, w in enumerate(words):
        gap = w["start"] - prev_end
        if i == 0:
            keep_from = prev_end
        elif gap > args.max_gap:
            # keep pad after previous word, then jump to (max_gap - pad) before this word
            segs.append((prev_end, prev_end + pad))
            t_out += pad
            keep_from = w["start"] - (args.max_gap - pad)
        else:
            keep_from = prev_end
        seg_end = w["end"]
        segs.append((keep_from, seg_end))
        new_words.append({"word": w["word"], "start": round(t_out + (w["start"] - keep_from), 3),
                          "end": round(t_out + (seg_end - keep_from), 3)})
        t_out += seg_end - keep_from
        prev_end = seg_end
    segs.append((prev_end, min(prev_end + 0.35, len(x) / sr)))
    out = np.concatenate([x[int(a * sr):int(b * sr)] for a, b in segs])
    with wave.open(args.out, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(out.astype(np.int16).tobytes())
    data["words"] = new_words
    data["tightened"] = {"max_gap": args.max_gap, "lead": args.lead}
    json.dump(data, open(args.words_out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("%.2fs -> %.2fs  (%s, %s)" % (words[-1]["end"], len(out) / sr, args.out, args.words_out))


def _decode_mono(path, sr=44100):
    import av
    import numpy as np
    c = av.open(path)
    rs = av.AudioResampler(format="flt", layout="mono", rate=sr)
    x = np.concatenate([f.to_ndarray().ravel() for fr in c.decode(c.streams.audio[0]) for f in rs.resample(fr)])
    c.close()
    return x


def cmd_tts_lines(args, key):
    """Voice script.json line by line on the original beats.

    script.json: [{"id", "start", "slot_end", "text", "say"?}] -> out-dir/line_NN.mp3 + vo.wav + words.json.
    Each line keeps prosody via previous_text/next_text; a line longer than its slot is sped up
    (atempo) up to --max-speed; anything still over is reported as OVERRUN (rephrase it shorter).
    """
    import subprocess
    import wave
    import numpy as np
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    lines = json.load(open(args.script, encoding="utf-8"))
    os.makedirs(args.out_dir, exist_ok=True)
    sr = 44100
    settings = dict(VOICE_SETTINGS)
    if args.speed:
        settings["speed"] = args.speed
    total = args.total or (lines[-1]["slot_end"] + 1.0)
    track = np.zeros(int(total * sr) + sr, dtype=np.float32)
    all_words, chars, report = [], 0, []
    for i, ln in enumerate(lines):
        if args.only and str(ln["id"]) not in args.only.split(","):
            continue
        text = ln.get("say") or ln["text"]
        mp3 = os.path.join(args.out_dir, "line_%02d.mp3" % ln["id"])
        wj = os.path.join(args.out_dir, "line_%02d.json" % ln["id"])
        if not os.path.exists(mp3) or args.force:
            payload = {"text": text, "model_id": args.model, "voice_settings": settings, "language_code": args.language}
            if i > 0:
                payload["previous_text"] = lines[i - 1].get("say") or lines[i - 1]["text"]
            if i + 1 < len(lines):
                payload["next_text"] = lines[i + 1].get("say") or lines[i + 1]["text"]
            body, _ = call(key, "/v1/text-to-speech/%s/with-timestamps?output_format=mp3_44100_128" % args.voice, data=payload)
            d = json.loads(body)
            open(mp3, "wb").write(base64.b64decode(d["audio_base64"]))
            json.dump(words_from_alignment(d.get("normalized_alignment") or d["alignment"]), open(wj, "w", encoding="utf-8"))
            chars += len(text)
        words = json.load(open(wj, encoding="utf-8"))
        x = _decode_mono(mp3, sr)
        a = max(words[0]["start"] - 0.03, 0); b = min(words[-1]["end"] + 0.10, len(x) / sr)
        seg = x[int(a * sr):int(b * sr)]
        dur = len(seg) / sr
        slot = ln["slot_end"] - ln["start"]
        tempo = 1.0
        if dur > slot:
            tempo = min(dur / slot, args.max_speed)
            tmp_in = os.path.join(args.out_dir, "_tmp_in.wav"); tmp_out = os.path.join(args.out_dir, "_tmp_out.wav")
            with wave.open(tmp_in, "wb") as wf:
                wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
                wf.writeframes((np.clip(seg, -1, 1) * 32767).astype(np.int16).tobytes())
            subprocess.run([ff, "-y", "-loglevel", "error", "-i", tmp_in, "-af", "atempo=%.4f" % tempo, tmp_out], check=True)
            seg = _decode_mono(tmp_out, sr)
        p = int(ln["start"] * sr)
        track[p:p + len(seg)] += seg[:max(len(track) - p, 0)]
        for w in words:
            all_words.append({"word": w["word"], "line": ln["id"],
                              "start": round(ln["start"] + (w["start"] - a) / tempo, 3),
                              "end": round(ln["start"] + (w["end"] - a) / tempo, 3)})
        over = len(seg) / sr - slot
        flag = "OVERRUN %.2fs" % over if over > 0.02 else ""
        report.append((ln["id"], dur, slot, tempo, flag))
        print("%2d  %5.2fs in %5.2fs slot  x%.3f  %s  %s" % (ln["id"], dur, slot, tempo, flag, text[:60]))
    out = os.path.join(args.out_dir, "vo.wav")
    with wave.open(out, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes((np.clip(track[:int(total * sr)], -1, 1) * 32767).astype(np.int16).tobytes())
    json.dump({"voice_id": args.voice, "voice_settings": settings, "words": all_words},
              open(os.path.join(args.out_dir, "words.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("characters billed this run: %d  ->  %s" % (chars, out))
    print("overruns:", [r[0] for r in report if r[4]] or "none")


def cmd_delete_voice(args, key):
    call(key, "/v1/voices/" + args.voice_id, method="DELETE")
    print("deleted %s" % args.voice_id)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--env", default=DEFAULT_ENV)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("voices")

    p = sub.add_parser("tts")
    p.add_argument("--text")
    p.add_argument("--text-file")
    p.add_argument("--voice", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--words")
    p.add_argument("--model", default="eleven_multilingual_v2")
    p.add_argument("--language", default="en")
    p.add_argument("--output-format", default="mp3_44100_128")
    p.add_argument("--speed", type=float)

    p = sub.add_parser("stt")
    p.add_argument("--audio", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--model", default="scribe_v1")
    p.add_argument("--language", default="eng")

    p = sub.add_parser("isolate")
    p.add_argument("--audio", required=True)
    p.add_argument("--out", required=True)

    p = sub.add_parser("design-voice", help="Voice Design previews + STT/pace check (default step for every brand)")
    p.add_argument("--description", required=True, help="voice description prompt (20-1000 chars)")
    p.add_argument("--text"); p.add_argument("--text-file", help="a real script line, 100-1000 chars")
    p.add_argument("--out-dir", required=True)
    p.add_argument("--model", default="eleven_multilingual_ttv_v2")
    p.add_argument("--guidance", type=float)
    p.add_argument("--language", default="eng")
    p.add_argument("--no-check", action="store_true")

    p = sub.add_parser("save-voice")
    p.add_argument("--generated-id", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--description", required=True)

    p = sub.add_parser("tighten", help="cap pauses between words; re-times words.json (local, free)")
    p.add_argument("--audio", required=True); p.add_argument("--words", required=True)
    p.add_argument("--out", required=True); p.add_argument("--words-out", required=True)
    p.add_argument("--max-gap", type=float, default=0.32)
    p.add_argument("--lead", type=float, default=0.12)

    p = sub.add_parser("tts-lines", help="voice script.json line by line on the original beats -> vo.wav + words.json")
    p.add_argument("--script", required=True); p.add_argument("--voice", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--model", default="eleven_multilingual_v2"); p.add_argument("--language", default="en")
    p.add_argument("--speed", type=float); p.add_argument("--max-speed", type=float, default=1.08)
    p.add_argument("--total", type=float); p.add_argument("--only"); p.add_argument("--force", action="store_true")

    p = sub.add_parser("delete-voice", help="operator rule 2026-11-12: only when all slots are full, delete the OLDEST custom voice (log it in VOICE_SPEC.md first)")
    p.add_argument("voice_id")

    args = ap.parse_args()
    key = load_key(args.env)
    {"voices": cmd_voices, "tts": cmd_tts, "stt": cmd_stt, "isolate": cmd_isolate,
     "design-voice": cmd_design_voice, "save-voice": cmd_save_voice, "tighten": cmd_tighten, "tts-lines": cmd_tts_lines,
     "delete-voice": cmd_delete_voice}[args.cmd](args, key)


if __name__ == "__main__":
    main()
