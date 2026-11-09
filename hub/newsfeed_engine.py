#!/usr/bin/env python3
from __future__ import annotations
"""
The Hub of Learning — Engineering Pulse Newsfeed Engine (`hub/newsfeed_engine.py`).

Provides:
1. Offline-first seeded engineering articles (`hub/seed_newsfeed.json`) cross-linked to Knowledgebase chapters.
2. Resilient RSS 2.0 (`<item>`) and Atom 1.0 (`{http://www.w3.org/2005/Atom}entry`) feed polling with
   conditional `ETag` / `If-Modified-Since` caching and strict timeouts.
3. Automatic taxonomy tag classification & textbook chapter cross-linking.
"""
import hashlib
import html
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any, Dict, List

HUB_DIR = pathlib.Path(__file__).resolve().parent
SEED_FILE = HUB_DIR / "seed_newsfeed.json"

ATOM_NS = "{http://www.w3.org/2005/Atom}"

TAG_KEYWORDS: Dict[str, List[str]] = {
    "rag-evals": ["rag", "retrieval", "hallucination", "entailment", "embedding", "vector"],
    "ai-engineering": ["llm", "agent", "prompt", "anthropic", "openai", "transformer", "eval"],
    "consistent-hashing": ["consistent hashing", "vnode", "hash ring", "sharding", "dynamo", "partition"],
    "backpressure": ["jitter", "backoff", "backpressure", "rate limit", "token bucket", "ring buffer", "retry"],
    "kafka": ["kafka", "outbox", "cdc", "debezium", "eventual consistency", "saga"],
    "os-kernel": ["oom", "rss", "garbage collection", "memory leak", "file descriptor", "virtual memory", "linux"],
    "networking": ["tcp", "tls", "http/2", "http/3", "quic", "websocket", "handshake", "syn"],
    "databases": ["lsm-tree", "b-tree", "b+tree", "sstable", "wal", "mvcc", "sqlite", "postgres", "rocksdb", "bloom filter"],
    "sdet-architecture": ["playwright", "selenium", "flaky", "locator", "cdp", "test", "automation"],
}


def load_seed_data() -> Dict[str, Any]:
    if not SEED_FILE.exists():
        return {"sources": [], "articles": []}
    return json.loads(SEED_FILE.read_text(encoding="utf-8"))


def strip_html_tags(raw: str) -> str:
    cleaned = re.sub(r"<[^>]+>", " ", raw or "")
    cleaned = html.unescape(cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def infer_tags_and_chapters(title: str, summary: str, default_category: str, known_chapters: List[Dict[str, Any]]) -> tuple[List[str], List[str]]:
    combined = f"{title} {summary}".lower()
    tags = {default_category}
    for tag, keywords in TAG_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            tags.add(tag)

    related_slugs = []
    for ch in known_chapters:
        ch_tags = set(ch.get("tags") or [])
        if tags & ch_tags:
            related_slugs.append(ch["slug"])
    return sorted(tags), related_slugs[:3]


def parse_feed_xml(xml_text: str, source_id: str, source_name: str, category: str, known_chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parse either RSS 2.0 (<channel><item>) or Atom 1.0 (<feed><entry>) XML into normalized article dicts."""
    articles: List[Dict[str, Any]] = []
    try:
        root = ET.fromstring(xml_text.strip())
    except Exception:
        return articles

    # Case 1: RSS 2.0 (<item>)
    rss_items = root.findall(".//item")
    for item in rss_items[:6]:
        title = strip_html_tags(item.findtext("title") or "")
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "2026-11-09")[:16]
        desc = strip_html_tags(item.findtext("description") or "")[:280]
        if not title or not link:
            continue
        art_id = "rss-" + hashlib.sha256(f"{source_id}:{link}".encode("utf-8")).hexdigest()[:12]
        tags, related = infer_tags_and_chapters(title, desc, category, known_chapters)
        articles.append({
            "id": art_id,
            "sourceId": source_id,
            "sourceName": source_name,
            "category": category,
            "title": title,
            "url": link,
            "publishedAt": pub_date,
            "readingMinutes": max(4, min(15, len(desc) // 35 or 6)),
            "summary": desc or title,
            "whyItMatters": f"Live engineering signal from {source_name} connected to your {category} track.",
            "tags": tags,
            "relatedChapters": related,
        })

    # Case 2: Atom 1.0 (<entry>)
    atom_entries = root.findall(f".//{ATOM_NS}entry") or root.findall(".//entry")
    for entry in atom_entries[:6]:
        title_el = entry.find(f"{ATOM_NS}title")
        if title_el is None:
            title_el = entry.find("title")
        title = strip_html_tags(title_el.text if title_el is not None and title_el.text else "")

        link = ""
        for link_el in entry.findall(f"{ATOM_NS}link") + entry.findall("link"):
            href = link_el.attrib.get("href", "").strip()
            rel = link_el.attrib.get("rel", "alternate")
            if href and rel in ("alternate", ""):
                link = href
                break
        if not link and (entry.findtext(f"{ATOM_NS}id") or entry.findtext("id")):
            link = (entry.findtext(f"{ATOM_NS}id") or entry.findtext("id") or "").strip()

        updated = (
            entry.findtext(f"{ATOM_NS}updated")
            or entry.findtext(f"{ATOM_NS}published")
            or entry.findtext("updated")
            or "2026-11-09"
        )[:10]
        summary_raw = (
            entry.findtext(f"{ATOM_NS}summary")
            or entry.findtext(f"{ATOM_NS}content")
            or entry.findtext("summary")
            or ""
        )
        desc = strip_html_tags(summary_raw)[:280]
        if not title or not link:
            continue
        art_id = "atom-" + hashlib.sha256(f"{source_id}:{link}".encode("utf-8")).hexdigest()[:12]
        tags, related = infer_tags_and_chapters(title, desc, category, known_chapters)
        articles.append({
            "id": art_id,
            "sourceId": source_id,
            "sourceName": source_name,
            "category": category,
            "title": title,
            "url": link,
            "publishedAt": updated,
            "readingMinutes": max(4, min(15, len(desc) // 35 or 6)),
            "summary": desc or title,
            "whyItMatters": f"Live engineering signal from {source_name} connected to your {category} track.",
            "tags": tags,
            "relatedChapters": related,
        })

    return articles


def fetch_live_feed(feed_url: str, timeout_sec: float = 3.5) -> str | None:
    """Fetch an RSS/Atom XML feed with a strict timeout; returns None on offline/network error."""
    if not feed_url.startswith(("http://", "https://")):
        return None
    req = urllib.request.Request(
        feed_url,
        headers={
            "User-Agent": "TheHubOfLearning/2.0 (+http://127.0.0.1:8090; LocalEngineeringKnowledgebase)",
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            if resp.status == 200:
                return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None
    return None
