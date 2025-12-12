# AI Conversation Feature

This document describes the AI conversation feature added to the Discord bot.

## Overview

The bot now supports AI-powered conversations when users mention it (`@botname`). The feature uses NVIDIA's AI API with the DeepSeek V3.1 Terminus model to provide intelligent responses.

## Features

- **Mention-based Conversations**: Users can start conversations by mentioning the bot
- **Conversation Memory**: The bot maintains conversation context for each user
- **Memory Management**: Users can clear their conversation history with the `clear_chat` command
- **Typing Indicators**: Shows typing indicator while generating responses
- **Message Length Handling**: Automatically truncates long responses for Discord limits
- **Command Recognition**: AI intelligently recognizes when users ask about commands and provides execution instructions
- **Command Execution**: AI can automatically execute commands when users ask for them
- **Natural Language Understanding**: Understands various ways users might ask for commands (e.g., "verse of the day", "roll dice", "flip coin")

## Configuration

### Environment Variables

Add the following to your `.env` file:

```env
# NVIDIA AI API Configuration
# Get your API key from https://build.nvidia.com/
NVIDIA_API_KEY=your_nvidia_api_key_here
```

### Dependencies

The feature requires the `openai` package, which has been added to `requirements.txt`.

## Usage

### Starting a Conversation

Simply mention the bot in any message:

```
@FaithUpBot Hello! How are you doing today?
```

### Command Execution

The AI can automatically execute commands when you ask for them:

```
@FaithUpBot What is the verse of the day?
→ The bot will fetch and display today's Bible verse

@FaithUpBot I want to roll some dice
→ The bot will roll a random number and show the result

@FaithUpBot Flip a coin for me
→ The bot will flip a coin and show heads or tails

@FaithUpBot Play slots
→ The bot will run the slot machine game
```

The bot recognizes natural language requests and executes the appropriate commands automatically.

### Clearing Conversation History

Use the `clear_chat` command to reset your conversation memory:

```
!clear_chat
```

## Technical Implementation

### Files Added/Modified

- [`ai_conversation.py`](../ai_conversation.py): AI conversation handler class
- [`mycog.py`](../mycog.py): Modified `on_message` listener and added `clear_chat` command
- [`requirements.txt`](../requirements.txt): Added `openai` dependency
- [`.env`](../.env): Added `NVIDIA_API_KEY` environment variable
- [`.env.example`](../.env.example): Updated example configuration

### Architecture

- **AIConversationHandler**: Main class handling AI conversations and memory
- **Memory Management**: Each user gets their own conversation history (max 10 messages)
- **Command Recognition**: Natural language processing to detect command requests
- **Command Execution**: Direct execution of command logic when requested
- **Command Mapping**: Maps various phrases to specific bot commands
- **Error Handling**: Graceful error handling with user-friendly messages
- **Performance**: Non-streaming API calls for simplicity and reliability

## API Details

- **Model**: `deepseek-ai/deepseek-v3.1-terminus`
- **Provider**: NVIDIA AI API (`https://integrate.api.nvidia.com/v1`)
- **Temperature**: 0.2 (for consistent responses)
- **Max Tokens**: 1024 (for reasonable response length)
- **Context Window**: 10 messages per user

## Testing

The feature has been tested with:
- API connectivity verification
- Conversation memory persistence
- Error handling scenarios
- Message length truncation

## Limitations

- Conversation memory is stored in-memory and will reset when the bot restarts
- Maximum response length is 2000 characters (Discord limit)
- API rate limits may apply depending on NVIDIA's pricing tier

## Future Enhancements

- Persistent conversation storage (database)
- Conversation statistics and analytics
- Customizable conversation parameters per user
- Support for multiple AI models