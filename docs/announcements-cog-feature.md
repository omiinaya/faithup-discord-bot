# Daily Announcements Cog Feature

## Overview

The Daily Announcements Cog provides automated scheduled messaging functionality for Discord servers. It allows server administrators to set up recurring announcements that are automatically sent at specified times.

## Features

- **Scheduled Announcements**: Set up daily announcements at specific times
- **Multiple Announcements**: Configure multiple announcements per server
- **Individual Control**: Enable/disable announcements independently
- **Test Functionality**: Test announcements before they go live
- **Permission Management**: Requires `manage_guild` permission for configuration

## Commands

### `[p]announcement add <channel> <time> <message>`
Add a new daily announcement.

**Parameters:**
- `channel`: The text channel where the announcement should be sent
- `time`: Time in 24-hour format (HH:MM)
- `message`: The announcement message content

**Example:**
```
[p]announcement add #general 09:00 Good morning everyone! Have a blessed day.
```

### `[p]announcement list`
List all announcements configured for the current server.

### `[p]announcement remove <id>`
Remove an announcement by its ID.

### `[p]announcement enable <id>`
Enable a disabled announcement.

### `[p]announcement disable <id>`
Disable an announcement (keeps it configured but stops it from sending).

### `[p]announcement test <id>`
Send a test announcement immediately.

## Technical Implementation

### Architecture
- Uses `discord.ext.tasks` for scheduling
- Stores configuration in Red-DiscordBot's Config system
- Runs a background task that checks every minute for announcements due
- Proper error handling for permission and channel issues

### Configuration Storage
Announcements are stored with the following structure:
```json
{
  "id": 1,
  "guild_id": 123456789,
  "channel_id": 987654321,
  "time": {"hour": 9, "minute": 0},
  "message": "Announcement text",
  "enabled": true
}
```

### Scheduling Logic
The cog runs a background task that:
1. Checks every minute if announcements are enabled globally
2. Iterates through all configured announcements
3. For each enabled announcement, checks if current time matches scheduled time
4. Sends the announcement if conditions are met
5. Handles errors gracefully (missing channels, permissions, etc.)

## Error Handling

The cog includes comprehensive error handling:

- **Missing Channels**: Logs warning and skips announcement
- **Permission Issues**: Logs warning and skips announcement
- **Invalid Time Format**: Provides clear error messages to users
- **Configuration Errors**: Graceful degradation with logging

## Integration

The cog integrates seamlessly with:
- Red-DiscordBot's permission system
- Discord.py's channel and message systems
- Existing bot logging infrastructure

## Usage Examples

### Basic Daily Greeting
```
[p]announcement add #general 09:00 🌅 Good morning! Time for daily devotion.
```

### Multiple Daily Announcements
```
[p]announcement add #devotionals 07:00 📖 Daily Bible reading time!
[p]announcement add #prayer-requests 20:00 🙏 Evening prayer session starting soon.
[p]announcement add #general 22:00 🌙 Good night! Rest well in God's peace.
```

### Testing Before Deployment
```
[p]announcement add #announcements 18:30 🎉 Weekend service reminder!
[p]announcement test 1  # Test the announcement
[p]announcement enable 1  # Activate it
```

## Best Practices

1. **Test First**: Always use the test command before enabling announcements
2. **Clear Messages**: Keep announcement messages concise and clear
3. **Reasonable Timing**: Avoid scheduling announcements during late night hours
4. **Channel Selection**: Choose appropriate channels for different types of announcements
5. **Regular Review**: Periodically review and update announcements

## Troubleshooting

### Announcements Not Sending
1. Check if the announcement is enabled: `[p]announcement list`
2. Verify bot permissions in the target channel
3. Ensure the channel still exists
4. Check bot logs for error messages

### Time Format Issues
- Use 24-hour format (HH:MM)
- Valid range: 00:00 to 23:59
- Example: `09:30` for 9:30 AM, `21:15` for 9:15 PM

### Permission Errors
- The bot needs `Send Messages` permission in the target channel
- Users need `Manage Server` permission to configure announcements

## Development Notes

- Built as a separate cog for modularity
- Follows Red-DiscordBot coding standards
- Includes comprehensive logging
- Uses async/await patterns throughout
- Proper cleanup on cog unload