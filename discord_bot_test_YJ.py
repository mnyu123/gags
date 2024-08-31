import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일에서 환경 변수를 로드합니다.

# 환경 변수에서 민감한 정보를 가져옵니다.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_APP_ID = int(os.getenv("DISCORD_APP_ID"))
GAG_CHANNEL_ID = int(os.getenv("GAG_CHANNEL_ID"))


intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            sync_command=True,
            application_id=DISCORD_APP_ID
        )
        self.gag_channel_id = GAG_CHANNEL_ID  # 이 부분을 올바른 채널 ID로 변경하세요

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
        
        activity = discord.Game("아재개그 테스트")
        await self.change_presence(status=discord.Status.online, activity=activity)

    @tasks.loop(seconds=10)
    async def gag_task(self):
        print(f"봇이 적용중인 ID: {self.gag_channel_id}")
        channel = self.get_channel(self.gag_channel_id)
        print(f"Channel: {channel}")
        if channel:
            print("Channel found")
            gag = self.get_gag()
            await channel.send(f"@everyone {gag}")
            print("Message sent")
        else:
            print("Channel not found")

    def get_gag(self):
        # 파일을 UTF-8 인코딩으로 엽니다.
        with open('gags.txt', 'r', encoding='utf-8') as file:
            gags = file.readlines()

        # 무작위로 개그 하나를 선택해서 반환
        import random
        return random.choice(gags).strip()

    @app_commands.command(name="ping")
    async def ping(self, ctx: commands.Context) -> None:
        await ctx.send("pong!")

bot = MyBot()
bot.run(DISCORD_TOKEN)