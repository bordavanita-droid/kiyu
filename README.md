# Daily pinemb.in social posting

Posts [pinemb.in](https://www.pinemb.in/) to the Facebook Page and Instagram every day at
**10:00 AM IST**, automatically. A scheduled Claude Routine wakes up, reads this repo,
picks the day's caption and image, publishes to both networks via Zapier, and logs the
result back here.

## How it picks what to post

Deterministic by date — no randomness, so you can always tell what will post when:

```bash
python3 scripts/pick_today.py            # today
python3 scripts/pick_today.py 2026-10-01 # preview any future date
```

Captions and images rotate independently (14 captions, N images), so the pairings keep
changing rather than repeating in lockstep.

## Changing things

| To do this | Edit |
|---|---|
| Change the wording | `content/captions.json` — add or rewrite entries freely |
| Add design photos | Drop JPG/PNG files into `content/images/` and push; picked up automatically |
| Change Page / IG account | `config.json` |
| Change what the agent does | `RUNBOOK.md` |
| Change the time, or pause | The Routine — ask Claude to reschedule, disable, or delete it |

### Image requirements

- JPG or PNG (Instagram also takes GIF/BMP; Facebook takes JPEG/BMP/PNG/GIF/TIFF)
- Under 4 MB; keep PNGs under 1 MB or Facebook may show them pixelated
- Square or 4:5 portrait works best on Instagram
- The repo is public, so Meta fetches these directly from `raw.githubusercontent.com`.
  **Only put images here that you are happy to have publicly readable.**

## History

`log/posted.jsonl` — one line per day with the caption index, image, and per-channel
status or error. It is also the duplicate guard: a channel already marked `ok` for today
will not be posted to twice.

## Channel status

| Channel | Status |
|---|---|
| **Instagram** (`OMEE`) | Live — posting daily |
| **Facebook Page** | **Disabled** — needs a reconnect, see below |

### Turning Facebook on

The Zapier Facebook connection is authenticated but returns an **empty Page list**, which
means it was authorized without access to the Page. To fix:

1. Reconnect Facebook, and when Facebook asks which Pages to allow, **tick the pinemb
   Page** (do not skip that screen):
   https://mcp.zapier.com/api/v1/connect-auth/FacebookV2CLIAPI?accountId=12392537&connectionId=65912764
2. Tell Claude to finish wiring Facebook — it will read the Page ID, put it in
   `config.json`, and flip `facebook.enabled` to `true`.

Instagram posting is unaffected by this and continues either way.

## Notes

- Instagram captions never render clickable links. The URL is in the caption to be read
  and typed; for a clickable path from Instagram, put pinemb.in in the profile bio link.
- Posting the same link every day is inherently spam-adjacent to Meta. Rotating captions
  and images is the mitigation. If reach drops, post fewer days per week rather than
  writing more copy.
