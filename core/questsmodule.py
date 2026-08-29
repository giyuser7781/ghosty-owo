"""
This code is only made for educational and practice purposes. 
Author and Async Development are not responsible for misuse.

GhoSty OwO V4 Alpha Build
Stable Alpha Build Version: 280826.4.1.0

GitHub: https://github.com/WannaBeGhoSt
Discord: https://discord.gg/asMJGgDA7u
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
import random

from core.ui import log_worker_event
from core.heart import WorkerManager, manager

QUESTS_FILE = "ghostyworkerquests.json"

def LoadGhoStysQuestsData(ws):
    if not os.path.exists(QUESTS_FILE):
        return {}
    try:
        with open(QUESTS_FILE, "r") as f:
            data = json.load(f)
        return data.get(str(ws.worker_number), {})
    except Exception as e:
        log_worker_event(ws.worker_number, f"Failed to load quests data: {e}", "WARNING")
        return {}

def SaveQuestsDataGhoStys(ws, worker_data):
    try:
        data = {}
        if os.path.exists(QUESTS_FILE):
            with open(QUESTS_FILE, "r") as f:
                try:
                    data = json.load(f)
                except:
                    pass
        data[str(ws.worker_number)] = worker_data
        with open(QUESTS_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        log_worker_event(ws.worker_number, f"Failed to save quests data: {e}", "WARNING")

def extract_text_from_node(node):
    text = ""
    if isinstance(node, dict):
        if "content" in node and isinstance(node["content"], str):
            text += node["content"] + "\n"
        for v in node.values():
            text += extract_text_from_node(v)
    elif isinstance(node, list):
        for item in node:
            text += extract_text_from_node(item)
    return text

def find_button_by_label(data, label, targets):
    if isinstance(data, dict):
        if data.get('type') == 2 and str(data.get('label', '')).lower() == label.lower():
            targets.append(data)
        elif data.get('type') == 2 and 'components' in data:
            pass
        if data.get('type') == 2:
            inner_text = extract_text_from_node(data).lower()
            if label.lower() in inner_text and data not in targets:
                targets.append(data)
                
        for v in data.values():
            find_button_by_label(v, label, targets)
    elif isinstance(data, list):
        for item in data:
            find_button_by_label(item, label, targets)

async def fetch_and_parse_quests(ctx, ws, bot):
    import discord
    from discord.interactions import _wrapped_interaction
    from discord.utils import _generate_nonce
    from discord.enums import InteractionType

    await asyncio.sleep(3.6)
    await ctx.send("owo q")
    await asyncio.sleep(4)

    bs_msg = None
    for _ in range(3):
        messages = [msg async for msg in ctx.channel.history(limit=20)]
        for msg in messages:
            if msg.author.id == 408785106942164992:
                try:
                    route = discord.http.Route("GET", "/channels/{channel_id}/messages?limit=1&around={message_id}", channel_id=ctx.channel.id, message_id=msg.id)
                    raw_data = await bot.http.request(route)
                    if isinstance(raw_data, list) and len(raw_data) > 0:
                        raw_data = raw_data[0]
                    if 'components' in raw_data:
                        raw_str = str(raw_data).lower()
                        if "quest log" in raw_str or "quests" in raw_str:
                            bs_msg = msg
                            break
                except:
                    pass
            if bs_msg:
                break
        if bs_msg:
            break
        await asyncio.sleep(2)
    
    if not bs_msg:
        log_worker_event(ws.worker_number, "Could not find 'owo q' response.", "DEBUG")
        return

    route = discord.http.Route("GET", "/channels/{channel_id}/messages?limit=1&around={message_id}", channel_id=ctx.channel.id, message_id=bs_msg.id)
    raw_data = await bot.http.request(route)
    if isinstance(raw_data, list) and len(raw_data) > 0:
        raw_data = raw_data[0]
        
    raw_str = str(raw_data).lower()
    ws.all_quests_finished = False
    if "you finished all of your quests" in raw_str:
        ws.all_quests_finished = True
        sleep_until = datetime.now() + timedelta(hours=12)
        import re
        match = re.search(r'<t:(\d+)', raw_str)
        if match:
            try:
                timestamp = int(match.group(1))
                sleep_until = datetime.fromtimestamp(timestamp) + timedelta(minutes=1)
            except:
                pass
                
        ws.next_quest_check_time = sleep_until
        log_worker_event(ws.worker_number, f"All quests finished! Sleeping quests until {sleep_until.strftime('%Y-%m-%d %H:%M:%S')}", "SUCCESS")
        active_quests = {}
        SaveQuestsDataGhoStys(ws, active_quests)
        return active_quests
    full_text = extract_text_from_node(raw_data.get('components', []))
    
    active_quests = {}
    lines = full_text.split('\n')
    
    current_quest = None
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if "battle with a friend" in line_lower:
            current_quest = "battle_with_friend"
            for j in range(i+1, min(i+5, len(lines))):
                if "/" in lines[j] and any(c.isdigit() for c in lines[j]):
                    try:
                        parts = lines[j].split("/")
                        current = int(''.join(filter(str.isdigit, parts[0])))
                        total = int(''.join(filter(str.isdigit, parts[1])))
                        active_quests[current_quest] = {"current": current, "total": total}
                    except:
                        pass
                    break
        elif "action from a friend" in line_lower:
            current_quest = "action_from_friend"
            for j in range(i+1, min(i+5, len(lines))):
                if "/" in lines[j] and any(c.isdigit() for c in lines[j]):
                    try:
                        parts = lines[j].split("/")
                        current = int(''.join(filter(str.isdigit, parts[0])))
                        total = int(''.join(filter(str.isdigit, parts[1])))
                        active_quests[current_quest] = {"current": current, "total": total}
                    except:
                        pass
                    break
        elif "send an action to a friend" in line_lower or "use an action command" in line_lower:
            current_quest = "send_action"
            for j in range(i+1, min(i+5, len(lines))):
                if "/" in lines[j] and any(c.isdigit() for c in lines[j]):
                    try:
                        parts = lines[j].split("/")
                        current = int(''.join(filter(str.isdigit, parts[0])))
                        total = int(''.join(filter(str.isdigit, parts[1])))
                        active_quests[current_quest] = {"current": current, "total": total}
                    except:
                        pass
                    break
        elif "receive cookies" in line_lower or "receive a cookie" in line_lower:
            current_quest = "receive_cookie"
            for j in range(i+1, min(i+5, len(lines))):
                if "/" in lines[j] and any(c.isdigit() for c in lines[j]):
                    try:
                        parts = lines[j].split("/")
                        current = int(''.join(filter(str.isdigit, parts[0])))
                        total = int(''.join(filter(str.isdigit, parts[1])))
                        active_quests[current_quest] = {"current": current, "total": total}
                    except:
                        pass
                    break
        elif "receive curses" in line_lower or "curse you" in line_lower:
            current_quest = "receive_curses"
            for j in range(i+1, min(i+5, len(lines))):
                if "/" in lines[j] and any(c.isdigit() for c in lines[j]):
                    try:
                        parts = lines[j].split("/")
                        current = int(''.join(filter(str.isdigit, parts[0])))
                        total = int(''.join(filter(str.isdigit, parts[1])))
                        active_quests[current_quest] = {"current": current, "total": total}
                    except:
                        pass
                    break
        elif "receive prayers" in line_lower or "pray to you" in line_lower:
            current_quest = "receive_prayers"
            for j in range(i+1, min(i+5, len(lines))):
                if "/" in lines[j] and any(c.isdigit() for c in lines[j]):
                    try:
                        parts = lines[j].split("/")
                        current = int(''.join(filter(str.isdigit, parts[0])))
                        total = int(''.join(filter(str.isdigit, parts[1])))
                        active_quests[current_quest] = {"current": current, "total": total}
                    except:
                        pass
                    break
        elif "say 'owo'" in line_lower or "say owo" in line_lower:
            current_quest = "say_owo"
            for j in range(i+1, min(i+5, len(lines))):
                if "/" in lines[j] and any(c.isdigit() for c in lines[j]):
                    try:
                        parts = lines[j].split("/")
                        current = int(''.join(filter(str.isdigit, parts[0])))
                        total = int(''.join(filter(str.isdigit, parts[1])))
                        active_quests[current_quest] = {"current": current, "total": total}
                    except:
                        pass
                    break
        elif "gamble your cowoncy" in line_lower or "gamble" in line_lower:
            current_quest = "gamble_cowoncy"
            for j in range(i+1, min(i+5, len(lines))):
                if "/" in lines[j] and any(c.isdigit() for c in lines[j]):
                    try:
                        parts = lines[j].split("/")
                        current = int(''.join(filter(str.isdigit, parts[0])))
                        total = int(''.join(filter(str.isdigit, parts[1])))
                        active_quests[current_quest] = {"current": current, "total": total}
                    except:
                        pass
                    break

    has_completed = "CLAIMED" in full_text
    for quest, data in active_quests.items():
        if data["current"] >= data["total"]:
            has_completed = True
            
    claim_targets = []
    find_button_by_label(raw_data.get('components', []), "Claim", claim_targets)
    
    if claim_targets:
        claim_btn = claim_targets[0]
        if not claim_btn.get("disabled", False):
            log_worker_event(ws.worker_number, "Clicking Claim Quests button!", "SUCCESS")
            try:
                ws.error_claiming = False
                await _wrapped_interaction(
                    bs_msg._state,
                    _generate_nonce(),
                    InteractionType.component,
                    None,
                    bs_msg.channel,
                    claim_btn,
                    message=bs_msg
                )
                await asyncio.sleep(2)
                return await fetch_and_parse_quests(ctx, ws, bot)
            except Exception as e:
                log_worker_event(ws.worker_number, f"Error clicking Claim: {e}", "WARNING")
                ws.error_claiming = True

    SaveQuestsDataGhoStys(ws, active_quests)
    log_worker_event(ws.worker_number, f"Fetched quests: {active_quests}", "DEBUG")
    return active_quests

async def check_and_handle_quests(ctx, ws, bot):
    if manager.total_workers <= 1:
        return

    if not hasattr(ws, 'quests_enabled'):
        ws.quests_enabled = True
        ws.next_quest_check_time = datetime.now()
        ws.next_friend_battle_time = datetime.now()
        ws.friend_battle_helper_id = None
        
    if not ws.quests_enabled:
        return

    if datetime.now() >= getattr(ws, 'next_quest_check_time', datetime.min):
        active_quests = await fetch_and_parse_quests(ctx, ws, bot)
        if getattr(ws, 'error_claiming', False):
            ws.next_quest_check_time = datetime.now() + timedelta(minutes=2)
            ws.error_claiming = False
            log_worker_event(ws.worker_number, "Claiming failed, scheduled retry in 2 minutes.", "DEBUG")
        elif not getattr(ws, 'all_quests_finished', False):
            ws.next_quest_check_time = datetime.now() + timedelta(minutes=20)
    else:
        active_quests = LoadGhoStysQuestsData(ws)

    if not active_quests:
        return

    if "battle_with_friend" in active_quests:
        qdata = active_quests["battle_with_friend"]
        if qdata["current"] < qdata["total"]:
            if datetime.now() >= ws.next_friend_battle_time:
                if getattr(ws, 'busy_with_quest', False):
               
                    return
                    
                helper = manager.try_claim_friend_battle_helper(ws.worker_number)
                        
                if helper and helper.bot and helper.bot.user:
                    log_worker_event(ws.worker_number, f"Executing friend battle with {helper.username} ({helper.bot.user.id})", "INFO")
                    
                    ws.friend_battle_helper_id = helper.worker_number
                  
                    
                    helper.paused = True
                    helper.pause_end_time = datetime.now() + timedelta(minutes=2)
                    ws.paused = True
                    ws.pause_end_time = datetime.now() + timedelta(minutes=2)
                    
                    await asyncio.sleep(2)
                    await ctx.send(f"owo b <@{helper.bot.user.id}>")
                    
                    await asyncio.sleep(2.5)
                    
                    helper_channel = helper.bot.get_channel(ctx.channel.id)
                    if helper_channel:
                        asyncio.run_coroutine_threadsafe(helper_channel.send("owo ab"), helper.bot.loop)
                        log_worker_event(ws.worker_number, f"Commanded helper to send 'owo ab'", "DEBUG")
                    else:
                        log_worker_event(ws.worker_number, "Helper cannot see this channel to accept the battle!", "WARNING")
                    
                    await asyncio.sleep(15)
                    
                    helper.paused = False
                    helper.pause_end_time = None
                    helper.busy_with_quest = False
                    
                    ws.paused = False
                    ws.pause_end_time = None
                    ws.busy_with_quest = False
                    ws.friend_battle_helper_id = None
                    
                    qdata["current"] += 1
                    SaveQuestsDataGhoStys(ws, active_quests)
                    
                    log_worker_event(ws.worker_number, f"Friend battle done! Progress: {qdata['current']}/{qdata['total']}", "SUCCESS")
                    
                    if qdata["current"] >= qdata["total"]:
                        await fetch_and_parse_quests(ctx, ws, bot)
                    else:
                        delay_mins = random.randint(5, 15)
                        ws.next_friend_battle_time = datetime.now() + timedelta(minutes=delay_mins)
                        log_worker_event(ws.worker_number, f"Next friend battle scheduled in {delay_mins} minutes.", "DEBUG")
                else:
                    log_worker_event(ws.worker_number, "No idle helper worker available for battle quest right now. Will retry later.", "DEBUG")
                    ws.next_friend_battle_time = datetime.now() + timedelta(minutes=2)

    if "action_from_friend" in active_quests:
        qdata = active_quests["action_from_friend"]
        if qdata["current"] < qdata["total"]:
            if not hasattr(ws, 'next_action_quest_time'):
                ws.next_action_quest_time = datetime.now()
                
            if datetime.now() >= ws.next_action_quest_time:
                needed = qdata["total"] - qdata["current"]
                helpers = manager.get_action_helpers(ws.worker_number, needed)
                
                if helpers:
                    log_worker_event(ws.worker_number, f"Found {len(helpers)} helpers for action quest.", "INFO")
                    actions = ["punch", "slap", "pat", "hug", "kiss", "cuddle"]
                    
                    for helper in helpers:
                        action = random.choice(actions)
                        helper_channel = getattr(helper, 'zoo_channel', None)
                        if not helper_channel:
                            helper_channel = helper.bot.get_channel(getattr(helper, 'active_channel_id', None))
                            
                        if helper_channel:
                            asyncio.run_coroutine_threadsafe(
                                helper_channel.send(f"owo {action} <@{ws.bot.user.id}>"),
                                helper.bot.loop
                            )
                            qdata["current"] += 1
                        else:
                            log_worker_event(ws.worker_number, "Helper has no active channel to send action.", "DEBUG")
                            
                    SaveQuestsDataGhoStys(ws, active_quests)
                    log_worker_event(ws.worker_number, f"Action quest progress: {qdata['current']}/{qdata['total']}", "SUCCESS")
                    
                    if qdata["current"] >= qdata["total"]:
                        asyncio.create_task(fetch_and_parse_quests(ctx, ws, bot))
                    else:
                        delay_mins = random.randint(3, 8)
                        ws.next_action_quest_time = datetime.now() + timedelta(minutes=delay_mins)
                        log_worker_event(ws.worker_number, f"Next action quest retry in {delay_mins} mins.", "DEBUG")
                else:
                    log_worker_event(ws.worker_number, "No helpers available for action quest right now. Will retry later.", "DEBUG")
                    ws.next_action_quest_time = datetime.now() + timedelta(minutes=2)

    if "receive_cookie" in active_quests:
        qdata = active_quests["receive_cookie"]
        if qdata["current"] < qdata["total"]:
            if not hasattr(ws, 'next_cookie_quest_time'):
                ws.next_cookie_quest_time = datetime.now()
                
            if datetime.now() >= ws.next_cookie_quest_time:
                needed = qdata["total"] - qdata["current"]
                helpers = manager.get_cookie_helpers(ws.worker_number, needed)
                
                if helpers:
                    log_worker_event(ws.worker_number, f"Found {len(helpers)} helpers for cookie quest.", "INFO")
                    
                    for helper in helpers:
                        helper_channel = getattr(helper, 'zoo_channel', None)
                        if not helper_channel:
                            helper_channel = helper.bot.get_channel(getattr(helper, 'active_channel_id', None))
                            
                        if helper_channel:
                            asyncio.run_coroutine_threadsafe(
                                helper_channel.send(f"owo rep <@{ws.bot.user.id}>"),
                                helper.bot.loop
                            )
                            qdata["current"] += 1
                        else:
                            log_worker_event(ws.worker_number, "Helper has no active channel to send cookie.", "DEBUG")
                            
                    SaveQuestsDataGhoStys(ws, active_quests)
                    log_worker_event(ws.worker_number, f"Cookie quest progress (optimistic): {qdata['current']}/{qdata['total']}", "SUCCESS")
                    
                    if qdata["current"] >= qdata["total"]:
                        asyncio.get_event_loop().call_later(5.0, lambda: asyncio.create_task(fetch_and_parse_quests(ctx, ws, bot)))
                    else:
                        delay_mins = random.randint(3, 8)
                        ws.next_cookie_quest_time = datetime.now() + timedelta(minutes=delay_mins)
                        log_worker_event(ws.worker_number, f"Next cookie quest retry in {delay_mins} mins.", "DEBUG")
                else:
                    log_worker_event(ws.worker_number, "No helpers available for cookie quest right now. Will retry later.", "DEBUG")
                    ws.next_cookie_quest_time = datetime.now() + timedelta(minutes=5)

    if "receive_curses" in active_quests:
        qdata = active_quests["receive_curses"]
        if qdata["current"] < qdata["total"]:
            if not hasattr(ws, 'next_curse_quest_time'):
                ws.next_curse_quest_time = datetime.now()
                
            if datetime.now() >= ws.next_curse_quest_time:
                needed = qdata["total"] - qdata["current"]
                helpers = manager.get_pray_curse_helpers(ws.worker_number, needed)
                
                if helpers:
                    log_worker_event(ws.worker_number, f"Found {len(helpers)} helpers for curse quest.", "INFO")
                    
                    for helper in helpers:
                        helper_channel = getattr(helper, 'zoo_channel', None)
                        if not helper_channel:
                            helper_channel = helper.bot.get_channel(getattr(helper, 'active_channel_id', None))
                            
                        if helper_channel:
                            asyncio.run_coroutine_threadsafe(
                                helper_channel.send(f"owo curse <@{ws.bot.user.id}>"),
                                helper.bot.loop
                            )
                            qdata["current"] += 1
                        else:
                            log_worker_event(ws.worker_number, "Helper has no active channel to send curse.", "DEBUG")
                            
                    SaveQuestsDataGhoStys(ws, active_quests)
                    log_worker_event(ws.worker_number, f"Curse quest progress: {qdata['current']}/{qdata['total']}", "SUCCESS")
                    
                    if qdata["current"] >= qdata["total"]:
                        asyncio.get_event_loop().call_later(5.0, lambda: asyncio.create_task(fetch_and_parse_quests(ctx, ws, bot)))
                    else:
                        delay_mins = 5
                        ws.next_curse_quest_time = datetime.now() + timedelta(minutes=delay_mins, seconds=15)
                        log_worker_event(ws.worker_number, f"Next curse quest retry in {delay_mins} mins.", "DEBUG")
                else:
                    log_worker_event(ws.worker_number, "No helpers available for curse quest right now. Will retry later.", "DEBUG")
                    ws.next_curse_quest_time = datetime.now() + timedelta(minutes=2)

    if "receive_prayers" in active_quests:
        qdata = active_quests["receive_prayers"]
        if qdata["current"] < qdata["total"]:
            if not hasattr(ws, 'next_pray_quest_time'):
                ws.next_pray_quest_time = datetime.now()
                
            if datetime.now() >= ws.next_pray_quest_time:
                needed = qdata["total"] - qdata["current"]
                helpers = manager.get_pray_curse_helpers(ws.worker_number, needed)
                
                if helpers:
                    log_worker_event(ws.worker_number, f"Found {len(helpers)} helpers for pray quest.", "INFO")
                    
                    for helper in helpers:
                        helper_channel = getattr(helper, 'zoo_channel', None)
                        if not helper_channel:
                            helper_channel = helper.bot.get_channel(getattr(helper, 'active_channel_id', None))
                            
                        if helper_channel:
                            asyncio.run_coroutine_threadsafe(
                                helper_channel.send(f"owo pray <@{ws.bot.user.id}>"),
                                helper.bot.loop
                            )
                            qdata["current"] += 1
                        else:
                            log_worker_event(ws.worker_number, "Helper has no active channel to send pray.", "DEBUG")
                            
                    SaveQuestsDataGhoStys(ws, active_quests)
                    log_worker_event(ws.worker_number, f"Pray quest progress: {qdata['current']}/{qdata['total']}", "SUCCESS")
                    
                    if qdata["current"] >= qdata["total"]:
                        asyncio.get_event_loop().call_later(5.0, lambda: asyncio.create_task(fetch_and_parse_quests(ctx, ws, bot)))
                    else:
                        delay_mins = 5
                        ws.next_pray_quest_time = datetime.now() + timedelta(minutes=delay_mins, seconds=15)
                        log_worker_event(ws.worker_number, f"Next pray quest retry in {delay_mins} mins.", "DEBUG")
                else:
                    log_worker_event(ws.worker_number, "No helpers available for pray quest right now. Will retry later.", "DEBUG")
                    ws.next_pray_quest_time = datetime.now() + timedelta(minutes=2)

    if "say_owo" in active_quests:
        qdata = active_quests["say_owo"]
        if qdata["current"] < qdata["total"]:
            if not hasattr(ws, 'next_say_owo_time'):
                ws.next_say_owo_time = datetime.now()
                
            if datetime.now() >= ws.next_say_owo_time:
                await ctx.send("OwO")
                
                qdata["current"] += 1
                SaveQuestsDataGhoStys(ws, active_quests)
                
                log_worker_event(ws.worker_number, f"Say OwO quest progress: {qdata['current']}/{qdata['total']}", "SUCCESS")
                
                if qdata["current"] >= qdata["total"]:
                    asyncio.get_event_loop().call_later(5.0, lambda: asyncio.create_task(fetch_and_parse_quests(ctx, ws, bot)))
                else:
                    ws.next_say_owo_time = datetime.now() + timedelta(minutes=2)
                    log_worker_event(ws.worker_number, f"Next say OwO scheduled in 2 minutes.", "DEBUG")

    if "send_action" in active_quests:
        qdata = active_quests["send_action"]
        if qdata["current"] < qdata["total"]:
            if not hasattr(ws, 'next_send_action_time'):
                ws.next_send_action_time = datetime.now()
                
            if datetime.now() >= ws.next_send_action_time:
                target_id = None
                workers = manager.get_all_workers()
                if len(workers) > 1:
                    targets = [w.bot.user.id for w_num, w in workers.items() if w_num != ws.worker_number and w.bot and w.bot.user]
                    if targets:
                        target_id = random.choice(targets)
                        
                if target_id:
                    actions = ["punch", "slap", "pat", "hug", "kiss", "cuddle"]
                    action = random.choice(actions)
                    
                    await ctx.send(f"owo {action} <@{target_id}>")
                    
                    qdata["current"] += 1
                    SaveQuestsDataGhoStys(ws, active_quests)
                    
                    log_worker_event(ws.worker_number, f"Send action quest progress: {qdata['current']}/{qdata['total']}", "SUCCESS")
                    
                    if qdata["current"] >= qdata["total"]:
                        asyncio.get_event_loop().call_later(5.0, lambda: asyncio.create_task(fetch_and_parse_quests(ctx, ws, bot)))
                    else:
                        ws.next_send_action_time = datetime.now() + timedelta(minutes=1, seconds=36)
                        log_worker_event(ws.worker_number, f"Next send action scheduled in 1.6 minutes.", "DEBUG")
                else:
                    log_worker_event(ws.worker_number, "No target available for send action quest. Retrying in 2 mins.", "DEBUG")
                    ws.next_send_action_time = datetime.now() + timedelta(minutes=2)

    if "gamble_cowoncy" in active_quests:
        qdata = active_quests["gamble_cowoncy"]
        if qdata["current"] < qdata["total"]:
            if not hasattr(ws, 'next_gamble_quest_time'):
                ws.next_gamble_quest_time = datetime.now()
                
            if datetime.now() >= ws.next_gamble_quest_time:
                action = random.choice(["cf", "s"])
                await ctx.send(f"owo {action} 1")
                
                qdata["current"] += 1
                SaveQuestsDataGhoStys(ws, active_quests)
                
                log_worker_event(ws.worker_number, f"Gamble quest progress: {qdata['current']}/{qdata['total']}", "SUCCESS")
                
                if qdata["current"] >= qdata["total"]:
                    asyncio.get_event_loop().call_later(5.0, lambda: asyncio.create_task(fetch_and_parse_quests(ctx, ws, bot)))
                else:
                    ws.next_gamble_quest_time = datetime.now() + timedelta(minutes=2)
                    log_worker_event(ws.worker_number, f"Next gamble scheduled in 2 minutes.", "DEBUG")
