import discord, asyncio, json
from discord.ext import commands, tasks
from discord.utils import get
intents = discord.Intents.all()

client = commands.Bot(command_prefix = ".", intents = intents)


@client.command()
@commands.has_permissions(administrator = True)
async def setup(ctx):
    timeout = discord.Embed(
        title = ":x: You ran out of time",
        color = discord.Color.red()
    )
    
    with open("guild.json", "r") as f:
        open_file = json.load(f)
    
    
    
    if str(ctx.guild.id) in open_file:
        already_channel = await client.fetch_channel(open_file[str(ctx.guild.id)])
        already_embed = discord.Embed(
            title = "You already setup your logs!",
            description = "Do you want to setup your logs elsewhere? (yes/no)",
            color = discord.Color.red()
        )
        already_embed.add_field(name = "Logs setup in", value = f"{already_channel.mention}")
        edit2 = await ctx.send(embed = already_embed)
        try:
            message2 = await client.wait_for("message", check = lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout = 30)
        except asyncio.TimeoutError:
            await edit2.edit(embed = timeout)
            return
        else:
            if message2.content.lower() == "yes":
                del open_file[str(ctx.guild.id)]

            elif message2.content.lower() == "no":
                cancel_embed = discord.Embed(
                    title = "You chose to prompt out of logs setup.",
                    color = discord.Color.red()
                )
                await edit2.edit(embed = cancel_embed)
                return
            else:
                await ctx.send("This isn't an option!")
                return
            
        

    
    logs = discord.Embed(
        title = "Where do you want to setup logs? (type in channel name or mention a channel)",
        color = discord.Color.green()
    )
    logs.set_footer(text = "Automatically prompts out in 30 seconds")
    
    
    edit1 = await ctx.send(embed = logs)



    def check(m):
        return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id 
    
    #Where do you want logs setup
    try: 
        message1 = await client.wait_for("message", check = check, timeout = 30)
    except asyncio.TimeoutError:
        await edit1.edit(embed = timeout)
        return

    #Convert channel
    
    try: 
        message_channel = await commands.TextChannelConverter().convert(ctx, argument = message1.content)
    except:
        await ctx.send("You need to mention a channel or type in a correct channel name.")
        return
    
    open_file[str(ctx.guild.id)] = str(message_channel.id)

    with open("guild.json", "w") as f:
        json.dump(open_file, f, indent = 1)
    
    success = discord.Embed(
        description = f":white_check_mark: **you have successfully setup logs in** {message_channel.mention}",
        color = discord.Color.green()
    )
    await ctx.send(embed = success)

async def if_setup(user):
   
    with open("guild.json", "r") as f:
        open_file = json.load(f)
    
    if str(user.guild.id) not in open_file:
        return
    
@setup.error
async def perms_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.author.send("You are missing permissions")

@client.event
async def on_message_delete(message):
 
    with open("guild.json", "r") as f:
        open_file = json.load(f)
    await if_setup(message)
    channel = await client.fetch_channel(open_file[str(message.guild.id)])
    delete_embed = discord.Embed(
        title = "Message Has Been Deleted",
        description = f"Message has been deleted by {message.author.mention} in {message.channel.mention}",
        color = discord.Color.blurple()
    )
    delete_embed.set_author(name = str(message.author), icon_url = str(message.author.avatar_url))
    delete_embed.add_field(name = "Deleted Content", value = message.content, inline = False)
    await channel.send(embed = delete_embed)

    
@client.event
async def on_message_edit(before, after):
    
    with open("guild.json", "r") as f:
        open_file = json.load(f)
    await if_setup(before)
    channel = await client.fetch_channel(open_file[str(before.guild.id)])
    edit_embed = discord.Embed(
        title = "Message Edited",
        description = f"Message edited by {before.author.mention} in {before.channel.mention}",
        color = discord.Color.blurple()
    )
    edit_embed.set_author(name = str(before.author), icon_url = str(before.author.avatar_url))
    edit_embed.add_field(name = "Before Content", value = before.content, inline = True)
    edit_embed.add_field(name = "After Content", value = after.content, inline = True)
    await channel.send(embed = edit_embed)


client.run("TOKEN") #Enter your bots token
