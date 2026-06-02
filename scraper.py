import requests
import json
import time
import os

API_URL = "https://search.production.ribo.digitalwallonia.be/d4w-entries_master/_search/template"
HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://www.digitalwallonia.be",
    "Referer": "https://www.digitalwallonia.be/",
}
OUTPUT_FILE = "data/companies.json"
BATCH_SIZE = 100


def fetch_batch(from_index: int, size: int = BATCH_SIZE) -> dict:
    payload = {
        "id": "filter-profile-search-template",
        "params": {
            "programsSlugList": [],
            "regionsList": [],
            "from": from_index,
            "size": size,
            "categoriesSlugList0": [],
            "categoriesSlugList1": [],
            "categoriesSlugList2": [],
            "categoriesSlugList3": [],
            "categoriesSlugList4": [],
            "language": "fr",
            "clientSites": [{"term": {"fields.clientSitesList.fr": "Digital-Wallonia"}}],
        },
    }
    r = requests.post(API_URL, json=payload, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def extract_company(hit: dict) -> dict:
    fields = hit["_source"]["fields"]
    sys_info = hit["_source"]["sys"]

    name = (fields.get("title", {}).get("fr") or fields.get("title", {}).get("en") or "").strip()

    description = (
        fields.get("shortDescription", {}).get("fr")
        or fields.get("shortDescription", {}).get("en")
        or ""
    )

    address = ""
    addresses = fields.get("addresses", {}).get("fr", [])
    if addresses:
        address = addresses[0].get("FormattedAddress", "")

    website = ""
    urls = fields.get("urlsWebSite", {}).get("fr", [])
    if urls:
        website = urls[0].get("URL", "")

    logo = ""
    logo_data = fields.get("logoAssetImage", {}).get("fr", {})
    if logo_data:
        file_data = logo_data.get("file", {})
        logo_url = (
            file_data.get("fr", {}).get("url")
            or file_data.get("en", {}).get("url")
            or ""
        )
        if logo_url and logo_url.startswith("//"):
            logo_url = "https:" + logo_url
        logo = logo_url

    slug = fields.get("slug", {}).get("fr", "")
    profile_url = f"https://www.digitalwallonia.be/fr/cartographie/{slug}" if slug else ""

    return {
        "id": hit["_id"],
        "name": name,
        "description": description,
        "address": address,
        "website": website,
        "logo": logo,
        "profile_url": profile_url,
        "updated_at": sys_info.get("updatedAt", ""),
    }


def scrape_all(max_records: int = None):
    os.makedirs("data", exist_ok=True)

    first = fetch_batch(0, 1)
    total = first["hits"]["total"]["value"]
    if max_records:
        total = min(total, max_records)

    print(f"Toplam aktör: {total}")

    companies = []
    from_index = 0

    while from_index < total:
        size = min(BATCH_SIZE, total - from_index)
        print(f"Çekiliyor: {from_index + 1} - {from_index + size} / {total}")

        data = fetch_batch(from_index, size)
        hits = data["hits"]["hits"]

        for hit in hits:
            companies.append(extract_company(hit))

        from_index += size
        time.sleep(0.3)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(companies, f, ensure_ascii=False, indent=2)

    print(f"\nTamamlandi! {len(companies)} sirket kaydedildi -> {OUTPUT_FILE}")
    return companies


if __name__ == "__main__":
    scrape_all()
