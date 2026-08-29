
"""
This code is only made for educational and practice purposes. 
Author and Async Development are not responsible for misuse.

GhoSty OwO V4 Alpha Build
Stable Alpha Build Version: 280826.4.1.0

GitHub: https://github.com/WannaBeGhoSt
Discord: https://discord.gg/asMJGgDA7u
"""

import os
import sys
import json
import traceback
import subprocess
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from core.heart import manager
from core.ui import GLOBAL_LOGS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "dashboard", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "dashboard", "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
CORS(app)

from flask import Flask, jsonify, request, render_template, send_from_directory

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory(os.path.join(BASE_DIR, "assets"), filename)

@app.route("/api/status", methods=["GET"])
def get_status():
    workers = manager.get_all_workers()
    data = {}
    total_cash = 0
    total_essence = 0
    active_workers = 0

    quests_data = {}
    quests_path = os.path.join(BASE_DIR, "ghostyworkerquests.json")
    if os.path.exists(quests_path):
        try:
            with open(quests_path, "r", encoding="utf-8") as f:
                quests_data = json.load(f)
        except:
            pass

    for w_num, w in workers.items():
        w_dict = w.to_dict()
        w_dict["quests"] = quests_data.get(str(w_num), {})
        
        total_cash += w.initial_cash or 0
        total_essence += w.initial_essence or 0
        
        if w.running and not w.paused and not w.sleep_mode:
            active_workers += 1
            
        data[w_num] = w_dict

    return jsonify({
        "workers": data,
        "summary": {
            "total_workers": len(workers),
            "active_workers": active_workers,
            "total_cash": total_cash,
            "total_essence": total_essence
        }
    })

@app.route("/api/logs", methods=["GET"])
def get_logs():
    worker_id = request.args.get("worker")
    logs = list(GLOBAL_LOGS)
    
    if worker_id and worker_id != "all":
        logs = [log for log in logs if log["worker"] == worker_id or log["worker"] == "SYS"]
        
    return jsonify(logs[-500:])

@app.route("/api/control/<worker_num>", methods=["POST"])
def control_worker(worker_num):
    action = request.json.get("action")
    if worker_num == "all":
        workers = manager.get_all_workers().values()
    else:
        try:
            w_num = int(worker_num)
            w = manager.get_worker(w_num)
            if w:
                workers = [w]
            else:
                return jsonify({"error": "Worker not found"}), 404
        except ValueError:
            return jsonify({"error": "Invalid worker ID"}), 400

    success_count = 0
    for w in workers:
        if action == "start":
            if not w.running:
                import asyncio
                from core.heart import _run_farming_loop, PseudoCtx
                chan_id = getattr(w, 'auto_start_channel_id', None)
                if not chan_id:
                    from main import channels_map
                    chan_id = channels_map.get(w.worker_number)
                
                if chan_id and w.bot:
                    channel = w.bot.get_channel(chan_id)
                    if channel:
                        ctx = PseudoCtx(channel, w.bot)
                        asyncio.run_coroutine_threadsafe(_run_farming_loop(ctx, w, w.bot), w.bot.loop)
                        success_count += 1

        elif action == "pause":
            if w.running and not w.paused:
                time_str = request.json.get("time")
                import datetime
                if time_str:
                    from core.heart import _parse_pause_time
                    secs = _parse_pause_time(time_str)
                    if secs is not None and secs >= 900:
                        w.paused = True
                        w.pause_end_time = datetime.datetime.now() + datetime.timedelta(seconds=secs)
                        success_count += 1
                else:
                    w.paused = True
                    w.pause_end_time = datetime.datetime.now() + datetime.timedelta(days=365)
                    success_count += 1
        elif action == "resume":
            if w.running and w.paused:
                w.paused = False
                w.pause_end_time = None
                success_count += 1
        elif action == "stop":
            if w.running:
                w.running = False
                success_count += 1
        elif action == "speed":
            mode = request.json.get("mode")
            if mode in ["efficient", "fast", "durable", "lifetime", "humanoid"]:
                w.current_speed_mode = mode
                import datetime
                w.last_mode_change_time = datetime.datetime.now()
                success_count += 1
        elif action == "huntbot":
            toggle = request.json.get("toggle")
            if toggle in ["on", "off"]:
                w.huntbot_enabled = (toggle == "on")
                success_count += 1
        elif action == "mail":
            import datetime
            if w.last_mail_claim:
                time_since = (datetime.datetime.now() - w.last_mail_claim).total_seconds()
                if time_since < 300:
                    continue
            if not getattr(w, "is_mail_claiming", False):
                w.last_mail_claim = datetime.datetime.now()
                w.is_mail_claiming = True
                
                chan_id = w.auto_start_channel_id
                if chan_id and w.bot and w.bot.loop and w.bot.loop.is_running():
                    channel = w.bot.get_channel(chan_id)
                    if channel:
                        from core.heart import PseudoCtx
                        from core.mailmodule import execute_mail_claim
                        import asyncio
                        ctx = PseudoCtx(channel, w.bot)
                        w.bot.loop.create_task(execute_mail_claim(ctx, w, w.bot))
                        success_count += 1
                
    return jsonify({"success": True, "affected": success_count, "action": action})

@app.route("/api/profit", methods=["GET"])
def fetch_profit():
    from core.heart import manager
    try:
        from core.heart import _fetch_zoo_for_main_status
    except ImportError:
        return jsonify({"success": False, "error": "Could not import zoo fetcher"})
    
    import asyncio
    
    all_ws = manager.get_all_workers()
    futures = []
    
    for wn, target_ws in sorted(all_ws.items()):
        if (
            target_ws.has_started
            and target_ws.zoo_channel
            and not target_ws.sleep_mode
            and not target_ws.paused
            and getattr(target_ws, 'bot', None)
            and getattr(target_ws.bot, 'loop', None)
            and target_ws.bot.loop.is_running()
        ):
            try:
                future = asyncio.run_coroutine_threadsafe(
                    _fetch_zoo_for_main_status(target_ws),
                    target_ws.bot.loop,
                )
                futures.append(future)
            except Exception:
                pass
                
    for future in futures:
        try:
            future.result(timeout=10)
        except Exception:
            pass

    def format_value(value):
        if value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.2f}K"
        else:
            return f"{int(value)}"

    total_profit = 0
    worker_data = []

    for wn, target_ws in sorted(all_ws.items()):
        if not target_ws.has_started:
            worker_data.append({
                "worker": wn,
                "username": target_ws.username,
                "status": "Not started",
                "profit": 0,
                "profit_str": "0",
                "start_cash": 0,
                "current_cash": 0
            })
            continue

        profit = getattr(target_ws, 'current_cash', 0) - (target_ws.initial_cash or 0)
        total_profit += profit

        if target_ws.sleep_mode:
            status = "Sleeping"
        elif target_ws.paused:
            status = "Paused"
        elif not target_ws.running:
            status = "Stopped"
        else:
            status = "Running"

        worker_data.append({
            "worker": wn,
            "username": target_ws.username,
            "status": status,
            "profit": profit,
            "profit_str": format_value(profit),
            "start_cash": format_value(target_ws.initial_cash or 0),
            "current_cash": format_value(getattr(target_ws, 'current_cash', 0))
        })

    return jsonify({
        "success": True, 
        "workers": worker_data,
        "total_profit": total_profit,
        "total_profit_str": format_value(total_profit)
    })

@app.route("/api/say", methods=["POST"])
def say_command():
    text = request.json.get("text", "").strip()
    if not text:
        return jsonify({"success": False, "error": "No text provided"})
        
    from core.heart import manager
    import asyncio
    all_ws = manager.get_all_workers()
    sent = 0
    for wn, target_ws in sorted(all_ws.items()):
        ch_id = getattr(target_ws, 'auto_start_channel_id', None)
        if ch_id and getattr(target_ws, 'bot', None) and getattr(target_ws.bot, 'loop', None) and target_ws.bot.loop.is_running():
            channel = target_ws.bot.get_channel(ch_id)
            if channel:
                asyncio.run_coroutine_threadsafe(channel.send(text), target_ws.bot.loop)
                sent += 1
                
    return jsonify({"success": True, "sent": sent})

@app.route("/api/config", methods=["GET", "POST"])
def manage_config():
    tokens_path = os.path.join(BASE_DIR, "tokens.txt")
    channels_path = os.path.join(BASE_DIR, "channels.txt")
    
    if request.method == "POST":
        data = request.json
        if "tokens" in data:
            with open(tokens_path, "w", encoding="utf-8") as f:
                f.write(data["tokens"])
        if "channels" in data:
            with open(channels_path, "w", encoding="utf-8") as f:
                f.write(data["channels"])
        return jsonify({"success": True})
    
    tokens_content = ""
    channels_content = ""
    if os.path.exists(tokens_path):
        with open(tokens_path, "r", encoding="utf-8") as f:
            tokens_content = f.read()
    if os.path.exists(channels_path):
        with open(channels_path, "r", encoding="utf-8") as f:
            channels_content = f.read()
            
    return jsonify({
        "tokens": tokens_content,
        "channels": channels_content
    })

@app.route("/api/restart", methods=["POST"])
def restart_script():
    import threading
    import time
    
    def _restart():
        time.sleep(1)
        os.execv(sys.executable, ['python'] + sys.argv)
        
    threading.Thread(target=_restart).start()
    return jsonify({"success": True, "message": "Restarting script in 1 second..."})

def start_server():
    import logging
    import socket
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass
        
    try:
        from waitress import serve
        serve(app, host='0.0.0.0', port=8765)
    except ImportError:
        app.run(host="0.0.0.0", port=8765, debug=False, use_reloader=False)

if __name__ == "__main__":
    start_server()
