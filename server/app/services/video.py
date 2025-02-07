from typing import List
from requests import Session
from app.schemas.video import VideoAnalyze
from config import Settings

class VideoService():
  @staticmethod
  async def analyze_video(video: VideoAnalyze, db: Session, settings: Settings) -> List[str]:
    """
    비디오 링크 -> tag_count 만큼의 태그 리스트 생성 후 반환
    """
    tags = []
    return tags