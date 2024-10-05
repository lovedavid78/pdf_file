import requests

url = 'http://www.google.com'


def check_website(u1, timeout=5):
    response = requests.get(u1, timeout=timeout)
    if response.status_code == 200:
        return 'ok'
    else:
        return '403'


if __name__ == "__main__":
    check_website(url)
