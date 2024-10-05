import requests

def check_website(url):
    # Check if the URL starts with 'http://' or 'https://'
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Website {url} is accessible.")
        else:
            print(f"Website {url} returned status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(response.headers)

if __name__ == "__main__":
    while True:
        url = input("Enter the URL of the website to check (or type 'exit' to quit): ")
        if url.lower() == 'exit':
            break
        check_website(url)