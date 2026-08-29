import discord
import a2s
import datetime
import socket
import asyncio

# ============================================================
# CONFIGURATION
# ============================================================

TOKEN = 'insert your token'

# Text channel for the status/debug message
STATUS_CHANNEL = 0000000000000000000


# Voice channel showing the server name + online status
# Example:
# 🟢・Server #1
SERVER_NAME_CHANNEL = 0000000000000000000

# Voice channel showing player count
# Example:
# 👥・1/10 Players
PLAYER_CHANNEL = 0000000000000000000

# Voice channel showing current map
# Example:
# 🗺️・de_lake
MAP_CHANNEL = 0000000000000000000

# How often to check the server
AUTO_REFRESH_SECONDS = 5

# Server (insert your details here)
SERVER_IP = "128.0.0.1" 
SERVER_PORT = 27015

# Text displayed in the status/debug message
JOIN_URL = "YOURTEXTHERE"

# Manual refresh reaction
REFRESH_EMOJI = "🔄"

# A2S address
a2sIP = (SERVER_IP, SERVER_PORT)


# ============================================================
# DISCORD SETUP
# ============================================================

intents = discord.Intents.default()

client = discord.Client(
    intents=intents
)

first_start = True


# ============================================================
# GET SERVER INFO
# ============================================================

def get_server_info():

    try:

        return a2s.info(a2sIP)

    except socket.timeout:

        return None

    except (
        ConnectionResetError,
        OSError,
        socket.gaierror
    ):

        return None


# ============================================================
# GENERATE STATUS EMBED
# ============================================================

def generate_embed():

    server_info = get_server_info()

    # --------------------------------------------------------
    # SERVER OFFLINE
    # --------------------------------------------------------

    if server_info is None:

        return discord.Embed(
            title="Server down",
            color=0xFF0000,
            description=(
                "The server is currently down."
            ),
            timestamp=datetime.datetime.now(
                datetime.UTC
            )
        )

    # --------------------------------------------------------
    # SERVER ONLINE
    # --------------------------------------------------------

    description = (
        f"Player count: "
        f"{server_info.player_count}/"
        f"{server_info.max_players}\n"
        f"Map: {server_info.map_name}\n\n"
        f"connect {JOIN_URL}"
    )

    if server_info.password_protected:

        description = (
            "**SERVER UNDER MAINTENANCE**\n\n"
            + description
        )

    embed = discord.Embed(
        title=server_info.server_name,
        color=0x00FF00,
        description=description,
        timestamp=datetime.datetime.now(
            datetime.UTC
        )
    )

    return embed


# ============================================================
# SET BOT STATUS
# ============================================================

async def set_status(server_info=None):

    if server_info is None:
        server_info = get_server_info()

    if server_info is None:

        text = "an offline server ☹️"
        status = discord.Status.dnd

    else:

        text = (
            f"{server_info.player_count}/"
            f"{server_info.max_players} players"
        )

        status = discord.Status.online

    game = discord.Activity(
        name=text,
        type=discord.ActivityType.watching
    )

    await client.change_presence(
        status=status,
        activity=game
    )


# ============================================================
# UPDATE SERVER NAME VOICE CHANNEL
# ============================================================

async def update_server_name_channel(server_info):

    if server_info is None:

        new_name = "🔴・Server Offline"

    else:

        new_name = f"🟢・{server_info.server_name}"

    channel = client.get_channel(
        SERVER_NAME_CHANNEL
    )

    if channel is None:

        print(
            f"Could not find server name channel "
            f"{SERVER_NAME_CHANNEL}"
        )

        return

    # TEMPORARY DEBUG
    print("\nSERVER NAME CHANNEL DEBUG")
    print(f"ID: {channel.id}")
    print(f"Name: {channel.name}")
    print(f"Type: {channel.type}")

    permissions = channel.permissions_for(
        channel.guild.me
    )

    print(
        f"View Channel: "
        f"{permissions.view_channel}"
    )

    print(
        f"Manage Channels: "
        f"{permissions.manage_channels}"
    )

    # Don't rename if the name is already correct
    if channel.name == new_name:
        return

    try:

        await channel.edit(
            name=new_name,
            reason="CS:GO server status update"
        )

        print(
            f"Server name channel updated: "
            f"{new_name}"
        )

    except discord.Forbidden:

        print(
            "Missing Manage Channels permission "
            "for server name channel."
        )

    except discord.HTTPException as e:

        print(
            f"Failed to update server name channel: "
            f"{e}"
        )

# ============================================================
# UPDATE PLAYER COUNT VOICE CHANNEL
# ============================================================

async def update_player_channel(
    server_info
):

    if server_info is None:

        new_name = "👥・Offline"

    else:

        new_name = (
            f"👥・{server_info.player_count}/"
            f"{server_info.max_players} Players"
        )

    channel = client.get_channel(
        PLAYER_CHANNEL
    )

    if channel is None:

        print(
            f"Could not find player channel "
            f"{PLAYER_CHANNEL}"
        )

        return

    # Don't rename if already correct
    if channel.name == new_name:
        return

    try:

        await channel.edit(
            name=new_name,
            reason="CS:GO player count update"
        )

        print(
            f"Player channel updated: "
            f"{new_name}"
        )

    except discord.Forbidden:

        print(
            "Missing Manage Channels permission "
            "for player channel."
        )

    except discord.HTTPException as e:

        print(
            f"Failed to update player channel: "
            f"{e}"
        )


# ============================================================
# UPDATE MAP VOICE CHANNEL
# ============================================================

async def update_map_channel(
    server_info
):

    if server_info is None:

        new_name = "🗺️・Offline"

    else:

        new_name = (
            f"🗺️・{server_info.map_name}"
        )

    channel = client.get_channel(
        MAP_CHANNEL
    )

    if channel is None:

        print(
            f"Could not find map channel "
            f"{MAP_CHANNEL}"
        )

        return

    # Don't rename if already correct
    if channel.name == new_name:
        return

    try:

        await channel.edit(
            name=new_name,
            reason="CS:GO map update"
        )

        print(
            f"Map channel updated: "
            f"{new_name}"
        )

    except discord.Forbidden:

        print(
            "Missing Manage Channels permission "
            "for map channel."
        )

    except discord.HTTPException as e:

        print(
            f"Failed to update map channel: "
            f"{e}"
        )


# ============================================================
# UPDATE STATUS EMBED
# ============================================================

async def update_embed():

    try:

        await client.status_message.edit(
            embed=generate_embed()
        )

    except discord.NotFound:

        print(
            "Status message no longer exists."
        )

    except discord.HTTPException as e:

        print(
            f"Failed to update status message: "
            f"{e}"
        )


# ============================================================
# UPDATE EVERYTHING
# ============================================================

async def update_server_display(
    server_info=None
):

    if server_info is None:
        server_info = get_server_info()

    await update_server_name_channel(
        server_info
    )

    await update_player_channel(
        server_info
    )

    await update_map_channel(
        server_info
    )

    await set_status(
        server_info
    )

    await update_embed()


# ============================================================
# AUTOMATIC SERVER MONITOR
# ============================================================

async def server_monitor():

    await client.wait_until_ready()

    print(
        "Server monitor started."
    )

    previous_players = None
    previous_max_players = None
    previous_map = None
    previous_server_name = None
    previous_online = None

    while not client.is_closed():

        try:

            server_info = get_server_info()

            # ------------------------------------------------
            # SERVER ONLINE
            # ------------------------------------------------

            if server_info is not None:

                current_players = (
                    server_info.player_count
                )

                current_max_players = (
                    server_info.max_players
                )

                current_map = (
                    server_info.map_name
                )

                current_server_name = (
                    server_info.server_name
                )

                current_online = True

            # ------------------------------------------------
            # SERVER OFFLINE
            # ------------------------------------------------

            else:

                current_players = None
                current_max_players = None
                current_map = None
                current_server_name = None
                current_online = False

            # ------------------------------------------------
            # DETECT CHANGES
            # ------------------------------------------------

            changed = (
                current_players != previous_players
                or current_max_players != previous_max_players
                or current_map != previous_map
                or current_server_name != previous_server_name
                or current_online != previous_online
            )

            if changed:

                print(
                    f"Server changed: "
                    f"players={current_players}, "
                    f"max={current_max_players}, "
                    f"map={current_map}, "
                    f"name={current_server_name}, "
                    f"online={current_online}"
                )

                previous_players = (
                    current_players
                )

                previous_max_players = (
                    current_max_players
                )

                previous_map = (
                    current_map
                )

                previous_server_name = (
                    current_server_name
                )

                previous_online = (
                    current_online
                )

                await update_server_display(
                    server_info
                )

        except Exception as e:

            print(
                f"Server monitor error: {e}"
            )

        await asyncio.sleep(
            AUTO_REFRESH_SECONDS
        )


# ============================================================
# MESSAGE COMMAND
# ============================================================

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.channel.id != STATUS_CHANNEL:
        return

    if message.content.startswith("!send"):

        await message.channel.send(
            "Hello!"
        )


# ============================================================
# MANUAL REFRESH REACTION
# ============================================================

@client.event
async def on_raw_reaction_add(
    payload
):

    if payload.event_type != "REACTION_ADD":
        return

    if payload.channel_id != STATUS_CHANNEL:
        return

    if payload.message_id != client.status_message.id:
        return

    if payload.member == client.user:
        return

    if str(payload.emoji) != REFRESH_EMOJI:
        return

    print(
        "Manual refresh requested."
    )

    await update_server_display()


# ============================================================
# BOT READY
# ============================================================

@client.event
async def on_ready():

    global first_start

    if not first_start:
        return

    first_start = False

    client.status_channel = (
        client.get_channel(
            STATUS_CHANNEL
        )
    )

    if client.status_channel is None:

        print(
            f"Could not find status channel "
            f"{STATUS_CHANNEL}"
        )

        return

    # --------------------------------------------------------
    # Get initial server info
    # --------------------------------------------------------

    server_info = get_server_info()

    # --------------------------------------------------------
    # Initial channel updates
    # --------------------------------------------------------

    await update_server_name_channel(
        server_info
    )

    await update_player_channel(
        server_info
    )

    await update_map_channel(
        server_info
    )

    await set_status(
        server_info
    )

    # --------------------------------------------------------
    # Create status/debug message
    # --------------------------------------------------------

    try:

        client.status_message = (
            await client.status_channel.send(
                embed=generate_embed()
            )
        )

    except discord.Forbidden:

        print(
            "ERROR: The bot cannot send messages "
            "in the STATUS_CHANNEL."
        )

        print(
            "Make sure it has View Channel, "
            "Send Messages and Embed Links."
        )

        return

    # --------------------------------------------------------
    # Add refresh reaction
    # --------------------------------------------------------

    try:

        await client.status_message.add_reaction(
            REFRESH_EMOJI
        )

    except discord.Forbidden:

        print(
            "Could not add refresh reaction."
        )

    print(
        f"We have logged in as {client.user}"
    )

    # --------------------------------------------------------
    # Start automatic server monitoring
    # --------------------------------------------------------

    asyncio.create_task(
        server_monitor()
    )


# ============================================================
# START BOT
# ============================================================

client.run(TOKEN)
