import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import re
from typing import List, Dict, Optional

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
bot = commands.Bot(intents=intents)

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

class LootSplitter(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="split",
        description="Split loot between participants with repair costs"
    )
    @app_commands.describe(
        total_loot="Total amount of silver to split",
        participants="List of participants and their repair costs (format: @user:repair_cost @user2:repair_cost2)"
    )
    async def split(
        self,
        interaction: discord.Interaction,
        total_loot: int,
        participants: str
    ):
        try:
            # Parse participants and their repair costs
            participant_list = []
            pattern = r'<@!?(\d+)>:(\d+)'
            
            for match in re.finditer(pattern, participants):
                user_id = int(match.group(1))
                repair_cost = int(match.group(2))
                user = await self.bot.fetch_user(user_id)
                participant_list.append({
                    'user': user,
                    'repair': repair_cost
                })
            
            if not participant_list:
                await interaction.response.send_message(
                    "No valid participants found. Please use the format: @user:repair_cost",
                    ephemeral=True
                )
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
            await interaction.response.send_message(
                f"Error: Invalid number format. Please check your input. Details: {str(e)}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred: {str(e)}",
                ephemeral=True
            )

    @app_commands.command(
        name="help",
        description="Show how to use the loot splitter bot"
    )
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Albion Loot Splitter Help",
            description="A bot to help split loot and repair costs in Albion Online",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="How to use /split",
            value=(
                "Use the `/split` command with the following parameters:\n\n"
                "• `total_loot`: The total amount of silver to split\n"
                "• `participants`: List of participants and their repair costs\n\n"
                "Example:\n"
                "`/split total_loot:1000000 participants:@User1:50000 @User2:30000`\n\n"
                "The bot will calculate each person's share, taking into account their repair costs."
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        await bot.add_cog(LootSplitter(bot))
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable not set.")
    bot.run(token) 