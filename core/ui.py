"""
This code is only made for educational and practice purposes. 
Author and Async Development are not responsible for misuse.

GhoSty OwO V4 Alpha Build
Stable Alpha Build Version: 280826.4.1.0

GitHub: https://github.com/WannaBeGhoSt
Discord: https://discord.gg/asMJGgDA7u
"""

import sys
import os
import re
import shutil
import ctypes
from collections import deque
import time

GLOBAL_LOGS = deque(maxlen=2000)

def _push_log(worker_num, level, msg, full_str):
    GLOBAL_LOGS.append({
        "timestamp": time.time(),
        "worker": str(worker_num) if worker_num is not None else "SYSTEM",
        "level": level,
        "msg": msg,
        "formatted": strip_ansi(full_str)
    })

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

def _enable_windows_vt():
    if os.name == 'nt':
        try:
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                mode.value |= 0x0004 
                kernel32.SetConsoleMode(handle, mode)
        except Exception:
            pass

_enable_windows_vt()

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"

CYAN_ELECTRIC = (0, 245, 255)
CYAN_MID      = (0, 195, 255)
BLUE_ELECTRIC = (30, 144, 255)
BLUE_NEON     = (59, 130, 246)
PURPLE_NEON   = (168, 85, 247)
PURPLE_LIGHT  = (192, 132, 252)
GREEN_NEON    = (52, 211, 153)
GREEN_EMERALD = (16, 185, 129)
YELLOW_GOLD   = (250, 204, 21)
RED_CRIMSON   = (248, 113, 113)
RED_BRIGHT    = (239, 68, 68)
GRAY_TEXT     = (148, 163, 184)
GRAY_MUTED    = (100, 116, 139)
GRAY_BORDER   = (51, 65, 85)
WHITE_BRIGHT  = (248, 250, 252)

def fg_rgb(r: int, g: int, b: int) -> str:
    return f"\033[38;2;{r};{g};{b}m"

def bg_rgb(r: int, g: int, b: int) -> str:
    return f"\033[48;2;{r};{g};{b}m"

def strip_ansi(text: str) -> str:
    return re.sub(r'\033\[[0-9;]*[a-zA-Z]', '', text)

def get_term_width(default: int = 86) -> int:
    try:
        w = shutil.get_terminal_size((default, 24)).columns
        return max(w, 60)
    except Exception:
        return default

def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        sys.stdout.write("\033[2J\033[H\033[3J")
        sys.stdout.flush()

def center(text: str, width: int = None) -> str:
    if width is None:
        width = get_term_width()
    plain_len = len(strip_ansi(text))
    if plain_len >= width:
        return text
    pad = (width - plain_len) // 2
    return " " * pad + text

def center_block(lines: list, width: int = None) -> list:
    if width is None:
        width = get_term_width()
    clean_lines = [strip_ansi(l) for l in lines]
    non_empty = [l for l in clean_lines if l.strip()]
    if not non_empty:
        return lines
    max_len = max(len(l) for l in non_empty)
    pad = max(0, (width - max_len) // 2)
    return [(" " * pad + line) if line.strip() else "" for line in lines]

def lerp_color(c1: tuple, c2: tuple, t: float) -> tuple:
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )

def multi_gradient_color(colors: list, t: float) -> tuple:
    if not colors:
        return (255, 255, 255)
    if len(colors) == 1 or t <= 0.0:
        return colors[0]
    if t >= 1.0:
        return colors[-1]
    
    seg_len = 1.0 / (len(colors) - 1)
    seg_idx = min(int(t / seg_len), len(colors) - 2)
    local_t = (t - (seg_idx * seg_len)) / seg_len
    return lerp_color(colors[seg_idx], colors[seg_idx + 1], local_t)

def colorize_gradient(text: str, colors: list = None) -> str:
    if colors is None:
        colors = [CYAN_ELECTRIC, CYAN_MID, BLUE_ELECTRIC, PURPLE_NEON]
    
    clean = strip_ansi(text)
    if not clean:
        return text
    
    n = len(clean)
    result = []
    clean_idx = 0
    
    in_ansi = False
    ansi_buf = []
    
    for ch in text:
        if ch == '\033':
            in_ansi = True
            ansi_buf.append(ch)
            continue
        if in_ansi:
            ansi_buf.append(ch)
            if ch.isalpha():
                in_ansi = False
                result.append("".join(ansi_buf))
                ansi_buf = []
            continue
        
        t = clean_idx / max(n - 1, 1)
        r, g, b = multi_gradient_color(colors, t)
        result.append(f"{fg_rgb(r, g, b)}{ch}")
        clean_idx += 1
        
    result.append(RESET)
    return "".join(result)


LOGO_GHOSTY_OWO = [
    '   ▄▄▄▄▄▄ ▄▄▄            ▄▄▄▄▄                 ▄▄▄▄▄▄                ▄▄▄▄▄▄',
    ' ██▀▀  ▀█  ██           ▄██ ▀█  ▄█            ██▀  ▀██              ██▀  ▀██',
    '███        ██▀██  ██▀█▄  ▀██▄▄ ▀██▀▀██▀▀█▀   ███    ███ ▀██▀██▀██▀ ███    ███',
    '▀██   ▀██▀ ██ ██ ███ ██ ▄  ▀▀██ ██  ▀███     ▀██    ██▀  ▀█▄▀███   ▀██    ██▀',
    ' ▀▀█▄▄▄█▀ ▄██▄██▄ ██▄█▀ █▀█▄▄█▀ ██▄  ▀█       ▀██▄▄██▀    ██ ▀█     ▀██▄▄██▀',
    '                                   ▄▄▄▀',
    '                                   ▀▀▀',
]

def render_header(worker_count: int, channel_count: int, has_main_ctrl: bool, width: int = None):
    if width is None:
        width = get_term_width()
    
    lines_out = []
    lines_out.append("")
    
    grad_colors = [CYAN_ELECTRIC, (45, 190, 255), BLUE_ELECTRIC, PURPLE_NEON]
    banner_grad = [colorize_gradient(l, grad_colors) for l in LOGO_GHOSTY_OWO]
    lines_out.extend(center_block(banner_grad, width))
    lines_out.append("")
    lines_out.append("")
    
    v_tag = (
        f"{fg_rgb(*CYAN_MID)}{BOLD}GhoSty OwO V4.1{RESET} "
        f"{fg_rgb(*GRAY_MUTED)}•{RESET} {fg_rgb(*PURPLE_LIGHT)}Alpha Build (280826.4.1.0){RESET} "
        f"{fg_rgb(*GRAY_MUTED)}•{RESET} {fg_rgb(*GREEN_NEON)}{BOLD}Free Forever{RESET}"
    )
    lines_out.append(center(v_tag, width))
    lines_out.append("")
    
    ctrl_status = f"{fg_rgb(*GREEN_NEON)}ACTIVE{RESET}" if has_main_ctrl else f"{fg_rgb(*GRAY_MUTED)}STANDALONE{RESET}"
    ch_status = f"{fg_rgb(*GREEN_NEON)}{channel_count} BOUND{RESET}" if channel_count > 0 else f"{fg_rgb(*YELLOW_GOLD)}MANUAL{RESET}"
    
    meta_line = (
        f"{fg_rgb(*GRAY_TEXT)}CONFIG: {RESET}{fg_rgb(*CYAN_ELECTRIC)}[config.json]{RESET}  "
        f"{fg_rgb(*GRAY_BORDER)}│{RESET}  {fg_rgb(*GRAY_TEXT)}WORKERS: {RESET}{fg_rgb(*CYAN_ELECTRIC)}<{worker_count}>{RESET}  "
        f"{fg_rgb(*GRAY_BORDER)}│{RESET}  {fg_rgb(*GRAY_TEXT)}CHANNELS: {RESET}{ch_status}  "
        f"{fg_rgb(*GRAY_BORDER)}│{RESET}  {fg_rgb(*GRAY_TEXT)}MAIN CTRL: {RESET}{ctrl_status}"
    )
    lines_out.append(center(meta_line, width))
    
    author_line = (
        f"{fg_rgb(*GRAY_MUTED)}< Made With {RESET}{fg_rgb(*RED_CRIMSON)}♥{RESET}{fg_rgb(*GRAY_MUTED)} in India By {RESET}"
        f"{fg_rgb(*CYAN_MID)}{BOLD}@jijaghosty{RESET}{fg_rgb(*GRAY_MUTED)} • {RESET}"
        f"{fg_rgb(*PURPLE_NEON)}🇮🇳 Async Development{RESET}{fg_rgb(*GRAY_MUTED)} >{RESET}"
    )
    lines_out.append(center(author_line, width))
    lines_out.append("")
    
    local_ip = "127.0.0.1"
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass
        
    dashboard_line = f"{fg_rgb(*GRAY_MUTED)}Access Dashboard: {RESET}{fg_rgb(*CYAN_ELECTRIC)}http://{local_ip}:8765{RESET}"
    lines_out.append(center(dashboard_line, width))
    lines_out.append("")
    
    box_lines = render_command_matrix(width=width)
    lines_out.extend(box_lines)
    lines_out.append("")
    
    div_title = f" {BOLD}{fg_rgb(*CYAN_ELECTRIC)}[ LIVE SESSION LOGS ]{RESET} "
    div_plain_len = len(strip_ansi(div_title))
    box_w = min(width - 4, 82)
    left_line_len = 4
    right_line_len = max(0, box_w - left_line_len - div_plain_len)
    
    section_div = f"{fg_rgb(*GRAY_BORDER)}{'─' * left_line_len}{RESET}{div_title}{fg_rgb(*GRAY_BORDER)}{'─' * right_line_len}{RESET}"
    lines_out.append(center(section_div, width))
    lines_out.append("")
    
    return "\n".join(lines_out)


def render_command_matrix(width: int = None) -> list:
    if width is None:
        width = get_term_width()
    
    box_w = min(width - 4, 82)
    if box_w < 60:
        box_w = 60
    
    b_col = fg_rgb(*CYAN_MID)
    tag_col = fg_rgb(*CYAN_ELECTRIC)
    
    col1 = [
        ("<01>", ".start [all/N]", "Start farm"),
        ("<02>", ".stop [all/N]",  "Halt worker"),
        ("<03>", ".status [N]",    "Worker stats"),
        ("<04>", ".workers",       "List all"),
    ]
    col2 = [
        ("<05>", ".speed [mode]",  "Change speed"),
        ("<06>", ".huntbot [on/off]", "Auto HB"),
        ("<07>", ".pause <time>",  "Pause farm"),
        ("<08>", ".resume",        "Resume farm"),
    ]
    col3 = [
        ("<09>", ".profit [N]",    "Zoo profit"),
        ("<10>", ".say <text>",    "Echo message"),
        ("<11>", ".help",          "Show guide"),
        ("<12>", "???",       "Soon?"),
    ]
    
    col_w = (box_w - 4) // 3
    
    lines = []
    top_border = f"{b_col}╭{'─' * (box_w - 2)}╮{RESET}"
    lines.append(center(top_border, width))
    
    title_text = f"{BOLD}{fg_rgb(*WHITE_BRIGHT)}ALL COMMANDS{RESET}"
    inner_pad = (box_w - 2 - len(strip_ansi(title_text))) // 2
    right_pad = box_w - 2 - len(strip_ansi(title_text)) - inner_pad
    lines.append(center(f"{b_col}│{RESET}{' ' * inner_pad}{title_text}{' ' * right_pad}{b_col}│{RESET}", width))
    
    sep_border = f"{b_col}├{'─' * (box_w - 2)}┤{RESET}"
    lines.append(center(sep_border, width))
    
    for r in range(4):
        c1_num, c1_cmd, c1_desc = col1[r]
        c2_num, c2_cmd, c2_desc = col2[r]
        c3_num, c3_cmd, c3_desc = col3[r]
        
        c1_str = f"{tag_col}{c1_num}{RESET} {fg_rgb(*WHITE_BRIGHT)}{c1_cmd:<15}{RESET}"
        c2_str = f"{tag_col}{c2_num}{RESET} {fg_rgb(*WHITE_BRIGHT)}{c2_cmd:<15}{RESET}"
        c3_str = f"{tag_col}{c3_num}{RESET} {fg_rgb(*WHITE_BRIGHT)}{c3_cmd:<14}{RESET}"
        
        raw_c1_len = len(strip_ansi(c1_str))
        raw_c2_len = len(strip_ansi(c2_str))
        raw_c3_len = len(strip_ansi(c3_str))
        
        row_content = (
            f" {c1_str}{' ' * max(0, col_w - raw_c1_len)}"
            f"{b_col}│{RESET} {c2_str}{' ' * max(0, col_w - raw_c2_len)}"
            f"{b_col}│{RESET} {c3_str}"
        )
        
        row_plain_len = len(strip_ansi(row_content))
        r_pad = max(0, box_w - 2 - row_plain_len)
        lines.append(center(f"{b_col}│{RESET}{row_content}{' ' * r_pad}{b_col}│{RESET}", width))
    
    bottom_border = f"{b_col}╰{'─' * (box_w - 2)}╯{RESET}"
    lines.append(center(bottom_border, width))
    return lines

def make_badge(text: str, bg_tuple: tuple, fg_tuple: tuple = (0, 0, 0), width: int = 10) -> str:
    padded = f" {text} ".center(width)
    return f"{bg_rgb(*bg_tuple)}{fg_rgb(*fg_tuple)}{BOLD}{padded}{RESET}"

def log_support_prompt(width: int = None):
    if width is None:
        width = get_term_width()
    b_col = fg_rgb(*CYAN_ELECTRIC)
    t_col = fg_rgb(*WHITE_BRIGHT)
    l_col = fg_rgb(*PURPLE_NEON)
    
    print("")
    print(center(f"{b_col}╭────────────── [ ASYNC DEVELOPMENT COMMUNITY SUPPORT ] ──────────────╮{RESET}", width))
    print(center(f"{b_col}│{RESET} {fg_rgb(239, 68, 68)}{BOLD}[!] An unexpected error occurred in your session.{RESET}                      {b_col}│{RESET}", width))
    print(center(f"{b_col}│{RESET} {t_col}Join our official Discord server for instant help & updates:{RESET}           {b_col}│{RESET}", width))
    print(center(f"{b_col}│{RESET} {l_col}{BOLD}https://discord.gg/asMJGgDA7u{RESET}                                         {b_col}│{RESET}", width))
    print(center(f"{b_col}│{RESET} {fg_rgb(*GRAY_MUTED)}Made With ♥ By @jijaghosty • Async Development Support{RESET}                {b_col}│{RESET}", width))
    print(center(f"{b_col}╰──────────────────────────────────────────────────────────────────────╯{RESET}", width))
    print("")

def log_worker_event(worker_num, msg: str, level: str = "INFO"):
    if isinstance(worker_num, int):
        tag = f"{fg_rgb(*CYAN_ELECTRIC)}[ W#{worker_num:02d} ]{RESET}"
    elif str(worker_num).upper() in ["CTRL", "MAIN-CTRL", "MAIN"]:
        tag = f"{fg_rgb(*PURPLE_NEON)}[ MAIN-CTRL ]{RESET}"
    else:
        tag = f"{fg_rgb(*CYAN_ELECTRIC)}[{worker_num}]{RESET}"
    
    lvl = level.upper()
    if lvl == "INFO":
        badge = make_badge("INFO", (14, 165, 233), (0, 0, 0), width=10)
        arrow = f"{fg_rgb(*CYAN_MID)}──>{RESET}"
        msg_colored = f"{fg_rgb(*WHITE_BRIGHT)}{msg}{RESET}"
    elif lvl == "DEBUG":
        badge = make_badge("DEBUG", (99, 102, 241), (255, 255, 255), width=10)
        arrow = f"{fg_rgb(*BLUE_NEON)}──>{RESET}"
        msg_colored = f"{fg_rgb(*GRAY_TEXT)}{msg}{RESET}"
    elif lvl in ["SUCCESS", "HUNT", "SOLVED"]:
        badge = make_badge("SUCCESS", (16, 185, 129), (0, 0, 0), width=10)
        arrow = f"{fg_rgb(*GREEN_NEON)}──>{RESET}"
        msg_colored = f"{fg_rgb(*GREEN_NEON)}{msg}{RESET}"
    elif lvl in ["WARNING", "WARN"]:
        badge = make_badge("WARNING", (217, 119, 6), (0, 0, 0), width=10)
        arrow = f"{fg_rgb(*YELLOW_GOLD)}──>{RESET}"
        msg_colored = f"{fg_rgb(*YELLOW_GOLD)}{msg}{RESET}"
    elif lvl == "CRITICAL":
        badge = make_badge("CRITICAL", (153, 27, 27), (255, 255, 255), width=10)
        arrow = f"{fg_rgb(239, 68, 68)}──>{RESET}"
        msg_colored = f"{fg_rgb(248, 113, 113)}{BOLD}{msg}{RESET}"
    elif lvl in ["FATAL", "FATAL ERROR"]:
        badge = make_badge("FATAL", (185, 28, 28), (255, 255, 255), width=10)
        arrow = f"{fg_rgb(*RED_BRIGHT)}──>{RESET}"
        msg_colored = f"{fg_rgb(*RED_BRIGHT)}{BOLD}{msg}{RESET}"
    else:
        badge = make_badge(lvl[:8], (14, 165, 233), (0, 0, 0), width=10)
        arrow = f"{fg_rgb(*CYAN_MID)}──>{RESET}"
        msg_colored = f"{fg_rgb(*WHITE_BRIGHT)}{msg}{RESET}"
        
    full_str = f"   {badge} {tag} {arrow} {msg_colored}"
    print(full_str)
    _push_log(worker_num, lvl, msg, full_str)
    if lvl in ["CRITICAL", "FATAL", "FATAL ERROR"]:
        log_support_prompt()

def log_info(msg: str):
    badge = make_badge("INFO", (14, 165, 233), (0, 0, 0), width=10)
    arrow = f"{fg_rgb(*CYAN_MID)}──>{RESET}"
    full_str = f"   {badge} {arrow} {fg_rgb(*WHITE_BRIGHT)}{msg}{RESET}"
    print(full_str)
    _push_log("SYS", "INFO", msg, full_str)

def log_success(msg: str):
    badge = make_badge("READY", (16, 185, 129), (0, 0, 0), width=10)
    arrow = f"{fg_rgb(*GREEN_NEON)}──>{RESET}"
    full_str = f"   {badge} {arrow} {fg_rgb(*GREEN_NEON)}{msg}{RESET}"
    print(full_str)
    _push_log("SYS", "SUCCESS", msg, full_str)

def log_warn(msg: str):
    badge = make_badge("WARNING", (217, 119, 6), (0, 0, 0), width=10)
    arrow = f"{fg_rgb(*YELLOW_GOLD)}──>{RESET}"
    full_str = f"   {badge} {arrow} {fg_rgb(*YELLOW_GOLD)}{msg}{RESET}"
    print(full_str)
    _push_log("SYS", "WARN", msg, full_str)

def log_error(msg: str):
    badge = make_badge("ERROR", (220, 38, 38), (255, 255, 255), width=10)
    arrow = f"{fg_rgb(*RED_BRIGHT)}──>{RESET}"
    full_str = f"   {badge} {arrow} {fg_rgb(248, 113, 113)}{msg}{RESET}"
    print(full_str)
    _push_log("SYS", "ERROR", msg, full_str)

def log_critical(worker_label: str, error: Exception | str):
    badge = make_badge("CRITICAL", (153, 27, 27), (255, 255, 255), width=10)
    tag = f"{fg_rgb(*RED_CRIMSON)}{worker_label}{RESET}"
    arrow = f"{fg_rgb(*RED_CRIMSON)}──>{RESET}"
    msg = f"{fg_rgb(*RED_CRIMSON)}{error}{RESET}"
    print(f"   {badge} {tag} {arrow} {msg}")
    log_support_prompt()

def log_worker_start(worker_num: int):
    badge = make_badge("INIT", (6, 182, 212), (0, 0, 0), width=10)
    tag = f"{fg_rgb(*CYAN_ELECTRIC)}[ W#{worker_num:02d} ]{RESET}"
    arrow = f"{fg_rgb(*GRAY_MUTED)}──>{RESET}"
    msg = f"{fg_rgb(*CYAN_MID)}Initializing worker thread...{RESET}"
    print(f"   {badge} {tag} {arrow} {msg}")

def log_worker_ready(worker_num: int, username: str, channel_id: int = None):
    badge = make_badge("ONLINE", (16, 185, 129), (0, 0, 0), width=10)
    tag = f"{fg_rgb(*GREEN_NEON)}[ W#{worker_num:02d} ]{RESET}"
    arrow = f"{fg_rgb(*GREEN_NEON)}──>{RESET}"
    user_str = f"{fg_rgb(*WHITE_BRIGHT)}{BOLD}@{username}{RESET}"
    
    if channel_id:
        ch_str = f"{fg_rgb(*GRAY_MUTED)}(Channel: {fg_rgb(*CYAN_ELECTRIC)}{channel_id}{fg_rgb(*GRAY_MUTED)}){RESET}"
        print(f"   {badge} {tag} {arrow} Connected as {user_str} {ch_str}")
    else:
        no_ch = f"{fg_rgb(*YELLOW_GOLD)}(No channel assigned — use .start from account or main){RESET}"
        print(f"   {badge} {tag} {arrow} Connected as {user_str} {no_ch}")

def log_controller_ready(username: str):
    badge = make_badge("CTRL", (147, 51, 234), (255, 255, 255), width=10)
    tag = f"{fg_rgb(*PURPLE_NEON)}[ MAIN-CTRL ]{RESET}"
    arrow = f"{fg_rgb(*PURPLE_NEON)}──>{RESET}"
    user_str = f"{fg_rgb(*WHITE_BRIGHT)}{BOLD}@{username}{RESET}"
    print(f"   {badge} {tag} {arrow} Main Controller online as {user_str}")

def log_disconnect(worker_label: str):
    badge = make_badge("OFFLINE", (234, 88, 12), (0, 0, 0), width=10)
    tag = f"{fg_rgb(*YELLOW_GOLD)}{worker_label}{RESET}"
    arrow = f"{fg_rgb(*YELLOW_GOLD)}──>{RESET}"
    msg = f"{fg_rgb(*GRAY_TEXT)}Disconnected from Discord — auto-reconnecting...{RESET}"
    print(f"   {badge} {tag} {arrow} {msg}")

def log_resumed(worker_label: str):
    badge = make_badge("RESUMED", (16, 185, 129), (0, 0, 0), width=10)
    tag = f"{fg_rgb(*GREEN_NEON)}{worker_label}{RESET}"
    arrow = f"{fg_rgb(*GREEN_NEON)}──>{RESET}"
    msg = f"{fg_rgb(*GREEN_NEON)}Gateway connection resumed.{RESET}"
    print(f"   {badge} {tag} {arrow} {msg}")

def log_retry(worker_label: str, delay: int, attempt: int):
    badge = make_badge("RETRY", (202, 138, 4), (0, 0, 0), width=10)
    tag = f"{fg_rgb(*YELLOW_GOLD)}{worker_label}{RESET}"
    arrow = f"{fg_rgb(*YELLOW_GOLD)}──>{RESET}"
    msg = f"{fg_rgb(*GRAY_TEXT)}Reconnecting in {fg_rgb(*YELLOW_GOLD)}{delay}s{fg_rgb(*GRAY_TEXT)} (attempt #{attempt})...{RESET}"
    print(f"   {badge} {tag} {arrow} {msg}")

def log_fatal_error(worker_label: str, error: Exception):
    badge = make_badge("FATAL", (185, 28, 28), (255, 255, 255), width=10)
    tag = f"{fg_rgb(*RED_BRIGHT)}{worker_label}{RESET}"
    arrow = f"{fg_rgb(*RED_BRIGHT)}──>{RESET}"
    msg = f"{fg_rgb(*RED_BRIGHT)}Auth error (token invalid/banned) — worker stopped: {error}{RESET}"
    print(f"   {badge} {tag} {arrow} {msg}")
    log_support_prompt()

def log_net_error(worker_label: str, error: Exception):
    badge = make_badge("NET_ERR", (202, 138, 4), (0, 0, 0), width=10)
    tag = f"{fg_rgb(*YELLOW_GOLD)}{worker_label}{RESET}"
    arrow = f"{fg_rgb(*YELLOW_GOLD)}──>{RESET}"
    msg = f"{fg_rgb(*GRAY_TEXT)}Network error ({type(error).__name__}): {error} — will retry{RESET}"
    print(f"   {badge} {tag} {arrow} {msg}")

def log_event_error(worker_label: str, event: str):
    badge = make_badge("ERROR", (220, 38, 38), (255, 255, 255), width=10)
    tag = f"{fg_rgb(*RED_BRIGHT)}{worker_label}{RESET}"
    arrow = f"{fg_rgb(*RED_BRIGHT)}──>{RESET}"
    print(f"   {badge} {tag} {arrow} Error in '{event}'")

def log_shutdown():
    badge = make_badge("SHUTDOWN", (220, 38, 38), (255, 255, 255), width=10)
    print(f"\n   {badge} {fg_rgb(*RED_BRIGHT)}Shutting down all active workers and threads...{RESET}")

