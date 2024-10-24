import os
import argparse
import subprocess
import sys
import json
from colorama import Fore, Style, init
import datetime
from datetime import datetime, timedelta
from dotenv import load_dotenv
from datetime import timezone
import requests 

# For colored output in help messages
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    # If colorama is not installed, define dummy color constants
    class Fore:
        RED = ''
        GREEN = ''
        YELLOW = ''
        BLUE = ''
        MAGENTA = ''
        CYAN = ''
        RESET = ''
    class Style:
        BRIGHT = ''
        NORMAL = ''
        RESET_ALL = ''

# Load environment variables from .env file
load_dotenv()

# Nextcloud server URL and recipient account ID from .env
NEXTCLOUD_URL = os.getenv('NEXTCLOUD_URL')
BOT_USERNAME = os.getenv('BOT_USERNAME')
BOT_PASSWORD = os.getenv('BOT_PASSWORD')
DEFAULT_RECIPIENT_ID = os.getenv('DEFAULT_RECIPIENT_ID')

LOG_FILE_PATH = "nextcloudtalkbot.log"  # Path to the log file

from colorama import Fore, Style, init

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

    version_info = """
    Version 1.03 - Provided By Dimitris Vagiakakos @sv1sjp - TuxHouse
    """
    print(Fore.GREEN + banner)
    print(Fore.YELLOW + "A powerful and flexible bot for automating tasks and sending messages via Nextcloud Talk.\n")
    print(Fore.CYAN + version_info)
    print(Style.BRIGHT + Fore.MAGENTA + "Efficient, Secure, and Reliability - All in One.")
    print(Fore.RED + "-----------------------------------------------")



def log_usage(flag, details=None):
    
    #Logs the bot's usage, appending to a log file with a timestamp and flag used.
    #If details are provided (e.g., command executed), they are included in the log.
    
    timestamp = datetime.now().strftime('%d.%m.%Y %H.%M')
    log_entry = f"{timestamp} - NextCloudTalkBot used the flag: {flag}"

    if details:
        log_entry += f" with details: {details}"
    
    log_entry += "\n"

    try:
        with open(LOG_FILE_PATH, "a") as log_file:
            log_file.write(log_entry)
    except IOError as e:
        print(f"Failed to write to log file: {e}")

def send_message(recipient_id, message):
    
    #Sends a message to a specified recipient via Nextcloud Talk.
    
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

def execute_command(command):
    
    #Executes a shell command and returns its output on Nextcloud Talk.
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Command failed with error: {e.stderr.strip()}"

def check_storage():
    
    #Checks the available storage of sda0 and returns the percentage of available storage.
    
    command = "df -h | grep sda0" #change this line to the desired one
    output = execute_command(command)
    if output:
        return output
    else:
        return "Could not retrieve storage information."


def check_nextcloud_login_attempts():
    
    #Checks the Nextcloud log file and identifies unsuccessful login attempts in the last 2 hours.
    log_file_path = '/media/TuxDriveB/nextcloud/nextcloud.log'  # Path to your Nextcloud log file
    two_hours_ago = datetime.now(timezone.utc) - timedelta(hours=1)  # Make `two_hours_ago` timezone-aware, change the number for more or less hours

    try:
        with open(log_file_path, 'r') as log_file:
            logs = log_file.readlines()

        attempts = []
        for line in logs:
            if 'Login failed' in line:
                log_data = json.loads(line.strip())
                log_time = datetime.strptime(log_data['time'], '%Y-%m-%dT%H:%M:%S%z')  # Parse with timezone

                # Check if the log is within the last two hours
                if log_time > two_hours_ago:
                    # Extract the correct user from the log entry
                    message_parts = log_data['message'].split(':')
                    if len(message_parts) > 1:
                        user = message_parts[1].split('(')[0].strip()  # Get the username before "(Remote IP"
                    else:
                        user = "Unknown"  # Fallback in case the format is incorrect

                    ip_address = log_data['remoteAddr']
                    log_time_formatted = log_time.strftime('%H:%M')

                    # Format the message
                    attempts.append(f"WARNING: Failed login to {user} from IP: {ip_address} at {log_time_formatted}.")

        if attempts:
            return '\n'.join(attempts)
        else:
            return "No unsuccessful login attempts in the last 2 hours."
    except Exception as e:
        return f"Error reading the log file: {str(e)}"




def check_wireguard_login_attempts():
    
    #Checks the logs of the Wireguard container via docker logs and identifies unsuccessful login attempts in the last 2 hours.
    
    two_hours_ago = datetime.now() - timedelta(hours=2)
    command = "docker logs wireguard"  # Adjust container name if different
    logs = execute_command(command)
    if logs:
        attempts = []
        for line in logs.split('\n'):
            if 'Handshake' in line or 'Login failed' in line:
                timestamp_str = line.split(' ')[0]
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S')
                    if timestamp > two_hours_ago:
                        attempts.append(line)
                except ValueError:
                    continue
        if attempts:
            return f"Unsuccessful Wireguard login attempts in the last 2 hours:\n" + '\n'.join(attempts)
        else:
            return "No unsuccessful Wireguard login attempts in the last 2 hours."
    else:
        return "Could not retrieve Wireguard logs."

def send_boot_time():
    #Calculates the hours since the system booted and returns a message.
    command = "uptime -s"
    output = execute_command(command)
    if output:
        boot_time = datetime.strptime(output.strip(), '%Y-%m-%d %H:%M:%S')
        time_since_boot = datetime.now() - boot_time
        hours_since_boot = time_since_boot.total_seconds() / 3600
        return f"The system has been up for {hours_since_boot:.2f} hours."
    else:
        return "Could not retrieve system boot time."

def check_status():
    #Checks the status of Docker containers and returns a summary.
    command = "docker ps --format '{{.Names}}: {{.Status}}'"
    output = execute_command(command)
    if output:
        return "Docker Containers Status:\n" + output
    else:
        return "Could not retrieve Docker containers status."

def check_cpu_usage():
    #Checks the current CPU usage and returns it.
    command = "top -bn1 | grep 'Cpu(s)'"
    output = execute_command(command)
    if output:
        return "CPU Usage:\n" + output
    else:
        return "Could not retrieve CPU usage."

def print_help():
    
    #Displays the help message with options and program name, styled with colors.
    display_banner()
    print(Fore.GREEN + "Usage:")
    print("  python3 nextcloudtalkbot.py [options]\n")
    print(Fore.GREEN + "Options:")
    print("  --send \"message\"           Send a message to the predefined recipient.")
    print("  --command \"bash command\"   Execute a bash command and send its output as a message.")
    print("  --chat \"chat_id\"           Send the message to a specified chat ID.")
    print("  --script [scripts]          Execute predefined scripts:")
    print("      storage                 Check available storage of sda0.")
    print("      nextcloud_login         Check Nextcloud login attempts in last 2 hours.")
    print("      wireguard               Check Wireguard login attempts in last 2 hours.")
    print("      boot                    Send a message about hours since system booted.")
    print("      status                  Check the status of Docker containers.")
    print("      cpu                     Check current CPU usage.")
    print("  -h, --help                  Show this help message.\n")
    print(Fore.MAGENTA + "Examples:")
    print("  python3 nextcloudtalkbot.py --send \"Hello!\"")
    print("  python3 nextcloudtalkbot.py --command \"ls -la\"")
    print("  python3 nextcloudtalkbot.py --chat \"chat_id\" --script storage")
    print("  python3 nextcloudtalkbot.py --script nextcloud_login wireguard")
    print("  python3 nextcloudtalkbot.py --script cpu\n")

def main():
    parser = argparse.ArgumentParser(description='Nextcloud Talk Bot', formatter_class=argparse.RawTextHelpFormatter, add_help=False)
    parser.add_argument('--send', metavar='"message"', help='Send a message to the predefined recipient.')
    parser.add_argument('--command', metavar='"bash command"', help='Execute a bash command and send its output as a message.')
    parser.add_argument('--chat', metavar='"chat_id"', help='Send the message to a specified chat ID.')
    parser.add_argument('--script', choices=['storage', 'nextcloud_login', 'wireguard', 'boot', 'status', 'cpu'], nargs='+',
                        help='Execute predefined scripts.')
    parser.add_argument('-h', '--help', action='store_true', help='Show this help message.')
    args = parser.parse_args()

    if args.help or len(sys.argv) == 1:
        print_help()
        sys.exit()

    recipient_id = DEFAULT_RECIPIENT_ID
    if args.chat:
        recipient_id = args.chat

    messages = []
    valid_flag = None

    if args.send:
        messages.append(args.send)
        valid_flag = "--send"
    
    if args.command:
        command_output = execute_command(args.command)
        messages.append(f"Command Output:\n{command_output}")
        valid_flag = "--command"
        log_usage(valid_flag, args.command)  # Log the command used

    if args.script:
        for script_name in args.script:
            valid_flag = "--script"
            if script_name == 'storage':
                storage_info = check_storage()
                messages.append(f"Storage Info:\n{storage_info}")
            elif script_name == 'nextcloud_login':
                login_attempts = check_nextcloud_login_attempts()
                messages.append(f"Nextcloud Login Attempts:\n{login_attempts}")
            elif script_name == 'wireguard':
                wg_attempts = check_wireguard_login_attempts()
                messages.append(f"Wireguard Login Attempts:\n{wg_attempts}")
            elif script_name == 'boot':
                boot_info = send_boot_time()
                messages.append(f"Boot Time Info:\n{boot_info}")
            elif script_name == 'status':
                status_info = check_status()
                messages.append(f"Status Info:\n{status_info}")
            elif script_name == 'cpu':
                cpu_info = check_cpu_usage()
                messages.append(f"CPU Usage Info:\n{cpu_info}")

        # Log the scripts used
        log_usage(valid_flag, ', '.join(args.script))

    if messages:
        full_message = '\n\n'.join(messages)
        send_message(recipient_id, full_message)
    else:
       
        display_banner()
        print_help()
        

if __name__ == '__main__':
    main()

