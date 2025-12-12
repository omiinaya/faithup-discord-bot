import random
import requests
import os
import discord
from dotenv import load_dotenv
from redbot.core import commands
from datetime import datetime
import logging
from typing import Optional
from .utils import is_valid_member
from .api_helpers import fetch_json
from .localization import t

# Load environment variables from .env file
load_dotenv()
logger = logging.getLogger("red.coghedrin.mycog")

# Check for required environment variables at startup
REQUIRED_ENV_VARS = ["SAMPLE_API", "WEATHER_API", "DAYNIGHT_API"]
for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        logger.warning(f"Environment variable {var} is not set. Some commands may not work.")

class MyCog(commands.Cog):
    """My custom cog with fun commands and best practices."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info("MyCog loaded and initialized.")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def roll(self, ctx: commands.Context, lang: str = 'en') -> None:
        """Roll a random number from 1-100. (5s cooldown per user, supports localization)"""
        logger.info(f"roll called by {ctx.author}")
        random_number = random.randint(1, 100)
        await ctx.send(t('roll', lang=lang, user=ctx.author.mention, number=random_number))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dice(self, ctx: commands.Context) -> None:
        """Roll a random number from 1-6. (5s cooldown per user)"""
        logger.info(f"dice called by {ctx.author}")
        random_number = random.randint(1, 6)
        await ctx.send(f"{ctx.author.mention}, you rolled a {random_number}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def rps(self, ctx: commands.Context, opponent: commands.MemberConverter) -> None:
        """Play Rock-Paper-Scissors against another player. (10s cooldown per user)"""
        logger.info(f"rps called by {ctx.author} vs {opponent}")
        try:
            valid, error = is_valid_member(ctx, opponent)
            if not valid:
                await ctx.send(error)
                return
            choices = ["rock", "paper", "scissors"]
            user_choice = random.choice(choices)
            opponent_choice = random.choice(choices)
            result = None
            if user_choice == opponent_choice:
                result = t('draw', lang='en')
            elif (user_choice == "rock" and opponent_choice == "scissors") or \
                 (user_choice == "scissors" and opponent_choice == "paper") or \
                 (user_choice == "paper" and opponent_choice == "rock"):
                result = t('user_win', lang='en', user=ctx.author.mention)
            else:
                result = t('opponent_win', lang='en', opponent=opponent.mention)
            await ctx.send(
                t('rps_result', lang='en', user=ctx.author.mention, user_choice=user_choice, opponent=opponent.mention, opponent_choice=opponent_choice, result=result)
            )
        except Exception as e:
            logger.error(f"Error in rps command: {e}")
            await ctx.send(f"Error: {e}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def apicall(self, ctx: commands.Context, url: Optional[str] = None) -> None:
        """Makes an API call and returns the response. Optionally takes a URL argument. (10s cooldown per user)"""
        logger.info(f"apicall called by {ctx.author} with url={url}")
        api_url = url or os.getenv('SAMPLE_API')
        if not api_url or not api_url.startswith(('http://', 'https://')):
            await ctx.send(t('api_url_invalid', lang='en'))
            return
        try:
            response = requests.get(api_url, timeout=10)
            logger.info(f"API call to {api_url} returned status {response.status_code}")
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    data = response.json()
                    message = t('api_response', lang='en', data=data)
                else:
                    data = response.text
                    message = t('api_response', lang='en', data=data)
                if len(message) > 1800:
                    message = message[:1800] + '... (truncated)'
                await ctx.send(message)
            else:
                await ctx.send(t('api_failed', lang='en', status=response.status_code))
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            await ctx.send(t('api_failed_exception', lang='en', error=e))
        except Exception as e:
            logger.error(f"Unexpected error in apicall: {e}")
            await ctx.send(t('unexpected_error', lang='en', error=e))
    
    @commands.command()
    async def weather(self, ctx):
        """Returns the current weather type for Eastern Americas and time until the next weather type."""
        url = os.getenv('WEATHER_API')
        data = fetch_json(url)
        if data:
            eastern_america_data = data[0]['data']['Eastern Americas']
            current_weather, time_until_next, next_weather = self.get_current_weather(eastern_america_data)
            message = f"Current weather is '{current_weather}'. Time until '{next_weather}' is {time_until_next}."
        else:
            message = "Failed to retrieve data from the API."
        await ctx.send(message)

    @commands.command()
    async def timeofday(self, ctx):
        """Returns the current time of day for Eastern Americas and time until the next one."""
        url = os.getenv('DAYNIGHT_API')
        data = fetch_json(url)
        if data:
            eastern_america_data = data[0]['data']['Eastern Americas']
            current_time_of_day, time_until_next, next_time_of_day = self.get_current_time_of_day(eastern_america_data)
            message = f"Current time of day is '{current_time_of_day}'. Time until '{next_time_of_day}' is {time_until_next}."
        else:
            message = "Failed to retrieve data from the API."
        await ctx.send(message)

    @commands.command()
    async def measure(self, ctx):
        """Responds randomly with 1 - 14 inches."""
        measurement = random.randint(1, 14)
        await ctx.send(f"{ctx.author.mention}, you measured {measurement} inches.")
        
    @commands.command()
    async def secret(self, ctx: commands.Context) -> None:
        """Sends a secret message to the user who invoked the command."""
        logger.info(f"secret called by {ctx.author}")
        try:
            await ctx.author.send(t('secret_dm', lang='en'))
            await ctx.send(t('secret_check_dm', lang='en', user=ctx.author.mention))
        except discord.Forbidden:
            await ctx.send(t('secret_dm_fail', lang='en', user=ctx.author.mention))
            
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if self.bot.user.mentioned_in(message) and not message.author.bot:
            if "ping" in message.content.lower():
                logger.info(f"on_message: ping detected from {message.author}")
                await message.channel.send(t('pong', lang='en'))
                
    @commands.command()
    async def roulette(self, ctx: commands.Context) -> None:
        """Play text-based Russian roulette where you have a 1/6 chance to die."""
        logger.info(f"roulette called by {ctx.author}")
        try:
            outcome = random.randint(1, 6)
            if outcome == 6:
                await ctx.send(t('roulette_dead', lang='en', outcome=outcome))
            else:
                await ctx.send(t('roulette_survive', lang='en', outcome=outcome))
        except Exception as e:
            logger.error(f"Error in roulette command: {e}")
            await ctx.send(t('roulette_error', lang='en', error=e))

    @commands.command()
    async def slots(self, ctx: commands.Context) -> None:
        """Play a slot machine game with Discord emojis."""
        logger.info(f"slots called by {ctx.author}")
        emojis = [":cherries:", ":lemon:", ":strawberry:", ":grapes:", ":seven:", ":bell:"]
        slot1 = random.choice(emojis)
        slot2 = random.choice(emojis)
        slot3 = random.choice(emojis)
        result = f"{slot1} | {slot2} | {slot3}"
        if slot1 == slot2 == slot3:
            message = t('slots_jackpot', lang='en', user=ctx.author.mention)
        else:
            message = t('slots_lose', lang='en', user=ctx.author.mention)
        await ctx.send(f"{result}\n{message}")

    @commands.command()
    async def coinflip(self, ctx: commands.Context, bet_on: Optional[str] = None, lang: str = 'en') -> None:
        """Play text-based coin flip game."""
        logger.info(f"coinflip called by {ctx.author} with bet_on={bet_on}")
        if not bet_on:
            await ctx.send(t('coinflip_specify', lang=lang))
            return
        try:
            bet_on = bet_on.lower()
            if bet_on not in ['even', 'odd', 'par', 'impar']:
                await ctx.send(t('coinflip_specify', lang=lang))
                return
            outcome = random.randint(1, 2)
            result = "odd" if outcome == 1 else "even"
            # Support Spanish synonyms
            if bet_on in ['par', 'even']:
                bet_on = 'even'
            elif bet_on in ['impar', 'odd']:
                bet_on = 'odd'
            if bet_on == result:
                await ctx.send(t('coinflip_win', lang=lang, result=result))
            else:
                await ctx.send(t('coinflip_lose', lang=lang, result=result))
        except Exception as e:
            logger.error(f"Error in coinflip command: {e}")
            await ctx.send(t('coinflip_error', lang=lang, error=e))

    @commands.command()
    async def decide(self, ctx: commands.Context) -> None:
        """Randomly decide yes or no."""
        logger.info(f"decide called by {ctx.author}")
        await ctx.send(t('decide_yes', lang='en') if random.random() < 0.5 else t('decide_no', lang='en'))

    @commands.command()
    async def balding(self, ctx: commands.Context) -> None:
        """Returns a random balding percentage."""
        logger.info(f"balding called by {ctx.author}")
        percent = random.randint(0, 100)
        if percent == 0:
            await ctx.send(t('balding_none', lang='en'))
        else:
            await ctx.send(t('balding_percent', lang='en', user=ctx.author.mention, percent=percent))

    @commands.command()
    async def commands(self, ctx: commands.Context, lang: str = 'en') -> None:
        """Lists all available commands and their descriptions."""
        logger.info(f"commands called by {ctx.author}")
        cmds = [
            ("roll", t('desc_roll', lang=lang)),
            ("dice", t('desc_dice', lang=lang)),
            ("rps", t('desc_rps', lang=lang)),
            ("apicall", t('desc_apicall', lang=lang)),
            ("measure", t('desc_measure', lang=lang)),
            ("secret", t('desc_secret', lang=lang)),
            ("roulette", t('desc_roulette', lang=lang)),
            ("slots", t('desc_slots', lang=lang)),
            ("coinflip", t('desc_coinflip', lang=lang)),
            ("decide", t('desc_decide', lang=lang)),
            ("balding", t('desc_balding', lang=lang)),
        ]
        msg = "**Available Commands:**\n" + "\n".join([f"`{name}`: {desc}" for name, desc in cmds])
        await ctx.send(msg)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MyCog(bot))