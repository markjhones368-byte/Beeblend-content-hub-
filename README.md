# BeeBlend AI Content Hub

Turns your brand guide + product list into Instagram-ready posts, with a
human approval step, using GitHub as the backbone.

## How it flows

```
brand/brand-dna.md  ─┐
                      ├─► scripts/generate_content.py ─► output/pending/*.json ─► PR opens
products/products.json ┘                                                            │
                                                                          you review & merge
                                                                                    │
                                                                                    ▼
                                                          scripts/publish_to_instagram.py
                                                                    (auto, on merge)
                                                                                    │
                                                                                    ▼
                                                                        Live on Instagram
```

## One-time setup

1. **Create the repo.** Push this folder to a new GitHub repo (private is fine —
   Instagram's API only needs the *image* to be publicly fetchable, not the repo).
   Actually, simplest: keep `products/images/` in a **public** repo, or in a
   public folder of an existing one, so the raw GitHub URL is fetchable.

2. **Get an Instagram Graph API access token.**
   - You need an Instagram **Business or Creator** account linked to a Facebook Page.
   - Go to developers.facebook.com → create an app → add the "Instagram Graph API" product.
   - Generate a long-lived Page Access Token and note your **Instagram Business Account ID**.
   - This part is fiddly — if you get stuck, tell me and I'll walk you through the
     exact clicks for your account.

3. **Add secrets to the repo** (Settings → Secrets and variables → Actions):
   - `ANTHROPIC_API_KEY` — your Claude API key
   - `IG_ACCESS_TOKEN` — the Page access token from step 2
   - `IG_BUSINESS_ACCOUNT_ID` — your Instagram business account ID

4. **Fill in your real data:**
   - Edit `brand/brand-dna.md` with your actual tone/colours/audience notes
   - Edit `products/products.json` with real SKUs
   - Drop real product photos into `products/images/` (same filename as each
     product's `"image"` field)

5. **Turn on the workflows** — they're already in `.github/workflows/`. GitHub
   runs `generate-content.yml` weekly (or on demand from the Actions tab), and
   `publish-approved.yml` fires automatically whenever a PR merges into `main`.

## Day-to-day use

- Every Monday (or whenever you trigger it manually), a PR appears with 3 new
  draft captions.
- Open the PR, read the captions in the "Files changed" tab, edit inline if
  you want changes, then **merge** to approve.
- Within a minute or two it's live on your Instagram feed.
- To reject a draft instead, just close the PR without merging, or delete
  that one file from the PR before merging.

## Notes / limits

- This generates **captions + hashtags** paired with your **existing product
  photos**. It does not generate new images — Claude's text API doesn't do
  that. If you want AI-generated imagery too, that's a separate step I can
  add later (e.g. calling an image model and committing the result before
  the PR opens).
- Instagram only accepts **feed image posts** through this exact script.
  Reels/Stories/Carousels need slightly different API calls — same idea,
  different endpoint. Ask me and I'll add those scripts once feed posting
  is working end to end.
