#!/usr/bin/env python3
"""Voice-over for video remakes: stems, voice clone, re-voiced lines spliced on their beats, mix.

Operator rule: all voice work goes through the ElevenLabs API directly (not Kie). Re-voiced lines use
an instant clone of the ORIGINAL video's voice, so the voice stays identical across the splice.

Subcommands
  separate SRC --out DIR                 demucs htdemucs two stems -> DIR/vocals.wav, DIR/music.wav
  skeleton ORIG_WORDS.json --out script.json [--seed N] [--total S]
                                         sentences -> lines; marks the 3 mandatory remakes (hook = opening
                                         sentence/thought, end = closing line/CTA, one random body line)
                                         with "remake"; every other line gets "keep": true (original voice)
  clone [SAMPLE.wav ...] --name "Krino v01 narrator" [--from vocals.wav --start S --end E]
                                         ElevenLabs instant clone (POST /v1/voices/add) -> prints voice_id
  delete-voice VOICE_ID                  free a clone slot (10 slots on Starter)
  voices --tts elevenlabs|edge [--locale es-MX]          list available voices
  audition --text "..." --out DIR [--spec A.json B.json] [--edge es-MX-JorgeNeural,...]
                                         same lines, several voices -> DIR/NN-<name>.mp3 for the operator
  build SCRIPT.json --out vo.wav --spec VOICE_SPEC.json [--match vocals.wav] [--one-take] [--max-speed 1.08]
                                         lines without "keep" are voiced, each placed at its beat start and
                                         fitted inside its slot; prints the --replace windows for mix
  mix --vo vo.wav --out mix.wav [--music music.wav] [--duck 9] [--lufs -14]
      [--orig orig.wav --replace 44.72-48.98,68.06-70.49]
                                         music ducked under the VO (--duck 0 = none), loudness-normalised,
                                         limited to -1 dBTP; --orig/--replace keeps the original audio
                                         outside the windows (splice mode for cloned-voice remakes)

SCRIPT.json: {"total": 23.5, "lines": [{"start": 0.0, "end": 2.30, "text": "...", "say": "...", "keep": false}]}
  start = original beat start (from video_transcribe.py); end = latest allowed end (next beat start
  minus ~0.05-0.14 s, never across a cut); "say" = TTS respelling (e.g. "Awe-ree-uh"), optional;
  "keep": true = the original voice stays for that line (not voiced, not in the --replace windows).
Fitting: trim silence, shorten inner pauses to 0.13 s, then speed up at most --max-speed (1.08).
  A line that still does not fit is reported REPHRASE (exit 2): shorten the text, never speed up more.
--match vocals.wav: VO set to the loudness of the original voice stem (splice mode; then mix --duck 0).
VOICE_SPEC.json (exact spec saved per video; defaults = the operator's ElevenLabs settings):
  {"provider": "elevenlabs", "voice_id": "...", "model_id": "eleven_multilingual_v2", "language_code": "es",
   "voice_settings": {"stability": 0.55, "similarity_boost": 0.9, "style": 0.15, "use_speaker_boost": true}}
  {"provider": "edge", "voice": "es-MX-JorgeNeural", "rate": "+10%"}   free; timing drafts only
  {"provider": "gemini", "request": {<Kie createTask body>}}         legacy; only if the operator asks
--one-take: synthesise the whole script in ONE call and split it at the silences. Needs faster-whisper.
Keys: ELEVENLABS_API_KEY (env, or --secrets file, default G:/Ecom/Products/.secrets/elevenlabs.env);
  KIE_API_KEY (env, legacy). Raw TTS takes are cached in --cache (default next to --out) by text hash,
  so re-runs cost nothing.
"""
import argparse, copy, hashlib, json, os, re, shutil, subprocess, sys, tempfile, time, urllib.request
import numpy as np

SR = 48000
SECRETS = "G:/Ecom/Products/.secrets/elevenlabs.env"
EL_DEFAULT = {"model_id": "eleven_multilingual_v2",
              "voice_settings": {"stability": 0.55, "similarity_boost": 0.9, "style": 0.15, "use_speaker_boost": True}}


def ffmpeg():
    p = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if p:
        return p
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


FF = ffmpeg()


def run(*a):
    subprocess.run([FF, "-v", "error", "-y", *a], check=True)


def load(p, ch=1):
    b = subprocess.run([FF, "-v", "error", "-i", p, "-ac", str(ch), "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True, check=True).stdout
    x = np.frombuffer(b, np.float32).copy()
    return x.reshape(-1, ch) if ch > 1 else x


def save(p, x):
    x = np.asarray(x, np.float32)
    ch = 1 if x.ndim == 1 else x.shape[1]
    fd, raw = tempfile.mkstemp(suffix=".f32")
    os.close(fd)
    x.tofile(raw)
    run("-f", "f32le", "-ar", str(SR), "-ac", str(ch), "-i", raw, "-c:a", "pcm_s16le", p)
    os.remove(raw)


def env_db(x, hop=0.01):
    h = int(SR * hop)
    n = len(x) // h
    return 20 * np.log10(np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-9), h


def lufs(p):
    err = subprocess.run([FF, "-hide_banner", "-i", p, "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True, errors="replace").stderr
    s = err[err.rfind("Summary:"):]
    return float(re.search(r"I:\s+(-?[\d.]+) LUFS", s).group(1)), float(re.search(r"Peak:\s+(-?[\d.inf]+) dBFS", s).group(1))


# ---------------- TTS providers ----------------
def http(url, body=None, headers=None, raw=False):
    r = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                               headers={"Content-Type": "application/json", **(headers or {})})
    d = urllib.request.urlopen(r, timeout=180).read()
    return d if raw else json.loads(d)


def eleven_key(secrets):
    k = os.environ.get("ELEVENLABS_API_KEY")
    if not k and secrets and os.path.exists(secrets):
        m = re.search(r"ELEVENLABS_API_KEY\s*=\s*(\S+)", open(secrets, encoding="utf-8").read())
        k = m and m.group(1).strip("\"'")
    if not k:
        sys.exit("ELEVENLABS_API_KEY missing (env or --secrets file)")
    return k


def tts(text, out, spec, secrets=SECRETS, prev=None, nxt=None):
    """Write `text` spoken with `spec` to `out` (any audio extension ffmpeg can read)."""
    prov = spec.get("provider") or ("gemini" if "request" in spec else "elevenlabs" if "voice_id" in spec else "edge")
    if prov == "edge":
        subprocess.run([sys.executable, "-m", "edge_tts", "--voice", spec.get("voice", "en-US-ChristopherNeural"),
                        f"--rate={spec.get('rate', '+0%')}", f"--pitch={spec.get('pitch', '+0Hz')}",
                        "--text", text, "--write-media", out], check=True)
    elif prov == "elevenlabs":
        body = {"text": text, "model_id": spec.get("model_id", EL_DEFAULT["model_id"]),
                "voice_settings": spec.get("voice_settings", EL_DEFAULT["voice_settings"])}
        for k in ("seed", "language_code"):
            if k in spec:
                body[k] = spec[k]
        if prev:
            body["previous_text"] = prev
        if nxt:
            body["next_text"] = nxt
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{spec['voice_id']}?output_format=mp3_44100_128"
        open(out, "wb").write(http(url, body, {"xi-api-key": eleven_key(secrets)}, raw=True))
    elif prov == "gemini":
        key = os.environ.get("KIE_API_KEY") or sys.exit("KIE_API_KEY missing")
        body = copy.deepcopy(spec["request"])
        body["input"]["dialogue_turns"][0]["text"] = text
        hd = {"Authorization": "Bearer " + key}
        for attempt in range(6):  # upstream 524 "generate task timeout" is common and free: retry
            tid = http("https://api.kie.ai/api/v1/jobs/createTask", body, hd)["data"]["taskId"]
            for _ in range(120):
                time.sleep(3)
                d = http(f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={tid}", None, hd)["data"]
                if d["state"] in ("success", "fail"):
                    break
            if d["state"] == "success":
                urllib.request.urlretrieve(json.loads(d["resultJson"])["resultUrls"][0], out)
                return out
            print(f"  gemini attempt {attempt + 1} failed: {d.get('failCode')} {d.get('failMsg')}")
        raise RuntimeError("Kie Gemini TTS failed 6 times")
    else:
        sys.exit(f"unknown provider {prov}")
    return out


def cached_tts(text, spec, cache, secrets, prev=None, nxt=None):
    os.makedirs(cache, exist_ok=True)
    h = hashlib.sha1(json.dumps([text, spec, prev, nxt], sort_keys=True).encode()).hexdigest()[:10]
    p = os.path.join(cache, f"tts-{h}.audio")
    if not os.path.exists(p):
        tts(text, p + ".part", spec, secrets, prev, nxt)
        os.replace(p + ".part", p)
    return p


# ---------------- fitting ----------------
TH = -42.0


def trim(x, pad=0.02):
    d, h = env_db(x)
    act = np.where(d > TH)[0]
    if not len(act):
        return x
    return x[max(0, act[0] * h - int(pad * SR)):min(len(x), (act[-1] + 1) * h + int(pad * SR))]


def shrink_pauses(x, need, keep=0.13):
    d, h = env_db(x)
    q, runs, i = d <= TH, [], 0
    while i < len(q):
        j = i
        while j < len(q) and q[j] == q[i]:
            j += 1
        if q[i] and i > 0 and j < len(q) and (j - i) * 0.01 > keep:
            runs.append((i * h, j * h))
        i = j
    cuts = []
    for a, b in sorted(runs, key=lambda r: r[0] - r[1]):  # longest pauses first
        if need <= 0:
            break
        c = min((b - a) / SR - keep, need)
        need -= c
        m, k = (a + b) // 2, int(c * SR / 2)
        cuts.append((m - k, m + k))
    for a, b in sorted(cuts, reverse=True):
        x = np.concatenate([x[:a], x[b:]])
    return x


def tempo(x, f):
    if f <= 1.0005:
        return x
    fd, a = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    save(a, x)
    b = a[:-4] + "_t.wav"
    run("-i", a, "-af", f"atempo={f:.4f}", b)
    y = load(b)
    os.remove(a), os.remove(b)
    return y


def split_take(x, lines, lang):
    """Cut one continuous take into lines at the longest silence near each char-proportional boundary."""
    from faster_whisper import WhisperModel
    fd, w = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    save(w, x)
    segs, _ = WhisperModel("small", device="cpu", compute_type="int8").transcribe(w, language=lang, word_timestamps=True)
    words = [(wd.start, wd.end, wd.word) for s in segs for wd in s.words]
    os.remove(w)
    clen = lambda s: len(re.sub(r"\W", "", s))
    tot_w = sum(clen(t) for _, _, t in words) or 1
    tot_s = sum(clen(l.get("say", l["text"])) for l in lines)
    d, h = env_db(x)
    bounds, acc = [0], 0
    for l in lines[:-1]:
        acc += clen(l.get("say", l["text"]))
        target, run_c, t_est = acc / tot_s * tot_w, 0, words[-1][1]
        for k, (s, e, t) in enumerate(words):
            run_c += clen(t)
            if run_c >= target:
                t_est = (e + words[k + 1][0]) / 2 if k + 1 < len(words) else e
                break
        lo, hi = max(0, int((t_est - 0.4) * 100)), min(len(d) - 1, int((t_est + 0.4) * 100))
        q, best, i = d[lo:hi + 1] < -45, (0, None), 0
        while i < len(q):
            j = i
            while j < len(q) and q[j] == q[i]:
                j += 1
            if q[i] and j - i > best[0]:
                best = (j - i, (i + j) // 2)
            i = j
        c = best[1] if best[1] is not None else int(np.argmin(d[lo:hi + 1]))
        bounds.append((lo + c) * h)
    bounds.append(len(x))
    return [x[bounds[i]:bounds[i + 1]] for i in range(len(lines))]


def cmd_build(a):
    sc = json.load(open(a.script, encoding="utf-8"))
    spec = json.load(open(a.spec, encoding="utf-8")) if a.spec else {"provider": "edge", "voice": a.voice}
    lines = [l for l in sc["lines"] if not l.get("keep")]
    cache = a.cache or os.path.join(os.path.dirname(os.path.abspath(a.out)), "tts-cache")
    say = [l.get("say", l["text"]) for l in lines]
    if a.one_take:
        segs = split_take(load(cached_tts(" ".join(say), spec, cache, a.secrets)), lines, a.lang)
    else:
        segs = [load(cached_tts(t, spec, cache, a.secrets, say[i - 1] if i else None,
                                say[i + 1] if i + 1 < len(say) else None)) for i, t in enumerate(say)]
    total = sc.get("total") or lines[-1]["end"] + 0.5
    track, info, bad = np.zeros(int(total * SR) + SR), [], 0
    for i, (l, x) in enumerate(zip(lines, segs)):
        x, slot = trim(x), l["end"] - l["start"]
        if len(x) / SR > slot:
            x = trim(shrink_pauses(x, len(x) / SR - slot))
        f = max(1.0, len(x) / SR / slot)
        ok = f <= a.max_speed
        x = tempo(x, min(f, a.max_speed))
        s = int(l["start"] * SR)
        track[s:s + len(x)] += x[:len(track) - s]
        info.append({"i": i, "start": l["start"], "end": round(l["start"] + len(x) / SR, 3), "slot_end": l["end"],
                     "speed": round(f, 3), "ok": ok, "text": l["text"]})
        bad += not ok
        print(f"{i:2d} {'OK      ' if ok else 'REPHRASE'} {l['start']:6.2f}-{l['start'] + len(x) / SR:6.2f} "
              f"(slot {l['end']:6.2f}) x{f:.3f}  {l['text']}")
    track = track[:int(total * SR)]
    if a.match:
        fd, tmp = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        save(tmp, track)
        g = lufs(a.match)[0] - lufs(tmp)[0]
        os.remove(tmp)
        track = track * 10 ** (g / 20)
        print(f"VO level matched to {a.match} ({g:+.1f} dB)")
    save(a.out, track)
    print("mix --replace " + ",".join(f"{max(0, l['start'] - 0.04):.2f}-{max(l['end'], i['end']) + 0.04:.2f}"
                                      for l, i in zip(lines, info)))
    json.dump(info, open(os.path.splitext(a.out)[0] + "_info.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("vo", a.out, f"({bad} line(s) to rephrase)" if bad else "")
    return 2 if bad else 0


# ---------------- mix ----------------
def cmd_mix(a):
    vo = load(a.vo, 2)
    n = len(vo)
    if a.orig:
        n = len(load(a.orig, 2))
    pad = lambda x: np.pad(x, ((0, max(0, n - len(x))), (0, 0)))[:n]
    vo = pad(vo)
    rep = vo.copy()
    if a.music:
        mu = pad(load(a.music, 2))
        d, h = env_db(vo.mean(1))
        core = d > (d.max() - 30)
        act = np.convolve(core.astype(float), np.ones(61), "same") > 0  # hold 0.3 s around speech
        md, _ = env_db(mu.mean(1))
        pw = lambda v: 10 * np.log10(np.mean(10 ** (v / 10)) + 1e-12)  # power mean of frame levels
        if core.any() and a.duck > 0:
            g_db = min(0.0, (pw(d[core]) - a.duck) - pw(md[core]))
            g = np.where(act, 10 ** (g_db / 20), 1.0)
            g = np.convolve(g, np.ones(9) / 9, "same")  # ~90 ms ramps
            g = np.repeat(g, h)
            g = np.pad(g, (0, n - len(g)), mode="edge")[:n]
            mu = mu * g[:, None]
            print(f"music gain under speech {g_db:+.1f} dB -> {pw(d[core]) - pw(md[core]) - g_db:.1f} dB below the voice (target {a.duck})")
        rep = vo + mu
    out = rep
    if a.orig:
        o = pad(load(a.orig, 2))
        w = np.ones(n)  # 1 = original
        for iv in filter(None, a.replace.split(",")):
            t0, t1 = (float(v) for v in iv.split("-"))
            s, e, r = int(t0 * SR), int(t1 * SR), int(a.xfade * SR)
            w[s:e] = 0
            w[max(0, s - r):s] = 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, s - max(0, s - r)))
            w[e:e + r] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, len(w[e:e + r])))
        out = o * w[:, None] + rep * (1 - w[:, None])
    fd, tmp = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    save(tmp, out)
    li, _ = lufs(tmp)
    run("-i", tmp, "-af", f"volume={a.lufs - li:.2f}dB,alimiter=limit=0.87:level=false", "-ar", str(SR), a.out)
    os.remove(tmp)
    lo, pk = lufs(a.out)
    print(f"mix {a.out}: {lo:.1f} LUFS, peak {pk:.1f} dBFS")


# ---------------- other subcommands ----------------
def cmd_separate(a):
    os.makedirs(a.out, exist_ok=True)
    tmp = tempfile.mkdtemp()
    wav = os.path.join(tmp, "audio.wav")
    run("-i", a.src, "-vn", "-ac", "2", "-ar", "44100", wav)
    subprocess.run([sys.executable, "-m", "demucs", "--two-stems", "vocals", "-n", a.model, "-o", tmp, wav], check=True)
    d = os.path.join(tmp, a.model, "audio")
    shutil.move(os.path.join(d, "vocals.wav"), os.path.join(a.out, "vocals.wav"))
    shutil.move(os.path.join(d, "no_vocals.wav"), os.path.join(a.out, "music.wav"))
    shutil.rmtree(tmp, ignore_errors=True)
    for s in ("vocals", "music"):
        print(s, os.path.join(a.out, s + ".wav"), "%.1f LUFS" % lufs(os.path.join(a.out, s + ".wav"))[0])


def cmd_skeleton(a):
    import random
    W = json.load(open(a.words, encoding="utf-8"))
    sents, cur = [], []
    for w in W:
        cur.append(w)
        if w[2].strip()[-1:] in ".?!":
            sents.append(cur)
            cur = []
    sents += [cur] if cur else []
    total = a.total or W[-1][1] + 0.5
    lines = []
    for k, st in enumerate(sents):
        nxt = sents[k + 1][0][0] - 0.06 if k + 1 < len(sents) else total - 0.05
        txt = re.sub(r" (?=[%,.!?:;])", "", " ".join(w[2].strip() for w in st))
        lines.append({"start": round(st[0][0], 2), "end": round(nxt, 2), "orig": txt, "text": txt, "keep": True})
    picks = {0: "hook", len(lines) - 1: "end"}
    if len(lines) > 2:
        picks[random.Random(a.seed).randrange(1, len(lines) - 1)] = "body"
    for k, why in picks.items():
        lines[k].update(keep=False, remake=why)
    json.dump({"total": round(total, 2), "lines": lines}, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for l in lines:
        print(f"{l['start']:6.2f}-{l['end']:6.2f} {l.get('remake', 'keep'):5s} {l['orig']}")
    print("skeleton", a.out, "- rewrite 'text' of the remake lines (same meaning, length, claim strength),"
          " split or merge lines so the hook is the whole opening thought, and set keep=false on every line"
          " that names the competitor")


def cmd_clone(a):
    files = list(a.samples)
    if a.src:
        fd, cut = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        run("-ss", str(a.start or 0), "-i", a.src, *(["-t", str(a.end - (a.start or 0))] if a.end else []),
            "-ac", "1", "-ar", "44100", cut)
        files.append(cut)
    bnd = "----vo" + hashlib.sha1(os.urandom(8)).hexdigest()

    def part(name, val):
        return f'--{bnd}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{val}\r\n'.encode()
    body = part("name", a.name) + part("remove_background_noise", "false")
    if a.description:
        body += part("description", a.description)
    for f in files:
        body += (f'--{bnd}\r\nContent-Disposition: form-data; name="files"; filename="{os.path.basename(f)}"\r\n'
                 'Content-Type: audio/wav\r\n\r\n').encode() + open(f, "rb").read() + b"\r\n"
    body += f"--{bnd}--\r\n".encode()
    r = urllib.request.Request("https://api.elevenlabs.io/v1/voices/add", data=body, method="POST",
                               headers={"xi-api-key": eleven_key(a.secrets),
                                        "Content-Type": f"multipart/form-data; boundary={bnd}"})
    vid = json.loads(urllib.request.urlopen(r, timeout=300).read())["voice_id"]
    print("voice_id", vid, "- record it in the PLAN; free the slot later with: video_vo.py delete-voice", vid)


def cmd_delete_voice(a):
    r = urllib.request.Request(f"https://api.elevenlabs.io/v1/voices/{a.voice_id}", method="DELETE",
                               headers={"xi-api-key": eleven_key(a.secrets)})
    print(urllib.request.urlopen(r, timeout=60).read().decode())


def cmd_voices(a):
    if a.tts == "edge":
        out = subprocess.run([sys.executable, "-m", "edge_tts", "--list-voices"], capture_output=True, text=True).stdout
        print("\n".join(l for l in out.splitlines() if not a.locale or a.locale in l or l.startswith("Name")))
    else:
        for v in http("https://api.elevenlabs.io/v1/voices", None, {"xi-api-key": eleven_key(a.secrets)})["voices"]:
            print(v["voice_id"], v["name"], v.get("category", ""), json.dumps(v.get("labels", {}), ensure_ascii=False))


def cmd_audition(a):
    os.makedirs(a.out, exist_ok=True)
    specs = [(os.path.splitext(os.path.basename(p))[0], json.load(open(p, encoding="utf-8"))) for p in a.spec or []]
    specs += [(v, {"provider": "edge", "voice": v, "rate": a.rate}) for v in filter(None, (a.edge or "").split(","))]
    for i, (name, spec) in enumerate(specs, 1):
        out = os.path.join(a.out, f"{i:02d}-{name}.mp3")
        src = tts(a.text, out + ".src", spec, a.secrets)
        run("-i", src, "-map_metadata", "-1", "-ac", "1", "-ar", "44100", "-b:a", "160k", out)
        os.remove(src)
        print(out, f"{len(load(out)) / SR:.1f} s")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("separate"); p.add_argument("src"); p.add_argument("--out", required=True)
    p.add_argument("--model", default="htdemucs"); p.set_defaults(f=cmd_separate)
    p = sub.add_parser("skeleton"); p.add_argument("words"); p.add_argument("--out", required=True)
    p.add_argument("--seed", type=int); p.add_argument("--total", type=float); p.set_defaults(f=cmd_skeleton)
    p = sub.add_parser("clone"); p.add_argument("samples", nargs="*"); p.add_argument("--name", required=True)
    p.add_argument("--from", dest="src"); p.add_argument("--start", type=float); p.add_argument("--end", type=float)
    p.add_argument("--description"); p.add_argument("--secrets", default=SECRETS); p.set_defaults(f=cmd_clone)
    p = sub.add_parser("delete-voice"); p.add_argument("voice_id"); p.add_argument("--secrets", default=SECRETS)
    p.set_defaults(f=cmd_delete_voice)
    p = sub.add_parser("voices"); p.add_argument("--tts", choices=["edge", "elevenlabs"], default="elevenlabs")
    p.add_argument("--locale"); p.add_argument("--secrets", default=SECRETS); p.set_defaults(f=cmd_voices)
    p = sub.add_parser("audition"); p.add_argument("--text", required=True); p.add_argument("--out", required=True)
    p.add_argument("--spec", nargs="*"); p.add_argument("--edge"); p.add_argument("--rate", default="+0%")
    p.add_argument("--secrets", default=SECRETS); p.set_defaults(f=cmd_audition)
    p = sub.add_parser("build"); p.add_argument("script"); p.add_argument("--out", required=True)
    p.add_argument("--spec"); p.add_argument("--voice", default="en-US-ChristopherNeural", help="edge voice if no --spec")
    p.add_argument("--one-take", action="store_true"); p.add_argument("--lang"); p.add_argument("--match")
    p.add_argument("--max-speed", type=float, default=1.08); p.add_argument("--cache")
    p.add_argument("--secrets", default=SECRETS); p.set_defaults(f=cmd_build)
    p = sub.add_parser("mix"); p.add_argument("--vo", required=True); p.add_argument("--out", required=True)
    p.add_argument("--music"); p.add_argument("--duck", type=float, default=9.0); p.add_argument("--lufs", type=float, default=-14.0)
    p.add_argument("--orig"); p.add_argument("--replace", default=""); p.add_argument("--xfade", type=float, default=0.04)
    p.set_defaults(f=cmd_mix)
    a = ap.parse_args()
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
