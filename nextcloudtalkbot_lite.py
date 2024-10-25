import os
import argparse
import sys
from colorama import Fore, Style, init
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Nextcloud server URL and recipient account ID from .env
NEXTCLOUD_URL = os.getenv('NEXTCLOUD_URL')
BOT_USERNAME = os.getenv('BOT_USERNAME')
BOT_PASSWORD = os.getenv('BOT_PASSWORD')
DEFAULT_RECIPIENT_ID = os.getenv('DEFAULT_RECIPIENT_ID')

# Initialize colorama
init(autoreset=True)

def display_banner():
    banner = r"""
    _   __          __  ________                __
   / | / /__  _  __/ /_/ ____/ /___  __  ______/ /
  /  |/ / _ \| |/_/ __/ /   / / __ \/ / / / __  / 
 / /|  /  __/>  </ /_/ /___/ / /_/ / /_/ / /_/ /  
/_/ |_/\___/_/|_|\__/\____/_/\____/\__,_/\__,_/   
                                                  
  ______      ____   ____        __ 
 /_  __/___ _/ / /__/ __ )____  / /_
  / / / __ `/ / //_/ __  / __ \/ __/
 / / / /_/ / / ,< / /_/ / /_/ / /_  
/_/  \__,_/_/_/|_/_____/\____/\__/ 
    """
    
    version_info = "Version 1.03 Lite - Powered by TuxHouse - This is a shorted version find the full version here: https://github.com/sv1sjp/NextCloudTalkAutomationBot"
    
    print(Fore.GREEN + banner)
    print(Fore.CYAN + version_info)
    print(Fore.RED + "-----------------------------------------------")

def send_message(recipient_id, message):
    """
    Sends a message to a specified recipient via Nextcloud Talk.
    """
    api_endpoint = f'{NEXTCLOUD_URL}/ocs/v2.php/apps/spreed/api/v1/chat/{recipient_id}'

    headers = {
        'OCS-APIRequest': 'true',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
        'message': message
    }

    response = requests.post(
        api_endpoint,
        auth=(BOT_USERNAME, BOT_PASSWORD),
        headers=headers,
        data=data,
        verify=True  # Ensure HTTPS verification
    )

    print(f'Status code: {response.status_code}')
    print(f'Response: {response.text}')

def print_help():
    """
    Displays the help message with options and program name, styled with colors.
    """
    display_banner()
    print(Fore.GREEN + "Usage:")
    print("  python3 nextcloudbot.py [options]\n")
    print(Fore.GREEN + "Options:")
    print("  --send \"message\"           Send a message to the predefined recipient.")
    print("  --chat \"chat_id\"           Specify a chat ID to send the message.")
    print("  -h, --help                  Show this help message.\n")
    print(Fore.MAGENTA + "Examples:")
    print("  python3 nextcloudbot.py --send \"Hello!\"")
    print("  python3 nextcloudbot.py --chat \"chat_id\" --send \"Custom Message\"")

def main():
    parser = argparse.ArgumentParser(description='Nextcloud Talk Bot - Messaging Only', add_help=False)
    parser.add_argument('--send', metavar='"message"', help='Send a message to the predefined recipient.')
    parser.add_argument('--chat', metavar='"chat_id"', help='Send the message to a specified chat ID.')
    parser.add_argument('-h', '--help', action='store_true', help='Show this help message.')
    args = parser.parse_args()

    if args.help or len(sys.argv) == 1:
        print_help()
        sys.exit()

    recipient_id = DEFAULT_RECIPIENT_ID
    if args.chat:
        recipient_id = args.chat

    if args.send:
        send_message(recipient_id, args.send)
    else:
        print_help()

if __name__ == '__main__':
    main()

