import time
import logging
import random
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import signal
import sys
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# User agents list
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    # Add more user agents if needed
]

# ASCII Art Title with Rainbow Colors (Line by Line)
def print_ascii_art():
    title = [
        r" ______     __  __     ______   ______        ______     ______     ______   ______     ______     ______     __  __     ______     ______",
        r"/\  __ \   /\ \ /\ \   /\__  _\ /\  __ \      /\  == \   /\  ___\   /\  ___\ /\  == \   /\  ___\   /\  ___\   /\ \_\ \   /\  ___\   /\  == \ ",
        r"\ \  __ \  \ \ \\_\ \  \/_/\ \/ \ \ \/\ \     \ \  __<   \ \  __\   \ \  __\ \ \  __<   \ \  __\   \ \___  \  \ \  __ \  \ \  __\   \ \  __< ",
        r" \ \_\ \_\  \ \_____\    \ \_\  \ \_____\     \ \_\ \_\  \ \_____\  \ \_\    \ \_\ \_\  \ \_____\  \/\_____\  \ \_\ \_\  \ \_____\  \ \_\ \_\ ",
        r"  \/_/\/_/   \/_____/     \/_/   \/_____/      \/_/ /_/   \/_____/   \/_/     \/_/ /_/   \/_____/   \/_____/   \/_/\/_/   \/_____/   \/_/ /_/ "
    ]
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE]
    for i, line in enumerate(title):
        print(colors[i % len(colors)] + line)

# Function to handle the auto-refresh logic
def auto_refresh(urls, interval, limit, headless, proxy, load_wait, screenshot, user_agent, browser_count):
    options = Options()
    if headless:
        options.add_argument("--headless")
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')
    options.add_argument(f'user-agent={user_agent}')
    
    drivers = [webdriver.Chrome(options=options) for _ in range(browser_count)]

    def signal_handler(sig, frame):
        logging.info('Termination signal received. Closing all browsers.')
        for driver in drivers:
            driver.quit()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    count = 0
    try:
        while limit == 0 or count < limit:
            for driver in drivers:
                for url in urls:
                    if url.lower() == 'end':
                        logging.info('End command received. Closing all browsers.')
                        raise KeyboardInterrupt
                    driver.get(url)
                    time.sleep(max(load_wait, 0) / 1000)  # Wait after loading, ensuring non-negative value
                    driver.refresh()
                    count += 1
                    print(Fore.CYAN + f"[INFO] Refresh count: {count}")
                    if screenshot:
                        driver.save_screenshot(f'screenshot_{count}.png')
                    if limit > 0 and count >= limit:
                        break
                if limit > 0 and count >= limit:
                    break
                time.sleep(max((interval + random.uniform(-500, 500)), 0) / 1000)  # Ensure non-negative sleep time
    except KeyboardInterrupt:
        logging.info("Closing all browsers.")
        for driver in drivers:
            driver.quit()
    except Exception as e:
        logging.error(f"Error occurred: {e}")
    finally:
        logging.info("Closing all browsers.")
        for driver in drivers:
            driver.quit()

# Interactive menu function
def menu():
    print_ascii_art()
    proxies = []
    user_agents = USER_AGENTS.copy()

    while True:
        print(Fore.YELLOW + "\n1. Add Proxy")
        print(Fore.YELLOW + "2. Add User-Agent")
        print(Fore.YELLOW + "3. Run the Auto-Refresh Script")
        print(Fore.YELLOW + "4. Credits")
        print(Fore.YELLOW + "5. Exit")
        choice = input(Fore.BLUE + "Choose an option: ")

        if choice.lower() == 'end':
            print(Fore.RED + "Ending script...")
            break
        elif choice == '1':
            proxy = input(Fore.BLUE + "Enter proxy (e.g., http://127.0.0.1:8080): ")
            proxies.append(proxy)
            print(Fore.GREEN + f"Proxy added: {proxy}")
        elif choice == '2':
            user_agent = input(Fore.BLUE + "Enter a custom User-Agent: ")
            user_agents.append(user_agent)
            print(Fore.GREEN + f"User-Agent added: {user_agent}")
        elif choice == '3':
            urls = input(Fore.BLUE + "Enter the URLs to refresh (separated by spaces): ").split()
            interval = max(int(input(Fore.BLUE + "Enter refresh interval in milliseconds: ")), 0)
            limit = int(input(Fore.BLUE + "Enter number of refreshes (0 for unlimited): "))
            headless = input(Fore.BLUE + "Run in headless mode? (y/n) [Headless mode runs the browser without a GUI, useful for background tasks]: ").lower() == 'y'
            load_wait = max(int(input(Fore.BLUE + "Enter wait time after page load in milliseconds (default 1000): ") or 1000), 0)
            screenshot = input(Fore.BLUE + "Take a screenshot after each refresh? (y/n): ").lower() == 'y'
            browser_count = max(int(input(Fore.BLUE + "Enter number of browsers to open simultaneously: ")), 1)

            # Select proxy if available
            proxy = None
            if proxies:
                print(Fore.MAGENTA + "Available proxies:")
                for i, p in enumerate(proxies):
                    print(Fore.MAGENTA + f"{i + 1}. {p}")
                proxy_choice = int(input(Fore.BLUE + "Choose a proxy by number (0 for none): "))
                if proxy_choice > 0:
                    proxy = proxies[proxy_choice - 1]

            # Select user-agent if available
            print(Fore.MAGENTA + "Available User-Agents:")
            for i, ua in enumerate(user_agents):
                print(Fore.MAGENTA + f"{i + 1}. {ua}")
            ua_choice = int(input(Fore.BLUE + "Choose a User-Agent by number: "))
            user_agent = user_agents[ua_choice - 1]

            # Run the auto-refresh script
            auto_refresh(urls, interval, limit, headless, proxy, load_wait, screenshot, user_agent, browser_count)
        elif choice == '4':
            print(Fore.GREEN + "\nAll credits to: https://github.com/Dalvelac/\n")
        elif choice == '5':
            print(Fore.RED + "Exiting...")
            break
        else:
            print(Fore.RED + "Invalid choice. Please try again.")

if __name__ == "__main__":
    menu()