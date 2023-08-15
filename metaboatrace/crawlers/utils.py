import io

import requests


def fetch_html_as_io(url: str) -> io.StringIO:
    response = requests.get(url)
    response.raise_for_status()
    return io.StringIO(response.text)
