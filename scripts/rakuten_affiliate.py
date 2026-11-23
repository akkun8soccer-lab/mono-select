#!/usr/bin/env python3
"""Fetch Rakuten affiliate URLs via the official 2026 Ichiba Item Search API.
Requires RAKUTEN_APPLICATION_ID, RAKUTEN_ACCESS_KEY, RAKUTEN_AFFILIATE_ID.
Never invents affiliate links. Generates a reviewable Astro Markdown draft.
"""
import datetime as dt
import html
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
API = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701"
OUTPUT = ROOT / "mono-site/src/content/articles/rakuten-product-picks.md"
TOPICS = ROOT / "scripts/rakuten-topics.json"

def clean(value, limit=110):
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]

def image_url(item):
    images = item.get("mediumImageUrls") or []
    if not images:
        return ""
    first = images[0]
    return first.get("imageUrl", "") if isinstance(first, dict) else str(first)

def fetch(keyword, app_id, access_key, affiliate_id):
    params = urllib.parse.urlencode({
        "applicationId": app_id,
        "affiliateId": affiliate_id,
        "keyword": keyword,
        "format": "json",
        "formatVersion": 2,
        "hits": 12,
        "availability": 1,
        "imageFlag": 1,
    })
    req = urllib.request.Request(API + "?" + params, headers={
        "accessKey": access_key,
        "User-Agent": "MONO-SELECT-Affiliate-Catalog/1.0",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.load(resp)
    return [row.get("item", row) for row in data.get("items", [])]

def select(items, topic):
    # Exact itemCode or required product token is safer than unverified generic search results.
    code = topic.get("itemCode")
    token = topic.get("mustContain")
    selected = []
    for item in items:
        if code and item.get("itemCode") != code:
            continue
        if token and token.casefold() not in str(item.get("itemName", "")).casefold():
            continue
        link = item.get("affiliateUrl")
        if not isinstance(link, str) or not link.startswith("https://"):
            continue
        if item.get("availability") != 1:
            continue
        selected.append(item)
    return selected[:int(topic.get("limit", 2))]

def build(topics, records):
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).strftime("%Y-%m-%d")
    lines = [
        "---", 'title: "楽天市場で探す省スペース家電｜商品候補一覧"',
        'description: "楽天市場の公式APIから取得した省スペース家電の商品候補と購入リンク。価格は取得時点の情報です。"',
        "pubDate: " + today, "category: 家電", "draft: false", "---", "",
        "> **広告・PR** 本ページには楽天アフィリエイト広告が含まれます。リンク先で購入などの成果条件を満たすと、当サイトに報酬が発生する場合があります。",
        "",
        "楽天市場の商品検索APIから取得した商品候補です。**実機レビュー・性能順位ではありません。** 価格・在庫・送料・仕様は変動します。購入前に販売ページとメーカー公式情報をご確認ください。",
        "",
        "取得日：" + today + "（日本時間）", "",
    ]
    for topic, items in zip(topics, records):
        if not items:
            continue
        lines += ["## " + clean(topic["label"]), ""]
        for item in items:
            name = clean(item.get("itemName"), 130)
            url = html.escape(item["affiliateUrl"], quote=True)
            price = item.get("itemPrice")
            if not name or not isinstance(price, (int, float)):
                continue
            lines += ["### " + name, ""]
            img = image_url(item)
            if img.startswith("https://"):
                lines += ['<img src="' + html.escape(img, quote=True) + '" alt="' + html.escape(name, quote=True) + '" width="128" loading="lazy">', ""]
            lines += [
                "**API取得時の掲載価格：** " + format(price, ",") + "円（送料・ポイント条件等は販売ページを確認）",
                "",
                '<a href="' + url + '" rel="nofollow sponsored">楽天市場で商品を見る（広告）</a>',
                "",
            ]
    if all(not group for group in records):
        raise RuntimeError("No verified affiliate URLs returned; existing page remains unchanged")
    return "\n".join(lines) + "\n"

def main():
    names = ("RAKUTEN_APPLICATION_ID", "RAKUTEN_ACCESS_KEY", "RAKUTEN_AFFILIATE_ID")
    missing = [name for name in names if not os.getenv(name)]
    if missing:
        raise RuntimeError("Missing GitHub Actions secrets: " + ", ".join(missing))
    topics = json.loads(TOPICS.read_text(encoding="utf-8"))
    records = []
    for topic in topics:
        items = fetch(topic["keyword"], *(os.environ[n] for n in names))
        records.append(select(items, topic))
    content = build(topics, records)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists() and OUTPUT.read_text(encoding="utf-8") == content:
        print("No changes")
        return
    OUTPUT.write_text(content, encoding="utf-8")
    print("Updated", OUTPUT)

if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, urllib.error.URLError, ValueError, KeyError) as exc:
        print("Rakuten API automation failed:", exc, file=sys.stderr)
        sys.exit(1)
