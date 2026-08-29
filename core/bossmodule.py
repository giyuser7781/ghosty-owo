"""
This code is only made for educational and practice purposes. 
Author and Async Development are not responsible for misuse.

GhoSty OwO V4 Alpha Build
Stable Alpha Build Version: 280826.4.1.0

GitHub: https://github.com/WannaBeGhoSt
Discord: https://discord.gg/asMJGgDA7u
"""

import asyncio as made_by_ghosty
import random as ghostyjija
from datetime import datetime, timedelta
import math

from .ui import log_worker_event

def calculate_boss_delay():
    min_delay = 17 * 60  
    max_delay = 31 * 60 

    u = max(0.0001, ghostyjija.random())
    v = ghostyjija.random() 
    z = math.sqrt(-2.0 * math.log(u)) * math.cos(2.0 * math.pi * v)
    
    skewed_val = (z * 0.2) + 0.4 

    t = max(0.0, min(1.0, skewed_val))

    p0, p1, p2, p3 = 0.0, 0.2, 0.8, 1.0
    bezier_t = (1-t)**3 * p0 + 3*((1-t)**2)*t * p1 + 3*(1-t)*(t**2) * p2 + t**3 * p3

    delay_range = max_delay - min_delay
    final_delay_seconds = min_delay + (bezier_t * delay_range)
    
    return final_delay_seconds

async def _monitor_boss_fights(ctx, ws, bot):
    await made_by_ghosty.sleep(5)
    log_worker_event(ws.worker_number, "⚔️ Boss module initialized.", "INFO")
    
    first_run = True
    
    while ws.running:
        if getattr(ws, "boss_tickets", 0) <= 0:
            log_worker_event(ws.worker_number, "🚫 Out of boss tickets. Boss module sleeping until restart.", "WARNING")
            break
            
        if first_run:

            delay = ghostyjija.uniform(120.0, 300.0)
            first_run = False
        else:
            delay = calculate_boss_delay()
            
        ws.next_boss_fight_time = datetime.now() + timedelta(seconds=delay)
        log_worker_event(ws.worker_number, f"⏳ Next boss check scheduled in {int(delay//60)}m {int(delay%60)}s (at {ws.next_boss_fight_time.strftime('%H:%M:%S')}).", "DEBUG")
        
        slept = 0
        while slept < delay:
            if not ws.running:
                return
            await made_by_ghosty.sleep(5)
            slept += 5
            
        if not ws.running or getattr(ws, "boss_tickets", 0) <= 0:
            break
            
        await execute_boss_fight(ctx, ws, bot)

async def execute_boss_fight(ctx, ws, bot):
    guild_id = 420104212895105044
    primary_channel_id = 1412234015578132511
    backup_channels = [1412269279398596728, 1412269382599704691]
    owo_bot_id = 408785106942164992
    
    guild = bot.get_guild(guild_id)
    if not guild:
        log_worker_event(ws.worker_number, f"⚠️ Not in target server ({guild_id}). Skipping boss fight.", "DEBUG")
        return
        
    channel = bot.get_channel(primary_channel_id)
    if not channel:
        for backup in backup_channels:
            channel = bot.get_channel(backup)
            if channel:
                break
                
    if not channel:
        log_worker_event(ws.worker_number, "⚠️ Cannot access any boss channels. Skipping boss fight.", "DEBUG")
        return

    log_worker_event(ws.worker_number, "⚔️ Attempting to find a Guild Boss...", "INFO")

    ws.is_boss_fighting = True
    
    try:
        import discord
        from discord.interactions import _wrapped_interaction
        from discord.utils import _generate_nonce
        from discord.enums import InteractionType

        def find_fight_button(data, targets):
            if isinstance(data, dict):
                lbl = str(data.get('label', '')).lower().strip()
                cid = str(data.get('custom_id', '')).lower().strip()
                if data.get('type') == 2 and ('fight' in lbl or 'fight' in cid):
                    if not data.get('disabled', False):
                        targets.append(data)
                    else:
                        log_worker_event(ws.worker_number, "🔍 Found 'Fight' button in raw JSON, but it is disabled.", "DEBUG")
                for v in data.values():
                    find_fight_button(v, targets)
            elif isinstance(data, list):
                for item in data:
                    find_fight_button(item, targets)

        target_message = None
        target_button = None
        
        async for msg in channel.history(limit=40):
            if msg.author.id == owo_bot_id:
                try:
                    route = discord.http.Route("GET", "/channels/{channel_id}/messages?limit=1&around={message_id}", channel_id=channel.id, message_id=msg.id)
                    raw_data = await bot.http.request(route)
                    if isinstance(raw_data, list) and len(raw_data) > 0:
                        raw_data = raw_data[0]
                    
                    if 'components' in raw_data:
                        raw_str = str(raw_data).lower()
                        if "boss" in raw_str or "fight" in raw_str:
                            targets = []
                            find_fight_button(raw_data.get('components', []), targets)
                            if targets:
                                target_message = msg
                                target_button = targets[0]
                                break
                except Exception as e:
                    pass
                
        if not target_button:
            log_worker_event(ws.worker_number, "❌ No active Guild Boss fights found.", "INFO")
            ws.is_boss_fighting = False
            return
            
        log_worker_event(ws.worker_number, "💥 Found Boss! Clicking Fight...", "SUCCESS")
        await _wrapped_interaction(
            target_message._state,
            _generate_nonce(),
            InteractionType.component,
            None,
            channel,
            target_button,
            message=target_message
        )
        
        def check(i):
            if i.user.id == bot.user.id and i.channel.id == channel.id:
                return True
            return False

        try:
            def check_msg(m):
                if m.channel.id == channel.id and getattr(m, 'flags', None) and m.flags.ephemeral:
                    return True
                return False
                
            resp = await bot.wait_for('message', check=check_msg, timeout=5.0)
            content = str(resp.content).lower()
            if not content and resp.embeds:
                for embed in resp.embeds:
                    if embed.description:
                        content += embed.description.lower()
                    if embed.title:
                        content += embed.title.lower()

            if "you don't have any boss tickets" in content:
                log_worker_event(ws.worker_number, "🚫 Out of boss tickets (Discord response).", "WARNING")
                ws.boss_tickets = 0
            elif "you already fought this boss" in content:
                log_worker_event(ws.worker_number, "⚠️ Already fought this boss. Skipping.", "DEBUG")
            else:
                log_worker_event(ws.worker_number, "✅ Boss fight interaction complete.", "SUCCESS")
                
        except made_by_ghosty.TimeoutError:
            log_worker_event(ws.worker_number, "✅ Boss fight clicked (no error messages received).", "SUCCESS")
            
    except Exception as e:
        log_worker_event(ws.worker_number, f"⚠️ Error executing boss fight: {e}", "WARNING")
    finally:
        ws.is_boss_fighting = False
