"""AI Conversation handler for Discord bot using NVIDIA API."""
import os
import logging
from typing import Dict, List
from openai import OpenAI

logger = logging.getLogger("red.cogfaithup.ai_conversation")


class AIConversationHandler:
    """Handles AI conversations with users using NVIDIA API."""
    
    def __init__(self):
        self._client = None
        self.model = "deepseek-ai/deepseek-v3.1-terminus"
        # user_id -> message history
        self.conversations: Dict[int, List[Dict[str, str]]] = {}
    
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
            # Initialize with system message
            self.conversations[user_id] = [
                {
                    "role": "system", 
                    "content": (
                        "You are a helpful AI assistant in a Discord server. "
                        "Be friendly, engaging, and keep responses concise "
                        "but meaningful. You can have conversations about "
                        "various topics but maintain appropriate discord "
                        "server etiquette."
                    )
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