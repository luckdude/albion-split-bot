# Albion Split Bot

A Discord bot for splitting loot and repair costs in Albion Online.

## Features

- Split loot between multiple players
- Account for individual repair costs
- Clean embed message with detailed breakdown
- Support for any number of participants

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Discord bot token:
   ```
   DISCORD_TOKEN=your_token_here
   ```

## Usage

Use the `!split` command with the following format:
```
!split <total_loot> <@user1>:<repair> <@user2>:<repair> ...
```

Example:
```
!split 1200000 @Bob:50000 @Alice:25000
```

## Deployment Options

### Railway.app

1. Create a new project on Railway.app
2. Connect your GitHub repository
3. Add the following environment variable:
   - `DISCORD_TOKEN`: Your Discord bot token
4. Deploy!

### Replit

1. Create a new Python repl
2. Upload the project files
3. Add the following environment variable in the Secrets tab:
   - `DISCORD_TOKEN`: Your Discord bot token
4. Run the bot using:
   ```python
   python main.py
   ```

## Development

The project is structured to make it easy to add new features. To add new commands:

1. Create new command functions in `main.py`
2. Use the `@bot.command()` decorator
3. Add any necessary database or storage functionality

## License

MIT License 