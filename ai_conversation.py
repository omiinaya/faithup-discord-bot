"""AI Conversation handler for Discord bot using NVIDIA API."""
import os
import logging
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
            # Initialize with system message including command context
            system_message = (
                "You are a helpful AI assistant in a Discord server. "
                "Be friendly, engaging, and keep responses concise "
                "but meaningful. You can have conversations about "
                "various topics but maintain appropriate discord "
                "server etiquette.\n\n"
                "IMPORTANT: When users ask about available commands or "
                "specific functionality, you should inform them about "
                "the relevant commands. Here are the available commands:\n\n"
                f"{self.command_descriptions}\n\n"
                "When a user asks for something that can be accomplished "
                "with a command, suggest they use the appropriate command "
                "and briefly explain what it does."
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
    
    async def generate_response(self, user_id: int, user_message: str) -> str:
        """Generate AI response for a user's message."""
        try:
            conversation_history = self._get_conversation_history(user_id)
            
            # Add user message to history
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
            
            # Check if the AI response suggests a command execution
            command_response = self._check_command_execution(ai_response, user_message)
            if command_response:
                return command_response
            
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
    
    def _check_command_execution(self, ai_response: str, user_message: str) -> Optional[str]:
        """Check if the user wants to execute a command and provide appropriate response."""
        import re
        
        # Map natural language requests to commands with execution instructions
        command_mapping = {
            'verse of the day': ('votd', 'I can fetch the Verse of the Day for you! Use `!votd` to get today\'s Bible verse.'),
            'bible verse': ('votd', 'Use `!votd` to retrieve today\'s Bible verse from YouVersion'),
            'daily verse': ('votd', 'Try `!votd` to see today\'s Verse of the Day'),
            'roll dice': ('roll', 'You can roll a random number (1-100) with `!roll`'),
            'dice roll': ('roll', 'Use `!roll` for a random number between 1 and 100'),
            'coin flip': ('coinflip', 'Flip a coin with `!coinflip` - it\'ll give you heads or tails!'),
            'flip coin': ('coinflip', 'Try `!coinflip` for a coin toss'),
            'rock paper scissors': ('rps', 'Challenge someone with `!rps @username` to play Rock-Paper-Scissors'),
            'slot machine': ('slots', 'Play the slot machine game with `!slots`'),
            'russian roulette': ('roulette', 'Try your luck with `!roulette` for text-based Russian roulette'),
            'random number': ('roll', 'Get a random number using `!roll`'),
            'balding percentage': ('balding', 'Check your balding percentage with `!balding`'),
            'secret message': ('secret', 'Send a secret message with `!secret @user your message`'),
            'source code': ('source', 'Get the GitHub source code link with `!source`'),
            'available commands': ('commands', 'See all available commands with `!commands`'),
            'list commands': ('commands', 'Use `!commands` to list all available commands')
        }
        
        # Check user message for natural language command requests
        user_message_lower = user_message.lower()
        matched_commands = []
        
        for phrase, (command, instruction) in command_mapping.items():
            if phrase in user_message_lower:
                matched_commands.append((command, instruction))
        
        # If we found specific command requests, provide execution instructions
        if matched_commands:
            # For single command requests, provide specific instructions
            if len(matched_commands) == 1:
                command, instruction = matched_commands[0]
                return f"{instruction}"
            else:
                # For multiple commands, list them all
                command_list = ", ".join([f"`!{cmd}`" for cmd, _ in matched_commands])
                instructions = "\n".join([f"- {instr}" for _, instr in matched_commands])
                return (
                    f"I can help you with several commands: {command_list}\n\n"
                    f"{instructions}\n\n"
                    f"Just type the command you'd like to use!"
                )
        
        return None
    
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