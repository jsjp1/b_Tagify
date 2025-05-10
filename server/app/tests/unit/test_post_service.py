from app.services.post import PostService
from bs4 import BeautifulSoup

# get favicon unit test
# 1. 절대 경로
# 2. 상대 경로
# 3. icon이 존재하지만, base url이 없는 경우
# 4. icon이 없는 경우


def test_get_favicon_absolute_url():
    html = """
    <html>
        <head>
            <link rel="icon" href="https://cdn.example.com/favicon.png">
        </head>
    </html>
    """
    bs = BeautifulSoup(html, "html.parser")
    result = PostService._get_favicon("https://example.com", bs)
    assert result == "https://cdn.example.com/favicon.png"


def test_get_favicon_relative_path():
    html = """
    <html>
        <head>
            <link rel="icon" href="/favicon.ico">
        </head>
    </html>
    """
    bs = BeautifulSoup(html, "html.parser")
    result = PostService._get_favicon("https://example.com", bs)
    assert result == "https://example.com/favicon.ico"


def test_get_favicon_relative_path_no_slash():
    html = """
    <html>
        <head>
            <link rel="icon" href="images/favicon.ico">
        </head>
    </html>
    """
    bs = BeautifulSoup(html, "html.parser")
    result = PostService._get_favicon("https://example.com", bs)
    assert result == "https://example.com/images/favicon.ico"


def test_get_favicon_no_icon_tag():
    html = "<html><head></head><body>No icons here</body></html>"
    bs = BeautifulSoup(html, "html.parser")
    result = PostService._get_favicon("https://example.com", bs)
    assert result == "https://example.com/favicon.ico"
