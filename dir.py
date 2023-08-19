import requests
import time
import concurrent.futures
from termcolor import colored
import sys

def check_path(url, line):
    line = line.strip()
    full_url = url.rstrip('/') + '/' + line.lstrip('/')
    response = requests.head(full_url)

    status_code = response.status_code

    if status_code == 200:
        content = requests.get(full_url).text
        if "404" in content:
            status = colored("404 Not Found", "black", "on_white")
        else:
            status = colored(f"{status_code} OK", "green")
    elif status_code == 301:
        status = colored("301 Moved Permanently", "blue")
    elif status_code == 304:
        status = colored("304 Not Modified", "yellow")
    elif status_code == 403:
        status = colored("403 Forbidden", "red")

    result = f"URL: {full_url} - Status: {status}"
    return result

def main():
    url = input("Enter the base URL: ")
    wordlist_path = input("Enter the path to the wordlist file: ")

    with open(wordlist_path, 'r') as wordlist_file:
        wordlist = wordlist_file.readlines()

    if url and wordlist:
        print('Results:\n')

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = [executor.submit(check_path, url, line) for line in wordlist]

            for future in concurrent.futures.as_completed(results):
                print(future.result())
                time.sleep(0.1)  # Memberikan jeda sebentar setelah setiap permintaan

        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"\nElapsed Time: {elapsed_time:.2f} seconds")
        sys.exit(0)  # Menghentikan eksekusi program setelah proses selesai

    else:
        print("URL and wordlist file are required.")
        sys.exit(1)  # Menghentikan eksekusi program karena kegagalan input

if __name__ == "__main__":
    main()
