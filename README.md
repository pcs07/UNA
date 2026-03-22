# UNA — UPSC News Analysis

Daily curated news and opinion pieces for UPSC Civil Services preparation,
automatically fetched from major Indian publications.

**Live Site:** [your-username.github.io/una](https://your-username.github.io/una)

## Sources

| Publication | Categories |
|-------------|------------|
| The Hindu | Editorial, Opinion, National, International, Economy, Science & Tech, Environment |
| Indian Express | Editorial, Opinion, National, International, Economy, Science & Tech |
| Economic Times | Economy, National, International, Science & Tech |
| Livemint | Opinion, Economy, National, Science & Tech |
| Business Standard | Economy, Editorial, International, Science & Tech |

## Features

- **Daily auto-update** via GitHub Actions at 6:00 AM IST
- Filter by **category**: Editorial · Opinion · International · Economy · Science & Tech · Environment · National
- Filter by **source**
- **Full-text search** across titles and descriptions
- Sort by newest / oldest / source
- Paginated — 24 articles per page
- Responsive, mobile-friendly dark UI

## Setup

### 1. Fork / clone and push to GitHub

```bash
cd ~/Desktop/UNA
git init
git add .
git commit -m "init: UNA UPSC News Analysis"
git remote add origin https://github.com/YOUR_USERNAME/una.git
git push -u origin main
```

### 2. Enable GitHub Pages

1. Go to **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / `root`
4. Save — your site will be at `https://YOUR_USERNAME.github.io/una`

### 3. Trigger the first workflow run

Go to **Actions → Fetch Daily UPSC News → Run workflow**

After that, it runs automatically every day at 6 AM IST.

### 4. Run locally (optional)

```bash
pip install -r requirements.txt
python scripts/fetch_news.py
# then open index.html with a local server:
python -m http.server 8080
```

## Project Structure

```
UNA/
├── index.html              # Main frontend
├── style.css               # Styles
├── script.js               # Frontend logic
├── requirements.txt        # Python dependencies
├── data/
│   └── news.json           # Auto-generated article data
├── scripts/
│   └── fetch_news.py       # RSS feed fetcher
└── .github/
    └── workflows/
        └── fetch-news.yml  # Daily GitHub Actions workflow
```

## Configuration

To add/remove feeds, edit `scripts/fetch_news.py` — the `FEEDS` list at the top.

To change how many days back to fetch, edit `LOOKBACK_DAYS` in the same file.

---

*Built for UPSC aspirants. For educational purposes only.*
