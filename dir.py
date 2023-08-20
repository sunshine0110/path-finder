import requests
import time
import concurrent.futures
from termcolor import colored
import sys
import signal

# Global flag to indicate if the process should be terminated
terminate_process = False

def signal_handler(sig, frame):
    global terminate_process
    print("\nCtrl+C detected. Finishing current tasks and exiting gracefully...")
    terminate_process = True

def check_path(session, url, line, timeout=10):
    if terminate_process:
        return  # If the termination flag is set, stop processing

    line = line.strip()
    full_url = url.rstrip('/') + '/' + line.lstrip('/')

    try:
        response = session.head(full_url, timeout=timeout)
        status_code = response.status_code

        if status_code == 200:
            content = response.content.decode("utf-8")
            status = colored(f"{status_code} OK", "green")
        elif status_code == 301:
            status = colored("301 Moved Permanently", "blue")
        elif status_code == 304:
            status = colored("304 Not Modified", "yellow")
        elif status_code == 403:
            status = colored("403 Forbidden", "red")
        else:
            status = colored(f"404 Not Found", "magenta")
    except requests.Timeout:
        status = colored("Timeout", "magenta")
    except requests.RequestException:
        status = colored("Connection Error", "red")

    result = f"URL: {full_url} - Status: {status}"
    return result

def main():
    signal.signal(signal.SIGINT, signal_handler)  # Register the signal handler

    url = input("Enter the base URL: ")
    wordlist_path = input("Enter the path to the wordlist file: ")

    with open(wordlist_path, 'r') as wordlist_file:
        wordlist = wordlist_file.readlines()

    if url and wordlist:
        print('Results:\n')

        session = requests.Session()

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = [executor.submit(check_path, session, url, line) for line in wordlist]

            for future in concurrent.futures.as_completed(results):
                if terminate_process:
                    break  # Exit the loop if termination flag is set
                print(future.result())
                time.sleep(0.1)

        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"\nElapsed Time: {elapsed_time:.2f} seconds")
        
    else:
        print("URL and wordlist file are required.")
        sys.exit(1)

if __name__ == "__main__":
    main()
    sys.exit(0)  # Move this line out of the main() function

