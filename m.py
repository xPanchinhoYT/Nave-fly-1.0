import asyncio
import random
from pyodide.ffi import create_proxy
from js import document, window, localStorage, Image

# --- Configuración del Canvas ---
canvas = document.getElementById("gameCanvas")
ctx = canvas.getContext("2d")

def resize():
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
resize()

# --- CARGA DE IMÁGENES ---
images_ready = 0
def image_loaded(event):
    global images_ready
    images_ready += 1

img_nave = Image.new()
img_nave.onload = create_proxy(image_loaded)
img_nave.src = "nave.png"

img_cierra = Image.new()
img_cierra.onload = create_proxy(image_loaded)
img_cierra.src = "cierra.png"

# --- Variables de Juego ---
WIDTH, HEIGHT = canvas.width, canvas.height
MARGIN = 50
player = {"x": 100, "y": HEIGHT//2, "w": 75, "h": 55, "vel_y": 0}
obstacles = []
stars = []
keys = {}
start_time = window.performance.now()
pause_start = 0
total_pause_time = 0
game_speed = 7
running = True
paused = False

immortal = False
immortal_end_time = 0
last_star_spawn_time = -1

# CARGAR RÉCORD AL INICIO
def get_high_score():
    saved = localStorage.getItem("max_record")
    return int(saved) if saved else 0

high_score = get_high_score()

FRASES = [
    "Hecho por el SUPER PROGRAMADOR xPanchinhoYT 🤑",
    "Cuidado con las bolas 😳",
    "Que record tan pobre ese que tienes 😫",
    "Tu contraseña es Soy_manco123*",
    "WOOOW Crei que yo era manco 😨",
    "Que pende 😂🫵🏻",
    "Obteniendo acceso de la camara... 🤢",    #<<<<< Esa es la libreria de frases XD
    "67",
    "zV1P NEVER DIEEEEE!!!",
    "VAMO QUE SI SE PUEDE 🤪",
    "Como que te gusta tocar las... Mejor no 😏",
    "Apostamos que no puedes compartir tu record en la comunidad de xPanchinhoYT 🤣",
    "Ni yo se como funciona esto (Soy muy pro 😎)",
    "Por tu culpa los servidores de xPanchinhoYT estan sobre saturados por todas las veces que haz muerto"




]

def on_keydown(event):
    global paused, pause_start, total_pause_time
    keys[event.code] = True
    if event.code == "Escape" and running:
        if not paused:
            paused = True
            pause_start = window.performance.now()
    if event.code == "Enter" and paused:
        paused = False
        total_pause_time += window.performance.now() - pause_start

document.addEventListener("keydown", create_proxy(on_keydown))
document.addEventListener("keyup", create_proxy(lambda e: keys.update({e.code: False})))

# --- CONTROLES UNIVERSALES (V1.2) ---
def start_up(event):
    keys["ArrowUp"] = True
    if event.type == "touchstart":
        event.preventDefault() # Evita zoom raro en móvil

def stop_up(event):
    keys["ArrowUp"] = False

# Eventos para Mouse
canvas.addEventListener("mousedown", create_proxy(start_up))
window.addEventListener("mouseup", create_proxy(stop_up))

# Eventos para Pantalla Táctil
canvas.addEventListener("touchstart", create_proxy(start_up))
canvas.addEventListener("touchend", create_proxy(stop_up))


async def game_loop():
    global running, game_speed, WIDTH, HEIGHT, paused, high_score, immortal, immortal_end_time, last_star_spawn_time
    
    while images_ready < 2:
        ctx.fillStyle = "#1a1a1a"; ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.fillStyle = "white"; ctx.textAlign = "center"
        ctx.fillText("CARGANDO TEXTURAS...", canvas.width/2, canvas.height/2)
        await asyncio.sleep(0.1)

    while running:
        resize()
        WIDTH, HEIGHT = canvas.width, canvas.height
        now = window.performance.now()
        
        if not paused:
            seconds = int((now - start_time - total_pause_time) / 1000)
            
            if immortal and now > immortal_end_time:
                immortal = False
            
            if keys.get("ArrowUp"): player["vel_y"] -= 1.2
            else: player["vel_y"] += 0.6
            
            player["vel_y"] = max(-12, min(12, player["vel_y"]))
            player["y"] += player["vel_y"]

            if player["y"] <= MARGIN or player["y"] + player["h"] >= HEIGHT - MARGIN:
                if not immortal: running = False
                else: player["y"] = max(MARGIN, min(HEIGHT-MARGIN-player["h"], player["y"]))

            if seconds > 0 and seconds % 20 == 0 and last_star_spawn_time != seconds:
                last_star_spawn_time = seconds
                star_y = random.randint(MARGIN + 100, HEIGHT - MARGIN - 100)
                stars.append({"x": WIDTH + 100, "y": star_y, "r": 30})

            game_speed = 7 + (seconds / 2.5)
            if random.random() < 0.06:
                r = random.randint(60, 120)
                obstacles.append({"x": WIDTH + 300, "y": random.randint(MARGIN+100, HEIGHT-MARGIN-100), "r": r})

            for obs in obstacles[:]:
                obs["x"] -= game_speed
                px = player["x"] + player["w"]/2
                py = player["y"] + player["h"]/2
                dist = ((obs["x"] - px)**2 + (obs["y"] - py)**2)**0.5
                if dist < obs["r"] * 0.6: 
                    if not immortal: running = False
                if obs["x"] < -400: obstacles.remove(obs)

            for star in stars[:]:
                star["x"] -= game_speed
                dx = star["x"] - (player["x"] + player["w"]/2)
                dy = star["y"] - (player["y"] + player["h"]/2)
                if (dx**2 + dy**2)**0.5 < 50: 
                    immortal = True
                    immortal_end_time = now + 10000 
                    stars.remove(star)
                elif star["x"] < -100: stars.remove(star)
        else:
            seconds = int((pause_start - start_time - total_pause_time) / 1000)
        
        # --- DIBUJO ---
        ctx.fillStyle = "#222222"; ctx.fillRect(0, 0, WIDTH, HEIGHT)
        ctx.fillStyle = "black"; ctx.fillRect(0, 0, WIDTH, MARGIN); ctx.fillRect(0, HEIGHT - MARGIN, WIDTH, MARGIN) 

        if not immortal or (int(now/100) % 2 == 0):
            ctx.drawImage(img_nave, player["x"], player["y"], player["w"], player["h"])

        for obs in obstacles:
            aspect = img_cierra.width / img_cierra.height
            h_vis = obs["r"] * 2
            w_vis = h_vis * aspect
            ctx.drawImage(img_cierra, obs["x"] - w_vis/2, obs["y"] - h_vis/2, w_vis, h_vis)

        for star in stars:
            ctx.font = "40px Arial"; ctx.textAlign = "center"
            ctx.fillText("⭐", star["x"], star["y"] + 15)

        # UI (PUNTUACIÓN Y RÉCORD)
        ctx.textAlign = "right"
        # Dibujar récord
        ctx.font = "20px Impact"
        ctx.fillStyle = "rgba(255, 215, 0, 0.8)" # Color oro suave
        ctx.fillText(f"Record: {high_score}s", WIDTH - 30, 40)
        
        # Dibujar tiempo actual
        ctx.font = "60px Impact"
        ctx.fillStyle = "#00f2ff" if immortal else "white"
        ctx.fillText(f"{seconds}s", WIDTH - 30, 100)
        
        if immortal:
            ctx.font = "20px Arial"
            ctx.fillText(f"INMORTAL, APROVECHA EL BUG!!: {int((immortal_end_time - now)/1000)}s", WIDTH - 30, 135)


        await asyncio.sleep(0.016)

    # --- GAME OVER ---
    final_score = int((window.performance.now() - start_time - total_pause_time) / 1000)
    es_nuevo_record = False
    
    if final_score > high_score:
        high_score = final_score
        localStorage.setItem("max_record", str(high_score))
        es_nuevo_record = True

    ctx.fillStyle = "rgba(0,0,0,0.95)"; ctx.fillRect(0, 0, WIDTH, HEIGHT)
    ctx.textAlign = "center"; ctx.fillStyle = "white"; ctx.font = "70px Impact"
    ctx.fillText("SE TERMINO JAJAJA", WIDTH/2, HEIGHT/2 - 50)
    
    if es_nuevo_record:
        ctx.fillStyle = "#FFD700"; ctx.font = "50px Impact"
        ctx.fillText("NUEVO RECORD!!", WIDTH/2, HEIGHT/2 + 20)
    
    ctx.fillStyle = "#00f2ff"; ctx.font = "25px Arial"
    ctx.fillText(random.choice(FRASES), WIDTH/2, HEIGHT/2 + 80)
    ctx.fillStyle = "white"
    ctx.fillText(f"Puntuación: {final_score}s | Record actual: {high_score}s", WIDTH/2, HEIGHT/2 + 130)
    
    await asyncio.sleep(4); window.location.reload()

asyncio.ensure_future(game_loop())