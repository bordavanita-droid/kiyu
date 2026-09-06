#!/usr/bin/env python3
"""Pick today's caption and image for the daily pinemb.in social post.

Deterministic by date: given the same date you always get the same pairing, so
you can tell in advance what will post on any given day.

Usage:
    python3 scripts/pick_today.py            # today, Asia/Kolkata
    python3 scripts/pick_today.py 2026-09-14 # any date, for previewing
"""

import json
import os
import sys
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".gif", ".bmp")


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        return json.load(fh)


def local_today(tz_offset_hours=5.5):
    """Today's date in the configured timezone, without needing tzdata."""
    return (datetime.now(timezone.utc) + timedelta(hours=tz_offset_hours)).date()


def already_posted_ok(day, channel):
    """True if log/posted.jsonl already records a successful post for this day."""
    log = os.path.join(ROOT, "log", "posted.jsonl")
    if not os.path.exists(log):
        return False
    with open(log, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("date") == day and entry.get(channel, {}).get("status") == "ok":
                return True
    return False


def main():
    config = load("config.json")
    captions = load("content/captions.json")["captions"]

    image_dir = os.path.join(ROOT, config["images"]["dir"])
    images = sorted(
        f for f in os.listdir(image_dir) if f.lower().endswith(IMAGE_EXTS)
    )
    if not images:
        sys.exit(f"No images in {config['images']['dir']} - nothing to post to Instagram.")

    today = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else local_today()
    start = date.fromisoformat(config["rotation_start"])
    day_index = max((today - start).days, 0)

    caption = captions[day_index % len(captions)]
    link = config["link"]
    if link not in caption:
        caption = f"{caption}\n{link}"
    image = images[day_index % len(images)]

    fb, ig = config["facebook"], config["instagram"]
    day = today.isoformat()

    def should_post(channel, cfg, id_key):
        """A channel posts only if enabled, wired up, and not already done today."""
        if not cfg.get("enabled"):
            return False, "disabled in config.json"
        if "REPLACE" in cfg[id_key]:
            return False, "channel id not configured"
        if already_posted_ok(day, channel):
            return False, "already posted successfully today"
        return True, None

    post_fb, fb_reason = should_post("facebook", fb, "page_id")
    post_ig, ig_reason = should_post("instagram", ig, "instagram_page_id")

    print(json.dumps({
        "date": day,
        "day_index": day_index,
        "caption_index": day_index % len(captions),
        "caption": caption,
        "image": image,
        "image_url": f"{config['images']['raw_url_base']}/{image}",
        "link": link,
        "facebook": {
            "post": post_fb, "skip_reason": fb_reason, "page_id": fb["page_id"],
        },
        "instagram": {
            "post": post_ig, "skip_reason": ig_reason,
            "instagram_page_id": ig["instagram_page_id"],
            "account_name": ig.get("account_name"),
        },
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
