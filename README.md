# VidDrop 🎬

Download any video from 1000+ platforms — YouTube, TikTok, Instagram, Twitter, and more. Pick quality, pick format, save.

## Stack

- **Frontend:** Vanilla HTML/CSS/JS — zero dependencies
- **Backend:** Python serverless functions (`yt-dlp`)
- **Hosting:** Vercel

---

## Deploy to Vercel

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Clone / upload this project

Put all these files in a folder:
```
viddrop/
├── api/
│   ├── info.py       ← fetches video metadata + formats
│   └── download.py   ← streams the actual download
├── public/
│   └── index.html    ← the frontend
├── requirements.txt  ← yt-dlp
└── vercel.json       ← routing config
```

### 3. Deploy

```bash
cd viddrop
vercel
```

Follow the prompts. On first deploy Vercel will ask:
- Set up and deploy? **Y**
- Which scope? (your account)
- Link to existing project? **N**
- Project name: `viddrop` (or anything)
- In which directory is your code? **./`** (current dir)

### 4. Done!

Your site will be live at `https://viddrop-xxxx.vercel.app`

---

## How it works

```
User pastes URL
   ↓
/api/info   →  yt-dlp --dump-json  →  returns title, thumbnail, all formats
   ↓
User picks format card
   ↓
/api/download → yt-dlp downloads to temp dir → streams file to browser
```

---

## Supported platforms

yt-dlp supports 1000+ sites including:
- YouTube (all qualities up to 4K)
- TikTok
- Instagram (Reels, posts)
- Twitter / X
- Facebook
- Reddit
- Vimeo
- Dailymotion
- Twitch clips
- SoundCloud (audio)
- ...and 990+ more

Full list: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

---

## Local dev

```bash
pip install yt-dlp
python -m http.server 8080 --directory public
# In another terminal:
vercel dev
```

Then open `http://localhost:3000`

---

## Notes

- Vercel free tier has a **10 second** function timeout. Long videos may fail on the `/download` endpoint. Upgrade to Pro for 60s, or host on Railway/Render for unlimited.
- For `/api/info`, 10s is usually enough.
- The download endpoint works best for short clips. For long videos, consider adding a queue system.

---

## Legal

Only download content you own or have permission to download. Respect platform Terms of Service and copyright law.
