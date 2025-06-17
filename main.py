import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import re
from typing import List, Dict

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class SplitCalculator:
    def __init__(self, total_loot: int, participants: List[Dict]):
        self.total_loot = total_loot
        self.participants = participants
        self.total_repairs = sum(p['repair'] for p in participants)
        self.net_loot = total_loot - self.total_repairs

    def calculate_splits(self) -> List[Dict]:
        num_participants = len(self.participants)
        base_share = self.net_loot / num_participants
        
        results = []
        for participant in self.participants:
            final_share = base_share + participant['repair']
            results.append({
                'user': participant['user'],
                'repair': participant['repair'],
                'share': final_share
            })
        
        return results

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="split", description="Split loot between participants with repair costs")
async def split(interaction: discord.Interaction, total_loot: int, participants: str):
    try:
        # Convert total loot to integer (in case it comes with commas)
        total_loot = int(str(total_loot).replace(',', ''))
        
        # Parse participants and their repair costs
        participant_list = []
        pattern = r'<@!?(\d+)>:(\d+)'
        
        for match in re.finditer(pattern, participants):
            user_id = int(match.group(1))
            repair_cost = int(match.group(2))
            user = await bot.fetch_user(user_id)
            participant_list.append({
                'user': user,
                'repair': repair_cost
            })
        
        if not participant_list:
            await interaction.response.send_message("No valid participants found. Please use the format: @user:repair_cost")
            return
        
        # Calculate splits
        calculator = SplitCalculator(total_loot, participant_list)
        results = calculator.calculate_splits()
        
        # Create embed
        embed = discord.Embed(
            title="Loot Split Results",
            color=discord.Color.green()
        )
        
        # Add total information
        embed.add_field(
            name="Total Loot",
            value=f"{total_loot:,} silver",
            inline=False
        )
        embed.add_field(
            name="Total Repairs",
            value=f"{calculator.total_repairs:,} silver",
            inline=False
        )
        embed.add_field(
            name="Net Loot",
            value=f"{calculator.net_loot:,} silver",
            inline=False
        )
        
        # Add individual splits
        for result in results:
            embed.add_field(
                name=f"{result['user'].name}'s Share",
                value=f"Repair: {result['repair']:,} silver\nFinal Share: {int(result['share']):,} silver",
                inline=True
            )
        
        await interaction.response.send_message(embed=embed)
        
    except ValueError as e:
        await interaction.response.send_message(f"Error: Invalid number format. Please check your input. Details: {str(e)}")
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}")

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable not set.")
    bot.run(token) 