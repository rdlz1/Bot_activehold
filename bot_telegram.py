import re
import logging
import configparser
from telethon import TelegramClient, events

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load config
config = configparser.ConfigParser()
config.read('config.ini')

api_id = int(config['telegram']['api_id'])
api_hash = config['telegram']['api_hash']
target_entity = config['telegram']['target']  # e.g. "@senttxtbot"

# Create the Telegram client (user session, not bot token)
client = TelegramClient('telegram_listening_session', api_id, api_hash)

async def extract_percentage(event: events.NewMessage.Event) -> None:
    """
    Extracts percentage values (0%, 25%, 50%, 75%, 100%) from the first line
    of an incoming Telegram message. If found, writes them to 'percentages.txt'
    and replies to the message with the findings.
    """
    message_text = event.text
    if not message_text:
        logging.info("Empty message received.")
        return

    lines = message_text.splitlines()
    first_line = lines[0] if lines else ""

    percentages_found = re.findall(r'\b(?:0|25|50|75|100)\s*%', first_line)
    
    if percentages_found:
        response = f"Found percentage(s) in the first line: {', '.join(percentages_found)}"
        try:
            with open('percentages.txt', 'a') as file:

                for percentage in percentages_found:
                    cleaned_input = percentage.rstrip('%').strip()
                    file.write(cleaned_input + '\n')
        except Exception as e:
            logging.error(f"Error writing to percentages.txt: {e}")
    else:
        response = "No valid percentage found in the first line."

    try:
        await event.reply(response)
        logging.info(response)
    except Exception as e:
        logging.warning(f"Reply failed: {e}")

@client.on(events.NewMessage(from_users=target_entity))
async def handle_new_message(event: events.NewMessage.Event) -> None:
    """
    Invoked whenever a new message arrives from the configured target user/entity.
    Logs the message content and calls 'extract_percentage' to process it.
    """
    logging.info(f"Received a message from {target_entity}: {event.text}")
    await extract_percentage(event)

async def main() -> None:
    """
    Starts the Telegram client session and listens for messages until disconnected.
    """
    await client.start()
    logging.info(f"Listening for new messages from {target_entity}...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    with client:
        client.loop.run_until_complete(main())
