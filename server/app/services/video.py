from typing import List
import json
import requests
from requests import Session
from yt_dlp import YoutubeDL
from sqlalchemy.orm import joinedload
from app.schemas.video import UserVideos, VideoAnalyze, VideoAnalyzeResponse
from config import Settings
from app.models.video import Video
from app.models.user import User
from app.models.video_tag import VideoTag

class VideoService():
  @staticmethod
  def _get_caption(video_url: str, lang: str = 'ko') -> str:
    """
    유튜브 비디오 링크 -> 자막 반환
    """
    ydl_opts = {
      "quiet": True,
      "skip_download": True,
    }
    
    with YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(video_url, download=False)
      
      caption_url = ""
      subtitles = info.get("subtitles", {}).get(lang, [])
      if subtitles:
        caption_url = subtitles[0]["url"]
      else:
        auto_captions = info.get("automatic_captions", {}).get(lang, [])
        caption_url = auto_captions[0]["url"]
        
      response = requests.get(caption_url)
      if response.status_code != 200:
        return ""
      
      data = json.loads(response.text)
      captions = []
      for event in data.get("events", []):
          for seg in event.get("segs", []):
              text = seg.get("utf8", "").strip()
              if text:
                  captions.append(text)

      full_caption_text = " ".join(captions)
        
      return full_caption_text
    
  @staticmethod
  async def analyze_video(video: VideoAnalyze, db: Session, settings: Settings) -> VideoAnalyzeResponse:
    """
    유저 oauth id + 비디오 링크 + ... -> tag_count 만큼의 태그 리스트 생성, db 저장 후 video_id 반환
    """
    caption = VideoService._get_caption(video.url)
    print(caption)
    return {"video_id": 123}
  
  @staticmethod
  async def get_user_videos(user: UserVideos, db: Session) -> List[Video]:
    """
    유저가 소유한 비디오 정보를 모두 반환
    """
    videos = (
        db.query(Video)
        .join(User)
        .filter(User.oauth_id == user.oauth_id)
        .options(joinedload(Video.video_tags).joinedload(VideoTag.tag)) 
        .all()
    )
      
    return videos