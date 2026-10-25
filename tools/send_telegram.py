"""Send a day's post (slides, story, caption, notes) to Thomas via his own Telegram bot.

Runs on Thomas's computer (Telegram is not reachable from the cloud). Standard library only.

usage: python3 send_telegram.py <date> [notes.txt]
  Reads TELEGRAM_TOKEN and TELEGRAM_CHAT_ID from the env file given by THOMAS_TG_ENV
  (default: ~/.thomas_telegram.env, lines KEY=VALUE). The token is never stored in the repo.
  Images and caption are downloaded from the repo's raw GitHub URLs.
"""
import json, os, sys, uuid, urllib.request

RAW = "https://raw.githubusercontent.com/tomassaaamir49-byte/thomas-posts/main/posts/{date}/{name}"


def load_env():
    path = os.path.expanduser(os.environ.get("THOMAS_TG_ENV", "~/.thomas_telegram.env"))
    env = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k.strip()] = v.strip()
    return env["TELEGRAM_TOKEN"], env["TELEGRAM_CHAT_ID"]


def get(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read()


def call(token, method, fields, files=None):
    url = f"https://api.telegram.org/bot{token}/{method}"
    if not files:
        data = json.dumps(fields).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    else:
        b = uuid.uuid4().hex
        body = b""
        for k, v in fields.items():
            body += f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
        for k, (fname, content) in files.items():
            body += (f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{fname}\"\r\n"
                     "Content-Type: image/jpeg\r\n\r\n").encode() + content + b"\r\n"
        body += f"--{b}--\r\n".encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        res = json.loads(r.read())
    if not res.get("ok"):
        raise SystemExit(f"{method} failed: {res}")
    return res


def main(date, notes_path=None):
    token, chat = load_env()
    slides = []
    for i in range(1, 21):
        name = f"slide_{i:02d}.jpg"
        try:
            slides.append((name, get(RAW.format(date=date, name=name))))
        except Exception:
            break
    if not slides:
        raise SystemExit("no slides found for " + date)
    media = [{"type": "photo", "media": f"attach://{n.split('.')[0]}"} for n, _ in slides]
    media[0]["caption"] = f"بوست {date} — {len(slides)} صور بالترتيب"
    call(token, "sendMediaGroup", {"chat_id": chat, "media": json.dumps(media, ensure_ascii=False)},
         {n.split('.')[0]: (n, c) for n, c in slides})
    call(token, "sendPhoto", {"chat_id": chat, "caption": "الستوري (بعد البوست بربع ساعة)"},
         {"photo": ("story.jpg", get(RAW.format(date=date, name="story.jpg")))})
    caption = get(RAW.format(date=date, name="caption.txt")).decode("utf-8")
    call(token, "sendMessage", {"chat_id": chat, "text": caption})
    if notes_path:
        with open(notes_path, encoding="utf-8") as f:
            call(token, "sendMessage", {"chat_id": chat, "text": f.read()})
    print("sent", len(slides), "slides + story + caption")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
