"""AI Conversation handler for Discord bot using NVIDIA API."""
import os
import logging
import random
from typing import Dict, List, Optional
from openai import OpenAI

logger = logging.getLogger("red.cogfaithup.ai_conversation")


class AIConversationHandler:
    """Handles AI conversations with users using NVIDIA API."""
    
    def __init__(self):
        self._client = None
        self.model = "deepseek-ai/deepseek-v3.1-terminus"
        # user_id -> message history
        self.conversations: Dict[int, List[Dict[str, str]]] = {}
        self.command_descriptions = self._get_command_descriptions()
    
    def _get_command_descriptions(self) -> str:
        """Get descriptions of available commands for AI context."""
        commands = [
            ("roll", "Roll a random number from 1-100"),
            ("dice", "Roll a random number from 1-6"),
            ("rps", "Play Rock-Paper-Scissors against another player"),
            ("measure", "Responds randomly with 1 - 14 inches"),
            ("secret", "Sends a secret message to another user"),
            ("roulette", "Play text-based Russian roulette"),
            ("slots", "Play a slot machine game with Discord emojis"),
            ("coinflip", "Flip a coin and return heads or tails"),
            ("decide", "Randomly decide yes or no"),
            ("balding", "Returns a random balding percentage"),
            ("votd", "Get the Verse of the Day from YouVersion"),
            ("clear_chat", "Clear your AI conversation history"),
            ("source", "Returns the GitHub source code link"),
            ("commands", "Lists all available commands and their descriptions")
        ]
        return "\n".join([f"!{cmd}: {desc}" for cmd, desc in commands])
    
    @property
    def client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            api_key = os.getenv("NVIDIA_API_KEY")
            if not api_key:
                raise ValueError("NVIDIA_API_KEY environment variable is not set")
            self._client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=api_key
            )
        return self._client
        
    def _get_conversation_history(self, user_id: int) -> List[Dict[str, str]]:
        """Get or create conversation history for a user."""
        if user_id not in self.conversations:
            # Initialize with system message including command integration
            system_message = (
                "You are a helpful AI assistant in a Discord server. "
                "Be friendly, engaging, and keep responses concise "
                "but meaningful. You can have conversations about "
                "various topics but maintain appropriate discord "
                "server etiquette.\n\n"
                "SPECIAL INSTRUCTIONS FOR COMMAND INTEGRATION:\n"
                "When users ask you to perform actions that match available commands, "
                "you should incorporate the command results into your response naturally. "
                "For example, if someone asks you to flip a coin, you might say: "
                "\"Sure! I flipped a coin for you and it landed on heads! 🪙\" "
                "Always integrate the action result conversationally rather than "
                "just stating the result."
            )
            self.conversations[user_id] = [
                {
                    "role": "system",
                    "content": system_message
                }
            ]
        return self.conversations[user_id]
    
    def _trim_conversation_history(
        self, 
        history: List[Dict[str, str]], 
        max_messages: int = 10
    ) -> List[Dict[str, str]]:
        """Trim conversation history to maintain context window."""
        if len(history) > max_messages:
            # Keep system message and recent messages
            return [history[0]] + history[-(max_messages-1):]
        return history
    
    async def generate_response(self, user_id: int, user_message: str, message_context=None) -> str:
        """Generate AI response for a user's message with command integration."""
        try:
            conversation_history = self._get_conversation_history(user_id)
            
            # Check if this message contains a command request
            command_result = await self._detect_and_execute_command(user_message, message_context)
            
            if command_result:
                # Add command result to the conversation context
                enhanced_message = f"{user_message}\n\n[Command Result: {command_result}]"
                conversation_history.append(
                    {"role": "user", "content": enhanced_message}
                )
            else:
                # Add normal user message
                conversation_history.append(
                    {"role": "user", "content": user_message}
                )
            
            # Trim history if needed
            conversation_history = self._trim_conversation_history(
                conversation_history
            )
            
            # Generate response
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=conversation_history,
                temperature=0.2,
                top_p=0.7,
                max_tokens=1024,
                extra_body={"chat_template_kwargs": {"thinking": True}},
                stream=False  # Use non-streaming for simplicity
            )
            
            ai_response = completion.choices[0].message.content
            
            # Add AI response to history
            conversation_history.append(
                {"role": "assistant", "content": ai_response}
            )
            
            # Update conversation history
            self.conversations[user_id] = conversation_history
            
            return ai_response
            
        except Exception as e:
            logger.error(
                f"Error generating AI response for user {user_id}: {e}"
            )
            return (
                "Sorry, I'm having trouble processing your message right now. "
                "Please try again later."
            )
    
    async def _detect_and_execute_command(self, user_message: str, message_context) -> Optional[str]:
        """Detect command requests and execute them, returning the result."""
        import random
        
        # Map natural language requests to command execution
        command_mapping = {
            'verse of the day': self._execute_votd,
            'bible verse': self._execute_votd,
            'daily verse': self._execute_votd,
            'roll dice': self._execute_roll,
            'dice roll': self._execute_roll,
            'coin flip': self._execute_coinflip,
            'flip coin': self._execute_coinflip,
            'flip a coin': self._execute_coinflip,
            'slot machine': self._execute_slots,
            'russian roulette': self._execute_roulette,
            'random number': self._execute_roll,
            'balding percentage': self._execute_balding,
        }
        
        user_message_lower = user_message.lower()
        
        for phrase, command_func in command_mapping.items():
            if phrase in user_message_lower:
                try:
                    return await command_func()
                except Exception as e:
                    logger.error(f"Error executing command for '{phrase}': {e}")
                    return f"Error executing {phrase}: {str(e)}"
        
        return None
    
    async def _execute_roll(self) -> str:
        """Execute roll command and return result."""
        random_number = random.randint(1, 100)
        return f"Rolled a {random_number} on a d100"
    
    async def _execute_coinflip(self) -> str:
        """Execute coinflip command and return result."""
        outcome = random.choice(['heads', 'tails'])
        return f"Coin landed on {outcome}"
    
    async def _execute_slots(self) -> str:
        """Execute slots command and return result."""
        emojis = [":cherries:", ":lemon:", ":strawberry:", ":grapes:", ":seven:", ":bell:"]
        slot1 = random.choice(emojis)
        slot2 = random.choice(emojis)
        slot3 = random.choice(emojis)
        result = f"{slot1} | {slot2} | {slot3}"
        if slot1 == slot2 == slot3:
            return f"{result} - JACKPOT!"
        else:
            return f"{result} - No win"
    
    async def _execute_roulette(self) -> str:
        """Execute roulette command and return result."""
        outcome = random.randint(1, 6)
        if outcome == 6:
            return f"BANG! Didn't make it (rolled {outcome}/6)"
        else:
            return f"Survived! (rolled {outcome}/6)"
    
    async def _execute_balding(self) -> str:
        """Execute balding command and return result."""
        percent = random.randint(0, 100)
        if percent == 0:
            return "Full head of hair - 0% balding"
        else:
            return f"{percent}% balding"
    
    async def _execute_votd(self) -> str:
        """Execute votd command and return result."""
        try:
            # Import inside function to avoid circular imports
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            from youversion.client import YouVersionClient
            client = YouVersionClient()
            verse_data = client.get_formatted_verse_of_the_day(None)
            return f"Verse of the Day: {verse_data['human_reference']} - {verse_data['verse_text'][:100]}..."
        except Exception as e:
            return f"Error fetching verse: {str(e)}"
    
    def clear_conversation(self, user_id: int) -> bool:
        """Clear conversation history for a user."""
        if user_id in self.conversations:
            del self.conversations[user_id]
            return True
        return False
    
    def get_conversation_count(self) -> int:
        """Get number of active conversations."""
        return len(self.conversations)


# Global instance
ai_handler = AIConversationHandler()