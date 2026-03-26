# News Tracker

A desktop news application that fetches live breaking headlines
using the NewsAPI, with a floating marquee ticker, live feed,
and keyword search.

## How to Run

**GUI version (recommended):**
```
python news_tracker_gui.py
```

**Command line version:**
```
python news_tracker.py
```

**Or download the executable** from the
[Releases](https://github.com/jamesdileva/Python-Projects/releases/tag/news-tracker-v1.0)
page — no Python installation required. Windows only.

## Setup

### Get a free API key
Sign up at [newsapi.org](https://newsapi.org) and copy your API key.
When you launch the app for the first time a settings popup will
appear asking for your key. It is saved locally to a .env file
and never shared or pushed to GitHub.

### Install dependencies
```
pip install requests python-dotenv
```

## Features

### GUI Version
- **Browse by category** — general, business, entertainment,
  health, science, sports, technology
- **Keyword search** — find articles on any topic
- **Click to open** — double-click any headline to open the
  full article in your browser
- **Three tabs:**
  - Headlines — latest articles from your selected category
  - Live Feed — auto-refreshing headlines on a configurable timer
  - Saved Articles — articles you have bookmarked for later
- **Save articles** — select one or multiple headlines and save
  them to your collection
- **Export saved articles** — export your saved collection to
  a text file
- **Floating marquee ticker** — a draggable always-on-top window
  that scrolls headlines continuously, can be moved to any
  monitor
- **Status bar** — shows loading, success, and error states
  in real time
- **API key settings** — enter and update your key from inside
  the app, stored securely in a local .env file
- **Dark mode toggle**
- **Background threading** — UI stays responsive during all
  API calls

### Command Line Version
- Fetch top headlines by category
- Search by keyword
- Live auto-refreshing ticker with countdown timer
- Save articles to text file

## Security
This app stores your API key in a local .env file on your machine.
The key is never hardcoded in the source code and never pushed
to GitHub. The .env file is excluded via .gitignore.

## Roadmap

### Completed
- ✅ GUI — Tkinter desktop app
- ✅ Browse headlines by category
- ✅ Keyword search
- ✅ Click to open article in browser
- ✅ Save and export articles
- ✅ Auto-refresh live feed tab
- ✅ Floating draggable marquee ticker
- ✅ Status bar with loading states
- ✅ API key settings popup
- ✅ Dark mode
- ✅ Background threading — UI never freezes
- ✅ Save multiple articles at once

### Planned
- **Marquee speed control** — slider in settings to adjust
  scrolling speed
- **Sentiment analysis** — rate headlines positive, negative,
  or neutral
- **Email digest** — send daily summary to your inbox
- **Favourite topics** — save preferred searches between sessions
- **Multiple country support** — fetch headlines from any country
- **Article summarizer** — one line AI summary per article
- **Desktop notifications** — alert when breaking news matches