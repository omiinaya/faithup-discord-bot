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
from .ai_conversation import ai_handler

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
        """Handle message events for bot mentions and AI conversations."""
        if (self.bot.user.mentioned_in(message) and
                not message.author.bot):
            
            # Check if it's a simple ping/pong
            if "ping" in message.content.lower():
                logger.info("on_message: ping detected from %s", message.author)
                await message.channel.send(t('pong', lang='en'))
                return
            
            # Handle AI conversation (which now includes command integration)
            await self._handle_ai_conversation(message)

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

    async def _handle_ai_conversation(self, message: discord.Message) -> None:
        """Handle AI conversation when bot is mentioned."""
        try:
            # Extract user message (remove bot mention)
            content = message.content
            for mention in message.mentions:
                content = content.replace(f"<@{mention.id}>", "").replace(f"<@!{mention.id}>", "")
            content = content.strip()
            
            if not content:  # Empty message after removing mention
                await message.channel.send(
                    f"Hello {message.author.mention}! How can I help you today?"
                )
                return
            
            # Show typing indicator
            async with message.channel.typing():
                # Generate AI response
                response = await ai_handler.generate_response(
                    message.author.id, content
                )
                
                # Send response (truncate if too long for Discord)
                if len(response) > 2000:
                    response = response[:1997] + "..."
                
                await message.channel.send(response)
                
        except Exception as e:
            logger.error(f"Error handling AI conversation: {e}")
            await message.channel.send(
                "Sorry, I encountered an error processing your message."
            )
    
    async def _try_execute_command(self, message: discord.Message, content: str) -> bool:
        """Try to execute a command based on natural language request."""
        # Map natural language requests to direct command execution
        command_mapping = {
            'verse of the day': self._execute_votd_direct,
            'bible verse': self._execute_votd_direct,
            'daily verse': self._execute_votd_direct,
            'roll dice': self._execute_roll_direct,
            'dice roll': self._execute_roll_direct,
            'coin flip': self._execute_coinflip_direct,
            'flip coin': self._execute_coinflip_direct,
            'flip a coin': self._execute_coinflip_direct,  # Added variation
            'slot machine': self._execute_slots_direct,
            'russian roulette': self._execute_roulette_direct,
            'random number': self._execute_roll_direct,
            'balding percentage': self._execute_balding_direct,
            'source code': self._execute_source_direct,
        }
        
        content_lower = content.lower()
        
        for phrase, command_func in command_mapping.items():
            if phrase in content_lower:
                try:
                    # If this is RPS, we need special handling
                    if 'rock paper scissors' in content_lower:
                        await message.channel.send(
                            f"{message.author.mention}, to play Rock-Paper-Scissors, "
                            f"use `!rps @username` to challenge someone!"
                        )
                        return True
                    
                    # Execute the command directly
                    await command_func(message)
                    return True
                    
                except Exception as e:
                    logger.error(f"Error executing command for '{phrase}': {e}")
                    # Fallback to suggestion
                    command_name = phrase.split()[-1] if ' ' in phrase else phrase
                    await message.channel.send(
                        f"{message.author.mention}, you can use `!{command_name}` for that!"
                    )
                    return True
        
        return False
    
    async def _execute_votd_direct(self, message: discord.Message) -> None:
        """Execute votd command directly."""
        try:
            from .youversion.client import YouVersionClient
            client = YouVersionClient()
            verse_data = client.get_formatted_verse_of_the_day(None)
            
            message_text = (
                f"📖 **Verse of the Day**\n"
                f"**{verse_data['human_reference']}**\n"
                f"{verse_data['verse_text']}"
            )
            
            await message.channel.send(message_text)
            
        except Exception as e:
            logger.error(f"Error fetching verse of the day: {e}")
            await message.channel.send(
                f"{message.author.mention}, I couldn't fetch the verse of the day. "
                "Please try again later."
            )
    
    async def _execute_roll_direct(self, message: discord.Message) -> None:
        """Execute roll command directly."""
        random_number = random.randint(1, 100)
        message_text = f"{message.author.mention}, you rolled a {random_number}!"
        await message.channel.send(message_text)
    
    async def _execute_coinflip_direct(self, message: discord.Message) -> None:
        """Execute coinflip command directly."""
        outcome = random.choice(['heads', 'tails'])
        message_text = f"{message.author.mention}, the coin landed on {outcome}!"
        await message.channel.send(message_text)
    
    async def _execute_slots_direct(self, message: discord.Message) -> None:
        """Execute slots command directly."""
        emojis = [":cherries:", ":lemon:", ":strawberry:",
                  ":grapes:", ":seven:", ":bell:"]
        slot1 = random.choice(emojis)
        slot2 = random.choice(emojis)
        slot3 = random.choice(emojis)
        result = f"{slot1} | {slot2} | {slot3}"
        if slot1 == slot2 == slot3:
            message_text = f"{result}\n🎉 Jackpot! {message.author.mention} wins!"
        else:
            message_text = f"{result}\nBetter luck next time, {message.author.mention}!"
        await message.channel.send(message_text)
    
    async def _execute_roulette_direct(self, message: discord.Message) -> None:
        """Execute roulette command directly."""
        outcome = random.randint(1, 6)
        if outcome == 6:
            message_text = f"💥 BANG! {message.author.mention} didn't make it... (rolled {outcome}/6)"
        else:
            message_text = f"🔫 Click... {message.author.mention} survives! (rolled {outcome}/6)"
        await message.channel.send(message_text)
    
    async def _execute_balding_direct(self, message: discord.Message) -> None:
        """Execute balding command directly."""
        percent = random.randint(0, 100)
        if percent == 0:
            message_text = f"{message.author.mention}, you have a full head of hair! 0% balding."
        else:
            message_text = f"{message.author.mention}, you are {percent}% balding."
        await message.channel.send(message_text)
    
    async def _execute_source_direct(self, message: discord.Message) -> None:
        """Execute source command directly."""
        message_text = (
            f"{message.author.mention}, here's the source code: "
            "https://github.com/omiinaya/faithup-discord-bot"
        )
        await message.channel.send(message_text)

    @commands.command()
    async def clear_chat(self, ctx: commands.Context) -> None:
        """Clear your conversation history with the AI."""
        logger.info("clear_chat called by %s", ctx.author)
        if ai_handler.clear_conversation(ctx.author.id):
            await ctx.send(
                f"{ctx.author.mention}, your conversation history has been cleared."
            )
        else:
            await ctx.send(
                f"{ctx.author.mention}, you don't have an active conversation to clear."
            )

    @commands.command()
    async def source(self, ctx: commands.Context) -> None:
        """Returns the GitHub source code link."""
        logger.info("source called by %s", ctx.author)
        message = (f"{ctx.author.mention}, here's the source code: "
                   "https://github.com/omiinaya/faithup-discord-bot")
        await ctx.send(message)

    @commands.command()
    async def bingbong(self, ctx: commands.Context,
                       *, question: Optional[str] = None) -> None:
        """Ask Bing Bong a question and get a random response."""
        logger.info("bingbong called by %s with question: %s",
                    ctx.author, question)
        
        # Get all response lists
        positive = t('bingbong_positive', lang='en')
        negative = t('bingbong_negative', lang='en')
        uncertain = t('bingbong_uncertain', lang='en')
        irrelevant = t('bingbong_irrelevant', lang='en')
        
        # Combine all response types
        all_responses = positive + negative + uncertain + irrelevant
        
        # Select a random response
        response = random.choice(all_responses)
        
        # If a question was provided, format the response to acknowledge it
        if question:
            message = (f"{ctx.author.mention} asked: \"{question}\"\n"
                       f"🎤 Bing Bong says: \"{response}\"")
        else:
            message = f"{ctx.author.mention}, Bing Bong says: \"{response}\""
            
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
            ("clear_chat", "Clear your AI conversation history"),
            ("source", t('desc_source', lang=lang)),
            ("bingbong", t('desc_bingbong', lang=lang)),
        ]
        command_list = "\n".join([f"`{name}`: {desc}" for name, desc in cmds])
        msg = "**Available Commands:**\n" + command_list
        await ctx.send(msg)


async def setup(bot: commands.Bot) -> None:
    """Setup function to add the cog to the bot."""
    await bot.add_cog(MyCog(bot))
