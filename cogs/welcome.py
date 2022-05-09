import asyncio
from nextcord.ext import commands
import nextcord
import subprocess
from subprocess import PIPE
import os
import sys
from nextcord import Interaction, SlashOption, ChannelType
from cogs.debug import save

sys.path.append('../')
from util import admin_check, n_fc, eh

# join message system
# Copilotでちょっとだけ楽をした。

#loggingの設定
import logging

class NoTokenLogFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        return 'token' not in message

logger = logging.getLogger(__name__)
logger.addFilter(NoTokenLogFilter())
formatter = '%(asctime)s$%(filename)s$%(lineno)d$%(funcName)s$%(levelname)s:%(message)s'
logging.basicConfig(format=formatter, filename=f'/home/nattyantv/nira_bot_rewrite/nira.log', level=logging.INFO)

class welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="welcome", aliases=("youkoso","goodbye","ようこそ","Welcome"), help="""\
ユーザーが加入/離脱したときに、特定のメッセージをこのチャンネルに送信するようにします。
書き方: `n!welcome [join/leave]` `[メッセージ]`
(メッセージは複数行可能です。)

メッセージ内には`%name%`/`%count%`/`%ment%`と入れることで、それぞれ`ユーザー名`/`ユーザー数`/`メンション`に置き換わります。

・例
```
n!welcome join %name%さんこんちゃ！！！！！
```

```
n!welcome leave %name%さんばいばい！！！
```

""")
    async def welcome(self, ctx: commands.Context):
        if not admin_check.admin_check(ctx.guild, ctx.author):
            await ctx.reply("・Welcomeメッセージコマンド\nエラー：権限がありません。")
            return  
        args = ctx.message.content.split(" ", 3)
        if len(args) != 3:
            await ctx.reply(f"・Welcomeメッセージコマンド\nエラー：書き方が間違っています。")
            return
        if args[1] != "join" and args[1] != "leave":
            await ctx.reply(f"・Welcomeメッセージコマンド\nエラー：書き方が間違っています。")
            return
        if ctx.guild.id not in n_fc.welcome_message_list:
            n_fc.welcome_message_list[ctx.guild.id] = {args[1]: (args[2], ctx.channel.id)}
        else:
            n_fc.welcome_message_list[ctx.guild.id][args[1]] = (args[2], ctx.channel.id)
        await ctx.reply(f"・Welcomeメッセージコマンド\n・成功\n```\n{args[2]}```\n{ctx.channel.name}にメッセージを設定しました。")
        save()
        return
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id not in n_fc.welcome_message_list:
            return
        if "join" not in n_fc.welcome_message_list[member.guild.id]:
            return
        message = n_fc.welcome_message_list[member.guild.id]["join"][0]
        message = message.replace("%name%", member.name)
        message = message.replace("%count%", str(len(member.guild.members)))
        message = message.replace("%ment%", member.mention)
        CHANNEL = member.guild.get_channel(n_fc.welcome_message_list[member.guild.id]["join"][1])
        await CHANNEL.send(message)
        return
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id not in n_fc.welcome_message_list:
            return
        if "leave" not in n_fc.welcome_message_list[member.guild.id]:
            return
        message = n_fc.welcome_message_list[member.guild.id]["leave"][0]
        message = message.replace("%name%", member.name)
        message = message.replace("%count%", str(len(member.guild.members)))
        message = message.replace("%ment%", member.mention)
        CHANNEL = member.guild.get_channel(n_fc.welcome_message_list[member.guild.id]["leave"][1])
        await CHANNEL.send(message)
        return

def setup(bot):
    bot.add_cog(welcome(bot))
