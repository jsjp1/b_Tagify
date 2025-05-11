from urllib.parse import urljoin

import pytest
from app.services.post import PostService
from bs4 import BeautifulSoup

## get favicon unit test
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


## extract first url unit test
# 1. 가장 일반적인 평범한 경로
# 2. url 앞부분에 문자열이 붙는 경우 (쿠팡 url)
# 3. url 뒷부분에 문자열이 붙는 경우
# 4. url 두개 오는 경우, 앞에 있는걸 취함
# 5. https 대신 http
# 6. 잘못된 프로토콜 스킴
# 7. 앞, 뒷부분 모두 문자열 붙는 경우
# 8. 괄호가 붙는 경우


@pytest.mark.parametrize(
    "input_text, expected_url",
    [
        ("https://www.example.com", "https://www.example.com"),
        ("check this out: https://www.example.com", "https://www.example.com"),
        ("https://www.example.com is great", "https://www.example.com"),
        ("first https://first.com and then https://second.com", "https://first.com"),
        ("visit http://test.com", "http://test.com"),
        ("link: https://example.com, and more", "https://example.com"),
        ("(https://example.com)", "https://example.com"),
    ],
)
def test_extract_first_url_valid(input_text, expected_url):
    assert PostService._extract_first_url(input_text) == expected_url


@pytest.mark.parametrize(
    "input_text",
    [
        "htp://notvalid.com is wrong",
        "this string has no link",
        "ftp://example.com",
    ],
)
def test_extract_first_url_invalid(input_text):
    with pytest.raises(ValueError) as exc_info:
        PostService._extract_first_url(input_text)
    assert str(exc_info.value) == "No valid URL found in input string"


## normalize url scheme unit test
# 1. 빈 문자열인 경우 → 빈 문자열 반환
# 2. 프로토콜이 생략된 경우 (//example.com) → https:// 붙여서 반환
# 3. 슬래시로 시작하는 상대경로인 경우 (/path/to/img) → base_url 기준으로 보정
# 4. 슬래시 없이 상대경로인 경우 (favicon.ico) → base_url 기준으로 보정
# 5. http로 시작하는 정상 URL → 그대로 반환
# 6. https로 시작하는 정상 URL → 그대로 반환


@pytest.mark.parametrize(
    "url, base_url, expected",
    [
        ("", "https://example.com", ""),
        (
            "//example.com/favicon.ico",
            "https://base.com",
            "https://example.com/favicon.ico",
        ),
        (
            "/images/icon.png",
            "https://example.com",
            urljoin("https://example.com", "/images/icon.png"),
        ),
        ("icon.png", "https://example.com", urljoin("https://example.com", "icon.png")),
        (
            "http://example.com/icon.png",
            "https://base.com",
            "http://example.com/icon.png",
        ),
        (
            "https://example.com/icon.png",
            "https://base.com",
            "https://example.com/icon.png",
        ),
    ],
)
def test_normalize_url_scheme(url, base_url, expected):
    result = PostService._normalize_url_scheme(url, base_url)
    assert result == expected
