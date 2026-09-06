# Daily post runbook

This is the exact procedure the daily agent follows. Edit this file to change what the
agent does; edit the Routine only to change *when* it runs.

## 0. Preconditions

Run `python3 scripts/pick_today.py`. It reports, per channel, whether to post and why not
if it is skipping. A channel is skipped when it is `enabled: false` in `config.json`, its
account id is still a `REPLACE_...` placeholder, or it already posted successfully today.

If **both** channels come back `"post": false`, there is nothing to do — log a skipped
entry and stop. Never post to a channel the script says to skip.

As of setup: Instagram is live (account **OMEE**); Facebook is disabled pending a
reconnect that grants Page access. See `README.md`.

## 1. Pick today's content

```
day_index   = whole days between config.rotation_start and today (Asia/Kolkata date)
caption     = captions[day_index % len(captions)]     from content/captions.json
image_file  = sorted(content/images/*)[day_index % count]
image_url   = config.images.raw_url_base + "/" + image_file
```

The two lists are different lengths on purpose, so text and image pairings keep varying
instead of repeating in lockstep. If the caption does not already contain `config.link`,
append it on its own line.

`scripts/pick_today.py` does all of this and prints the result as JSON. Run it rather than
recomputing by hand:

```bash
python3 scripts/pick_today.py
```

## 2. Duplicate guard

Already handled by `pick_today.py`: if `log/posted.jsonl` has a line for today's date with
`"status": "ok"` for a channel, that channel comes back `"post": false`. This protects
against a double fire or a manual re-run. Log it as `skipped`.

## 3. Post to Facebook

`execute_zapier_write_action` with:

- `tool_name`: `facebook_pages_create_page_post`
- `selected_api`: `FacebookV2CLIAPI`
- `page`: `config.facebook.page_id`
- `message`: the caption
- `link_url`: `config.link` — this renders as a real clickable link preview
- (no `source`; Facebook uses the link preview image)

## 4. Post to Instagram

`execute_zapier_write_action` with:

- `tool_name`: `instagram_for_business_publish_photo_s`
- `selected_api`: `InstagramBusinessCLIAPI`
- `instagramPageId`: `config.instagram.instagram_page_id` (account **OMEE**)
- `media`: `[image_url]` — Meta fetches this URL server-side, so it must be publicly
  reachable. The repo is public, so `raw.githubusercontent.com` works.
- `caption`: the caption

Instagram **requires** an image. There is no link-only Instagram post.

Attempt each channel independently: an Instagram failure must not suppress the Facebook
post, and vice versa.

## 5. Log and push

Append one line to `log/posted.jsonl`:

```json
{"date":"2026-09-07","day_index":0,"caption_index":0,"image":"elephant.png","facebook":{"status":"ok","id":"..."},"instagram":{"status":"ok","id":"..."}}
```

Use `{"status":"error","error":"..."}` for a failure and `{"status":"skipped"}` for a
duplicate. Then commit and push to `claude/agent-daily-social-messaging-wzgkqk`.

## 6. On failure — do not retry blindly

One attempt per channel per day. An auth error retried in a loop is how an app gets
rate-limited by Meta. Log the error, push, and report it — the Routine's push
notification carries the reason.

Common failures:

| Symptom | Cause | Fix |
|---|---|---|
| `Session has expired` / `Error validating access token` | Facebook OAuth token lapsed | Reconnect Facebook Pages in Zapier |
| `Authorization access_token missing` | Instagram connection dropped | Reconnect Instagram for Business in Zapier |
| Facebook Page dropdown is empty | Connection authorized without Page access | Reconnect Facebook in Zapier and tick the Page |
| Instagram rejects the media | Image URL not publicly reachable, or wrong format/size | Confirm the raw URL returns 200 and the file is JPG/PNG |
| Post succeeds but no link preview on Facebook | `link_url` omitted | Include `link_url` |
