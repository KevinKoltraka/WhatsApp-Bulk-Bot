from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor
from webdriver_manager.chrome import ChromeDriverManager
import os

# Set up Selenium options
options = Options()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument("--profile-directory=Default")
options.add_argument("--user-data-dir=/var/tmp/chrome_user_data")  # Ensure path exists and is writable

os.system("")
os.environ["WDM_LOG_LEVEL"] = "0"

class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

print(style.BLUE)
print("*****                                               ******")
print("*****  THANK YOU FOR USING WHATSAPP BULK MESSENGER  ******")
print("*****      This tool was built by Kevin      ******")
print("*****           https://github.com/KevinKoltraka/WhatsApp-Bulk-Bot         ******")
print("*****                                               ******")
print(style.RESET)

# Read message from file
with open("message.txt", "r") as f:
    message = f.read()
message = quote(message)

print(style.YELLOW + '\nThis is your message-')
print(style.GREEN + message)
print("\n" + style.RESET)

# Read numbers from file
def read_numbers(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

numbers = read_numbers("numbers.txt")
total_numbers = len(numbers)
print(style.RED + f'We found {total_numbers} numbers in the file' + style.RESET)

delay = 30
failed_numbers = []

# Set up WebDriver globally
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

print('Once your browser opens up, sign in to WhatsApp Web.')
driver.get("https://web.whatsapp.com")
input(style.MAGENTA + "AFTER logging into WhatsApp Web, if your chats are visible, press ENTER..." + style.RESET)

# Send message function
def send_message(number):
    global failed_numbers
    try:
        url = f'https://web.whatsapp.com/send?phone={number}&text={message}'
        driver.get(url)
        sent = False

        # Retry mechanism
        for attempt in range(3):
            if not sent:
                try:
                    # Wait for the send button to appear
                    click_btn = WebDriverWait(driver, delay).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[@data-icon='send']"))
                    )
                    sleep(1)
                    driver.execute_script("arguments[0].click();", click_btn)
                    sent = True
                    sleep(3)
                    print(style.GREEN + f'Message sent to: {number}' + style.RESET)
                except Exception as e:
                    print(style.RED + f'Failed to send message to {number}, retrying ({attempt + 1}/3)' + style.RESET)
        if not sent:
            print(style.RED + f'Failed to send message to {number} after retries.' + style.RESET)
            failed_numbers.append(number)
    except Exception as e:
        print(style.RED + f'Error with number {number}: {str(e)}' + style.RESET)
        failed_numbers.append(number)

# Process numbers in chunks to avoid memory issues
def process_numbers_in_chunks(numbers, chunk_size=100):
    for i in range(0, len(numbers), chunk_size):
        yield numbers[i:i + chunk_size]

# Thread pool for parallel message sending
def send_messages_in_parallel(numbers, max_threads=5):
    with ThreadPoolExecutor(max_threads) as executor:
        executor.map(send_message, numbers)

# Main processing loop
for chunk in process_numbers_in_chunks(numbers):
    print(style.YELLOW + f'Processing chunk of {len(chunk)} numbers...' + style.RESET)
    send_messages_in_parallel(chunk)

# Log failed numbers
if failed_numbers:
    with open("failed_numbers.txt", "w") as f:
        f.write("\n".join(failed_numbers))
    print(style.RED + f'{len(failed_numbers)} numbers failed to receive messages. Saved to "failed_numbers.txt".' + style.RESET)
else:
    print(style.GREEN + 'All messages sent successfully!' + style.RESET)

# Close the browser
driver.quit()
