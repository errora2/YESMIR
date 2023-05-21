import disnake
from disnake.ext import commands

import asyncio
import yt_dlp


bot = commands.Bot(command_prefix="!", help_command=None, intents=disnake.Intents.all(), test_guilds=[1109888999323074672])

CENSORED_WORDS = ["репа"]


voice_clients = {}

yt_dl_opts = {'format': 'bestaudio/best'}
ytdl = yt_dlp.YoutubeDL(yt_dl_opts)

ffmpeg_options = {'options': "-vn"}

@bot.event
async def on_message(msg):
    if msg.content.startswith("play"):

        try:
            voice_client = await msg.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
        except:
            print("error")

        try:
            url = msg.content.split()[1]

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

            song = data['url']
            player = disnake.FFmpegPCMAudio(song, **ffmpeg_options)

            voice_clients[msg.guild.id].play(player)

        except Exception as err:
            print(err)

    if msg.content.startswith("pause"):
        try:
            voice_clients[msg.guild.id].pause()
        except Exception as err:
            print(err)

    if msg.content.startswith("resume"):
        try:
            voice_clients[msg.guild.id].resume()
        except Exception as err:
            print(err)

    # This stops the current playing song
    if msg.content.startswith("stop"):
        try:
            voice_clients[msg.guild.id].stop()
            await voice_clients[msg.guild.id].disconnect()
        except Exception as err:
            print(err)

@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready to work!")

@bot.event
async def on_member_join(member):
    role = disnake.utils.get(member.guild.roles, id=1109177181499834438)
    channel = bot.get_channel(1109817575937933382)

    embed = disnake.Embed(
        title="Новый участник!",
        description=f"{member.name}#{member.discriminator}",color=0xffffff)

    await member.add_roles(role)
    await channel.send(embed=embed)

@bot.event
async def on_message(message):
    await bot.process_commands(message)

    for content in message.content.split():
        for censored_word in CENSORED_WORDS:
            if content == censored_word:
                await message.delete()
                await message.channel.send(f'{message.author.mention} такие слова запрещены!')

@bot.event
async def on_command_error(ctx, error):
    print(error)

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{ctx.author}, у вас недостаточно прав для выполнения данной команды!")
    elif isinstance(error, commands.UserInputError):
        await ctx.send(embed=disnake.Embed(
            description=f"Правильное использование команды: `{ctx.prefix}{ctx.command.name}` ({ctx.command.brief})\nExample: {ctx.prefix}{ctx.command.usage}"))

@bot.command()
@commands.has_permissions(kick_members=True, administrator=True)
async def kick(ctx, member: disnake.Member, *, reason="Нарушение правил!"):
    await ctx.send(f"Администратор {ctx.author.mention} исключил пользователя {member.mention}", delete_after=2)
    await member.kick(reason=reason)
    await ctx.message.delete()

@bot.command(name="бан", aliases=["забанить", "выдать бан"])
@commands.has_permissions(ban_members=True, administrator=True)
async def ban(ctx, member: disnake.Member, *, reason="Нарушение правил!"):
    await ctx.send(f"Администратор {ctx.author.mention} забанил пользователя {member.mention}", delete_after=2)
    await member.ban(reason=reason)
    await ctx.message.delete()

@bot.command(aliases=['j', 'J', 'jn', 'JN','Jn', 'Join', 'JOIN'])
async def join(ctx):
    if ctx.message.author.voice:
        if not ctx.voice_client:
            await ctx.message.author.voice.channel.connect(reconnect=True)
        else:
            await ctx.voice_client.move_to(ctx.message.author.voice.channel)
    else:
        await ctx.message.reply('Вы должны находиться в голосовом канале')


@bot.command(aliases=['Disconnect', 'DISCONNECT', 'DC', 'dc', 'Dc', 'Disc', 'disc'])
async def disconnect(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run("MTEwODY5MjM4NTI0NTk2MjI3MA.GBtiyn.iCjnIEMz-4OwQsXTtbJU8YSZjZao_rFZGgXMjI")