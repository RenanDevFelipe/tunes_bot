import discord
from discord.ext import commands
import asyncio
import yt_dlp

DISCORD_TOKEN = 'seu_token_aqui'

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

ytdlp_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
}

ytdlp = yt_dlp.YoutubeDL(ytdlp_format_options)

class MusicPlayer:
    def __init__(self, bot):
        self.bot = bot
        self.queue = asyncio.Queue()
        self.voice_client = None
        self.current_text_channel = None
        self.play_next_song = asyncio.Event()

    async def play_music(self):
        while True:
            self.play_next_song.clear()
            song = await self.queue.get()
            await self.send_playing_message(song)
            try:
                ffmpeg_options = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': '-vn'
                }
                source = discord.FFmpegPCMAudio(song['url'], **ffmpeg_options)
                self.voice_client.play(source, after=lambda e: self.bot.loop.call_soon_threadsafe(self.play_next_song.set))
                await self.play_next_song.wait()
            except Exception as e:
                await self.current_text_channel.send(f'Erro ao tocar a música: {e}')
                print(f'Erro ao tocar a música: {e}')

    async def send_playing_message(self, song):
        embed = discord.Embed(
            title=f'Tocando: {song["title"]}',
            description=f'[Link da música]({song["webpage_url"]})',
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=song['thumbnail'])
        await self.current_text_channel.send(embed=embed)

    def add_to_queue(self, song):
        self.queue.put_nowait(song)
        print(f'Adicionado à fila: {song["title"]}')

        if self.voice_client and not self.voice_client.is_playing():
            asyncio.ensure_future(self.play_music())

    async def start_playing(self, ctx, song_url):
        self.current_text_channel = ctx.channel
        if not self.voice_client or not self.voice_client.is_connected():
            await self.join_voice_channel(ctx)

        info = await self.bot.loop.run_in_executor(None, lambda: ytdlp.extract_info(song_url, download=False))
        if 'entries' in info:
            info = info['entries'][0]

        song = {
            'title': info.get('title'),
            'url': info['url'],
            'webpage_url': info.get('webpage_url'),
            'thumbnail': info.get('thumbnail')
        }

        print(f'Adicionando à fila: {song["title"]}')
        self.add_to_queue(song)

    async def join_voice_channel(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            try:
                self.voice_client = await channel.connect()
                print(f'Conectado ao canal de voz: {channel}')
                await ctx.send(f'Conectado ao canal de voz: {channel}')
                if not self.bot.loop.is_running():
                    self.bot.loop.create_task(self.play_music())
            except discord.ClientException as e:
                print(f'Erro ao conectar ao canal de voz: {e}')
                await ctx.send(f'Erro ao conectar ao canal de voz: {e}')
            except Exception as e:
                print(f'Erro inesperado: {e}')
                await ctx.send(f'Erro inesperado: {e}')
        else:
            await ctx.send("Você não está conectado a um canal de voz.")

    async def disconnect_voice_channel(self, ctx):
        if self.voice_client and self.voice_client.is_connected():
            await self.voice_client.disconnect()

    async def pause(self, ctx):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()
            await ctx.send("Música pausada.")

    async def resume(self, ctx):
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()
            await ctx.send("Música retomada.")

bot = commands.Bot(command_prefix='!', description='Um bot para tocar música do YouTube no Discord', intents=intents)
music_player = MusicPlayer(bot)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name} ({bot.user.id})')

@bot.command()
async def join(ctx, *, channel: discord.VoiceChannel = None):
    if channel is None:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
        else:
            await ctx.send('Você precisa especificar um canal de voz ou estar em um para usar esse comando.')
            return

    await music_player.join_voice_channel(ctx)

@bot.command()
async def leave(ctx):
    """Comando para desconectar o bot do canal de voz."""
    await music_player.disconnect_voice_channel(ctx)

@bot.command()
async def play(ctx, *, query):
    """Toca uma música do YouTube."""
    async with ctx.typing():
        await music_player.start_playing(ctx, query)

@bot.command()
async def stop(ctx):
    """Para e desconecta o bot do canal de voz."""
    await music_player.disconnect_voice_channel(ctx)

@bot.command()
async def pause(ctx):
    """Pausa a música."""
    await music_player.pause(ctx)

@bot.command()
async def resume(ctx):
    """Retoma a música."""
    await music_player.resume(ctx)

bot.run(DISCORD_TOKEN)
