import requests

def check_website(url='www.google.com', timeout=5):
    # Check if the URL starts with 'http://' or 'https://'
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return 'ok'
    except requests.exceptions.RequestException as e:
        return '403'

if __name__ == "__main__":
    check_website(url)