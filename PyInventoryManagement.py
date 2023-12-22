import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)
bot.remove_command('help')

if not os.path.exists('data'):
    os.makedirs('data')

items_file = 'items.json'
investments_file = 'investments.json'
sales_file = 'sales.json'

def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(f"Error loading JSON from {file_path}. File is not valid JSON.")
        return {}

if not os.path.exists(items_file):
    with open(items_file, 'w') as f:
        json.dump({}, f)

if not os.path.exists(investments_file):
    with open(investments_file, 'w') as f:
        json.dump({}, f)

if not os.path.exists(sales_file):
    with open(sales_file, 'w') as f:
        json.dump({}, f)


@bot.event
async def on_ready():
    global items
    try:
        with open(items_file, 'r') as f:
            items = json.load(f)
    except FileNotFoundError:
        items = {}
        print("Items file not found. Creating a new one.")
    except json.JSONDecodeError:
        print("Error loading item data. Please check the file for valid JSON.")
    print(f'We have logged in as {bot.user}')

@bot.command()
async def inventory(ctx):
    with open(items_file, 'r') as f:
        items = json.load(f)

    if not items:
        await ctx.send("The inventory is empty.")
        return

    for item_id, item_info in items.items():
        name = item_info.get('name', 'N/A')
        quantity = item_info.get('quantity', 'N/A')
        purchase_price = item_info.get('purchase_price', 'N/A')
        normal_sell_price = item_info.get('normal_sell_price', 'N/A')
        picture = item_info.get('picture', None)

        embed = discord.Embed(title=f"Item ID: {item_id}", color=discord.Color.green())
        embed.add_field(name="Name:", value=name, inline=True)
        embed.add_field(name="Quantity:", value=quantity, inline=True)
        embed.add_field(name="Purchase Price:", value=f"${purchase_price}", inline=True)
        embed.add_field(name="Normal Sell Price:", value=f"${normal_sell_price}", inline=True)
        embed.add_field(name="Estimated Gain:", value=f":arrow_up:    %{get_change(purchase_price, normal_sell_price)}", inline=True)

        if picture:
            embed.set_image(url=picture)

        await ctx.send(embed=embed)

@bot.command()
async def additem(ctx):

    name, purchase_price, normal_sell_price, quantity, picture = "", 0.0, 0.0, 0, None

    await ctx.send("What's the item name?")
    name = await bot.wait_for('message', check=lambda m: m.author == ctx.author)

    await ctx.send("What's the item purchase price?")
    purchase_price = await bot.wait_for('message', check=lambda m: m.author == ctx.author)

    await ctx.send("What's the normal sell price for this item?")
    normal_sell_price = await bot.wait_for('message', check=lambda m: m.author == ctx.author)

    await ctx.send("How many of this item do you have?")
    quantity = await bot.wait_for('message', check=lambda m: m.author == ctx.author)

    await ctx.send("Please provide a picture URL for the item (optional):")
    picture = await bot.wait_for('message', check=lambda m: m.author == ctx.author)

    with open(items_file, 'r') as f:
        items = json.load(f)

    item_id = len(items) + 1
    items[item_id] = {
        'name': name.content,
        'purchase_price': float(purchase_price.content),
        'normal_sell_price': float(normal_sell_price.content),
        'quantity': int(quantity.content),
        'picture': picture.content if picture and picture.content else None
    }

    with open(items_file, 'w') as f:
        json.dump(items, f)

    await ctx.send(f"Item '{name.content}' added successfully. Quantity: {quantity.content}, Purchase Price: ${purchase_price.content}, Normal Sell Price: ${normal_sell_price.content}")


@bot.command()
async def deleteitem(ctx):

    await ctx.send("What's the item ID you want to delete?")
    item_id_input = await bot.wait_for('message', check=lambda m: m.author == ctx.author)

    with open(items_file, 'r') as f:
        items = json.load(f)

    item_id_str = str(item_id_input.content)
    if item_id_str not in items:
        await ctx.send("Invalid item ID.")
        return

    item_info = items[item_id_str]
    name = item_info.get('name', 'N/A')

    del items[item_id_str]

    with open(items_file, 'w') as f:
        json.dump(items, f)

    await ctx.send(f"Item '{name}' deleted successfully.")



@bot.command(name='investments')
async def investments(ctx):
    investments_file = 'C:/Users/Admin/Documents/served/data/investments.json'
    items_file = 'C:/Users/Admin/Documents/served/data/items.json'

    with open(investments_file, 'r') as f:
        investments = json.load(f)

    with open(items_file, 'r') as f:
        items = json.load(f)

    embed = discord.Embed(title="Investments", color=discord.Color.blue())

    target_item_id = '1'
    if target_item_id in investments and target_item_id in items:
        investment = investments[target_item_id]
        item = items[target_item_id]
        item_name = item.get('name', 'Unknown Item')
        purchase_price = item.get('purchase_price', 0)
        normal_sell_price = item.get('normal_sell_price', 0)
        quantity = item.get('quantity', 0)
        total_value = quantity * purchase_price
        investor_amount = investment.get('amount', 0)
        percentage = (investor_amount / total_value) * 100 if total_value != 0 else 0
        estimated_return = (percentage / 100) * investor_amount
        owned_percentage = f"{percentage:.2f}%"
        embed.add_field(name="Item Name", value=item_name, inline=False)
        embed.add_field(name="Investor Name", value=investment.get('investor_name', 'Unknown Investor'), inline=False)
        embed.add_field(name="Investor Amount", value=f"${investor_amount:.2f}", inline=False)
        embed.add_field(name="Total Value", value=f"${total_value:.2f}", inline=False)
        embed.add_field(name="Owned Percentage", value=owned_percentage, inline=False)
        embed.add_field(name="Estimated Return", value=f"${estimated_return:.2f}", inline=False)
    else:
        embed.add_field(name="Investment Not Found", value="The specified item ID is not present in the investments or items data.", inline=False)
    await ctx.send(embed=embed)



@bot.command()
async def addinvestment(ctx):
    investments = {}
    try:
        with open(investments_file, 'r') as f:
            content = f.read()

        if content:
            investments = json.loads(content)
    except json.JSONDecodeError:
        await ctx.send("Error loading investment data. Please check the file for valid JSON.")
        return
    except FileNotFoundError:
        await ctx.send("Investments file not found. Creating a new one.")
    await ctx.send("What's the item ID for the investment?")
    item_id = await bot.wait_for("message", check=lambda m: m.author == ctx.author, timeout=60)
    item_id = item_id.content.strip()
    await ctx.send("How much is the investment amount?")
    amount = await bot.wait_for("message", check=lambda m: m.author == ctx.author, timeout=60)
    amount = float(amount.content.strip())
    await ctx.send("What's the name of the investor?")
    investor_name = await bot.wait_for("message", check=lambda m: m.author == ctx.author, timeout=60)
    investor_name = investor_name.content.strip()
    investment_id = len(investments) + 1
    investments[investment_id] = {
        "item_id": item_id,
        "amount": amount,
        "investor_name": investor_name
    }
    with open(investments_file, 'w') as f:
        json.dump(investments, f)
    await ctx.send("Investment added successfully.")


@bot.command()
async def deleteinvestment(ctx):
    await ctx.send("What's the investment ID you want to delete?")
    investment_id_input = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
    with open(investments_file, 'r') as f:
        investments = json.load(f)
    investment_id_str = str(investment_id_input.content)
    if investment_id_str not in investments:
        await ctx.send("Invalid investment ID.")
        return
    investment_info = investments[investment_id_str]
    item_id = investment_info.get('item_id', 'N/A')
    amount = investment_info.get('amount', 0.0)
    investor_name = investment_info.get('investor_name', 'N/A')
    del investments[investment_id_str]
    with open(investments_file, 'w') as f:
        json.dump(investments, f)

    await ctx.send(f"Investment ID '{investment_id_str}' deleted successfully. Investor: {investor_name}, Amount: ${amount}, Item: {item_id}")

@bot.command()
async def sell(ctx):
    item_id, quantity, sell_price = None, 0, 0.0
    await ctx.send("What's the item ID you want to sell?")
    item_id_input = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
    with open(items_file, 'r') as f:
        items = json.load(f)
    item_id_str = str(item_id_input.content)
    if item_id_str not in items:
        await ctx.send("Invalid item ID.")
        return
    item_info = items[item_id_str]
    name = item_info.get('name', 'N/A')
    purchase_price = item_info.get('purchase_price', 0.0)
    normal_sell_price = item_info.get('normal_sell_price', 0.0)
    await ctx.send(f"How many {name} do you want to sell?")
    quantity = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
    await ctx.send(f"What's the selling price for {name} (per item)?")
    sell_price = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
    total_purchase_price = purchase_price * int(quantity.content)
    total_sell_price = float(sell_price.content) * int(quantity.content)
    profit = total_sell_price - total_purchase_price
    with open(sales_file, 'r') as f:
        sales = json.load(f)
    sale_id = len(sales) + 1
    sales[sale_id] = {
        'item_id': item_id_str,
        'quantity': int(quantity.content),
        'total_purchase_price': total_purchase_price,
        'total_sell_price': total_sell_price,
        'profit': profit
    }
    with open(sales_file, 'w') as f:
        json.dump(sales, f)
    await ctx.send(f"Sale recorded for {name}. Profit: ${profit}")


@bot.command()
async def undolastsale(ctx):
    with open(sales_file, 'r') as f:
        sales = json.load(f)
    if not sales:
        await ctx.send("No sales to undo.")
        return
    last_sale_id = max(sales.keys())
    last_sale = sales.pop(last_sale_id)
    with open(sales_file, 'w') as f:
        json.dump(sales, f)
    await ctx.send(f"Last sale undone. Item ID: {last_sale['item_id']}, Quantity: {last_sale['quantity']}, Profit: ${last_sale['profit']}")

def get_change(current, previous):
    if current == previous:
        return 100.0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return 0

@bot.command(name='inventory_value')
async def inventory_value(ctx):
    items_file = 'C:/Users/Admin/Documents/served/data/items.json'
    with open(items_file, 'r') as f:
        items = json.load(f)
    bought_for_value = sum(item['purchase_price'] * item['quantity'] for item in items.values())
    projected_value = sum(item['normal_sell_price'] * item['quantity'] for item in items.values())
    prfprcnt = get_change(bought_for_value, projected_value)
    embed = discord.Embed(title="Inventory Value", color=discord.Color.green())
    embed.add_field(name="Bought for Value", value=f"${bought_for_value:.2f}", inline=False)
    embed.add_field(name="Projected Value", value=f"${projected_value:.2f}", inline=False)
    embed.add_field(name="Proft Percentage", value=f":arrow_up: %{prfprcnt:.2f}", inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def edititem(ctx):
    await ctx.send("What's the item ID you want to edit?")
    item_id_input = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
    with open(items_file, 'r') as f:
        items = json.load(f)
    item_id_str = str(item_id_input.content)
    if item_id_str not in items:
        await ctx.send("Invalid item ID.")
        return
    item_info = items[item_id_str]
    await ctx.send(f"Current item details for ID '{item_id_str}':\n"
                   f"Name: {item_info.get('name', 'N/A')}\n"
                   f"Purchase Price: ${item_info.get('purchase_price', 'N/A')}\n"
                   f"Normal Sell Price: ${item_info.get('normal_sell_price', 'N/A')}\n"
                   f"Quantity: {item_info.get('quantity', 'N/A')}\n"
                   f"Picture: {item_info.get('picture', 'N/A')}\n\n"
                   "What field do you want to edit? (name/purchase_price/normal_sell_price/quantity/picture)")
    field_to_edit = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
    field_to_edit = field_to_edit.content.lower()
    if field_to_edit not in ['name', 'purchase_price', 'normal_sell_price', 'quantity', 'picture']:
        await ctx.send("Invalid field to edit.")
        return
    await ctx.send(f"What's the new value for {field_to_edit}?")
    new_value = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
    if field_to_edit == 'purchase_price' or field_to_edit == 'normal_sell_price':
        item_info[field_to_edit] = float(new_value.content)
    elif field_to_edit == 'quantity':
        item_info[field_to_edit] = int(new_value.content)
    else:
        item_info[field_to_edit] = new_value.content
    with open(items_file, 'w') as f:
        json.dump(items, f)
    await ctx.send(f"Item ID '{item_id_str}' updated successfully. {field_to_edit.capitalize()}: {new_value.content}")


@bot.command()
async def addmore(ctx, item_id, quantity):
    with open(items_file, 'r') as f:
        items = json.load(f)
    item_id = int(item_id)
    if item_id not in items:
        await ctx.send("Invalid item ID.")
        return
    items[item_id]['quantity'] = items[item_id].get('quantity', 0) + int(quantity)
    with open(items_file, 'w') as f:
        json.dump(items, f)
    await ctx.send(f"{quantity} more of item ID {item_id} added.")


@bot.command()
async def stats(ctx):
    with open(sales_file, 'r') as f:
        sales = json.load(f)
    total_sales = len(sales)
    total_profit = sum(sale['profit'] for sale in sales.values())
    embed = discord.Embed(title="Stats Board", color=discord.Color.green())
    embed.add_field(name="Total Sales", value=total_sales)
    embed.add_field(name="Total Profit", value=f"${total_profit}")
    await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Inventory Bot Commands",
        description="Welcome to the Inventory Bot! Here are the available commands:",
        color=discord.Color.blue()
    )
    embed.add_field(name="/additem", value="Add a new item to the inventory.", inline=False)
    embed.add_field(name="/inventory", value="View the current inventory.", inline=False)
    embed.add_field(name="/sell", value="Record a sale and update inventory.", inline=False)
    embed.add_field(name="/deleteitem", value="Delete an item from the inventory.", inline=False)
    embed.add_field(name="/deleteinvestment", value="Delete an investment from an item.", inline=False)
    embed.add_field(name="/undo", value="Undo the last recorded sale.", inline=False)
    embed.add_field(name="/edititem", value="Edit details of an existing item.", inline=False)
    embed.set_footer(text="For detailed information on each command, use /help <command>")
    await ctx.send(embed=embed)

bot.run('YOUR TOKEN HERE')
