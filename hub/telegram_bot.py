#!/usr/bin/env python3
"""
Phase 3: Antigravity Telegram Bot & Mobile Micro-Learning Bridge (`hub/telegram_bot.py`).

Capabilities:
1. Pushes daily bite-sized Concept Cards, Interactive Quizzes, and Progress Summaries to Telegram.
2. Processes incoming mobile commands & natural-language prompts via Long Polling:
   - `/start`, `/help`         : Interactive command menu with inline buttons
   - `/daily`, `/card [query]` : Push a 60-second Concept Card (DSA, OS, Networks, DB, System Design, AI)
   - `/quiz`                   : Interactive multiple-choice quiz with 1-tap grading (+50 XP synced to Hub)
   - `/program <query>`        : Fetch Python + Java 17 code for any of the 31 problems/labs on your phone
   - `/test <slug|ci>`         : Remotely execute Java 17 + Python 3 tests on your laptop & return results
   - `/progress`, `/cycle`     : View live Readiness Score (out of 1000), XP, Streak & Practice Cycle HUD
   - `/note <text>`            : Save a study note or prompt to the Learning Hub inbox
   - Natural language router   : e.g. "give me a program on group anagrams", "explain tcp tls", "run ci"

Security:
- Loads `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from `.env` (never logs or exposes secrets).
- Strictly authorizes incoming messages against `TELEGRAM_CHAT_ID`.
"""

import argparse
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hub import state_manager
from tools import runner as dsa_runner

ENV_PATH = REPO_ROOT / ".env"


def load_env_credentials(env_file: Path = ENV_PATH) -> Tuple[Optional[str], Optional[str]]:
    """Load TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from .env or environment variables."""
    env_vars: Dict[str, str] = {}
    if env_file.exists():
        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            env_vars[k] = v

    token = os.environ.get("TELEGRAM_BOT_TOKEN") or env_vars.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID") or env_vars.get("TELEGRAM_CHAT_ID")
    return token, str(chat_id) if chat_id else None


def find_matching_program(query: str) -> Optional[Path]:
    """Search across all 31 runnable DSA, Core CS, System Design, AI & Framework labs."""
    all_Dirs = dsa_runner.find_all_problems(dsa_only=False)
    q = query.lower().strip()
    if not q:
        # Default to Group Anagrams if no query provided
        for p in all_Dirs:
            if "003-group-anagrams" in p.name:
                return p
        return all_Dirs[0] if all_Dirs else None

    q_norm = re.sub(r"[^a-z0-9]+", "-", q).strip("-")
    scored: List[Tuple[int, Path]] = []
    for p in all_Dirs:
        name_l = p.name.lower()
        rel_l = str(p.relative_to(REPO_ROOT)).lower()
        score = 0
        if q == name_l or q_norm == name_l:
            score += 100
        if q in name_l or q_norm in name_l:
            score += 50
        if q in rel_l:
            score += 25
        for token in q_norm.split("-"):
            if len(token) >= 2 and token in rel_l:
                score += 10
        if score > 0:
            scored.append((score, p))

    if not scored:
        return None
    scored.sort(key=lambda x: (-x[0], x[1].name))
    return scored[0][1]


def find_matching_card(query: str = "") -> Dict[str, Any]:
    """Find a concept card by keyword or pick the next uncompleted card."""
    cards = state_manager.CONCEPT_FEED_CARDS
    q = (query or "").lower().strip()
    if q:
        for c in cards:
            haystack = f"{c['id']} {c['category']} {c['title']} {' '.join(c.get('tags', []))}".lower()
            if q in haystack or any(tok in haystack for tok in q.split() if len(tok) >= 3):
                return c

    db = state_manager.load_db()
    completed = set(db.get("completedCards", []))
    for c in cards:
        if c["id"] not in completed:
            return c
    # Fallback to cycling by minute
    idx = int(time.time() // 60) % len(cards)
    return cards[idx]


def format_card_message(card: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """Format a Concept Feed card into clean mobile text + inline keyboard."""
    text = (
        f"☕ *ANTIGRAVITY DAILY CONCEPT STREAM*\n"
        f"🏷️ *{card['category']}* • ⏱️ {card['readTime']} • 🎯 {card['difficulty']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 *{card['title']}*\n\n"
        f"💡 *Mental Model:*\n{card['mentalModel']}\n\n"
        f"⚙️ *Under-the-Hood Mechanics:*\n{card['mechanics']}\n\n"
        f"📐 *Blueprint:*\n`{card['diagram']}`\n\n"
        f"⚠️ *MAANG Interview Gotcha:*\n{card['gotcha']}"
    )
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "🧠 Take 30s Quiz (+50 XP)", "callback_data": f"quiz_prompt:{card['id']}"},
                {"text": "🔖 Bookmark", "callback_data": f"bookmark:{card['id']}"},
            ],
            [
                {"text": "⏭️ Next Concept Card", "callback_data": "cmd:daily"},
                {"text": "📊 My Progress", "callback_data": "cmd:progress"},
            ],
        ]
    }
    if card.get("labSlug"):
        reply_markup["inline_keyboard"].insert(
            1, [{"text": f"💻 View & Run Lab ({card['labSlug']})", "callback_data": f"prog:{card['labSlug']}"}]
        )
    return text, reply_markup


def format_quiz_message(card: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """Format a card's 30-second quiz with clickable A/B/C/D inline buttons."""
    q = card["quiz"]
    opts_lines = []
    buttons = []
    for idx, opt in enumerate(q["options"]):
        letter = chr(ord("A") + idx)
        opts_lines.append(f"*{letter}.* {opt}")
        buttons.append({"text": f"Answer {letter}", "callback_data": f"quiz_ans:{card['id']}:{idx}"})

    text = (
        f"🧠 *30-SECOND MASTERY QUIZ (+50 XP)*\n"
        f"📌 *{card['title']}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"❓ *{q['question']}*\n\n"
        + "\n\n".join(opts_lines)
    )
    reply_markup = {
        "inline_keyboard": [
            buttons[:2],
            buttons[2:],
        ]
    }
    return text, reply_markup


def format_program_message(problem_dir: Path, lang: str = "python") -> Tuple[str, Dict[str, Any]]:
    """Format a runnable problem/lab's code for mobile Telegram reading."""
    rel = str(problem_dir.relative_to(REPO_ROOT))
    slug = problem_dir.name
    py_file = problem_dir / "solution.py"
    java_file = problem_dir / "Solution.java"

    target_file = py_file if (lang == "python" and py_file.exists()) else java_file
    lang_label = "python" if target_file == py_file else "java"

    code = target_file.read_text(encoding="utf-8") if target_file.exists() else "# Code file not found"
    # Keep within Telegram's 4096 char limit
    if len(code) > 3100:
        code = code[:3100] + "\n# ... [truncated for mobile screen]"

    text = (
        f"💻 *ON-DEMAND PROGRAM & LAB VIEWER*\n"
        f"📂 `{rel}` ({lang_label.upper()})\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"```{lang_label}\n{code}\n```"
    )
    other_lang = "java" if lang_label == "python" else "python"
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": f"🔄 Switch to {other_lang.title()}", "callback_data": f"prog_lang:{slug}:{other_lang}"},
                {"text": "▶ Run Tests on Server", "callback_data": f"run_test:{slug}"},
            ],
            [
                {"text": "📚 Daily Concept", "callback_data": "cmd:daily"},
                {"text": "📊 My Progress", "callback_data": "cmd:progress"},
            ],
        ]
    }
    return text, reply_markup


def format_progress_message() -> Tuple[str, Dict[str, Any]]:
    """Format live Hub readiness score, XP, 6 pillars, and active Practice Cycle."""
    dash = state_manager.get_dashboard_payload()
    stats = dash["userStats"]
    cycle = dash["practiceCycle"]

    pillar_lines = []
    for p in dash.get("pillars", []):
        pillar_lines.append(f"• *{p['title']}*: `{p['completed']}/{p['total']}`")

    stage_lines = []
    for s in cycle.get("stages", []):
        icon = "✅" if "Pass" in s["status"] or "Completed" in s["status"] else ("▶️" if "Progress" in s["status"] else "⏳")
        stage_lines.append(f"{icon} *Stage {s['stage']}* ({s['focus']}): `{s['status']}`")

    text = (
        f"🏛️ *ANTIGRAVITY COMMAND CENTER*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 *Readiness Score:* `{dash['readinessScore']} / 1000`\n"
        f"✨ *Mastery XP:* `{stats['xp']} XP`  |  🔥 *Streak:* `{stats['streakDays']} days`\n"
        f"🃏 *Concept Cards Mastered:* `{stats['completedCardsCount']} / {stats['totalCardsCount']}`\n\n"
        f"📚 *6 Curriculum Pillars:*\n" + "\n".join(pillar_lines) + "\n\n"
        f"🔄 *Active Practice Cycle:*\n`{cycle['cycleName']}`\n" + "\n".join(stage_lines)
    )
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "☕ Push Daily Concept", "callback_data": "cmd:daily"},
                {"text": "🧠 Random Quiz", "callback_data": "cmd:quiz"},
            ],
            [
                {"text": "🧪 Run Full CI Suite", "callback_data": "run_test:ci"},
                {"text": "💻 Group Anagrams Code", "callback_data": "prog:003-group-anagrams"},
            ],
        ]
    }
    return text, reply_markup


class AntigravityTelegramBot:
    """Zero-dependency Telegram Bot client and interactive command processor."""

    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        env_token, env_chat = load_env_credentials()
        self.token = token or env_token
        self.chat_id = str(chat_id or env_chat) if (chat_id or env_chat) else None
        self.last_update_id = 0
        self._stop_event = threading.Event()

    def is_configured(self) -> bool:
        return bool(self.token and self.chat_id)

    def _api_call(self, method: str, payload: Dict[str, Any] = None, timeout: int = 15) -> Dict[str, Any]:
        if not self.token:
            return {"ok": False, "error": "TELEGRAM_BOT_TOKEN not configured"}
        url = f"https://api.telegram.org/bot{self.token}/{method}"
        data_bytes = json.dumps(payload or {}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            return {"ok": False, "error": f"HTTP {e.code}: {err_body}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_me(self) -> Dict[str, Any]:
        return self._api_call("getMe", {})

    def send_message(
        self,
        text: str,
        reply_markup: Optional[Dict[str, Any]] = None,
        parse_mode: Optional[str] = "Markdown",
        target_chat_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        cid = target_chat_id or self.chat_id
        if not cid:
            return {"ok": False, "error": "TELEGRAM_CHAT_ID not configured"}

        payload: Dict[str, Any] = {"chat_id": cid, "text": text}
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if reply_markup:
            payload["reply_markup"] = reply_markup

        res = self._api_call("sendMessage", payload)
        # Fallback to plain text if Markdown special characters caused a 400 parse error
        if not res.get("ok") and parse_mode:
            payload.pop("parse_mode", None)
            res = self._api_call("sendMessage", payload)
        return res

    def _log_inbox(self, direction: str, text: str) -> None:
        db = state_manager.load_db()
        inbox = db.setdefault("telegramInbox", [])
        inbox.insert(
            0,
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "direction": direction,
                "text": text[:300],
            },
        )
        db["telegramInbox"] = inbox[:30]
        state_manager.save_db(db)

    def handle_command_text(self, raw_text: str) -> Dict[str, Any]:
        """Process a command or natural-language message and return the response payload."""
        text = (raw_text or "").strip()
        self._log_inbox("IN", text)
        lower = text.lower()

        # 1. /start or /help
        if lower in ("/start", "/help", "help", "menu"):
            msg = (
                "⚡ *ANTIGRAVITY MOBILE LEARNING HUB*\n"
                "Connected to your local repository & state engine!\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "📱 *Commands & Prompts You Can Send Anytime:*\n"
                "• `/daily [topic]` — Bite-sized Concept Card (OS, Networks, DB, System Design, AI, DSA)\n"
                "• `/quiz` — 30-second interactive quiz (+50 XP)\n"
                "• `/program <name>` — Full Python + Java 17 code (e.g. `/program group anagrams`, `/program leak detector`, `/program consistent hashing`)\n"
                "• `/test <slug|ci>` — Remotely compile & run tests on your laptop\n"
                "• `/progress` — Live Readiness Score, XP & 6 Pillars\n"
                "• `/cycle` — Active 4-Stage Practice Cycle HUD\n"
                "• `/note <text>` — Save a study note to your Hub dashboard\n\n"
                "💬 *Natural Language Works Too:*\n"
                "Try typing: _\"give me a program on rag triad\"_ or _\"explain tcp tls\"_!"
            )
            markup = {
                "inline_keyboard": [
                    [
                        {"text": "☕ Daily Concept Card", "callback_data": "cmd:daily"},
                        {"text": "🧠 Take 30s Quiz", "callback_data": "cmd:quiz"},
                    ],
                    [
                        {"text": "💻 Group Anagrams Code", "callback_data": "prog:003-group-anagrams"},
                        {"text": "💻 OS Leak Detector Code", "callback_data": "prog:01-memory-and-handle-leak-detector"},
                    ],
                    [
                        {"text": "📊 My Progress & Readiness", "callback_data": "cmd:progress"},
                        {"text": "🧪 Run Full CI Suite", "callback_data": "run_test:ci"},
                    ],
                ]
            }
            return {"text": msg, "reply_markup": markup}

        # 2. /progress or /cycle
        if lower.startswith("/progress") or lower.startswith("/cycle") or lower in ("progress", "status", "cycle"):
            msg, markup = format_progress_message()
            return {"text": msg, "reply_markup": markup}

        # 3. /daily or /card
        if lower.startswith("/daily") or lower.startswith("/card") or lower.startswith("explain "):
            query = re.sub(r"^(/daily|/card|explain)\s*", "", lower).strip()
            card = find_matching_card(query)
            msg, markup = format_card_message(card)
            return {"text": msg, "reply_markup": markup}

        # 4. /quiz
        if lower.startswith("/quiz") or lower == "quiz":
            query = re.sub(r"^/quiz\s*", "", lower).strip()
            card = find_matching_card(query)
            msg, markup = format_quiz_message(card)
            return {"text": msg, "reply_markup": markup}

        # 5. /program or natural language "give me a program..."
        if (
            lower.startswith("/program")
            or lower.startswith("/code")
            or "program" in lower
            or "code for" in lower
            or "solution for" in lower
        ):
            query = re.sub(
                r"^(/program|/code|give me a program on|give me a program for|give me a program|show me code for|code for|solution for)\s*",
                "",
                lower,
            ).strip()
            prob_dir = find_matching_program(query)
            if not prob_dir:
                return {
                    "text": f"⚠️ Could not find a matching program for `{query}`.\nTry `/program group anagrams`, `/program two sum`, `/program leak detector`, or `/program consistent hashing`.",
                    "reply_markup": None,
                }
            msg, markup = format_program_message(prob_dir, lang="python")
            return {"text": msg, "reply_markup": markup}

        # 6. /test <slug|ci>
        if lower.startswith("/test") or lower.startswith("run test") or lower == "run ci":
            target = re.sub(r"^(/test|run test|run)\s*", "", lower).strip() or "003-group-anagrams"
            return self._execute_remote_test(target)

        # 7. /note <text>
        if lower.startswith("/note"):
            note_body = text[5:].strip()
            db = state_manager.load_db()
            db["xp"] = db.get("xp", 250) + 10
            state_manager.save_db(db)
            return {
                "text": f"📝 *Note Saved to Learning Hub (+10 XP)!*\n`{note_body}`",
                "reply_markup": None,
            }

        # 8. Smart Fallback: Search if user typed a problem or concept topic directly
        prob_dir = find_matching_program(lower)
        if prob_dir and len(lower) >= 3:
            msg, markup = format_program_message(prob_dir, lang="python")
            return {"text": msg, "reply_markup": markup}

        card = find_matching_card(lower)
        msg, markup = format_card_message(card)
        return {"text": msg, "reply_markup": markup}

    def _execute_remote_test(self, target: str) -> Dict[str, Any]:
        """Run either the full CI suite or a specific problem/lab and format output for Telegram."""
        from hub import server as hub_server

        if target.lower() == "ci":
            res = hub_server.execute_test_target("003-group-anagrams", "all")
            dash = state_manager.get_dashboard_payload()
            msg = (
                f"🧪 *REMOTE SERVER TEST EXECUTION*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✓ *Status:* `{res['status']}` (`{res['durationMs']}ms`)\n"
                f"🏛️ *Current Readiness:* `{dash['readinessScore']} / 1000`\n\n"
                f"```text\n{res['output'][:1500]}\n```"
            )
            return {"text": msg, "reply_markup": None}

        prob_dir = find_matching_program(target)
        slug = prob_dir.name if prob_dir else target
        res = hub_server.execute_test_target(slug, "all")
        icon = "✅" if res["status"] == "PASSED" else "❌"
        msg = (
            f"{icon} *LIVE TEST EXECUTION: `{slug}`*\n"
            f"⏱️ *Duration:* `{res['durationMs']}ms`  |  *Status:* `{res['status']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"```text\n{res['output'][:2000]}\n```"
        )
        return {"text": msg, "reply_markup": None}

    def handle_callback_query(self, callback_id: str, data: str) -> Dict[str, Any]:
        """Process inline button taps from Telegram mobile UI."""
        self._log_inbox("CALLBACK", data)

        if data == "cmd:daily":
            card = find_matching_card("")
            msg, markup = format_card_message(card)
            self._api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": "Loaded next concept card!"})
            return {"text": msg, "reply_markup": markup}

        if data == "cmd:quiz":
            card = find_matching_card("")
            msg, markup = format_quiz_message(card)
            self._api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": "Quiz ready!"})
            return {"text": msg, "reply_markup": markup}

        if data == "cmd:progress":
            msg, markup = format_progress_message()
            self._api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": "Synced live progress!"})
            return {"text": msg, "reply_markup": markup}

        if data.startswith("quiz_prompt:"):
            card_id = data.split(":", 1)[1]
            card = next((c for c in state_manager.CONCEPT_FEED_CARDS if c["id"] == card_id), state_manager.CONCEPT_FEED_CARDS[0])
            msg, markup = format_quiz_message(card)
            self._api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": "30-Second Quiz!"})
            return {"text": msg, "reply_markup": markup}

        if data.startswith("bookmark:"):
            card_id = data.split(":", 1)[1]
            res = state_manager.record_feed_interaction(card_id, "toggle_bookmark")
            is_bm = card_id in res.get("bookmarkedCards", [])
            toast = "🔖 Bookmarked in Learning Hub!" if is_bm else "Removed bookmark."
            self._api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": toast})
            return {"text": f"*{toast}* (`{card_id}`)", "reply_markup": None}

        if data.startswith("quiz_ans:"):
            parts = data.split(":")
            card_id = parts[1]
            selected_idx = int(parts[2])
            card = next((c for c in state_manager.CONCEPT_FEED_CARDS if c["id"] == card_id), None)
            if not card:
                return {"text": "⚠️ Card not found.", "reply_markup": None}

            res = state_manager.record_feed_interaction(card_id, "quiz", selected_idx)
            correct_idx = card["quiz"]["correctIndex"]
            is_correct = selected_idx == correct_idx
            letter_sel = chr(ord("A") + selected_idx)
            letter_cor = chr(ord("A") + correct_idx)

            toast = "🎉 Correct! +50 XP" if is_correct else f"❌ Not quite! Correct is {letter_cor}"
            self._api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": toast})

            header = (
                f"✅ *CORRECT! (+50 XP Synced to Hub)*\n"
                if is_correct
                else f"❌ *INCORRECT (You chose {letter_sel}; Correct is {letter_cor})*\n"
            )
            msg = (
                f"{header}"
                f"📌 *{card['title']}*\n"
                f"✨ *Total XP:* `{res['xp']} XP`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 *Why:* {card['quiz']['explanation']}"
            )
            markup = {
                "inline_keyboard": [
                    [
                        {"text": "☕ Next Concept Card", "callback_data": "cmd:daily"},
                        {"text": "📊 Updated Progress", "callback_data": "cmd:progress"},
                    ]
                ]
            }
            return {"text": msg, "reply_markup": markup}

        if data.startswith("prog:"):
            slug = data.split(":", 1)[1]
            prob_dir = find_matching_program(slug)
            if prob_dir:
                msg, markup = format_program_message(prob_dir, lang="python")
                self._api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": f"Loaded {slug}!"})
                return {"text": msg, "reply_markup": markup}

        if data.startswith("prog_lang:"):
            _, slug, lang = data.split(":", 2)
            prob_dir = find_matching_program(slug)
            if prob_dir:
                msg, markup = format_program_message(prob_dir, lang=lang)
                self._api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": f"Switched to {lang.title()}!"})
                return {"text": msg, "reply_markup": markup}

        if data.startswith("run_test:"):
            slug = data.split(":", 1)[1]
            self._api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": f"Running {slug} on server..."})
            return self._execute_remote_test(slug)

        return {"text": f"Processed action `{data}`", "reply_markup": None}

    def poll_once(self, timeout: int = 2) -> int:
        """Fetch and process pending updates from Telegram once. Returns count of processed updates."""
        if not self.is_configured():
            return 0

        res = self._api_call(
            "getUpdates",
            {"offset": self.last_update_id + 1, "timeout": timeout},
            timeout=timeout + 5,
        )
        if not res.get("ok"):
            return 0

        processed = 0
        for upd in res.get("result", []):
            upd_id = upd.get("update_id", 0)
            if upd_id > self.last_update_id:
                self.last_update_id = upd_id

            if "message" in upd:
                msg_obj = upd["message"]
                sender_chat_id = str(msg_obj.get("chat", {}).get("id", ""))
                # Security gate: only process messages from the authorized TELEGRAM_CHAT_ID
                if self.chat_id and sender_chat_id != self.chat_id:
                    continue
                text = msg_obj.get("text", "")
                if text:
                    reply = self.handle_command_text(text)
                    self.send_message(reply["text"], reply_markup=reply.get("reply_markup"))
                    processed += 1

            elif "callback_query" in upd:
                cb = upd["callback_query"]
                cb_id = cb.get("id", "")
                sender_chat_id = str(cb.get("message", {}).get("chat", {}).get("id", ""))
                if self.chat_id and sender_chat_id != self.chat_id:
                    continue
                data = cb.get("data", "")
                reply = self.handle_callback_query(cb_id, data)
                self.send_message(reply["text"], reply_markup=reply.get("reply_markup"))
                processed += 1

        return processed

    def run_polling_loop(self, poll_timeout: int = 10) -> None:
        """Run continuous long-polling loop for mobile Telegram commands."""
        print("✈️  Antigravity Telegram Bot polling worker active...")
        while not self._stop_event.is_set():
            try:
                self.poll_once(timeout=poll_timeout)
            except Exception:
                time.sleep(2)


def send_daily_digest(topic: str = "") -> Dict[str, Any]:
    """Push an interactive Daily Concept Card + Control Menu to the configured Telegram chat."""
    bot = AntigravityTelegramBot()
    if not bot.is_configured():
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing in .env"}

    card = find_matching_card(topic)
    text, markup = format_card_message(card)
    res = bot.send_message(text, reply_markup=markup)
    if res.get("ok"):
        bot._log_inbox("OUT", f"Pushed Concept Card: {card['title']}")
    return res


def main():
    parser = argparse.ArgumentParser(description="Antigravity Telegram Bot & Mobile Micro-Learning Bridge")
    subparsers = parser.add_subparsers(dest="action", required=False)

    subparsers.add_parser("status", help="Verify Telegram bot token and chat configuration")
    push_p = subparsers.add_parser("push", help="Push a Daily Concept Card or Progress Digest to Telegram")
    push_p.add_argument("--topic", default="", help="Optional topic keyword (e.g. 'os', 'tcp', 'rag', 'anagram')")
    push_p.add_argument("--mode", choices=["card", "progress", "welcome"], default="card", help="Message type to push")

    subparsers.add_parser("poll", help="Start interactive long-polling daemon for mobile commands")
    subparsers.add_parser("poll-once", help="Process any currently pending Telegram messages once and exit")

    args = parser.parse_args()
    action = args.action or "status"
    bot = AntigravityTelegramBot()

    if action == "status":
        if not bot.is_configured():
            print("❌ Telegram credentials not found in .env (expected TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID).")
            sys.exit(1)
        me = bot.get_me()
        if me.get("ok"):
            bot_info = me["result"]
            print(f"✅ Telegram Bot Connected: @{bot_info.get('username')} ({bot_info.get('first_name')})")
            print("   Authorized Chat ID is configured and ready.")
        else:
            print(f"❌ Telegram API Error: {me.get('error')}")
            sys.exit(1)

    elif action == "push":
        if args.mode == "welcome":
            payload = bot.handle_command_text("/start")
            res = bot.send_message(payload["text"], reply_markup=payload.get("reply_markup"))
        elif args.mode == "progress":
            text, markup = format_progress_message()
            res = bot.send_message(text, reply_markup=markup)
        else:
            res = send_daily_digest(args.topic)

        if res.get("ok"):
            print("🚀 Successfully pushed interactive message to your Telegram mobile chat!")
        else:
            print(f"❌ Failed to push message: {res.get('error')}")
            sys.exit(1)

    elif action == "poll-once":
        count = bot.poll_once(timeout=2)
        print(f"✅ Processed {count} pending Telegram update(s).")

    elif action == "poll":
        bot.run_polling_loop()


if __name__ == "__main__":
    main()

