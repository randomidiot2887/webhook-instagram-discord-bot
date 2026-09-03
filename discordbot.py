import os
import asyncio
import discord

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")


async def _set_status(phrase, emoji=None):
    client = discord.Client()
    done = asyncio.Event()

    @client.event
    async def on_ready():
        try:
            activity = discord.CustomActivity(
                name=phrase,
                emoji=discord.PartialEmoji(name=emoji) if emoji else None,
            )
            await client.change_presence(activity=activity)
            print(f"Discord status set to: {phrase}")
        finally:
            done.set()

    await client.login(DISCORD_TOKEN)
    task = asyncio.create_task(client.connect())
    await done.wait()
    await client.close()
    task.cancel()


def set_discord_status(phrase, emoji=None):
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN environment variable is not set")
    asyncio.run(_set_status(phrase, emoji))


if __name__ == "__main__":
    set_discord_status("Automated status test", emoji="🤖")