
from typing import Optional
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import BadRequest
import html
import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN or TELEGRAM_BOT_TOKEN is required")

bot = Bot(TELEGRAM_TOKEN)

def _chunks(text: str, limit: int = 4096):
    for i in range(0, len(text), limit):
        yield text[i:i+limit]

def tg_send(chat_id: str | int, text: str, parse_mode: Optional[str] = "HTML", disable_web_page_preview: bool = False):
    """
    Send long messages in chunks. If HTML parsing fails, retry as plain text automatically.
    """
    last_msg = None
    for chunk in _chunks(text):
        try:
            last_msg = bot.send_message(chat_id=chat_id, text=chunk, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
        except BadRequest as e:
            # Common: can't parse entities — retry as plain without parse mode
            if "can't parse entities" in str(e).lower() or "parse" in str(e).lower():
                last_msg = bot.send_message(chat_id=chat_id, text=chunk, disable_web_page_preview=disable_web_page_preview)
            else:
                raise
    return last_msg

def tg_send_or_edit(chat_id: str | int, message_id: Optional[int], text: str, pin: bool = False, parse_mode: Optional[str] = "HTML"):
    """
    If message_id provided, try edit; otherwise send new. Optionally pin.
    """
    try:
        if message_id:
            try:
                m = bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode=parse_mode, disable_web_page_preview=True)
            except BadRequest as e:
                # Fallback to plain text on parse issues
                m = bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, disable_web_page_preview=True)
        else:
            m = tg_send(chat_id, text, parse_mode=parse_mode, disable_web_page_preview=True)

        if pin and m:
            try:
                bot.pin_chat_message(chat_id=chat_id, message_id=m.message_id, disable_notification=True)
            except Exception:
                pass
        return m
    except BadRequest as e:
        # Final fallback: send as plain text
        m = bot.send_message(chat_id=chat_id, text=text)
        return m
