# testbot

import discord

# just a python file with 'token' defined
# not included for obvious reasons
import discToken


MATHBOT_VERSION = 0.5


# todo: update this

# id of server
MATH_SERVER = 'id here'

# id of channel for commands
COMMAND_CHANNEL = 'id here'

# name of roles that can use commands in command channel
TUTOR_ROLES = set(['banana', 'apple'])

# name of check in role
CHECK_IN_ROLE = 'apple'

# name of check out role
CHECK_OUT_ROLE = 'banana'

# name of the color roles
COLOR_ROLES = ['blue', 'green']

# create client instance
client = discord.Client()


@client.event
async def on_ready():
    try:
        if not client.get_guild(MATH_SERVER):
            print('Unable to connect to the Math Center Discord'
                  '(maybe the ID has changed?)')
            raise ConnectionError

        if not client.get_channel(COMMAND_CHANNEL):
            print('Unable to find the commands channel'
                  '(maybe the ID has changed?')
            raise ConnectionError

        print(f'Mathbot v{MATHBOT_VERSION} is ready')

    except ConnectionError:
        print('Unable to connect')
        input()
        quit()


@client.event
async def on_message(message):
    if command_is_valid(message):
        try:
            command = message.content.lower()

            if command.startswith('!checkin'):
                if not valid_permissions():
                    raise PermissionError
                await check('in', message.author, message.channel)

            if command.startswith('!checkout'):
                if not valid_permissions():
                    raise PermissionError
                await check('out', message.author, message.channel)

            for c in COLOR_ROLES:
                if command.startswith(f'!{c}'):
                    if not valid_permissions():
                        raise PermissionError
                    await color(c, message.author, message.channel)

        except PermissionError:
            await message.channel.send('i don\'t have permission to '
                                       'manage roles on this server')


async def check(arg, author, channel):
    # checks user in or out
    in_role = get_role(CHECK_IN_ROLE)
    out_role = get_role(CHECK_OUT_ROLE)

    if not in_role or not out_role:
        await channel.send(f'{author.mention}, i\'m unable to find the '
                           f'appropriate role(s)')
        return

    if arg == 'in':
        if in_role in author.roles:
            await channel.send(f'{author.mention}, you already appear to be '
                               f'checked in')
            return
        await channel.send(f'hi, {author.mention}, checking you in')
        await author.add_roles(in_role, reason='user request', atomic=True)
        await author.remove_roles(out_role, reason='user request', atomic=True)

    if arg == 'out':
        if out_role in author.roles:
            await channel.send(f'{author.mention}, you already appear to be '
                               f'checked out')
            return
        await channel.send(f'hi, {author.mention}, checking you out')
        await author.add_roles(out_role, reason='user request', atomic=True)
        await author.remove_roles(in_role, reason='user request', atomic=True)


async def color(color_s, author, channel):
    # changes color of user via role
    color_role = get_role(color_s)
    # the next line is beautiful
    all_color_roles = [get_role(c) for c in COLOR_ROLES if get_role(c)]

    if not color_role:
        await channel.send(f'{author.mention}, i\'m unable to find the '
                           f'appropriate role(s)')
        return

    await channel.send(f'changing {author.mention} to team {color_s}')
    await author.remove_roles(*all_color_roles, reason='user request',
                              atomic=True)
    await author.add_roles(color_role, reason='user request', atomic=True)


def get_role(role_name):
    # gets the discord.role.Role for a given name
    roles = client.get_guild(MATH_SERVER).roles
    for r in roles:
        if r.name == role_name:
            return r
    else:
        return None


def valid_permissions():
    # checks if bot has permission to manage roles in the server
    return client.get_guild(MATH_SERVER).me.guild_permissions.manage_roles


def command_is_valid(message):
    # checks if message is in the right channel, server, etc.
    if message.author == client.user:
        return False

    if message.guild != client.get_guild(MATH_SERVER):
        return False

    if message.channel != client.get_channel(COMMAND_CHANNEL):
        return False

    if not isinstance(message.author, discord.member.Member):
        return False

    if not TUTOR_ROLES & set(r.name for r in message.author.roles):
        return False

    return True


client.run(discToken.token)