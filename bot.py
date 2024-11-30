import discord
from discord.ext import commands
from discord.ui import Select, View, Button
import asyncio

# إعداد البوت
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

async def get_or_create_category(guild, category_name):
    category = discord.utils.get(guild.categories, name=category_name)
    if not category:
        category = await guild.create_category(category_name)
    return category

async def create_ticket(guild, user, ticket_name, category_name):
    category = await get_or_create_category(guild, category_name)
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }
    ticket_channel = await category.create_text_channel(ticket_name, overwrites=overwrites)
    return ticket_channel

@bot.command(name="start")
async def open_menu(ctx):
    if not ctx.guild:
        return await ctx.send("❌ This command can only be used in servers.")
    
    if not ctx.guild.me.guild_permissions.manage_channels:
        return await ctx.send("❌ I don't have the necessary permissions to create channels.")
    
    embed = discord.Embed(
        title="Choose Your Package",
        description="Please select the package that suits you from the list below.",
        color=0x00FF00
    )
    embed.set_footer(text="Made By Fighter ! < Developers Team >")
    embed.set_image(url="https://media.discordapp.net/attachments/1309832378385956866/1311355915584405623/Sans_titre_82_20241127163704.png?ex=674bda9e&is=674a891e&hm=eaab54ecf61ac68d97907858cc618b4c55486ff9f9ca1a75287b5f894c71bf80&=&format=webp&quality=lossless&width=951&height=535")
    
    select = Select(
        placeholder="Select a package...",
        options=[
            discord.SelectOption(label="50 Million", description="Package 50M", emoji="💰"),
            discord.SelectOption(label="80 Million", description="Package 80M", emoji="✨"),
            discord.SelectOption(label="100 Million", description="Package 100M", emoji="🌟"),
        ]
    )
    
    async def callback(interaction):
        choice = select.values[0]
        ticket_name = f"{choice}-{interaction.user.name}"
        category_name = "Customers"
        
        try:
            ticket_channel = await create_ticket(interaction.guild, interaction.user, ticket_name, category_name)
            await ticket_channel.send(f"{interaction.user.mention} 🎫 Your ticket has been created!")

            rules_embed = discord.Embed(
                title="Ticket Rules",
                description="Please do not open a ticket without a valid reason. Follow the rules for a smooth service.",
                color=0xFF0000
            )
            rules_embed.set_footer(text="Made By Fighter ! < Developers Team >")
            await ticket_channel.send(embed=rules_embed)

            close_button = Button(label="Close", style=discord.ButtonStyle.red)
            claim_button = Button(label="Claim", style=discord.ButtonStyle.green)

            async def close_callback(interaction):
                if interaction.user.guild_permissions.manage_channels:
                    await interaction.response.send_message("The ticket will be deleted in 3 seconds...", ephemeral=True)
                    await asyncio.sleep(3)
                    await ticket_channel.delete()
                else:
                    await interaction.response.send_message("❌ You don't have permission to close the ticket.", ephemeral=True)

            async def claim_callback(interaction):
                await ticket_channel.set_permissions(interaction.user, send_messages=True)
                await interaction.response.send_message(f"{interaction.user.mention} is now responsible for the ticket.", ephemeral=True)

            close_button.callback = close_callback
            claim_button.callback = claim_callback

            control_view = View()
            control_view.add_item(close_button)
            control_view.add_item(claim_button)

            await ticket_channel.send("Use the buttons below to manage the ticket.", view=control_view)

        except Exception as e:
            await interaction.response.send_message(f"❌ An error occurred while creating the ticket: {str(e)}", ephemeral=True)
    
    select.callback = callback
    view = View()
    view.add_item(select)
    
    await ctx.send(embed=embed, view=view)

# Commands for managing tickets
@bot.command(name="close")
@commands.has_permissions(manage_channels=True)
async def close_ticket(ctx):
    if ctx.channel.category and ctx.channel.category.name == "Customers":
        await ctx.send("The ticket will be deleted in 3 seconds...")
        await asyncio.sleep(3)
        await ctx.channel.delete()
    else:
        await ctx.send("❌ This command can only be used in ticket channels.")

@bot.command(name="delete")
@commands.has_permissions(manage_channels=True)
async def delete_ticket(ctx):
    await ctx.send("The ticket will be deleted in 3 seconds...")
    await asyncio.sleep(3)
    await ctx.channel.delete()

@bot.command(name="add")
@commands.has_permissions(manage_channels=True)
async def add_user(ctx, member: discord.Member):
    if member in ctx.channel.members:
        await ctx.send(f"{member.mention} is already in the ticket.")
    else:
        await ctx.channel.set_permissions(member, read_messages=True, send_messages=True)
        await ctx.send(f"✅ {member.mention} has been added to the ticket.")

@bot.command(name="remove")
@commands.has_permissions(manage_channels=True)
async def remove_user(ctx, member: discord.Member):
    if member not in ctx.channel.members:
        await ctx.send(f"{member.mention} is not in the ticket.")
    else:
        await ctx.channel.set_permissions(member, overwrite=None)
        await ctx.send(f"✅ {member.mention} has been removed from the ticket.")

@bot.command(name="setImage")
@commands.has_permissions(manage_channels=True)
async def set_image(ctx, url: str):
    try:
        embed = discord.Embed(
            title="New Image Set",
            description="The image for the ticket system has been updated.",
            color=0x00FF00
        )
        embed.set_image(url=url)
        embed.set_footer(text="Made By Fighter ! < Developers Team >")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ An error occurred while setting the image: {str(e)}")

# تشغيل البوت (أضف التوكن الخاص بك هنا)
bot.run("YOUR_DISCORD_BOT_TOKEN")
