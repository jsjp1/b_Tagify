from requests import Session
from app.schemas.video import VideoAnalyze, VideoAnalyzeResponse
from config import Settings
from yt_dlp import YoutubeDL

class VideoService():
  @staticmethod
  async def analyze_video(video: VideoAnalyze, db: Session, settings: Settings) -> VideoAnalyzeResponse:
    """
    비디오 링크 -> tag_count 만큼의 태그 리스트 생성, db 저장 후 video_id 반환
    """
    return {"video_id": 1234}