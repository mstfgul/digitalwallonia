# Digital Wallonia Actor Scraper

Scrapes all actors (companies, organizations, startups) listed on [digitalwallonia.be/fr/cartographie](https://www.digitalwallonia.be/fr/cartographie/) and displays them in a simple web interface.

## Requirements

```bash
pip install requests flask playwright
python -m playwright install chromium
```

## Usage

**1. Scrape the data**

```bash
python scraper.py
```

Fetches all ~6800 actors from the Digital Wallonia API and saves them to `data/companies.json`.

**2. Start the web interface**

```bash
python app.py
```

Open your browser at `http://localhost:5001`

## Features

- Full-text search by name, description, or address
- Pagination (20 results per page)
- Company logo, website link, and profile link
- Stats bar showing total actors, websites, addresses, and logos
