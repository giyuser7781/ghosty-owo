const API_BASE = '/api';
let isAutoScroll = true;
let isStreamerMode = localStorage.getItem('ghostyStreamerMode') === 'true';

window.showToast = function (message, type = "success") {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.style.padding = '12px 20px';
    toast.style.marginBottom = '10px';
    toast.style.borderRadius = '8px';
    toast.style.color = '#fff';
    toast.style.background = type === 'success' ? 'var(--success)' : 'var(--danger)';
    toast.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
    toast.style.transition = 'opacity 0.3s ease';
    toast.style.opacity = '0';
    toast.innerText = message;

    container.appendChild(toast);

    setTimeout(() => toast.style.opacity = '1', 10);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
};

window.controlAll = async function (action) {
    window.controlWorker('all', action);
};

window.controlWorker = async function (id, action) {
    try {
        await fetch(`${API_BASE}/control/${id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action })
        });
        window.fetchStatus();
        window.showToast(`Action '${action}' dispatched successfully!`, "success");
    } catch (e) {
        window.showToast("Action failed!", "error");
    }
};

window.applyControllerSettings = async function (settingType) {
    let workerId, payload = {};

    if (settingType === 'speed') {
        workerId = document.getElementById('ctrl-speed-worker').value;
        payload = { action: 'speed', mode: document.getElementById('ctrl-speed-mode').value };
    } else if (settingType === 'huntbot') {
        workerId = document.getElementById('ctrl-hb-worker').value;
        payload = { action: 'huntbot', toggle: document.getElementById('ctrl-hb-toggle').value };
    } else if (settingType === 'pause_time') {
        workerId = document.getElementById('ctrl-pause-worker').value;
        const timeVal = document.getElementById('ctrl-pause-time').value.trim();
        if (!timeVal) {
            window.showToast("Please enter a valid time (e.g., 30m, 1h)", "error");
            return;
        }
        payload = { action: 'pause', time: timeVal };
    } else if (settingType === 'mail') {
        workerId = document.getElementById('ctrl-mail-worker').value;
        payload = { action: 'mail' };
    }

    try {
        const res = await fetch(`${API_BASE}/control/${workerId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            window.showToast(`Settings applied to ${data.affected} worker(s)!`, "success");
            window.fetchStatus();
        } else {
            window.showToast("Failed to apply settings", "error");
        }
    } catch (e) {
        window.showToast("Error applying settings", "error");
    }
};

window.fetchStatus = async function () {
    try {
        const res = await fetch(`${API_BASE}/status`);
        const data = await res.json();
        document.getElementById('home-total-workers').innerText = data.summary.total_workers;
        document.getElementById('home-active-workers').innerText = data.summary.active_workers;
        document.getElementById('home-total-cowoncy').innerText = (data.summary.total_cash || 0).toLocaleString();
        document.getElementById('home-total-essence').innerText = (data.summary.total_essence || 0).toLocaleString();

        const statusGrid = document.getElementById('status-grid');
        const controlGrid = document.getElementById('control-grid');
        let statusHTML = '';
        let controlHTML = '';

        const filterSelect = document.getElementById('console-filter');
        const currentFilter = filterSelect ? filterSelect.value : 'all';
        let filterHTML = '<option value="all">All Workers</option>';
        let workerDropdownHTML = '<option value="all">All Workers</option>';

        Object.keys(data.workers).sort((a, b) => parseInt(a) - parseInt(b)).forEach(w_num => {
            const w = data.workers[w_num];
            const displayUsername = isStreamerMode ? '***' : w.username;
            filterHTML += `<option value="${w.worker_number}">Worker [${w.worker_number}] - ${displayUsername}</option>`;
            workerDropdownHTML += `<option value="${w.worker_number}">Worker #${w.worker_number} (${displayUsername})</option>`;

            let statusBadge = '';
            if (!w.running) statusBadge = `<span class="badge badge-danger">Stopped</span>`;
            else if (w.paused) statusBadge = `<span class="badge badge-warning">Paused</span>`;
            else if (w.sleep_mode) statusBadge = `<span class="badge badge-info">Sleeping</span>`;
            else statusBadge = `<span class="badge badge-success">Running</span>`;

            let uptimeStr = "0h 0m 0s";
            if (w.ghosty_start_time) {
                const startDt = new Date(w.ghosty_start_time);
                const now = new Date();
                const diffSec = Math.floor((now - startDt) / 1000);
                const h = Math.floor(diffSec / 3600);
                const m = Math.floor((diffSec % 3600) / 60);
                const s = diffSec % 60;
                uptimeStr = `${h}h ${m}m ${s}s`;
            }

            let runningSince = "Never";
            if (w.ghosty_start_time) {
                const startDt = new Date(w.ghosty_start_time);
                runningSince = startDt.toLocaleString();
            }

            let currentCycleDuration = "0s";
            if (w.lifetime_cycle_start_time) {
                const cycleDt = new Date(w.lifetime_cycle_start_time);
                const now = new Date();
                const diffSec = Math.floor((now - cycleDt) / 1000);
                const h = Math.floor(diffSec / 3600);
                const m = Math.floor((diffSec % 3600) / 60);
                const s = diffSec % 60;
                currentCycleDuration = `${h}h ${m}m ${s}s`;
            }

            let lastGemCheck = "Never";
            if (w.last_gem_check) {
                const gemDt = new Date(w.last_gem_check * 1000);
                lastGemCheck = gemDt.toLocaleString();
            }

            let activeQuestsText = '';
            if (w.quests && Object.keys(w.quests).length > 0) {
                activeQuestsText = Object.keys(w.quests).map(qKey => {
                    const q = w.quests[qKey];
                    return `${qKey.replace(/_/g, ' ')}: ${q.current}/${q.total}`;
                }).join(', ');
            } else {
                activeQuestsText = 'No active quests';
            }

            statusHTML += `
                <div style="background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid var(--border);">
                        <div>
                            <h4 style="margin: 0; font-size: 16px;">Worker #${w.worker_number}</h4>
                            <div style="font-size: 12px; color: var(--text-muted);">${displayUsername}</div>
                        </div>
                        ${statusBadge}
                    </div>
                    <div style="font-size: 13px; display: grid; grid-template-columns: 1fr; gap: 6px;">
                        <div><i class="fa-solid fa-clock" style="color: var(--text-muted); width: 16px;"></i> <strong>Running Since:</strong> ${runningSince}</div>
                        <div><i class="fa-solid fa-arrow-trend-up" style="color: var(--text-muted); width: 16px;"></i> <strong>Uptime:</strong> ${uptimeStr}</div>
                        <div><i class="fa-solid fa-terminal" style="color: var(--text-muted); width: 16px;"></i> <strong>Commands Sent:</strong> ${w.ghosty_commands_sent}</div>
                        <div><i class="fa-solid fa-gem" style="color: var(--text-muted); width: 16px;"></i> <strong>Gems Used:</strong> ${w.ghosty_gems_used}</div>
                        <div><i class="fa-solid fa-bolt" style="color: var(--text-muted); width: 16px;"></i> <strong>Speed Mode:</strong> <span class="badge" style="background:#334155;">${w.current_speed_mode}</span></div>
                        <div><i class="fa-solid fa-rotate" style="color: var(--text-muted); width: 16px;"></i> <strong>Work Cycles:</strong> ${w.lifetime_work_cycles || 0}</div>
                        <div><i class="fa-solid fa-sun" style="color: var(--text-muted); width: 16px;"></i> <strong>Day Skip Active:</strong> ${w.lifetime_day_skip_active ? "Yes" : "No"}</div>
                        <div><i class="fa-solid fa-hourglass" style="color: var(--text-muted); width: 16px;"></i> <strong>Cycle Duration:</strong> ${currentCycleDuration}</div>
                        <div><i class="fa-solid fa-bed" style="color: var(--text-muted); width: 16px;"></i> <strong>Sleeping?:</strong> ${w.sleep_mode ? "Yes" : "No"}</div>
                        <div><i class="fa-solid fa-crosshairs" style="color: var(--text-muted); width: 16px;"></i> <strong>HuntBot Active:</strong> ${w.huntbot_enabled ? "✅ Yes" : "❌ No"}</div>
                        <div><i class="fa-solid fa-brain" style="color: var(--text-muted); width: 16px;"></i> <strong>Solver Available:</strong> ${w.huntbot_solver_available ? "Yes" : "No"}</div>
                        <div><i class="fa-solid fa-recycle" style="color: var(--text-muted); width: 16px;"></i> <strong>Last Gem Check:</strong> ${lastGemCheck}</div>
                        <div style="margin-top: 5px; padding-top: 5px; border-top: 1px dashed var(--border);"><i class="fa-solid fa-list-check" style="color: var(--text-muted); width: 16px;"></i> <strong>Quests:</strong> ${activeQuestsText}</div>
                        <div style="margin-top: 5px; padding-top: 5px; border-top: 1px dashed var(--border);"><i class="fa-solid fa-ghost" style="color: var(--text-muted); width: 16px;"></i> <strong>Boss Tickets:</strong> ${w.boss_tickets}/3 ${w.is_boss_fighting ? '<span class="badge" style="background:#ef4444;">Fighting!</span>' : ''}</div>
                    </div>
                </div>
            `;

            let actionButtons = '';
            if (w.running && !w.paused) {
                actionButtons = `
                    <button class="btn btn-sm btn-warning" onclick="window.controlWorker(${w.worker_number}, 'pause')"><i class="fa-solid fa-pause"></i> Pause</button>
                    <button class="btn btn-sm btn-danger" onclick="window.controlWorker(${w.worker_number}, 'stop')"><i class="fa-solid fa-stop"></i> Stop</button>
                `;
            } else if (w.running && w.paused) {
                actionButtons = `
                    <button class="btn btn-sm btn-success" onclick="window.controlWorker(${w.worker_number}, 'resume')"><i class="fa-solid fa-play"></i> Resume</button>
                    <button class="btn btn-sm btn-danger" onclick="window.controlWorker(${w.worker_number}, 'stop')"><i class="fa-solid fa-stop"></i> Stop</button>
                `;
            } else {
                actionButtons = `<button class="btn btn-sm btn-primary" onclick="window.controlWorker(${w.worker_number}, 'start')"><i class="fa-solid fa-play"></i> Start</button>`;
            }

            controlHTML += `
                <div class="worker-control-card">
                    <div class="wcc-header">
                        <div>
                            <h4 style="margin-bottom:4px;">Worker #${w.worker_number}</h4>
                            <span class="text-muted" style="font-size:12px;">${displayUsername}</span>
                        </div>
                        ${statusBadge}
                    </div>
                    <div class="wcc-actions">
                        ${actionButtons}
                    </div>
                </div>
            `;
        });

        if (statusGrid) statusGrid.innerHTML = statusHTML;
        if (controlGrid) controlGrid.innerHTML = controlHTML;

        ['ctrl-speed-worker', 'ctrl-hb-worker', 'ctrl-pause-worker', 'ctrl-mail-worker'].forEach(id => {
            const el = document.getElementById(id);
            if (el && document.activeElement !== el) {
                const val = el.value;
                el.innerHTML = workerDropdownHTML;
                el.value = val || 'all';
            }
        });
        if (filterSelect && filterSelect.innerHTML !== filterHTML && filterHTML.length > 50) {
            filterSelect.innerHTML = filterHTML;
            filterSelect.value = currentFilter;
        }
    } catch (e) {
        console.error("Status fetch error", e);
    }
};

window.fetchLogs = async function () {
    try {
        const filterSelect = document.getElementById('console-filter');
        const filter = filterSelect ? filterSelect.value : 'all';
        let url = `${API_BASE}/logs`;
        if (filter !== 'all') url += `?worker=${filter}`;

        const res = await fetch(url);
        const logs = await res.json();
        const consoleOut = document.getElementById('console-output');

        if (logs.length > 0 && consoleOut) {
            let html = '';
            logs.forEach(log => {
                const date = new Date(log.timestamp * 1000);
                const timeStr = date.toLocaleTimeString();
                html += `<div class="log-line"><span class="log-time">[${timeStr}]</span> <span class="log-${log.level}">${log.formatted}</span></div>`;
            });
            consoleOut.innerHTML = html;
            if (isAutoScroll) {
                consoleOut.scrollTop = consoleOut.scrollHeight;
            }
        }
    } catch (e) {
        console.error("Log fetch error", e);
    }
};

window.fetchConfig = async function () {
    try {
        const res = await fetch(`${API_BASE}/config`);
        const data = await res.json();
        document.getElementById('settings-tokens').value = data.tokens;
        document.getElementById('settings-channels').value = data.channels;
    } catch (e) {
        console.error("Config fetch error", e);
    }
};

window.saveConfig = async function (type) {
    try {
        const val = document.getElementById(`settings-${type}`).value;
        const payload = {};
        payload[type] = val;

        const res = await fetch(`${API_BASE}/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            window.showToast("Saved successfully!", "success");
        }
    } catch (e) {
        window.showToast("Failed to save!", "error");
    }
};

window.restartScript = async function () {
    if (confirm("Are you sure you want to completely restart the bot script?")) {
        try {
            const res = await fetch(`${API_BASE}/restart`, { method: 'POST' });
            if (res.ok) {
                window.showToast("Restarting script! Dashboard will reconnect shortly...", "success");
                setTimeout(() => location.reload(), 3000);
            }
        } catch (e) {
            window.showToast("Failed to restart!", "error");
        }
    }
};

window.sayCommand = async function () {
    const input = document.getElementById('say-input');
    if (!input || !input.value.trim()) {
        window.showToast("Please enter text to say", "error");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/say`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: input.value })
        });
        const data = await res.json();
        if (data.success) {
            window.showToast(`Message sent to ${data.sent} workers!`, "success");
            input.value = "";
        } else {
            window.showToast("Failed: " + data.error, "error");
        }
    } catch (e) {
        window.showToast("Error sending message", "error");
    }
};

window.fetchProfit = async function () {
    const grid = document.getElementById('profit-grid');
    if (grid) grid.innerHTML = '<i>Fetching zoo data from Discord... (This may take a few seconds)</i>';

    try {
        const res = await fetch(`${API_BASE}/profit`);
        const data = await res.json();

        if (data.success && grid) {
            let html = `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; margin-top: 15px;">`;

            data.workers.forEach(w => {
                const profitColor = w.profit >= 0 ? 'var(--success)' : 'var(--danger)';
                const sign = w.profit >= 0 ? '+' : '';
                const displayUsername = isStreamerMode ? '***' : w.username;

                html += `
                    <div style="background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <h4 style="margin: 0; font-size: 16px;">Worker #${w.worker}</h4>
                            <span class="badge" style="background: #334155;">${w.status}</span>
                        </div>
                        <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 10px;">${displayUsername}</div>
                        
                        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border); padding-top: 10px;">
                            <div>
                                <div style="font-size: 11px; color: var(--text-muted);">PROFIT</div>
                                <div style="font-size: 18px; font-weight: bold; color: ${profitColor};">${sign}${w.profit_str}</div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 11px; color: var(--text-muted);">BALANCES</div>
                                <div style="font-size: 13px;">${w.start_cash} &rarr; ${w.current_cash}</div>
                            </div>
                        </div>
                    </div>
                `;
            });

            html += `</div>`;

            const totalColor = data.total_profit >= 0 ? 'var(--success)' : 'var(--danger)';
            const totalSign = data.total_profit >= 0 ? '+' : '';

            html += `
                <div style="margin-top: 20px; background: var(--bg-color); border-left: 4px solid var(--primary); padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 16px; font-weight: bold;">Total Cash Profit Across All Workers</div>
                    <div style="font-size: 24px; font-weight: bold; color: ${totalColor};">${totalSign}${data.total_profit_str}</div>
                </div>
            `;

            grid.innerHTML = html;
            window.showToast("Profit fetched successfully!", "success");
        } else {
            if (grid) grid.innerHTML = `<div class="text-danger">Failed to fetch profit: ${data.error || 'Unknown error'}</div>`;
            window.showToast("Failed to fetch profit", "error");
        }
    } catch (e) {
        if (grid) grid.innerHTML = `<div class="text-danger">Error: ${e.message}</div>`;
        window.showToast("Error fetching profit", "error");
    }
};

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(t => t.classList.remove('active'));

            btn.classList.add('active');
            const target = btn.getAttribute('data-target');
            const targetEl = document.getElementById(target);
            if (targetEl) targetEl.classList.add('active');

            const sidebar = document.getElementById('sidebar');
            if (window.innerWidth <= 768 && sidebar) {
                sidebar.classList.remove('open');
            }
            if (target === 'tab-settings') window.fetchConfig();
        });
    });

    const mobToggle = document.getElementById('mobile-toggle');
    const mobClose = document.getElementById('mobile-close');
    const sidebar = document.getElementById('sidebar');

    if (mobToggle) mobToggle.addEventListener('click', () => sidebar.classList.add('open'));
    if (mobClose) mobClose.addEventListener('click', () => sidebar.classList.remove('open'));

    const autoScrollToggle = document.getElementById('console-autoscroll');
    if (autoScrollToggle) {
        autoScrollToggle.addEventListener('change', (e) => {
            isAutoScroll = e.target.checked;
        });
    }

    const clearBtn = document.getElementById('console-clear');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            document.getElementById('console-output').innerHTML = '';
        });
    }

    const streamerModeToggle = document.getElementById('settings-streamer-mode');
    if (streamerModeToggle) {
        streamerModeToggle.checked = isStreamerMode;
        streamerModeToggle.addEventListener('change', (e) => {
            isStreamerMode = e.target.checked;
            localStorage.setItem('ghostyStreamerMode', isStreamerMode);
            window.fetchStatus();
            if (document.getElementById('tab-profit').classList.contains('active')) {
                window.fetchProfit();
            }
        });
    }

    setInterval(() => {
        window.fetchStatus();
        const tabConsole = document.getElementById('tab-console');
        if (tabConsole && tabConsole.classList.contains('active')) {
            window.fetchLogs();
        }
    }, 2000);

    window.fetchStatus();
    window.fetchLogs();
});
