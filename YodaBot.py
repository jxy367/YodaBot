import discord
import asyncio

import base64
import json
import os
import requests

API_KEY = os.environ.get('API_KEY')
TOKEN = os.environ.get('TOKEN')
client = discord.Client()

# The actual http request


def request(url):
    """Translates the input file into a json output file.

    Args:
        input_file: a file object, containing lines of input to convert.
        output_filename: the name of the file to output the json to.
    """
    request_list = []
    image_data = base64.b64encode(requests.get(url).content).decode('UTF-8')

    content_json_obj = {'content': image_data}

    feature_json_obj = []
    feature_json_obj.append({
        'type': 'WEB_DETECTION',
        'maxResults': 4,
    })

    request_list.append({
        'features': feature_json_obj,
        'image': content_json_obj,
    })

    with open('hold.txt', 'w') as hold:
        json.dump({'requests': request_list}, hold)
    data = open('hold.txt', 'rb').read()
    response = requests.post(url='https://vision.googleapis.com/v1/images:annotate?key=' + API_KEY,
                             data=data,
                             headers={'Content-Type': 'application/json'})

    response_data = json.loads(response.text)

    descriptions = ""
    for webEntity in response_data['responses'][0]['webDetection']['webEntities']:
        if 'description' in webEntity.keys():
            descriptions = descriptions + webEntity['description'] + " "

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


# Standard bot stuff


@client.event
async def on_message(message):
    all_descriptions = ""
    if message.attachments is not None:
        for attachment in message.attachments:
            descriptions = request(attachment.proxy_url)
            all_descriptions = all_descriptions + descriptions + " "
    if message.embeds is not None:
        for embed in message.embeds:
            descriptions = request(embed.url)
            all_descriptions = all_descriptions + descriptions + " "
    #print(all_descriptions)
    if ("yoda" in all_descriptions.lower()) or ("yoda" in message.content.lower()):
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

client.run(TOKEN)
