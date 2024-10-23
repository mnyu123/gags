import random
from flask import Flask
from threading import Thread
import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_APP_ID = int(os.getenv("DISCORD_APP_ID"))
GAG_CHANNEL_ID = int(os.getenv("GAG_CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True  # 이 옵션을 켜야 멤버의 온라인 상태를 가져올 수 있습니다.
intents.members = True  # 서버 멤버 정보를 가져오기 위해 필요

app = Flask('')


@app.route('/')
def home():
    return "Bot is alive!"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


class MyBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="!",
                         intents=intents,
                         sync_command=True,
                         application_id=DISCORD_APP_ID)
        self.gag_channel_id = GAG_CHANNEL_ID

    async def setup_hook(self):
        self.gag_task.start()
        await self.tree.sync()

    async def on_ready(self):
        print("아재개그 봇 준비완료!")
        print("가능한 디코 채널목록:")
        for guild in self.guilds:
            for channel in guild.text_channels:
                print(f"Channel: {channel.name}, ID: {channel.id}")
        channel = self.get_channel(self.gag_channel_id)
        if channel:
            permissions = channel.permissions_for(channel.guild.me)
            print(f"읽기 권한 가능한지: {permissions.read_messages}")
            print(f"쓰기 권한 가능한지: {permissions.send_messages}")
            print(f"태그 everyone가능한지: {permissions.mention_everyone}")
        else:
            print("채널을 찾을수 없음")

        activity = discord.Game("아재개그 생각")
        await self.change_presence(status=discord.Status.online,
                                   activity=activity)

    @tasks.loop(seconds=60)  # minutes=30 seconds hours
    async def gag_task(self):
        print(f"봇이 적용중인 ID: {self.gag_channel_id}")
        channel = self.get_channel(self.gag_channel_id)
        print(f"채널: {channel}")
        if channel:
            print("채널 찾음")
            gag = self.get_gag()
            online_members = self.get_online_members(channel.guild)
            if online_members:
                random_member = random.choice(online_members)
                mention = random_member.mention
                await channel.send(f"{mention} {gag}")
                print("메시지 성공적으로 전송완료.")
            else:
                await channel.send(gag)
        else:
            print("Channel not found")

    def get_gag(self):
        # 파일을 UTF-8 인코딩으로 엽니다.
        with open('gags.txt', 'r', encoding='utf-8') as file:
            gags = file.readlines()

        # 무작위로 개그 하나를 선택해서 반환
        import random
        return random.choice(gags).strip()

    def get_online_members(self, guild):
        # 서버에서 온라인,자리비움 상태인 멤버를 가져옵니다.
        online_members = []
        for member in guild.members:
            if member.status in [discord.Status.online, discord.Status.idle] and not member.bot:
                online_members.append(member)
        return online_members

    @app_commands.command(name="ping")
    async def ping(self, ctx: commands.Context) -> None:
        await ctx.send("pong!")


bot = MyBot()

keep_alive()  # 이 함수로 웹 서버가 실행됩니다.
bot.run(DISCORD_TOKEN)
