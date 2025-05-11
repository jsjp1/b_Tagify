import pytest
from app.services.video import VideoService

## extract video id unit test
# 1. 일반적인 youtube 영상 주소 -> video id 반환 (1, 2)
# 2. 일반적인 youtube music 주소 -> video id 반환 (3)
# 3. 일반적인 shorts 영상 주소 -> video id 반환 (4)
# 4. youtube 영상 주소 + v 쿼리스트링 없음 -> video id 반환 (5, 6)
# 5. 잘못된 youtube 영상 주소 -> 빈 문자열 반환 (7, 8, 9)


@pytest.mark.parametrize(
    "url, expected_video_id",
    [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtube.com/watch?v=abcdef12345", "abcdef12345"),
        ("https://music.youtube.com/watch?v=12345abcdef", "12345abcdef"),
        ("https://www.youtube.com/shorts/AbCdEf12345", "AbCdEf12345"),
        ("https://youtu.be/zYxkezUr8MQ", "zYxkezUr8MQ"),
        ("https://youtu.be/zYxkezUr8MQ?t=45", "zYxkezUr8MQ"),
        ("https://example.com/watch?v=notyoutube", ""),
        ("https://www.youtube.com/", ""),
        ("https://www.youtube.com/shorts/", ""),
    ],
)
def test_extract_video_id(url, expected_video_id):
    assert VideoService._extract_video_id(url) == expected_video_id
