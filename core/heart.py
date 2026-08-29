"""
This code is only made for educational and practice purposes. 
Author and Async Development are not responsible for misuse.

GhoSty OwO V4 Alpha Build
Stable Alpha Build Version: 280826.4.1.0

GitHub: https://github.com/WannaBeGhoSt
Discord: https://discord.gg/asMJGgDA7u
"""

import random as ghostyjija
import time
import re
import os
import unicodedata
import threading
import json as ghostop
import asyncio as made_by_ghosty
from datetime import datetime, timedelta
from .modules import parse_zoo_message, fetch_zoo_data, format_value, parse_gems, SPEED_MODES
from .ghostycorehb import GhoStySolveNormalCap, GhoStySyncedCaptchaSolve
from .ui import log_worker_event, log_critical, log_support_prompt
from .bossmodule import _monitor_boss_fights

class WorkerState:
    def __init__(self, worker_number):
        self.worker_number = worker_number
        self.bot = None
        self.username = "Unknown"
        self.running = False
        self.has_started = False
        self.sleep_mode = False
        self.farming_start_time = None
        self.sleep_start_time = None
        self.ghosty_start_time = datetime.now()
        self.ghosty_commands_sent = 0
        self.ghosty_gems_used = 0
        self.last_gem_check = 0
        self.current_speed_mode = "lifetime"
        self.last_mode_change_time = datetime.now()
        self.lifetime_work_cycles = 0
        self.lifetime_day_skip_active = False
        self.lifetime_cycle_start_time = None
        self.initial_cash = 0
        self.initial_essence = 0
        self.current_cash = 0
        self.current_essence = 0
        self.zoo_channel = None
        self.GhoStyHbAlrActiveVar = False
        self.GhoStyCoreAvailCheck = True
        self.huntbot_enabled = True        
        self.active_channel_id = None
        self.auto_start_channel_id = None    
        self.paused = False                  
        self.pause_end_time = None          
        self.boss_tickets = 3
        self.is_boss_fighting = False
        self.next_boss_fight_time = None
        self.is_mail_claiming = False
        self.last_mail_claim = None
        
    def to_dict(self):
        def serialize_dt(dt):
            return dt.isoformat() if dt else None
            
        return {
            "worker_number": self.worker_number,
            "username": self.username,
            "running": self.running,
            "has_started": self.has_started,
            "sleep_mode": self.sleep_mode,
            "paused": self.paused,
            "current_speed_mode": self.current_speed_mode,
            "initial_cash": self.initial_cash,
            "initial_essence": self.initial_essence,
            "ghosty_commands_sent": self.ghosty_commands_sent,
            "ghosty_gems_used": self.ghosty_gems_used,
            "farming_start_time": serialize_dt(self.farming_start_time),
            "pause_end_time": serialize_dt(self.pause_end_time),
            "sleep_start_time": serialize_dt(self.sleep_start_time),
            "ghosty_start_time": serialize_dt(self.ghosty_start_time),
            "lifetime_work_cycles": self.lifetime_work_cycles,
            "lifetime_day_skip_active": self.lifetime_day_skip_active,
            "lifetime_cycle_start_time": serialize_dt(self.lifetime_cycle_start_time),
            "huntbot_enabled": self.huntbot_enabled,
            "huntbot_solver_available": self.GhoStyCoreAvailCheck,
            "last_gem_check": self.last_gem_check,
            "boss_tickets": self.boss_tickets,
            "is_boss_fighting": self.is_boss_fighting,
            "next_boss_fight_time": serialize_dt(self.next_boss_fight_time),
            "is_mail_claiming": self.is_mail_claiming,
            "last_mail_claim": serialize_dt(self.last_mail_claim)
        }

class WorkerManager:
    _instance = None
    _lock = threading.Lock()

    HB_DATA_FILE = "ghostyhbworkers.json"

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._workers = {}
                cls._instance._channel_locks = {}
                cls._instance._main_token = None
                cls._instance._total_workers = 0
                cls._instance._hb_lock = threading.Lock()
                cls._instance._has_channels_config = False  # NEW
            return cls._instance

    def register_worker(self, state):
        with self._lock:
            self._workers[state.worker_number] = state
            self._total_workers = len(self._workers)

    def get_worker(self, worker_number):
        with self._lock:
            return self._workers.get(worker_number)

    def get_all_workers(self):
        with self._lock:
            return dict(self._workers)

    def set_main_token(self, token):
        self._main_token = token

    def set_has_channels_config(self, value: bool):
        self._has_channels_config = value

    @property
    def has_channels_config(self):
        return self._has_channels_config

    @property
    def main_token(self):
        return self._main_token

    @property
    def total_workers(self):
        return self._total_workers

    def try_claim_channel(self, channel_id, worker_number):
        with self._lock:
            existing = self._channel_locks.get(channel_id)
            if existing is not None and existing != worker_number:
                return False, existing
            self._channel_locks[channel_id] = worker_number
            return True, None

    def release_channel(self, channel_id, worker_number):
        with self._lock:
            if self._channel_locks.get(channel_id) == worker_number:
                del self._channel_locks[channel_id]

    def get_channel_worker(self, channel_id):
        with self._lock:
            return self._channel_locks.get(channel_id)

    def try_claim_friend_battle_helper(self, requester_number):
        with self._lock:
            requester = self._workers.get(requester_number)
            if not requester or getattr(requester, 'busy_with_quest', False):
                return None
                
            for w_num, w_state in self._workers.items():
                if w_num != requester_number:
                    is_busy = getattr(w_state, 'busy_with_quest', False)
                    if w_state.running and not w_state.paused and not w_state.sleep_mode and not is_busy:
                        # Claim both!
                        requester.busy_with_quest = True
                        w_state.busy_with_quest = True
                        return w_state
            return None

    def get_action_helpers(self, requester_number, count):
        with self._lock:
            helpers = []
            now = time.time()
            for w_num, w_state in self._workers.items():
                if w_num == requester_number:
                    continue
                if not w_state.running:
                    continue
                last_action_time = getattr(w_state, 'last_action_helper_time', 0)
                if now - last_action_time < 3.0:
                    continue
                
                w_state.last_action_helper_time = now
                helpers.append(w_state)
                if len(helpers) >= count:
                    break
            return helpers

    def get_cookie_helpers(self, requester_number, count):
        with self._lock:
            helpers = []
            now = datetime.now()
            for w_num, w_state in self._workers.items():
                if w_num == requester_number:
                    continue
                if not w_state.running:
                    continue
                
                reset_time = getattr(w_state, 'cookie_reset_time', datetime.min)
                if now < reset_time:
                    continue
                
                w_state.cookie_reset_time = now + timedelta(minutes=5)
                helpers.append(w_state)
                if len(helpers) >= count:
                    break
            return helpers

    def get_pray_curse_helpers(self, requester_number, count):
        with self._lock:
            helpers = []
            now = datetime.now()
            for w_num, w_state in self._workers.items():
                if w_num == requester_number:
                    continue
                if not w_state.running:
                    continue
                reset_time = getattr(w_state, 'pray_curse_reset_time', datetime.min)
                if now < reset_time:
                    continue
                
                w_state.pray_curse_reset_time = now + timedelta(minutes=5, seconds=10)
                helpers.append(w_state)
                if len(helpers) >= count:
                    break
            return helpers

    def load_hb_data(self, worker_number):
        with self._hb_lock:
            try:
                if os.path.exists(self.HB_DATA_FILE):
                    with open(self.HB_DATA_FILE, "r") as f:
                        all_data = ghostop.load(f)
                    return all_data.get(str(worker_number), {})
            except:
                pass
        return {}

    def save_hb_data(self, worker_number, data):
        with self._hb_lock:
            all_data = {}
            try:
                if os.path.exists(self.HB_DATA_FILE):
                    with open(self.HB_DATA_FILE, "r") as f:
                        all_data = ghostop.load(f)
            except:
                pass
            all_data[str(worker_number)] = data
            with open(self.HB_DATA_FILE, "w") as f:
                ghostop.dump(all_data, f, indent=4)


manager = WorkerManager()

def ParseGhoStyTimeStrs(time_str):
    time_str = time_str.upper().strip()
    h = int(re.search(r'(\d+)H', time_str).group(1)) if 'H' in time_str else 0
    m = int(re.search(r'(\d+)M', time_str).group(1)) if 'M' in time_str else 0
    return timedelta(hours=h, minutes=m)


def LoadGhoStysHbData(ws):
    return manager.load_hb_data(ws.worker_number)


def SaveHbDataGhoStys(ws, data):
    manager.save_hb_data(ws.worker_number, data)


def GhoStyEmbedParser(msg_content):
    try:
        content = msg_content.lower().replace(",", "")
        match = re.search(r"current max autohunt:.*?for (\d+) cowoncy", content)
        if match:
            return int(match.group(1))
    except:
        pass
    return 20000


async def GhoStyCapUrlSolver(url):
    try:
        if GhoStySolveNormalCap:
            try:
                return await GhoStySolveNormalCap(url)
            except:
                pass
        if GhoStySyncedCaptchaSolve:
            try:
                return GhoStySyncedCaptchaSolve(url)
            except:
                pass
    except:
        pass
    return None


async def CheckGhoStyHbMsgFetch(ctx, ws, cowoncy_amount=None):
    if not ws.huntbot_enabled:
        return False

    try:
        await made_by_ghosty.sleep(1)
        messages = [msg async for msg in ctx.channel.history(limit=5)]

        for msg in messages:
            if msg.author.id != 408785106942164992:
                continue

            msg_content = str(msg.content)
            if not msg_content and msg.embeds:
                embed = msg.embeds[0]
                msg_content = (embed.description or "") + "".join(
                    f"{f.name}\n{f.value}" for f in embed.fields
                )
            msg_content_lower = msg_content.lower()

            if "beep. boop. i am huntbot" in msg_content_lower:
                optimal_cowoncy = GhoStyEmbedParser(msg_content)
                log_worker_event(ws.worker_number, f"HuntBot: Found optimal cowoncy: {optimal_cowoncy}", "INFO")
                data = LoadGhoStysHbData(ws)
                data["optimal_cowoncy"] = optimal_cowoncy
                data["channel_id"] = ctx.channel.id
                SaveHbDataGhoStys(ws, data)
                await made_by_ghosty.sleep(2)
                await ctx.send(f"owo hb {optimal_cowoncy}")
                await made_by_ghosty.sleep(4)
                return await CheckGhoStyHbMsgFetch(ctx, ws, optimal_cowoncy)

            if "i will be back in" in msg_content_lower:
                match = re.search(r"i will be back in (\d+h\s*\d*m?|\d+m)", msg_content_lower)
                if match:
                    time_str = match.group(1).strip()
                    delta = ParseGhoStyTimeStrs(time_str)
                    next_time = datetime.now() + delta
                    data = LoadGhoStysHbData(ws)
                    data.update({
                        "next_huntbot_time": next_time.isoformat(),
                        "is_hunting": True,
                        "last_updated": datetime.now().isoformat(),
                        "channel_id": ctx.channel.id,
                    })
                    SaveHbDataGhoStys(ws, data)
                    ws.GhoStyHbAlrActiveVar = True
                    log_worker_event(ws.worker_number, f"⏰ Next huntbot in {delta} (at {next_time.strftime('%H:%M:%S')})", "INFO")
                    await ctx.send(f" ⏰ HuntBot will trigger in {delta}")
                    return True

            if "here is your password!" in msg_content_lower and msg.attachments:
                url = msg.attachments[0].url
                log_worker_event(ws.worker_number, f"🔍 Solving captcha from {url}", "DEBUG")
                result = await GhoStyCapUrlSolver(url)
                if result:
                    use_cowoncy = cowoncy_amount or LoadGhoStysHbData(ws).get("optimal_cowoncy", 20000)
                    await made_by_ghosty.sleep(2)
                    await ctx.send(f"owo autohunt {use_cowoncy} {result}")
                    log_worker_event(ws.worker_number, f"✅ Auto-solved HuntBot: `{result}` (Used {use_cowoncy})", "SUCCESS")
                    await made_by_ghosty.sleep(4)
                    return await CheckGhoStyHbMsgFetch(ctx, ws, use_cowoncy)
                else:
                    await ctx.send(" ❌ GhoSty Core Module failed to solve HuntBot. Please join the support server to get help.")
                    return False

            if (
                "you spent" in msg_content_lower
                and "cowoncy" in msg_content_lower
                and "i will be back in" in msg_content_lower
            ):
                match = re.search(r"i will be back in (\d+h\s*\d*m?|\d+m)", msg_content_lower)
                if match:
                    time_str = match.group(1).strip()
                    delta = ParseGhoStyTimeStrs(time_str)
                    next_time = datetime.now() + delta
                    data = LoadGhoStysHbData(ws)
                    data.update({
                        "next_huntbot_time": next_time.isoformat(),
                        "is_hunting": True,
                        "last_updated": datetime.now().isoformat(),
                        "channel_id": ctx.channel.id,
                        "hunt_stage": "waiting_for_return",
                    })
                    SaveHbDataGhoStys(ws, data)
                    ws.GhoStyHbAlrActiveVar = True
                    log_worker_event(ws.worker_number, f"🎯 Hunt started. Will return in {delta}", "INFO")
                    await ctx.send(f"🎯 Hunt active. Bot will return in {delta}")
                    return True

            if "i am back with" in msg_content_lower and "animals" in msg_content_lower:
                log_worker_event(ws.worker_number, "🎉 Hunt completed!", "SUCCESS")
                await ctx.send("🎉 Hunt completed! Restarting HuntBot in 15 seconds")
                await made_by_ghosty.sleep(15)
                await ctx.send("owo hb")
                log_worker_event(ws.worker_number, "📤 Sent: owo hb (after hunt return)", "DEBUG")
                await made_by_ghosty.sleep(4)
                return await CheckGhoStyHbMsgFetch(ctx, ws)

        return False
    except Exception as e:
        log_worker_event(ws.worker_number, f"⚠️ Error in CheckGhoStyHbMsgFetch: {e}", "WARNING")
        return False

async def _do_gem_check(ctx, ws):
    if ws.sleep_mode or ws.paused:
        return
    await ctx.send("owo lb all")
    await made_by_ghosty.sleep(2)
    await ctx.send("owo inventory")
    await made_by_ghosty.sleep(3)
    try:
        latest_messages = [msg async for msg in ctx.channel.history(limit=2)]
        for message in latest_messages:
            if message.author.id == 408785106942164992:
                if "inventory" in message.content.lower():
                    gem_numbers = await parse_gems(message.content)
                    if gem_numbers:
                        use_command = "owo use " + " ".join(gem_numbers)
                        await ctx.send(use_command)
                        ws.ghosty_gems_used += len(gem_numbers)
                        await made_by_ghosty.sleep(3)
                    else:
                        log_worker_event(ws.worker_number, "No gems found in inventory", "DEBUG")
                    break
    except Exception as e:
        log_worker_event(ws.worker_number, f"Error in gem check: {e}", "WARNING")



async def _check_warning(ctx, ws):
    if ws.sleep_mode or ws.paused:
        return False
    try:
        messages = [msg async for msg in ctx.channel.history(limit=10)]
        for msg in messages:
            msg_content = str(msg.content)
            if not msg_content:
                continue
            msg_content_clean = unicodedata.normalize("NFKC", msg_content)
            msg_content_clean = re.sub(r'[\u200B-\u200D\uFEFF]', '', msg_content_clean)
            msg_content_lower = msg_content_clean.lower()

            if "captcha" in msg_content_lower and "verify" in msg_content_lower:
                warning_pattern = r'[\(\[\{]?\s*(\d+)\s*[\/／]\s*5\s*[\)\]\}]?'
                match = re.search(warning_pattern, msg_content_lower)
                if match:
                    warning_count = int(match.group(1))
                    log_worker_event(ws.worker_number, f"⚠️ CAPTCHA WARNING: ({warning_count}/5)", "WARNING")
                    if warning_count == 1:
                        ws.running = False
                        ws.paused = False
                        ws.pause_end_time = None
                        manager.release_channel(ctx.channel.id, ws.worker_number)
                        await ctx.send(
                            "⚠ WARNING DETECTED! 🛑 Stopping | **SOLVE YOUR CAPTCHA FIRST** | "
                            "Then Type `.start` again to restart grinding."
                        )
                        log_worker_event(ws.worker_number, "🛑 Stopped due to CAPTCHA (1/5)", "CRITICAL")
                        return True
        return False
    except Exception as e:
        log_worker_event(ws.worker_number, f"Warning check error: {e}", "WARNING")
        return False


async def _monitor_huntbot(ctx, ws, bot):
    while ws.running:
        if not ws.huntbot_enabled:
            log_worker_event(ws.worker_number, "HuntBot monitor exiting (disabled)", "DEBUG")
            return

        try:
            data = LoadGhoStysHbData(ws)
            if "next_huntbot_time" in data and data.get("channel_id") == ctx.channel.id:
                next_time_str = data["next_huntbot_time"]
                next_time = datetime.fromisoformat(next_time_str)
                current_time = datetime.now()

                if current_time >= next_time and data.get("is_hunting"):
                    log_worker_event(ws.worker_number, "⏰ HuntBot timer reached!", "INFO")
                    await ctx.send("⏰ HuntBot timer reached! Restarting...")
                    data["is_hunting"] = False
                    SaveHbDataGhoStys(ws, data)
                    ws.GhoStyHbAlrActiveVar = False
                    await made_by_ghosty.sleep(2)
                    await ctx.send("owo hb")
                    log_worker_event(ws.worker_number, "📤 Sent: owo hb (auto-triggered)", "DEBUG")
                    await made_by_ghosty.sleep(4)
                    await CheckGhoStyHbMsgFetch(ctx, ws)

            await made_by_ghosty.sleep(30)
        except Exception as e:
            log_worker_event(ws.worker_number, f"⚠️ Error in monitor_huntbot: {e}", "WARNING")
            await made_by_ghosty.sleep(60)


def _parse_pause_time(time_str):

    m = re.fullmatch(r'(?:(\d+)h)?(?:(\d+)m)?', time_str.strip().lower())
    if not m or (not m.group(1) and not m.group(2)):
        return None
    hours = int(m.group(1)) if m.group(1) else 0
    mins = int(m.group(2)) if m.group(2) else 0
    return hours * 3600 + mins * 60


def _format_duration(seconds):
    h, rem = divmod(int(seconds), 3600)
    m = rem // 60
    if h and m:
        return f"{h}h {m}m"
    elif h:
        return f"{h}h"
    else:
        return f"{m}m"


async def setup_user_settings(ctx, ws):
    await made_by_ghosty.sleep(3.4)
    await ctx.send("owo bs")
    await made_by_ghosty.sleep(5.1)
    try:
        import discord
        from discord.interactions import _wrapped_interaction
        from discord.utils import _generate_nonce
        from discord.enums import InteractionType

        def find_buttons(data, targets):
            if isinstance(data, dict):
                if data.get('type') == 2 and str(data.get('label', '')).lower() == 'image':
                    targets.append(data)
                for v in data.values():
                    find_buttons(v, targets)
            elif isinstance(data, list):
                for item in data:
                    find_buttons(item, targets)

        bs_msg = None
        for _ in range(3):
            messages = [msg async for msg in ctx.channel.history(limit=40)]
            for msg in messages:
                if msg.author.id == 408785106942164992:
                    try:
                        route = discord.http.Route("GET", "/channels/{channel_id}/messages?limit=1&around={message_id}", channel_id=ctx.channel.id, message_id=msg.id)
                        raw_data = await ws.bot.http.request(route)
                        if isinstance(raw_data, list) and len(raw_data) > 0:
                            raw_data = raw_data[0]
                        if 'components' in raw_data:
                            raw_str = str(raw_data).lower()
                            if "user settings" in raw_str or "battle display" in raw_str or "custom_id" in raw_str:
                                bs_msg = msg
                                break
                    except Exception:
                        pass
                if bs_msg:
                    break
            
            if bs_msg:
                break
            await made_by_ghosty.sleep(2)

        if not bs_msg:
            log_worker_event(ws.worker_number, "Could not find 'owo bs' response", "DEBUG")
            return

        max_clicks = 10
        clicks = 0
        while clicks < max_clicks:
            route = discord.http.Route("GET", "/channels/{channel_id}/messages?limit=1&around={message_id}", channel_id=ctx.channel.id, message_id=bs_msg.id)
            raw_data = await ws.bot.http.request(route)
            if isinstance(raw_data, list) and len(raw_data) > 0:
                raw_data = raw_data[0]
            
            targets = []
            find_buttons(raw_data.get('components', []), targets)
            
            if not targets:
                log_worker_event(ws.worker_number, "User settings configured (all set to 'text'!)", "SUCCESS")
                break
                
            target = targets[0]
            log_worker_event(ws.worker_number, f"Clicking settings button: {target.get('custom_id')}", "DEBUG")
            
            try:
                await _wrapped_interaction(
                    bs_msg._state,
                    _generate_nonce(),
                    InteractionType.component,
                    None,
                    bs_msg.channel,
                    target,
                    message=bs_msg
                )
            except Exception as e:
                log_worker_event(ws.worker_number, f"Error clicking button: {e}", "WARNING")
                
            clicks += 1
            await made_by_ghosty.sleep(2.5)

    except Exception as e:
        log_worker_event(ws.worker_number, f"Error setting up user settings: {e}", "WARNING")

def _get_humanoid_delay(ws, min_delay, max_delay):
    uptime_mins = (datetime.now() - ws.ghosty_start_time).total_seconds() / 60
    if uptime_mins <= 30:
        fatigue = 0.8
    elif uptime_mins <= 90:
        fatigue = 1.0
    else:
        fatigue = 1.3
        
    base = ghostyjija.gauss(mu=(min_delay + max_delay) / 2, sigma=(max_delay - min_delay) / 4)
    t = (base - min_delay) / (max_delay - min_delay)
    t = max(0.0, min(1.0, t))
    bezier_t = 3 * (t**2) - 2 * (t**3)
    
    final_delay = min_delay + bezier_t * (max_delay - min_delay)
    final_delay *= fatigue
    return max(min_delay * 0.8, min(max_delay * 1.5, final_delay))


async def _run_farming_loop(ctx, ws, bot):
    ws.running = True
    ws.sleep_mode = False
    ws.has_started = True
    ws.paused = False
    ws.pause_end_time = None
    ws.zoo_channel = ctx.channel
    ws.last_gem_check = time.time()
    ws.sleep_start_time = None
    ws.farming_start_time = datetime.now()
    ws.last_mode_change_time = datetime.now()
    ws.ghosty_start_time = datetime.now()
    ws.active_channel_id = ctx.channel.id

    ws.lifetime_work_cycles = 0
    ws.lifetime_day_skip_active = False
    ws.lifetime_cycle_start_time = datetime.now()

    current_config = SPEED_MODES[ws.current_speed_mode]
    zoo_data = await fetch_zoo_data(ctx)
    if zoo_data:
        ws.initial_cash = zoo_data["total_cash"]
        ws.initial_essence = zoo_data["total_essence"]

    await setup_user_settings(ctx, ws)

    if ws.huntbot_enabled:
        await made_by_ghosty.sleep(2)
        data = LoadGhoStysHbData(ws)
        data["channel_id"] = ctx.channel.id
        SaveHbDataGhoStys(ws, data)
        await ctx.send("owo hb")
        await made_by_ghosty.sleep(4)
        await CheckGhoStyHbMsgFetch(ctx, ws)
        bot.loop.create_task(_monitor_huntbot(ctx, ws, bot))
        await made_by_ghosty.sleep(2)
    else:
        log_worker_event(ws.worker_number, "Auto-HuntBot disabled, skipping HB setup", "DEBUG")
    bot.loop.create_task(_monitor_boss_fights(ctx, ws, bot))

    last_command = None

    while ws.running:
        try:
            if ws.paused and not ws.sleep_mode:
                now = datetime.now()
                if now >= ws.pause_end_time:
                    ws.paused = False
                    ws.pause_end_time = None
                    ws.farming_start_time = datetime.now()
                    ws.last_mode_change_time = datetime.now()
                    if ws.lifetime_cycle_start_time is not None:
                        ws.lifetime_cycle_start_time = datetime.now()
                    await ctx.send("⏰ **Pause over!** Resuming farming now.")
                    log_worker_event(ws.worker_number, "⏰ Pause ended, resuming farming", "INFO")
                else:
                    await made_by_ghosty.sleep(10)
                    continue

            if ws.has_started and ws.running and not ws.sleep_mode and not ws.paused:
                current_time = datetime.now()
                
                try:
                    from .questsmodule import check_and_handle_quests
                    await check_and_handle_quests(ctx, ws, bot)
                except Exception as e:
                    log_worker_event(ws.worker_number, f"Error checking quests: {e}", "WARNING")

                if ws.current_speed_mode in ["lifetime", "humanoid"]:
                    current_config = SPEED_MODES[ws.current_speed_mode]

                    if not ws.lifetime_day_skip_active:
                        should_skip_day = ghostyjija.random() < 0.5
                        if ws.lifetime_work_cycles >= ghostyjija.randint(3, 4) and should_skip_day:
                            ws.lifetime_day_skip_active = True
                            day_skip_duration = 24 * 3600
                            skip_end_time = current_time + timedelta(seconds=day_skip_duration)
                            await ctx.send(
                                f"😴 **LIFETIME MODE: DAY SKIP ACTIVATED** 🌙\n"
                                f"Full 24-hour rest. Will resume at **{skip_end_time.strftime('%d-%b-%Y %I:%M:%S %p')}**"
                            )
                            log_worker_event(ws.worker_number, "⏸️ LIFETIME DAY SKIP started", "INFO")
                            await made_by_ghosty.sleep(day_skip_duration)
                            ws.lifetime_day_skip_active = False
                            ws.lifetime_work_cycles = 0
                            ws.farming_start_time = datetime.now()
                            ws.lifetime_cycle_start_time = datetime.now()
                            await ctx.send("⏰ **LIFETIME MODE: RESUMING AFTER DAY SKIP** 🚀")
                            log_worker_event(ws.worker_number, "⏰ LIFETIME DAY SKIP ENDED — resuming", "INFO")
                            continue

                    if ws.lifetime_cycle_start_time is None:
                        ws.lifetime_cycle_start_time = current_time

                    work_duration = ghostyjija.uniform(
                        current_config["work_duration_min"],
                        current_config["work_duration_max"],
                    )
                    elapsed_cycle_time = (current_time - ws.lifetime_cycle_start_time).total_seconds()

                    if elapsed_cycle_time >= work_duration:
                        ws.sleep_mode = True
                        break_duration = ghostyjija.uniform(
                            current_config["break_duration_min"],
                            current_config["break_duration_max"],
                        )
                        ws.sleep_start_time = current_time
                        sleep_end_time = current_time + timedelta(seconds=break_duration)
                        ws.lifetime_work_cycles += 1
                        hours, remainder = divmod(int(break_duration), 3600)
                        mins = remainder // 60
                        await ctx.send(
                            f"😴 **LIFETIME MODE: BREAK TIME** 🌙\n"
                            f"Work cycle #{ws.lifetime_work_cycles} complete. Breaking for {hours}h {mins}m. "
                            f"Resume at **{sleep_end_time.strftime('%d-%b-%Y %I:%M:%S %p')}**"
                        )
                        log_worker_event(ws.worker_number, f"😴 LIFETIME BREAK #{ws.lifetime_work_cycles}: {hours}h {mins}m", "INFO")
                        await made_by_ghosty.sleep(break_duration)
                        ws.sleep_mode = False
                        ws.lifetime_cycle_start_time = datetime.now()
                        if not ws.paused:
                            await ctx.send(
                                f"⏰ **LIFETIME MODE: BACK TO WORK** 🚀\n"
                                f"Starting work cycle #{ws.lifetime_work_cycles + 1}"
                            )
                            log_worker_event(ws.worker_number, f"⏰ LIFETIME WORK CYCLE #{ws.lifetime_work_cycles + 1} started", "INFO")
                        continue

                else:
                    active_mode = ws.current_speed_mode
                    current_config = SPEED_MODES[active_mode]
                    elapsed_time = (current_time - ws.farming_start_time).total_seconds()
                    max_run_time = ghostyjija.uniform(
                        current_config["run_duration_min"],
                        current_config["run_duration_max"],
                    )
                    if elapsed_time >= max_run_time:
                        ws.sleep_mode = True
                        sleep_duration = ghostyjija.uniform(
                            current_config["sleep_duration_min"],
                            current_config["sleep_duration_max"],
                        )
                        ws.sleep_start_time = current_time
                        sleep_end_time = current_time + timedelta(seconds=sleep_duration)
                        await ctx.send(
                            f"😴 Entering sleep mode. Will resume at "
                            f"**{sleep_end_time.strftime('%d-%b-%Y %I:%M:%S %p')}**"
                        )
                        log_worker_event(ws.worker_number, "😴 Sleep mode started", "INFO")
                        await made_by_ghosty.sleep(sleep_duration)
                        ws.sleep_mode = False
                        ws.farming_start_time = datetime.now()
                        ws.last_mode_change_time = datetime.now()
                        if not ws.paused:
                            await ctx.send("⏰ Waking up from sleep. Resuming")
                            log_worker_event(ws.worker_number, "⏰ Waking up from sleep mode, resuming", "INFO")
                        continue

            if ws.sleep_mode:
                await made_by_ghosty.sleep(10)
                continue

            if ws.paused:
                await made_by_ghosty.sleep(10)
                continue

            if getattr(ws, "is_boss_fighting", False):
                await made_by_ghosty.sleep(5)
                continue
                
            if getattr(ws, "is_mail_claiming", False):
                await made_by_ghosty.sleep(5)
                continue

            current_time_ts = time.time()
            current_config = SPEED_MODES[ws.current_speed_mode]

            gem_check_interval = ghostyjija.randint(
                int(current_config["gem_check_interval_min"]),
                int(current_config["gem_check_interval_max"]),
            )

            if current_time_ts - ws.last_gem_check >= gem_check_interval:
                warning_detected = await _check_warning(ctx, ws)
                if warning_detected or not ws.running:
                    break
                await _do_gem_check(ctx, ws)
                ws.last_gem_check = current_time_ts
                continue

            def ghostysmarttypo(command):
                if ghostyjija.random() < 0.12:
                    idx = ghostyjija.randint(0, len(command) - 1)
                    ghostytypochars = ghostyjija.choice("abcdefghijklmnopqrstuvwxyz")
                    return command[:idx] + ghostytypochars + command[idx + 1:]
                return command

            cmds = [
                ghostysmarttypo("owoh"),
                ghostysmarttypo("owo pray"),
                ghostysmarttypo("owo h"),
                ghostysmarttypo("owo b"),
                ghostysmarttypo("owob"),
                ghostysmarttypo("owoh"),
                ghostysmarttypo("owo h"),
                ghostysmarttypo(ghostyjija.choice(["owo cf 1", "owoz", "owo s 2", "owo owo", "owoq"])),
                ghostysmarttypo(ghostyjija.choice(["owo pup", "owo army", "owo piku", "owo run"])),
                ghostysmarttypo(ghostyjija.choice(["owo punch <@408785106942164992>", "owo roll"])),
            ]
            command = ghostyjija.choice(cmds)
            while command == last_command:
                command = ghostyjija.choice(cmds)
            last_command = command

            await ctx.send(command)
            ws.ghosty_commands_sent += 1

            await made_by_ghosty.sleep(current_config["command_delay"])
            warning_detected = await _check_warning(ctx, ws)
            if warning_detected or not ws.running:
                break

            if ws.current_speed_mode == "humanoid":
                delay = _get_humanoid_delay(ws, current_config["action_delay_min"], current_config["action_delay_max"])
                try:
                    if bot and hasattr(bot, 'guilds') and bot.guilds:
                        g = ghostyjija.choice(bot.guilds)
                        channels = [c for c in g.text_channels if c.permissions_for(g.me).view_channel]
                        if channels:
                            c = ghostyjija.choice(channels)
                            _ = [msg async for msg in c.history(limit=5)]
                except Exception:
                    pass
                await made_by_ghosty.sleep(delay)
            else:
                await made_by_ghosty.sleep(
                    ghostyjija.uniform(
                        current_config["action_delay_min"],
                        current_config["action_delay_max"],
                    )
                )
            if ghostyjija.random() < 0.05:
                await made_by_ghosty.sleep(
                    ghostyjija.uniform(
                        current_config["random_long_delay_min"],
                        current_config["random_long_delay_max"],
                    )
                )

        except Exception as e:
            log_worker_event(ws.worker_number, f"Error in main loop: {e}", "CRITICAL")


async def _fetch_zoo_for_main_status(ws):
    if not ws.has_started or not ws.zoo_channel or ws.sleep_mode or ws.paused:
        return
    try:
        await ws.zoo_channel.send("owo zoo")
        await made_by_ghosty.sleep(5)
        messages = [msg async for msg in ws.zoo_channel.history(limit=10)]
        zoo_messages = []
        for msg in messages:
            if msg.author.id == 408785106942164992:
                content_lower = msg.content.lower()
                if (any(kw in content_lower for kw in ["zoo", "animals", "cowoncy", "points:"]) or any(sup in msg.content for sup in "⁰¹²³⁴⁵⁶⁷⁸⁹")):
                    zoo_messages.append(msg.content)
                    if "common" in content_lower:
                        break
        if zoo_messages:
            zoo_messages.reverse()
            zoo_data = await parse_zoo_message(zoo_messages)
            ws.current_cash = zoo_data["total_cash"]
            ws.current_essence = zoo_data["total_essence"]
            log_worker_event(ws.worker_number, "Zoo data fetched for main status", "DEBUG")
    except Exception as e:
        log_worker_event(ws.worker_number, f"Error in main-status zoo fetch: {e}", "WARNING")


async def _send_status(ctx, ws_target, live_fetch=True):
    current_config = SPEED_MODES[ws_target.current_speed_mode]

    if ws_target.paused:
        remaining = ws_target.pause_end_time - datetime.now() if ws_target.pause_end_time else timedelta(0)
        rem_secs = max(0, int(remaining.total_seconds()))
        rem_str = _format_duration(rem_secs) if rem_secs > 0 else "ending soon"
        if ws_target.sleep_mode:
            ghosty_state = f"⏸️ Paused (after current sleep) — {rem_str} remaining"
        else:
            ghosty_state = f"⏸️ Paused — {rem_str} remaining"
    elif ws_target.current_speed_mode == "lifetime":
        if ws_target.lifetime_day_skip_active:
            ghosty_state = f"🌙 Day Skip Mode ({current_config['name']})"
        elif ws_target.sleep_mode:
            ghosty_state = f"😴 Break Time (Cycle #{ws_target.lifetime_work_cycles}) ({current_config['name']})"
        elif ws_target.has_started and ws_target.running:
            ghosty_state = f"🚀 Working (Cycle #{ws_target.lifetime_work_cycles + 1}) ({current_config['name']})"
        else:
            ghosty_state = f"⚫ Not Running ({current_config['name']})"
    else:
        if ws_target.sleep_mode:
            ghosty_state = f"😴 Sleeping ({current_config['name']})"
            if ws_target.sleep_start_time:
                sleep_elapsed = datetime.now() - ws_target.sleep_start_time
                hrs, rem = divmod(int(sleep_elapsed.total_seconds()), 3600)
                mins, secs = divmod(rem, 60)
                ghosty_state += f" | Slept: {hrs}h {mins}m {secs}s"
        elif ws_target.has_started and ws_target.running:
            ghosty_state = f"🟢 Running ({current_config['name']})"
        else:
            ghosty_state = f"⚫ Not Running ({current_config['name']})"

    ghosty_uptime = datetime.now() - ws_target.ghosty_start_time
    hrs, rem = divmod(int(ghosty_uptime.total_seconds()), 3600)
    mins, secs = divmod(rem, 60)

    profit_text = ""
    if live_fetch and ws_target.has_started and ws_target.zoo_channel and not ws_target.sleep_mode and not ws_target.paused:
        await ctx.send("🔍 Fetching current zoo data for profit calculation...")
        await ws_target.zoo_channel.send("owo zoo")
        await made_by_ghosty.sleep(5)
        try:
            messages = [msg async for msg in ws_target.zoo_channel.history(limit=10)]
            zoo_messages = []
            for msg in messages:
                if msg.author.id == 408785106942164992:
                    content_lower = msg.content.lower()
                    if (any(kw in content_lower for kw in ["zoo", "animals", "cowoncy", "points:"]) or any(sup in msg.content for sup in "⁰¹²³⁴⁵⁶⁷⁸⁹")):
                        zoo_messages.append(msg.content)
                        if "common" in content_lower:
                            break
            if zoo_messages:
                zoo_messages.reverse()
                zoo_data = await parse_zoo_message(zoo_messages)
                ws_target.current_cash = zoo_data["total_cash"]
                ws_target.current_essence = zoo_data["total_essence"]
                cash_profit = ws_target.current_cash - ws_target.initial_cash
                essence_profit = ws_target.current_essence - ws_target.initial_essence
                profit_text = (
                    f"\n\n💰 **Profit Since Start:**\n"
                    f"> 💵 Cash: {format_value(cash_profit)} ({format_value(ws_target.initial_cash)} → {format_value(ws_target.current_cash)})\n"
                    f"> ✨ Essence: {format_value(essence_profit)} ({format_value(ws_target.initial_essence)} → {format_value(ws_target.current_essence)})"
                )
        except Exception as e:
            log_worker_event(ws_target.worker_number, f"Error fetching status zoo data: {e}", "WARNING")
            profit_text = "\n\n⚠ Could not fetch current zoo data."
    elif not live_fetch and ws_target.has_started:
        if ws_target.current_cash or ws_target.current_essence:
            cash_profit = ws_target.current_cash - ws_target.initial_cash
            essence_profit = ws_target.current_essence - ws_target.initial_essence
            profit_text = (
                f"\n\n💰 **Profit (Cached):**\n"
                f"> 💵 Cash: {format_value(cash_profit)} ({format_value(ws_target.initial_cash)} → {format_value(ws_target.current_cash)})\n"
                f"> ✨ Essence: {format_value(essence_profit)} ({format_value(ws_target.initial_essence)} → {format_value(ws_target.current_essence)})"
            )

    lifetime_info = ""
    if ws_target.current_speed_mode == "lifetime":
        lifetime_info = (
            f"\n> ♾️ **Work Cycles:** {ws_target.lifetime_work_cycles}\n"
            f"> 🌙 **Day Skip Active:** {'Yes' if ws_target.lifetime_day_skip_active else 'No'}"
        )
        if ws_target.lifetime_cycle_start_time:
            cycle_elapsed = datetime.now() - ws_target.lifetime_cycle_start_time
            cycle_hrs, cycle_rem = divmod(int(cycle_elapsed.total_seconds()), 3600)
            cycle_mins = cycle_rem // 60
            lifetime_info += f"\n> ⏱️ **Current Cycle Duration:** {cycle_hrs}h {cycle_mins}m"

    if not ws_target.huntbot_enabled:
        hb_status = "🔴 Disabled"
    elif ws_target.GhoStyHbAlrActiveVar:
        hb_status = "✅ Active"
    else:
        hb_status = "⏳ Inactive"

    pause_info = ""
    if ws_target.paused and ws_target.pause_end_time:
        pause_info = f"\n> ⏸️ **Paused Until:** {ws_target.pause_end_time.strftime('%d-%b-%Y %I:%M:%S %p')}"

    boss_status = f"{ws_target.boss_tickets}/3 Tickets"
    if ws_target.boss_tickets <= 0:
        boss_status += " 🚫 (Out of Tickets)"
    elif ws_target.is_boss_fighting:
        boss_status += " ⚔️ (Fighting Now!)"
    elif ws_target.next_boss_fight_time:
        boss_status += f" ⏳ (Next Check: <t:{int(ws_target.next_boss_fight_time.timestamp())}:R>)"

    gstatusghosty = f"""
🔍 **GhoSty OwO Worker #{ws_target.worker_number} Status:** {ghosty_state}

> 👤 **Username:** {ws_target.username}
> 🕒 **Running Since:** {ws_target.ghosty_start_time.strftime('%d-%b-%Y %I:%M:%S %p')}
> 📈 **Uptime:** {hrs}h {mins}m {secs}s
> 📊 **Commands Sent:** {ws_target.ghosty_commands_sent}
> 💎 **Gems Potentially Used:** {ws_target.ghosty_gems_used}
> ⚡ **Speed Mode:** {current_config['name']}{lifetime_info}
> 🛏️ **Sleeping?:** {"Yes" if ws_target.sleep_mode else "No"}
> 🎯 **HuntBot:** {hb_status}
> 🧠 **HuntBot Solver:** {"Available" if ws_target.GhoStyCoreAvailCheck else "Not Available"}
> 👹 **Guild Boss:** {boss_status}
> ♻️ **Last Gem Check:** {'<t:' + str(int(ws_target.last_gem_check)) + ':R>' if ws_target.last_gem_check else 'Never'}{pause_info}{profit_text}
"""
    await ctx.send(gstatusghosty)



class PseudoCtx:
    def __init__(self, channel, bot_instance):
        self.channel = channel
        self.bot = bot_instance
        self.author = bot_instance.user

    async def send(self, *args, **kwargs):
        return await self.channel.send(*args, **kwargs)


def _has_main_controller_args(ctx):

    raw = ctx.message.content.strip()

    after = raw[len(ctx.prefix + ctx.invoked_with):].strip()
    if not after:
        return False

    first = after.split()[0].lower().rstrip(",")
    return first == "all" or first.isdigit()


def register_commands(bot, ws):

    @bot.command(aliases=["h"])
    async def help(ctx):
        if ctx.author.id != bot.user.id:
            return
        ghosty_help = """
    # 🤑 GhoSty OwO Farm V4.1 🤑 
Prefix: `.`

**__Main__**
 🌟 `.start` — Start farming in this channel
 🛑 `.stop` — Stop this worker
 🔍 `.status` — Show worker status
 ⚡ `.speed [mode]` — View/change speed mode
 🎯 `.huntbot [on/off]` — Toggle auto-HuntBot
 ⏸️ `.pause <time>` — Pause farming (min 15m, e.g. .pause 30m / .pause 1h)
 ▶️ `.resume` — Resume from pause early

**__Speed Modes__**
 `efficient` | `fast` | `durable` | `lifetime` (default)

**__Made with 💖 and 🧠 by GhoSty | [Async Development]__** 
"""
        await ctx.send(ghosty_help)

    @bot.command()
    async def speed(ctx, mode: str = None):
        if ctx.author.id != bot.user.id:
            return

        if _has_main_controller_args(ctx):
            return

        if mode is None:
            current_config = SPEED_MODES[ws.current_speed_mode]
            await ctx.send(
                f"⚡ Current speed mode: **{current_config['name']}**\n\n"
                "Available modes: `efficient`, `fast`, `durable`, `lifetime`"
            )
            return

        mode = mode.lower()
        if mode not in SPEED_MODES:
            await ctx.send("❌ Invalid speed mode. Available: `efficient`, `fast`, `durable`, `lifetime`, `humanoid`")
            return

        ws.current_speed_mode = mode
        ws.last_mode_change_time = datetime.now()
        current_config = SPEED_MODES[ws.current_speed_mode]
        await ctx.send(f"✅ Speed mode changed to: **{current_config['name']}**")

    @bot.command()
    async def start(ctx):
        if ctx.author.id != bot.user.id:
            return

        if _has_main_controller_args(ctx):
            return

        if ws.running and ws.has_started:
            await ctx.send(
                "⚠️ **GhoSty OwO Worker is already running!**\n\n"
                "🛑 Please use `.stop` first, then `.start` to restart."
            )
            return

        success, blocking_worker = manager.try_claim_channel(ctx.channel.id, ws.worker_number)
        if not success:
            bw = manager.get_worker(blocking_worker)
            bw_name = bw.username if bw else "Unknown"
            await ctx.send(
                f"GhoSty OwO Worker number {blocking_worker} with username {bw_name} already working in this channel."
            )
            return

        await ctx.send(f"🌟 **GhoSty OwO Worker #{ws.worker_number} Starting!**")
        await _run_farming_loop(ctx, ws, bot)

    @bot.command()
    async def stop(ctx):
        if ctx.author.id != bot.user.id:
            return

        if _has_main_controller_args(ctx):
            return

        await ctx.send("🛑 Stopping | Type `.start` again to re-start grinding")
        ws.running = False
        ws.has_started = False
        ws.sleep_mode = False
        ws.paused = False
        ws.pause_end_time = None
        manager.release_channel(ctx.channel.id, ws.worker_number)

    @bot.command()
    async def status(ctx):
        if ctx.author.id != bot.user.id:
            return
        if _has_main_controller_args(ctx):
            return

        await _send_status(ctx, ws, live_fetch=True)

    @bot.command()
    async def mail(ctx):
        if ctx.author.id != bot.user.id:
            return

        if _has_main_controller_args(ctx):
            return

        if ws.last_mail_claim:
            time_since = (datetime.now() - ws.last_mail_claim).total_seconds()
            if time_since < 300:
                await ctx.send(f"⏳ **Cooldown active!** Please wait {int(300 - time_since)}s before checking mail again.")
                return

        if ws.is_mail_claiming:
            await ctx.send("⚠️ Currently already checking mail. Please wait.")
            return

        ws.last_mail_claim = datetime.now()
        ws.is_mail_claiming = True
        await ctx.send("📩 Started checking mailbox in the background...")
        from core.mailmodule import execute_mail_claim
        bot.loop.create_task(execute_mail_claim(ctx, ws, bot))

    @bot.command()
    async def huntbot(ctx, toggle: str = None):
        if ctx.author.id != bot.user.id:
            return

        if _has_main_controller_args(ctx):
            return

        if toggle is None:
            state = "🟢 ON" if ws.huntbot_enabled else "🔴 OFF"
            await ctx.send(f"🎯 **Auto-HuntBot is currently: {state}**\nUse `.huntbot on` or `.huntbot off` to toggle.")
            return

        toggle = toggle.lower()
        if toggle == "on":
            ws.huntbot_enabled = True
            await ctx.send("✅ **Auto-HuntBot is now ON.** Will trigger on next `.start`.")
        elif toggle == "off":
            if ws.GhoStyHbAlrActiveVar:
                ws.GhoStyHbAlrActiveVar = False
                log_worker_event(ws.worker_number, "HuntBot toggled off while active — resetting tracking", "INFO")
            ws.huntbot_enabled = False
            await ctx.send("🔴 **Auto-HuntBot is now OFF.** HuntBot will be skipped.")
        else:
            await ctx.send("❌ Invalid option. Use `.huntbot on` or `.huntbot off`")

    @bot.command()
    async def pause(ctx, time_str: str = None):
        if ctx.author.id != bot.user.id:
            return

        if _has_main_controller_args(ctx):
            return

        if time_str is None:
            if ws.paused and ws.pause_end_time:
                remaining = ws.pause_end_time - datetime.now()
                rem_secs = max(0, int(remaining.total_seconds()))
                await ctx.send(
                    f"⏸️ **Currently paused.** Resumes at "
                    f"**{ws.pause_end_time.strftime('%d-%b-%Y %I:%M:%S %p')}** "
                    f"({_format_duration(rem_secs)} remaining)\n"
                    f"Use `.resume` to end the pause early."
                )
            else:
                await ctx.send(
                    "❌ No active pause. Usage: `.pause 30m` / `.pause 1h` / `.pause 1h30m`\n"
                    "Minimum pause time is **15 minutes**."
                )
            return

        if not ws.running or not ws.has_started:
            await ctx.send("❌ Worker is not running. Use `.start` first.")
            return

        if ws.paused:
            await ctx.send(
                f"⏸️ Already paused until **{ws.pause_end_time.strftime('%d-%b-%Y %I:%M:%S %p')}**.\n"
                f"Use `.resume` to end the pause early."
            )
            return

        secs = _parse_pause_time(time_str)
        if secs is None:
            await ctx.send("❌ Invalid time format. Examples: `.pause 30m` / `.pause 1h` / `.pause 1h30m`")
            return

        if secs < 900:
            await ctx.send("❌ Minimum pause time is **15 minutes**. Example: `.pause 15m`")
            return

        ws.paused = True
        ws.pause_end_time = datetime.now() + timedelta(seconds=secs)
        resume_str = ws.pause_end_time.strftime('%d-%b-%Y %I:%M:%S %p')

        extra = ""
        if ws.sleep_mode or ws.lifetime_day_skip_active:
            extra = "\n⚠️ A natural sleep is currently running — pause will begin after it completes."
        if secs > 86400:
            extra += f"\n⚠️ Long pause ({_format_duration(secs)}) — use `.stop` if you meant to stop entirely."

        await ctx.send(
            f"⏸️ **Farming paused for {_format_duration(secs)}.**\n"
            f"Auto-resumes at **{resume_str}**{extra}"
        )
        log_worker_event(ws.worker_number, f"⏸️ Paused for {_format_duration(secs)}", "INFO")

    @bot.command()
    async def resume(ctx):
        if ctx.author.id != bot.user.id:
            return

        if _has_main_controller_args(ctx):
            return

        if not ws.paused:
            await ctx.send("❌ Worker is not currently paused.")
            return

        ws.paused = False
        ws.pause_end_time = None
        ws.farming_start_time = datetime.now()
        ws.last_mode_change_time = datetime.now()
        if ws.lifetime_cycle_start_time is not None:
            ws.lifetime_cycle_start_time = datetime.now()
        await ctx.send("▶️ **Pause cancelled. Resuming farming on next cycle.**")
        log_worker_event(ws.worker_number, "▶️ Manual resume from pause", "INFO")

    ws.bot = bot

def register_main_commands(bot):

    @bot.command()
    async def help(ctx):
        if ctx.author.id != bot.user.id:
            return
        main_help = f"""
# 🎮 GhoSty OwO Main Controller

Prefix: `.`   **Total Workers:** {manager.total_workers}

**__Worker Management__**
 📋 `.workers` — List all workers and their status
 🌟 `.start <N/N,M>` — Start specific worker(s) in this channel
 🌟 `.start all` — Start all workers using channels.txt pairing
 🛑 `.stop <N/N,M/all>` — Stop specific/all workers
 🔍 `.status <N>` — Show a specific worker's status
 💰 `.profit` — Show cash profit summary across all workers
 💬 `.say <text>` — Make all workers send text in their designated channels

**__Control__**
 ⚡ `.speed <N/all> <mode>` — Change speed mode for worker(s)
 🎯 `.huntbot <N/all> <on/off>` — Toggle auto-HuntBot
 ⏸️ `.pause <N/all> <time>` — Pause worker(s) (e.g. .pause 1 30m)
 ▶️ `.resume <N/all>` — Resume paused worker(s)

**__Speed Modes:__** `efficient` | `fast` | `durable` | `lifetime` | `humanoid`
**__Made with 💖 by GhoSty | [Async Development]__**
"""
        await ctx.send(main_help)

    @bot.command()
    async def workers(ctx):
        if ctx.author.id != bot.user.id:
            return

        all_ws = manager.get_all_workers()
        if not all_ws:
            await ctx.send("⚫ No workers registered yet.")
            return

        lines = [f"📋 **GhoSty OwO Workers ({manager.total_workers} total):**\n"]
        for wn, w in sorted(all_ws.items()):
            if w.paused:
                icon = "⏸️"
            elif w.running and w.has_started and not w.sleep_mode:
                icon = "🟢"
            elif w.sleep_mode:
                icon = "😴"
            else:
                icon = "⚫"
            hb = "🎯" if w.huntbot_enabled else "🔴"
            lines.append(f"> {icon} Worker #{wn} — {w.username} {hb}")
        await ctx.send("\n".join(lines))

    @bot.command()
    async def start(ctx, *, args: str = None):
        if ctx.author.id != bot.user.id:
            return

        if args is None:
            await ctx.send(
                "❌ Usage: `.start <N>` / `.start 1, 2, 3` / `.start all`\n"
                "Note: `.start all` requires channels.txt to be configured."
            )
            return

        use_all = args.strip().lower() == "all"

        if use_all:
            if not manager.has_channels_config:
                await ctx.send(
                    "❌ **No channels configured.** Add channel IDs to `channels.txt` to use `.start all`."
                )
                return

            started_count = 0
            skipped = []
            for wn, target_ws in sorted(manager.get_all_workers().items()):
                ch_id = target_ws.auto_start_channel_id
                if ch_id is None:
                    skipped.append(f"Worker #{wn}: no channel assigned in channels.txt")
                    continue

                if target_ws.running and target_ws.has_started:
                    skipped.append(f"Worker #{wn} ({target_ws.username}): already running")
                    continue

                success, blocking = manager.try_claim_channel(ch_id, wn)
                if not success:
                    bw = manager.get_worker(blocking)
                    bw_name = bw.username if bw else "Unknown"
                    skipped.append(
                        f"Worker #{wn}: channel locked by Worker #{blocking} ({bw_name})"
                    )
                    continue

                target_bot = target_ws.bot
                if not (target_bot and target_bot.loop and target_bot.loop.is_running()):
                    manager.release_channel(ch_id, wn)
                    skipped.append(f"Worker #{wn}: bot not connected yet")
                    continue

                target_channel = target_bot.get_channel(ch_id)
                if not target_channel:
                    manager.release_channel(ch_id, wn)
                    skipped.append(f"Worker #{wn}: cannot see channel {ch_id} (not in server?)")
                    continue

                pseudo_ctx = PseudoCtx(target_channel, target_bot)
                made_by_ghosty.run_coroutine_threadsafe(
                    _run_farming_loop(pseudo_ctx, target_ws, target_bot),
                    target_bot.loop,
                )
                started_count += 1

            reply_lines = [f"🌟 **Started {started_count} worker(s) via channels.txt.**"]
            if skipped:
                reply_lines.append("\n⚠️ **Skipped:**")
                for s in skipped:
                    reply_lines.append(f"> {s}")
            await ctx.send("\n".join(reply_lines))
            return

        target_numbers = _parse_worker_args(args)
        if target_numbers is None:
            await ctx.send(f"❌ Invalid worker number in: `{args}`")
            return
        if not target_numbers:
            await ctx.send("❌ No valid worker numbers provided.")
            return

        for wn in target_numbers:
            target_ws = manager.get_worker(wn)
            if target_ws is None:
                await ctx.send(f"❌ Worker {wn} does not exist. Available: 1-{manager.total_workers}")
                continue

            if target_ws.running and target_ws.has_started:
                await ctx.send(
                    f"⚠️ Worker #{wn} ({target_ws.username}) is already running! Use `.stop {wn}` first."
                )
                continue

            success, blocking = manager.try_claim_channel(ctx.channel.id, wn)
            if not success:
                bw = manager.get_worker(blocking)
                bw_name = bw.username if bw else "Unknown"
                await ctx.send(
                    f"GhoSty OwO Worker number {blocking} with username {bw_name} already working in this channel."
                )
                continue

            target_bot = target_ws.bot
            if not (target_bot and target_bot.loop and target_bot.loop.is_running()):
                manager.release_channel(ctx.channel.id, wn)
                await ctx.send(f"⚠️ Worker #{wn} bot is not connected yet. Try again shortly.")
                continue

            target_channel = target_bot.get_channel(ctx.channel.id)
            if not target_channel:
                manager.release_channel(ctx.channel.id, wn)
                await ctx.send(f"⚠️ Worker #{wn} cannot see this channel.")
                continue

            await ctx.send(f"🌟 Starting Worker #{wn} ({target_ws.username}) in this channel...")
            pseudo_ctx = PseudoCtx(target_channel, target_bot)
            made_by_ghosty.run_coroutine_threadsafe(
                _run_farming_loop(pseudo_ctx, target_ws, target_bot),
                target_bot.loop,
            )

    @bot.command()
    async def stop(ctx, *, args: str = None):
        if ctx.author.id != bot.user.id:
            return

        if args is None:
            await ctx.send(
                "❌ Usage: `.stop <N>` / `.stop 1, 2, 3` / `.stop all`"
            )
            return

        target_numbers = _parse_worker_args(args)
        if target_numbers is None:
            await ctx.send(f"❌ Invalid worker number in: `{args}`")
            return

        for wn in target_numbers:
            target_ws = manager.get_worker(wn)
            if target_ws is None:
                await ctx.send(f"❌ Worker {wn} does not exist. Available: 1-{manager.total_workers}")
                continue

            if not target_ws.running and not target_ws.has_started:
                await ctx.send(f"⚫ Worker #{wn} ({target_ws.username}) is not running.")
                continue

            target_ws.running = False
            target_ws.has_started = False
            target_ws.sleep_mode = False
            target_ws.paused = False
            target_ws.pause_end_time = None
            if target_ws.active_channel_id:
                manager.release_channel(target_ws.active_channel_id, wn)
            await ctx.send(f"🛑 Worker #{wn} ({target_ws.username}) stopped.")

    @bot.command()
    async def status(ctx, worker_number: int = None):
        if ctx.author.id != bot.user.id:
            return

        if worker_number is None:
            await ctx.send(
                "❌ Usage: `.status <worker_number>`\n"
                "Example: `.status 1`\n"
                "Use `.workers` to see all workers at a glance."
            )
            return

        target_ws = manager.get_worker(worker_number)
        if target_ws is None:
            await ctx.send(f"❌ Worker {worker_number} does not exist. Available: 1-{manager.total_workers}")
            return

        if (
            target_ws.has_started
            and target_ws.zoo_channel
            and not target_ws.sleep_mode
            and not target_ws.paused
            and target_ws.bot
            and target_ws.bot.loop
            and target_ws.bot.loop.is_running()
        ):
            try:
                await ctx.send("🔍 Fetching live zoo data for Worker #{}...".format(worker_number))
                future = made_by_ghosty.run_coroutine_threadsafe(
                    _fetch_zoo_for_main_status(target_ws),
                    target_ws.bot.loop,
                )
                await made_by_ghosty.wrap_future(future)
            except Exception as e:
                log_worker_event("CTRL", f"Zoo fetch failed for W#{worker_number}: {e}", "WARNING")

        await _send_status(ctx, target_ws, live_fetch=False)

    @bot.command()
    async def speed(ctx, *, args: str = None):
        if ctx.author.id != bot.user.id:
            return

        if args is None:
            await ctx.send(
                "❌ Usage: `.speed <N/all> <mode>`\n"
                "Example: `.speed 1 lifetime` / `.speed all durable`\n"
                "Modes: `efficient`, `fast`, `durable`, `lifetime`"
            )
            return

        parts = args.split()
        if len(parts) < 2:
            await ctx.send(
                "❌ Usage: `.speed <N/all> <mode>`\n"
                "Example: `.speed 1 lifetime` / `.speed all durable`"
            )
            return

        mode = parts[-1].lower()
        if mode not in SPEED_MODES:
            await ctx.send(f"❌ Unknown speed mode `{mode}`. Available: `efficient`, `fast`, `durable`, `lifetime`, `humanoid`")
            return

        worker_spec = " ".join(parts[:-1])
        target_numbers = _parse_worker_args(worker_spec)
        if target_numbers is None:
            await ctx.send(f"❌ Invalid worker number in: `{worker_spec}`")
            return
        if not target_numbers:
            await ctx.send("❌ No valid worker numbers provided.")
            return

        current_config = SPEED_MODES[mode]
        changed = []
        for wn in target_numbers:
            target_ws = manager.get_worker(wn)
            if target_ws is None:
                await ctx.send(f"❌ Worker {wn} does not exist.")
                continue
            target_ws.current_speed_mode = mode
            target_ws.last_mode_change_time = datetime.now()
            changed.append(f"Worker #{wn} ({target_ws.username})")

        if changed:
            await ctx.send(
                f"✅ Speed mode set to **{current_config['name']}** for: "
                + ", ".join(changed)
            )

    @bot.command()
    async def huntbot(ctx, *, args: str = None):
        if ctx.author.id != bot.user.id:
            return

        if args is None:
            await ctx.send(
                "❌ Usage: `.huntbot <N/all> <on/off>`\n"
                "Example: `.huntbot 1 off` / `.huntbot all on`"
            )
            return

        parts = args.split()
        if len(parts) < 2:
            await ctx.send("❌ Usage: `.huntbot <N/all> <on/off>`")
            return

        toggle = parts[-1].lower()
        if toggle not in ("on", "off"):
            await ctx.send("❌ Toggle must be `on` or `off`. Example: `.huntbot all off`")
            return

        worker_spec = " ".join(parts[:-1])
        target_numbers = _parse_worker_args(worker_spec)
        if target_numbers is None:
            await ctx.send(f"❌ Invalid worker number in: `{worker_spec}`")
            return
        if not target_numbers:
            await ctx.send("❌ No valid worker numbers provided.")
            return

        changed = []
        for wn in target_numbers:
            target_ws = manager.get_worker(wn)
            if target_ws is None:
                await ctx.send(f"❌ Worker {wn} does not exist.")
                continue
            if toggle == "on":
                target_ws.huntbot_enabled = True
            else:
                if target_ws.GhoStyHbAlrActiveVar:
                    target_ws.GhoStyHbAlrActiveVar = False
                target_ws.huntbot_enabled = False
            changed.append(f"Worker #{wn} ({target_ws.username})")

        state_str = "🟢 ON" if toggle == "on" else "🔴 OFF"
        if changed:
            await ctx.send(
                f"🎯 Auto-HuntBot set to **{state_str}** for: " + ", ".join(changed)
            )

    @bot.command()
    async def pause(ctx, *, args: str = None):
        if ctx.author.id != bot.user.id:
            return

        if args is None:
            await ctx.send(
                "❌ Usage: `.pause <N/all> <time>`\n"
                "Example: `.pause 1 30m` / `.pause all 1h` / `.pause 2, 3 1h30m`\n"
                "Minimum pause time is **15 minutes**."
            )
            return

        parts = args.split()
        if len(parts) < 2:
            await ctx.send(
                "❌ Usage: `.pause <N/all> <time>`\n"
                "Example: `.pause 1 30m` / `.pause all 1h`"
            )
            return

        time_str = parts[-1].lower()
        worker_spec = " ".join(parts[:-1])

        secs = _parse_pause_time(time_str)
        if secs is None:
            await ctx.send("❌ Invalid time format. Examples: `30m`, `1h`, `1h30m`")
            return

        if secs < 900:
            await ctx.send("❌ Minimum pause time is **15 minutes**. Example: `.pause all 15m`")
            return

        target_numbers = _parse_worker_args(worker_spec)
        if target_numbers is None:
            await ctx.send(f"❌ Invalid worker number in: `{worker_spec}`")
            return
        if not target_numbers:
            await ctx.send("❌ No valid worker numbers provided.")
            return

        pause_end = datetime.now() + timedelta(seconds=secs)
        applied = []
        skipped = []

        for wn in target_numbers:
            target_ws = manager.get_worker(wn)
            if target_ws is None:
                skipped.append(f"Worker #{wn}: does not exist")
                continue
            if not target_ws.running or not target_ws.has_started:
                skipped.append(f"Worker #{wn} ({target_ws.username}): not running")
                continue
            if target_ws.paused:
                skipped.append(
                    f"Worker #{wn} ({target_ws.username}): already paused until "
                    f"{target_ws.pause_end_time.strftime('%H:%M:%S')}"
                )
                continue
            target_ws.paused = True
            target_ws.pause_end_time = pause_end
            applied.append(f"Worker #{wn} ({target_ws.username})")
            log_worker_event(wn, f"⏸️ Paused via main controller for {_format_duration(secs)}", "INFO")

        lines = []
        if applied:
            extra = ""
            if secs > 86400:
                extra = f" ⚠️ Long pause ({_format_duration(secs)})."
            lines.append(
                f"⏸️ **Paused for {_format_duration(secs)}** — auto-resumes at "
                f"**{pause_end.strftime('%d-%b-%Y %I:%M:%S %p')}**{extra}\n"
                f"Applied to: " + ", ".join(applied)
            )
        if skipped:
            lines.append("\n⚠️ **Skipped:**\n" + "\n".join(f"> {s}" for s in skipped))
        if lines:
            await ctx.send("\n".join(lines))

    @bot.command()
    async def resume(ctx, *, args: str = None):
        if ctx.author.id != bot.user.id:
            return

        if args is None:
            await ctx.send(
                "❌ Usage: `.resume <N/all>`\n"
                "Example: `.resume 1` / `.resume all`"
            )
            return

        target_numbers = _parse_worker_args(args)
        if target_numbers is None:
            await ctx.send(f"❌ Invalid worker number in: `{args}`")
            return
        if not target_numbers:
            await ctx.send("❌ No valid worker numbers provided.")
            return

        resumed = []
        skipped = []

        for wn in target_numbers:
            target_ws = manager.get_worker(wn)
            if target_ws is None:
                skipped.append(f"Worker #{wn}: does not exist")
                continue
            if not target_ws.paused:
                skipped.append(f"Worker #{wn} ({target_ws.username}): not paused")
                continue
            target_ws.paused = False
            target_ws.pause_end_time = None
            target_ws.farming_start_time = datetime.now()
            target_ws.last_mode_change_time = datetime.now()
            if target_ws.lifetime_cycle_start_time is not None:
                target_ws.lifetime_cycle_start_time = datetime.now()
            resumed.append(f"Worker #{wn} ({target_ws.username})")
            log_worker_event(wn, "▶️ Resumed via main controller", "INFO")

        lines = []
        if resumed:
            lines.append("▶️ **Resumed:** " + ", ".join(resumed))
        if skipped:
            lines.append("⚠️ **Skipped:** " + " | ".join(skipped))
        if lines:
            await ctx.send("\n".join(lines))

    @bot.command()
    async def profit(ctx):
        if ctx.author.id != bot.user.id:
            return

        all_ws = manager.get_all_workers()
        if not all_ws:
            await ctx.send("⚫ No workers registered.")
            return

        await ctx.send("💰 Fetching live zoo data for all active workers...")

        for wn, target_ws in sorted(all_ws.items()):
            if (
                target_ws.has_started
                and target_ws.zoo_channel
                and not target_ws.sleep_mode
                and not target_ws.paused
                and target_ws.bot
                and target_ws.bot.loop
                and target_ws.bot.loop.is_running()
            ):
                try:
                    future = made_by_ghosty.run_coroutine_threadsafe(
                        _fetch_zoo_for_main_status(target_ws),
                        target_ws.bot.loop,
                    )
                    await made_by_ghosty.wrap_future(future)
                except Exception as e:
                    log_worker_event("CTRL", f"Profit zoo fetch failed for W#{wn}: {e}", "WARNING")

        lines = ["💰 **GhoSty OwO Profit Summary:**\n"]
        total_profit = 0

        for wn, target_ws in sorted(all_ws.items()):
            if not target_ws.has_started:
                lines.append(f"> Worker {wn} ({target_ws.username}): ⚫ Not started")
                continue

            profit = target_ws.current_cash - target_ws.initial_cash
            total_profit += profit

            if target_ws.sleep_mode:
                state_tag = " 😴"
            elif target_ws.paused:
                state_tag = " ⏸️"
            elif not target_ws.running:
                state_tag = " 🛑"
            else:
                state_tag = ""

            profit_sign = "+" if profit >= 0 else ""
            lines.append(
                f"> Worker {wn} ({target_ws.username}){state_tag}: "
                f"**{profit_sign}{format_value(profit)}** "
                f"({format_value(target_ws.initial_cash)} → {format_value(target_ws.current_cash)})"
            )

        total_sign = "+" if total_profit >= 0 else ""
        lines.append(
            f"\n> 💵 **Total Cash Profit Across All Workers: {total_sign}{format_value(total_profit)}**"
        )

        await ctx.send("\n".join(lines))

    @bot.command()
    async def say(ctx, *, text: str = None):
        if ctx.author.id != bot.user.id:
            return

        if text is None or not text.strip():
            await ctx.send(
                "❌ Usage: `.say <text>`\n"
                "Example: `.say Hello everyone!`\n"
                "Makes all workers send the text in their designated channels."
            )
            return

        text = text.strip()
        all_ws = manager.get_all_workers()
        if not all_ws:
            await ctx.send("⚫ No workers registered.")
            return

        sent = []
        skipped = []

        for wn, target_ws in sorted(all_ws.items()):
            ch_id = target_ws.auto_start_channel_id

            if ch_id is None:
                skipped.append(f"Worker #{wn} ({target_ws.username}): no channel assigned in channels.txt")
                continue

            target_bot = target_ws.bot
            if not (target_bot and target_bot.loop and target_bot.loop.is_running()):
                skipped.append(f"Worker #{wn} ({target_ws.username}): bot not connected")
                continue

            channel = target_bot.get_channel(ch_id)
            if not channel:
                skipped.append(f"Worker #{wn} ({target_ws.username}): cannot see channel {ch_id}")
                continue

            try:
                made_by_ghosty.run_coroutine_threadsafe(
                    channel.send(text),
                    target_bot.loop,
                )
                sent.append(f"Worker #{wn} ({target_ws.username})")
                log_worker_event(wn, f".say dispatched to channel {ch_id}", "INFO")
            except Exception as e:
                skipped.append(f"Worker #{wn} ({target_ws.username}): send error — {e}")
                log_worker_event(wn, f".say error: {e}", "WARNING")

        reply_lines = []
        if sent:
            reply_lines.append(f"💬 **Sent to {len(sent)} worker channel(s):** " + ", ".join(sent))
        if skipped:
            reply_lines.append("⚠️ **Skipped:**\n" + "\n".join(f"> {s}" for s in skipped))
        if not sent and not skipped:
            reply_lines.append("⚫ No workers had designated channels to send to.")

        await ctx.send("\n".join(reply_lines))

    @bot.command()
    async def mail(ctx, *, args: str = None):
        if ctx.author.id != bot.user.id:
            return

        if args is None:
            await ctx.send("❌ Usage: `.mail all` or `.mail 1, 2`")
            return

        target_numbers = _parse_worker_args(args)
        if target_numbers is None:
            await ctx.send(f"❌ Invalid worker number in: `{args}`")
            return
        if not target_numbers:
            await ctx.send("❌ No valid worker numbers provided.")
            return

        started = []
        skipped = []

        for wn in target_numbers:
            target_ws = manager.get_worker(wn)
            if target_ws is None:
                skipped.append(f"Worker #{wn}: does not exist")
                continue
            
            target_bot = target_ws.bot
            if not (target_bot and target_bot.loop and target_bot.loop.is_running()):
                skipped.append(f"Worker #{wn} ({target_ws.username}): bot not connected")
                continue
                
            ch_id = target_ws.auto_start_channel_id
            if ch_id is None:
                skipped.append(f"Worker #{wn} ({target_ws.username}): no channel assigned in channels.txt")
                continue
                
            target_channel = target_bot.get_channel(ch_id)
            if not target_channel:
                skipped.append(f"Worker #{wn} ({target_ws.username}): cannot see channel {ch_id}")
                continue

            if target_ws.last_mail_claim:
                time_since = (datetime.now() - target_ws.last_mail_claim).total_seconds()
                if time_since < 300:
                    skipped.append(f"Worker #{wn} ({target_ws.username}): Cooldown active ({int(300 - time_since)}s remaining)")
                    continue

            if getattr(target_ws, "is_mail_claiming", False):
                skipped.append(f"Worker #{wn} ({target_ws.username}): already checking mail")
                continue

            target_ws.last_mail_claim = datetime.now()
            target_ws.is_mail_claiming = True
            started.append(f"Worker #{wn} ({target_ws.username})")
            log_worker_event(wn, ".mail dispatched via main controller", "INFO")
            
            pseudo_ctx = PseudoCtx(target_channel, target_bot)
            from core.mailmodule import execute_mail_claim
            target_bot.loop.create_task(execute_mail_claim(pseudo_ctx, target_ws, target_bot))

        reply_lines = []
        if started:
            reply_lines.append("📩 **Started checking mail for:** " + ", ".join(started))
        if skipped:
            reply_lines.append("⚠️ **Skipped:**\n" + "\n".join(f"> {s}" for s in skipped))

        await ctx.send("\n".join(reply_lines))


def _parse_worker_args(args_str):
    raw = args_str.replace(",", " ").split()

    if "all" in [r.lower() for r in raw]:
        return list(manager.get_all_workers().keys())

    target_numbers = []
    for r in raw:
        r = r.strip()
        if not r:
            continue
        try:
            target_numbers.append(int(r))
        except ValueError:
            return None

    return target_numbers