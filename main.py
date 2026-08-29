"""
This code is only made for educational and practice purposes. 
Author and Async Development are not responsible for misuse.

GhoSty OwO V4 Alpha Build
Stable Alpha Build Version: 280826.4.1.0

GitHub: https://github.com/WannaBeGhoSt
Discord: https://discord.gg/asMJGgDA7u
"""

import os as brutality_ghosty
import sys
import re
import json as ghostop
import threading
import asyncio
import time as _time
import logging
from datetime import datetime, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

brutality_ghosty.system("pip install -r requirements.txt")

from colorama import Fore, Style, init
import discord

logging.getLogger("discord").setLevel(logging.CRITICAL)
logging.getLogger("discord.http").setLevel(logging.CRITICAL)
logging.getLogger("discord.gateway").setLevel(logging.CRITICAL)
logging.getLogger("discord.state").setLevel(logging.CRITICAL)

init(autoreset=True)

from core.ui import (
    render_header,
    clear_screen,
    log_info,
    log_warn,
    log_error,
    log_success,
    log_worker_start,
    log_worker_ready,
    log_controller_ready,
    log_disconnect,
    log_resumed,
    log_retry,
    log_fatal_error,
    log_net_error,
    log_event_error,
    log_shutdown,
)

_RETRY_DELAY_INITIAL  = 5    
_RETRY_DELAY_MAX      = 60 
_RETRY_DELAY_FACTOR   = 2  

_FATAL_EXCEPTIONS = (
    discord.LoginFailure,
    discord.Forbidden, 
)

tokens_file = "tokens.txt"
if not brutality_ghosty.path.exists(tokens_file):
    log_error("tokens.txt not found! Create a tokens.txt file with one token per line.")
    sys.exit(1)

with open(tokens_file, "r") as f:
    raw_token_lines = f.readlines()

token_entries = []
for slot_num, raw_line in enumerate(raw_token_lines, start=1):
    stripped = raw_line.strip()
    if stripped and not stripped.startswith("#"):
        token_entries.append((slot_num, stripped))

if not token_entries:
    log_error("tokens.txt has no valid tokens! Add at least one token.")
    sys.exit(1)


def _parse_channel_line(raw_line):

    line = raw_line.strip()

    if not line or line.startswith("#"):
        return None

    discord_link_match = re.search(r'/channels/\d+/(\d+)', line)
    if discord_link_match:
        return int(discord_link_match.group(1))

    if re.fullmatch(r'\d+', line):
        return int(line)

    log_warn(f"channels.txt: Unrecognised line (skipped): {repr(line)}")
    return None


channels_map = {}
channels_file = "channels.txt"

if brutality_ghosty.path.exists(channels_file):
    with open(channels_file, "r") as f:
        raw_lines = f.readlines()

    worker_idx = 0
    for raw_line in raw_lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            worker_idx += 1
            channels_map[worker_idx] = None
            continue
        worker_idx += 1
        ch_id = _parse_channel_line(raw_line)
        channels_map[worker_idx] = ch_id

    valid_channels = [v for v in channels_map.values() if v is not None]
    if not valid_channels:
        channels_map = {}
else:
    valid_channels = []

config_file = "config.json"
main_token = None
web_dashboard_enabled = True
if brutality_ghosty.path.exists(config_file):
    try:
        with open(config_file, "r") as f:
            config = ghostop.load(f)
        main_token = config.get("MAIN_TOKEN", "").strip()
        web_dashboard_enabled = config.get("WEB_DASHBOARD", True)
    except Exception as e:
        log_warn(f"Could not read config.json: {e}")


clear_screen()

print(render_header(
    worker_count=len(token_entries),
    channel_count=len(valid_channels),
    has_main_ctrl=bool(main_token),
))


from core.utils import create_bot
from core.heart import (
    WorkerState, WorkerManager, manager,
    register_commands, register_main_commands,
    _run_farming_loop, PseudoCtx,
)

has_any_channel = any(v is not None for v in channels_map.values())
manager.set_has_channels_config(has_any_channel)

if main_token:
    manager.set_main_token(main_token)


def run_worker(worker_number, token):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    label = f"[W#{worker_number:02d}]"
    retry_delay = _RETRY_DELAY_INITIAL
    attempt = 0

    while True:
        attempt += 1
        if attempt > 1:
            log_retry(label, retry_delay, attempt)
            _time.sleep(retry_delay)
            retry_delay = min(retry_delay * _RETRY_DELAY_FACTOR, _RETRY_DELAY_MAX)

        try:
            bot = create_bot(worker_number)
            if attempt == 1:
                ws = WorkerState(worker_number)
                ws.bot = bot
                ws.auto_start_channel_id = channels_map.get(worker_number, None)
                manager.register_worker(ws)
                register_commands(bot, ws)
            else:
                ws = manager.get_worker(worker_number)
                ws.bot = bot
                bot = create_bot(worker_number)
                ws.bot = bot
                register_commands(bot, ws)

            @bot.event
            async def on_ready():
                ws.username = str(bot.user)
                retry_delay_ref = _RETRY_DELAY_INITIAL
                log_worker_ready(worker_number, str(bot.user), ws.auto_start_channel_id)

            @bot.event
            async def on_disconnect():
                log_disconnect(label)

            @bot.event
            async def on_resumed():
                log_resumed(label)

            @bot.event
            async def on_error(event, *args, **kwargs):
                import traceback
                log_event_error(label, event)
                traceback.print_exc()

            @bot.listen('on_message')
            async def parse_cookie_cooldown(message):
                if message.author.id == 408785106942164992:
                    content = message.content
                    if not content:
                        return
                    
                    if "You got a cookie from" in content:
                        if f"<@{bot.user.id}>" in content or f"<@!{bot.user.id}>" in content:
                            sender_part = content.split("You got a cookie from")[-1]
                            if str(bot.user.id) in sender_part:
                                ws.cookie_reset_time = datetime.now() + timedelta(hours=24)
                                log_info(f"{label} Cookie sent successfully! Reset in 24H.")
                                
                    elif "Nu! You need to wait" in content:
                        name_match = False
                        if hasattr(bot.user, 'display_name') and bot.user.display_name and bot.user.display_name in content:
                            name_match = True
                        elif bot.user.name in content:
                            name_match = True
                            
                        if name_match:
                            import re
                            hours, minutes, seconds = 0, 0, 0
                            h_match = re.search(r'(\d+)H', content)
                            m_match = re.search(r'(\d+)M', content)
                            s_match = re.search(r'(\d+)S', content)
                            if h_match: hours = int(h_match.group(1))
                            if m_match: minutes = int(m_match.group(1))
                            if s_match: seconds = int(s_match.group(1))
                            
                            total_seconds = hours * 3600 + minutes * 60 + seconds
                            if total_seconds > 0:
                                ws.cookie_reset_time = datetime.now() + timedelta(seconds=total_seconds)
                                log_warn(f"{label} Cookie failed. Cooldown: {hours}H {minutes}M {seconds}S.")

            log_worker_start(worker_number)
            bot.run(token, log_handler=None)
            break

        except _FATAL_EXCEPTIONS as e:
            log_fatal_error(label, e)
            break

        except (OSError, ConnectionResetError, TimeoutError) as e:
            log_net_error(label, e)

        except Exception as e:
            log_net_error(label, e)

    loop.close()

def run_main_controller(token):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    label = "[MAIN-CTRL]"
    retry_delay = _RETRY_DELAY_INITIAL
    attempt = 0

    while True:
        attempt += 1
        if attempt > 1:
            log_retry(label, retry_delay, attempt)
            _time.sleep(retry_delay)
            retry_delay = min(retry_delay * _RETRY_DELAY_FACTOR, _RETRY_DELAY_MAX)

        try:
            bot = create_bot(0)
            register_main_commands(bot)

            @bot.event
            async def on_ready():
                log_controller_ready(str(bot.user))

            @bot.event
            async def on_disconnect():
                log_disconnect(label)

            @bot.event
            async def on_resumed():
                log_resumed(label)

            @bot.event
            async def on_error(event, *args, **kwargs):
                import traceback
                log_event_error(label, event)
                traceback.print_exc()

            bot.run(token, log_handler=None)

            break

        except _FATAL_EXCEPTIONS as e:
            log_fatal_error(label, e)
            break

        except (OSError, ConnectionResetError, TimeoutError) as e:
            log_net_error(label, e)

        except Exception as e:
            log_net_error(label, e)

    loop.close()

threads = []

if web_dashboard_enabled:
    try:
        from dashboard.app import start_server
        dash_t = threading.Thread(target=start_server, daemon=True, name="Dashboard")
        dash_t.start()
        threads.append(dash_t)
    except Exception as e:
        print(f"Failed to start dashboard: {e}")

for slot_num, token in token_entries:
    t = threading.Thread(target=run_worker, args=(slot_num, token), daemon=True, name=f"Worker-{slot_num}")
    t.start()
    threads.append(t)

if main_token:
    _time.sleep(2)
    t = threading.Thread(target=run_main_controller, args=(main_token,), daemon=True, name="MainController")
    t.start()
    threads.append(t)

try:
    for t in threads:
        t.join()
except KeyboardInterrupt:
    log_shutdown()
    sys.exit(0)