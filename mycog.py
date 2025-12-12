"""MyCog module for Discord bot commands implementing various fun utilities."""
import logging
import random
from typing import Optional

import discord
from dotenv import load_dotenv
from redbot.core import commands

from .localization import t
from .utils import is_valid_member
from .youversion.client import YouVersionClient

# Load environment variables from .env file.
load_dotenv()
logger = logging.getLogger("red.cogfaithup.mycog")


class MyCog(commands.Cog):
    """My custom cog with fun commands and best practices."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info("MyCog loaded and initialized.")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def roll(self, ctx: commands.Context, lang: str = 'en') -> None:
        """Roll a random number from 1-100."""
        logger.info("roll called by %s", ctx.author)
        random_number = random.randint(1, 100)
        message = t('roll', lang=lang, user=ctx.author.mention,
                    number=random_number)
        await ctx.send(message)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dice(self, ctx: commands.Context) -> None:
        """Roll a random number from 1-6. (5s cooldown per user)"""
        logger.info("dice called by %s", ctx.author)
        random_number = random.randint(1, 6)
        message = f"{ctx.author.mention}, you rolled a {random_number}"
        await ctx.send(message)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def rps(self, ctx: commands.Context,
                  opponent: commands.MemberConverter) -> None:
        """Play Rock-Paper-Scissors against another player."""
        logger.info("rps called by %s vs %s", ctx.author, opponent)
        try:
            valid, error = is_valid_member(ctx, opponent)
            if not valid:
                await ctx.send(error)
                return
            choices = ["rock", "paper", "scissors"]
            user_choice = random.choice(choices)
            opponent_choice = random.choice(choices)
            result = None

            # Simplify the complex boolean expression
            win_conditions = {
                ("rock", "scissors"): True,
                ("scissors", "paper"): True,
                ("paper", "rock"): True
            }

            if user_choice == opponent_choice:
                result = t('draw', lang='en')
            elif win_conditions.get(
                (user_choice, opponent_choice)
            ):
                result = t('user_win', lang='en', user=ctx.author.mention)
            else:
                result = t('opponent_win', lang='en', opponent=opponent.mention)

            # Fix line length by splitting the long line
            message = t('rps_result', lang='en',
                        user=ctx.author.mention,
                        user_choice=user_choice,
                        opponent=opponent.mention,
                        opponent_choice=opponent_choice,
                        result=result)
            await ctx.send(message)
        except discord.DiscordException as e:
            logger.error("Error in rps command: %s", e)
            await ctx.send(f"Error: {e}")

    @commands.command()
    async def measure(self, ctx: commands.Context) -> None:
        """Responds randomly with 1 - 14 inches."""
        measurement = random.randint(1, 14)
        message = f"{ctx.author.mention}, you measured {measurement} inches."
        await ctx.send(message)

    @commands.command()
    async def secret(self, ctx: commands.Context,
                     target: commands.MemberConverter, *, message: str) -> None:
        """Sends a secret message to the specified user."""
        logger.info("secret called by %s targeting %s with message: %s",
                    ctx.author, target, message)
        try:
            # Allow sending messages to self for testing
            if target == ctx.author:
                await ctx.send("Sending test message to yourself...")

            await target.send(t('secret_dm', lang='en', message=message))
            check_msg = t('secret_check_dm', lang='en', user=ctx.author.mention)
            await ctx.send(check_msg)
        except discord.Forbidden:
            fail_msg = t('secret_dm_fail', lang='en', user=ctx.author.mention)
            await ctx.send(fail_msg)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Handle message events for bot mentions."""
        if (self.bot.user.mentioned_in(message) and
                not message.author.bot):
            if "ping" in message.content.lower():
                logger.info("on_message: ping detected from %s", message.author)
                await message.channel.send(t('pong', lang='en'))

    @commands.command()
    async def roulette(self, ctx: commands.Context) -> None:
        """Play text-based Russian roulette."""
        logger.info("roulette called by %s",
                    ctx.author)
        try:
            outcome = random.randint(1, 6)
            if outcome == 6:
                await ctx.send(t('roulette_dead', lang='en', outcome=outcome))
            else:
                await ctx.send(t('roulette_survive', lang='en', outcome=outcome))
        except discord.DiscordException as e:
            logger.error("Error in roulette command: %s", e)
            error_msg = t('roulette_error', lang='en', error=e)
            await ctx.send(error_msg)

    @commands.command()
    async def slots(self, ctx: commands.Context) -> None:
        """Play a slot machine game with Discord emojis."""
        logger.info("slots called by %s",
                    ctx.author)
        emojis = [":cherries:", ":lemon:", ":strawberry:",
                  ":grapes:", ":seven:", ":bell:"]
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
    async def coinflip(self, ctx: commands.Context) -> None:
        """Flip a coin and return heads or tails."""
        logger.info("coinflip called by %s", ctx.author)
        outcome = random.choice(['heads', 'tails'])
        message = f"{ctx.author.mention}, the coin landed on {outcome}!"
        await ctx.send(message)

    @commands.command()
    async def decide(self, ctx: commands.Context) -> None:
        """Randomly decide yes or no."""
        logger.info("decide called by %s", ctx.author)
        if random.random() < 0.5:
            result = t('decide_yes', lang='en')
        else:
            result = t('decide_no', lang='en')
        await ctx.send(result)

    @commands.command()
    async def balding(self, ctx: commands.Context) -> None:
        """Returns a random balding percentage."""
        logger.info("balding called by %s", ctx.author)
        percent = random.randint(0, 100)
        if percent == 0:
            message = t('balding_none', lang='en')
        else:
            message = t('balding_percent', lang='en',
                        user=ctx.author.mention, percent=percent)
        await ctx.send(message)

    @commands.command()
    async def votd(self, ctx: commands.Context, day: Optional[int] = None) -> None:
        """Get the Verse of the Day from YouVersion."""
        logger.info("votd called by %s", ctx.author)
        
        try:
            client = YouVersionClient()
            verse_data = client.get_formatted_verse_of_the_day(day)
            
            # Format the message
            message = (
                f"📖 **Verse of the Day**\n"
                f"**{verse_data['human_reference']}**\n"
                f"{verse_data['verse_text']}"
            )
            
            await ctx.send(message)
            
        except ValueError as e:
            logger.error("Error fetching verse of the day: %s", e)
            error_msg = (
                f"{ctx.author.mention}, I couldn't fetch the verse of the day. "
                "Please check if YOUVERSION_USERNAME and YOUVERSION_PASSWORD "
                "are set correctly in the environment variables."
            )
            await ctx.send(error_msg)
        except Exception as e:
            logger.error("Unexpected error in votd command: %s", e)
            await ctx.send(
                f"{ctx.author.mention}, an unexpected error occurred. "
                "Please try again later."
            )

    @commands.command()
    async def source(self, ctx: commands.Context) -> None:
        """Returns the GitHub source code link."""
        logger.info("source called by %s", ctx.author)
        message = (f"{ctx.author.mention}, here's the source code: "
                   "https://github.com/omiinaya/faithup-discord-bot")
        await ctx.send(message)

    @commands.command()
    async def commands(self, ctx: commands.Context, lang: str = 'en') -> None:
        """Lists all available commands and their descriptions."""
        logger.info("commands called by %s", ctx.author)
        cmds = [
            ("roll", t('desc_roll', lang=lang)),
            ("dice", t('desc_dice', lang=lang)),
            ("rps", t('desc_rps', lang=lang)),
            ("measure", t('desc_measure', lang=lang)),
            ("secret", t('desc_secret', lang=lang)),
            ("roulette", t('desc_roulette', lang=lang)),
            ("slots", t('desc_slots', lang=lang)),
            ("coinflip", t('desc_coinflip', lang=lang)),
            ("decide", t('desc_decide', lang=lang)),
            ("balding", t('desc_balding', lang=lang)),
            ("votd", "Get the Verse of the Day from YouVersion"),
            ("source", t('desc_source', lang=lang)),
        ]
        command_list = "\n".join([f"`{name}`: {desc}" for name, desc in cmds])
        msg = "**Available Commands:**\n" + command_list
        await ctx.send(msg)


async def setup(bot: commands.Bot) -> None:
    """Setup function to add the cog to the bot."""
    await bot.add_cog(MyCog(bot))
