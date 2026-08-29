"""
This code is only made for educational and practice purposes. 
Author and Async Development are not responsible for misuse.

GhoSty OwO V4 Alpha Build
Stable Alpha Build Version: 280826.4.1.0

GitHub: https://github.com/WannaBeGhoSt
Discord: https://discord.gg/asMJGgDA7u
"""

import asyncio
import discord
from discord.ext import commands
from colorama import Fore, Style

GhoStyyy = "."

def create_bot(worker_number):
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    bot = commands.Bot(
        command_prefix=GhoStyyy, case_insensitive=True, self_bot=True
    )
    bot.remove_command("help")
    bot.worker_number = worker_number
    return bot