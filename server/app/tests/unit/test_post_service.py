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


def test_extract_first_url_only_url():
    url = "https://www.example.com"
    assert PostService._extract_first_url(url) == "https://www.example.com"


def test_extract_first_url_with_prefix_text():
    url = "check this out: https://www.example.com"
    assert PostService._extract_first_url(url) == "https://www.example.com"


def test_extract_first_url_with_suffix_text():
    url = "https://www.example.com is great"
    assert PostService._extract_first_url(url) == "https://www.example.com"


def test_extract_first_url_multiple_urls():
    url = "first https://first.com and then https://second.com"
    assert PostService._extract_first_url(url) == "https://first.com"


def test_extract_first_url_with_http():
    url = "visit http://test.com"
    assert PostService._extract_first_url(url) == "http://test.com"


def test_extract_first_url_invalid_format():
    url = "htp://notvalid.com is wrong"
    with pytest.raises(ValueError) as exc_info:
        PostService._extract_first_url(url)
    assert str(exc_info.value) == "No valid URL found in input string"


def test_extract_first_url_with_trailing_punctuation():
    url = "link: https://example.com, and more"
    assert PostService._extract_first_url(url) == "https://example.com"


def test_extract_first_url_with_brackets():
    url = "(https://example.com)"
    assert PostService._extract_first_url(url) == "https://example.com"


## normalize url scheme unit test
# 1. 빈 문자열인 경우 → 빈 문자열 반환
# 2. 프로토콜이 생략된 경우 (//example.com) → https:// 붙여서 반환
# 3. 슬래시로 시작하는 상대경로인 경우 (/path/to/img) → base_url 기준으로 보정
# 4. 슬래시 없이 상대경로인 경우 (favicon.ico) → base_url 기준으로 보정
# 5. http로 시작하는 정상 URL → 그대로 반환
# 6. https로 시작하는 정상 URL → 그대로 반환


def test_normalize_url_empty():
    assert PostService._normalize_url_scheme("", "https://example.com") == ""


def test_normalize_url_protocol_relative():
    url = "//example.com/favicon.ico"
    expected = "https://example.com/favicon.ico"
    result = PostService._normalize_url_scheme(url, "https://base.com")
    assert result == expected


def test_normalize_url_relative_path_with_slash():
    url = "/images/icon.png"
    base_url = "https://example.com"
    expected = urljoin(base_url, url)
    result = PostService._normalize_url_scheme(url, base_url)
    assert result == expected


def test_normalize_url_relative_path_no_slash():
    url = "icon.png"
    base_url = "https://example.com"
    expected = urljoin(base_url, url)
    result = PostService._normalize_url_scheme(url, base_url)
    assert result == expected


def test_normalize_url_full_http():
    url = "http://example.com/icon.png"
    result = PostService._normalize_url_scheme(url, "https://base.com")
    assert result == url


def test_normalize_url_full_https():
    url = "https://example.com/icon.png"
    result = PostService._normalize_url_scheme(url, "https://base.com")
    assert result == url
