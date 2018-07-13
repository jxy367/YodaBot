import discord
import asyncio

import base64
import json
import os
import requests

API_KEY = os.environ.get('API_KEY')
TOKEN = os.environ.get('TOKEN')
client = discord.Client()

# Information for cooldown
on_cooldown = {}
cooldown_time = 20

# The actual http request


def request(url):
    url_is_image = False
    descriptions = ""
    image_types = ['jpg', 'jpeg', 'png', 'gif', 'application']

    test_response = requests.post(url)
    content_type = ''
    try:
        content_type = test_response.headers['Content-Type']
    except KeyError:
        return ""
    print(content_type)
    if any(ext in content_type for ext in image_types):
        print("requesting")
        request_list = []
        image_data = base64.b64encode(requests.get(url).content).decode('UTF-8')

        content_json_obj = {'content': image_data}

        feature_json_obj = []
        feature_json_obj.append({
            'type': 'WEB_DETECTION',
            'maxResults': 10,
        })

        request_list.append({
            'features': feature_json_obj,
            'image': content_json_obj,
        })

        with open('hold.txt', 'w') as hold:
            json.dump({'requests': request_list}, hold)
        data = open('hold.txt', 'rb').read()
        #print("post")
        response = requests.post(url='https://vision.googleapis.com/v1/images:annotate?key=' + API_KEY,
                                 data=data,
                                 headers={'Content-Type': 'application/json'})
        print("received data")
        response_data = json.loads(response.text)
        print(response_data)
        descriptions = ""
        try:
            for webEntity in response_data['responses'][0]['webDetection']['webEntities']:
                if 'description' in webEntity.keys():
                    descriptions = descriptions + webEntity['description'] + " "
        except KeyError:
            descriptions = ""
    print(descriptions)
    return descriptions


async def reset_display_name():
    for changed_guild in client.guilds:
        if changed_guild.me.display_name != "Moist Crab":
            print(changed_guild.name)
            print(changed_guild.me.display_name)
            print("---")
            await changed_guild.me.edit(nick=None)


async def background_update():
    await client.wait_until_ready()
    while not client.is_closed():
        await reset_display_name()
        await asyncio.sleep(60)


async def cooldown():
    global on_cooldown
    await client.wait_until_ready()
    while not client.is_closed():
        for guild in on_cooldown:
            on_cooldown[guild] = on_cooldown[guild] - 1
            if on_cooldown[guild] < 0:
                on_cooldown[guild] = 0
        await asyncio.sleep(1)


# Standard bot stuff


@client.event
async def on_message(message):
    global on_cooldown
    guild_id = message.guild
    if guild_id not in on_cooldown:
        on_cooldown[guild_id] = 0

    if message.author.bot:
        return

    guild_cooldown = on_cooldown[guild_id] <= 0
    if guild_cooldown:
        return

    has_yoda = False
    if "yoda" in message.content.lower():
        has_yoda = True
    else:
        all_descriptions = ""

        if message.attachments is not None:
            for attachment in message.attachments:
                descriptions = request(attachment.proxy_url)
                all_descriptions = all_descriptions + descriptions + " "

        if message.embeds is not None:
            for embed in message.embeds:
                descriptions = request(embed.url)
                all_descriptions = all_descriptions + descriptions + " "

        if "yoda" in all_descriptions.lower():
            has_yoda = True

        on_cooldown[guild_id] = cooldown_time

    if has_yoda:
        await message.channel.send("That's racist!")
        await message.add_reaction("🇷")
        await message.add_reaction("🇦")
        await message.add_reaction("🇨")
        await message.add_reaction("🇮")
        await message.add_reaction("🇸")
        await message.add_reaction("🇹")



@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    client.loop.create_task(background_update())
    client.loop.create_task(cooldown())

client.run(TOKEN)
