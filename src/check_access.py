import re, asyncio, logging, os
from urllib.parse import urlparse
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import UserAlreadyParticipantError, InviteHashExpiredError, InviteHashInvalidError
from .config import settings
from .logging_setup import setup_logging

setup_logging()
log = logging.getLogger("access")

def parse_list(val: str):
    return [s.strip() for s in re.split(r"[\s,]+", val or "") if s.strip()]

async def ensure_membership(client: TelegramClient, invites):
    # Try to join invites if provided
    for link in invites:
        try:
            u = urlparse(link)
            if not (u.scheme and u.netloc.endswith("t.me")):
                continue
            # Supports https://t.me/+joincode or https://t.me/username?start=
            await client(telethon.functions.messages.ImportChatInviteRequest(u.path.strip("/").split("+")[-1]))  # type: ignore
        except UserAlreadyParticipantError:
            pass
        except (InviteHashExpiredError, InviteHashInvalidError) as e:
            log.warning("Invite invalid/expired: %s", link)
        except Exception as e:
            log.debug("Invite join skipped: %s -> %s", link, e)

async def main():
    srcs = parse_list(settings.SRC_CHANNELS)
    invites = parse_list(settings.SRC_INVITES)
    if not (settings.TELEGRAM_API_ID and settings.TELEGRAM_API_HASH and settings.TELETHON_SESSION):
        log.error("Missing TELEGRAM creds; set TELEGRAM_API_ID/HASH and TELETHON_SESSION")
        raise SystemExit(1)
    async with TelegramClient(StringSession(settings.TELETHON_SESSION), settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH) as client:
        # Attempt optional invite joins
        if invites:
            await ensure_membership(client, invites)

        # Build dialog map: id -> entity (has access_hash)
        idmap = {}
        async for d in client.iter_dialogs():
            ent = d.entity
            try:
                idmap[getattr(ent, 'id', None)] = ent
            except Exception:
                pass

        bad = []
        for s in srcs:
            if s.startswith("@") or s.startswith("http"):
                continue
            # numeric? -100xxxxxxxxxx
            m = re.fullmatch(r"-?\d{6,}", s)
            if m:
                # Telethon uses positive IDs in entities; -100... corresponds to channel id
                as_int = int(s)
                pos = abs(as_int)  # map -100.. -> positive key
                if pos not in idmap:
                    bad.append(s)
            else:
                bad.append(s)

        if bad:
            log.error("Private/numeric channels not found in your dialogs: %s", " ".join(bad))
            log.error("→ 해결: 해당 계정으로 해당 채널을 먼저 '가입'하거나, SRC_INVITES에 초대링크를 제공하세요.")
            raise SystemExit(1)

if __name__ == "__main__":
    asyncio.run(main())
