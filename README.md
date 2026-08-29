<div align="center">
  <center><img src="assets/ghosty%20owo%20logo.jpeg" width="150" style="border-radius: 10%"></center>
  <br>
  <a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.herokuapp.com?font=Merriweather&size=40&pause=1000&color=00e5ff&center=true&vCenter=true&random=false&width=425&lines=GhoSty+OwO" alt="Typing SVG" /></a>
  <br/>
  <a href="https://discord.gg/asMJGgDA7u"><img src="https://invidget.switchblade.xyz/asMJGgDA7u" alt="Discord Invite"/> </a>
  <br/>
  <small><p>Be sure to drop by our community server! (Please use an alt account that doesn't actively play OwO to stay safe.)<br>
  Joining with your main grinding account puts you at serious risk of an OwO ban!<br>
  Need direct assistance? Shoot a friend request to `@jijaghosty` on Discord.</p></small>
</div>

---

Currently the most intelligent and advanced selfbot for owobot. Use it yourself to see why it stands out.

> [!IMPORTANT]
> ⚠️🚨 **DISCLAIMER:** This software is provided strictly for educational and research purposes. Using self-bots directly violates Discord's Terms of Service and OwO Bot's community guidelines. We accept zero liability for any account bans or penalties. If you choose to run this script, operate cautiously: limit the number of workers per server, strictly grind in isolated/private servers, and never publicly discuss your usage.

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=transparent&color=gradient&customColorList=00e5ff,00ffaa&height=60&section=header&text=✨%20Features&fontSize=40&fontAlignY=35" alt="Features" />
</div>

- 🔄 **Advanced Automation & Scalable Multi-Worker Support**
- 🤖 **Neural-Powered Auto HuntBot Captcha Solving**
- 🌐 **Sleek Real-time Web Dashboard for Monitoring**
- ⚡ **Highly Optimized & Secure Architecture**
- ⚠ **Anti-Detection Mechanics & Ban Mitigation**
- 🚨 **Instant OwO Warning Detection**
- ⏱ **Failsafe System (Auto-halts after 1 Warning)**
- 💎 **Intelligent Auto-Gem Usage**
- 🛌 **Smart Dynamic Sleep System to mimic human patterns**
- ♾️ **True Lifetime Mode for Infinite Grinding**
- 🎒 **Smart Auto Quest Completion with Inter-worker Interaction**
- 👹 **Auto Guild Boss Fighting System**
- 🧠 **Humanoid Speed Mode with Dynamic Bezier Curves**

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=transparent&color=gradient&customColorList=b500ff,ff007f&height=60&section=header&text=🛠️%20Setup%20and%20Installation&fontSize=40&fontAlignY=35" alt="Setup" />
</div>

### 1️⃣ Universal Setup Suite

GhoSty OwO V4.1 features a massive **Cross-Platform Setup Assistant** that automates dependencies and scaffolding. It works seamlessly across Windows, Linux, macOS, and **Android (Termux)**!

```bash
python setup.py
```
*The setup script will guide you through entering your Main Token and will automatically generate `setup_files/` containing easy launch scripts (`run.bat`, `run.sh`, `termux_setup.sh`).*

### 2️⃣ Architecture & Working Principles

#### 🔗 The 1:1 Binding System (`tokens.txt` & `channels.txt`)
- **`tokens.txt`**: Contains your worker Discord tokens (one per line).
- **`channels.txt`**: Contains your target farming channel IDs (one per line).

**How it works**: GhoSty automatically binds them on a **1:1 ratio**. Worker #1 uses Token #1 and farms exclusively in Channel #1. Worker #2 uses Token #2 and farms in Channel #2. This isolated routing ensures workers never overlap, preventing Discord rate limits and preventing bot detection.

#### 🤖 The Worker Ecosystem
- **Self Worker**: An autonomous, isolated grinding instance powered by a single token. Each worker runs in its own asynchronous thread, autonomously executing commands, solving neural captchas, and handling quests without interfering with other workers.
- **Main Controller**: Your "Master" account (configured via `MAIN_TOKEN` in `config.json`). It doesn't grind. Instead, it monitors all active workers, receives DM logs for captchas or warnings, and acts as a central command hub. You can send commands like `.start all` from the Main Controller to instantly control the entire fleet!

### 3️⃣ Basic Usage  

- Run `python main.py` or double-click `setup_files/run.bat`.
- Simply type `.start` or `.start all` from your Main Controller inside Discord, or trigger it directly via the **Web Dashboard** to begin farming!
> [!TIP]
> Running into setup errors? Hop into our Discord community (or add `@jijaghosty` directly) and we'll gladly help you get everything configured properly!

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=transparent&color=gradient&customColorList=ff007f,b500ff&height=60&section=header&text=📸%20Showcase&fontSize=40&fontAlignY=35" alt="Showcase" />
</div>

<div align="center">
  <center><img src="assets/cli%20view.png" width="800"></center>
  <br>
  <p><b>Terminal CLI Interface</b></p>
  <br>
  <center><img src="assets/web%20dashboard.png" width="800"></center>
  <br>
  <p><b>Web Dashboard Interface</b></p>
</div>

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=transparent&color=gradient&customColorList=00e5ff,b500ff&height=60&section=header&text=👨‍💻%20About%20Developer&fontSize=40&fontAlignY=35" alt="About Developer" />
</div>

<div align="center">
  <p><b>GhoSty | Brutality (Async Development)</b></p>
  <a href="https://discord.com/users/940896719045034024" target="_blank">
    <img src="https://lanyard.cnrad.dev/api/940896719045034024?theme=dark&bg=16161a&animated=true&hideDiscrim=true&borderRadius=10px" alt="Live Discord Profile Widget" />
  </a>
</div>

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=transparent&color=gradient&customColorList=00ffaa,00e5ff&height=60&section=header&text=💖%20Support%20the%20Project&fontSize=40&fontAlignY=35" alt="Support" />
</div>

If this tool has been helpful, consider supporting the development!

**LTC (Litecoin) Wallet:**
```
LbeKrDeUF7mTB8LZLHkjicQfEW6tyhVGny
```

Alternatively, you can support us directly via **[Donatree](https://donatr.ee/brutality/)**.

*Thank you so much! Once you donate, shoot me a DM on Discord with your transaction ID, and I'll hook you up with an exclusive Donator role!*

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=transparent&color=gradient&customColorList=ff3300,ff9900&height=60&section=header&text=🚨%20Important%20Notices&fontSize=40&fontAlignY=35" alt="Notices" />
</div>

- **🚫 Unauthorized reselling or redistribution of this software is strictly prohibited and will result in a permanent blacklist.**
- **⚠️ Please use this software responsibly. The creator assumes no responsibility for TOS infractions.**

---
<div align="center">
  <i>Thanks for checking out GhoSty OwO! We hope this drastically improves your grinding experience! ❤</i>
  <br><br>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=WannaBeGhoSt.ghosty-owo" alt="Repository Views" />
</div>

<br>
<details>
<summary>Keywords</summary>
owo bot macro, owo bot auto farm, owo bot auto hunt, owo auto captcha solver, discord owo bot hack, owo bot script, discord selfbot, owo auto zoo, owo auto quest, auto gem, cowoncy generator, owo bot grinder, owo script python, owo bot automation, discord python selfbot, auto battle, auto pray, auto curse, auto huntbot, owo bot auto cowoncy, owo bot auto level, discord automation, python script for owo bot, owo farm, owo bot farm, owo farm, owo selfbot, owo farm selfbot, ghosty owo, ghosty owo farm, async development, ghosty, brutality owo, brutality owo farm, owo farm antiban, ghosty owo antiban
</details>
