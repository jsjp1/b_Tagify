from http.client import HTTPException
from typing import List
import json
import requests
from requests import Session
from yt_dlp import YoutubeDL
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from app.schemas.video import UserVideos, VideoAnalyze, VideoAnalyzeResponse
from config import Settings
from app.models.video import Video
from app.models.user import User
from app.models.video_tag import VideoTag
from app.models.tag import Tag
from app.models.user_video import UserVideo

class VideoService():
  @staticmethod
  def _extract_video_info(video_url: str, lang: str = 'ko') -> dict:
    """
    유튜브 비디오 링크 -> 자막 반환
    """
    ydl_opts = {
      "quiet": True,
      "skip_download": True,
      "cookiefile": "cookie.txt"
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
        return {
          "title": "",
          "thumbnail": "",
          "description": "",
          "tags": "",
          "length": "", # second
          "summation": "",
        }
      
      data = json.loads(response.text)
      captions = []
      for event in data.get("events", []):
          for seg in event.get("segs", []):
              text = seg.get("utf8", "").strip()
              if text:
                  captions.append(text)

      full_caption_text = " ".join(captions)
      
      video_info = {
        "title": info["title"],
        "thumbnail": info["thumbnail"],
        "description": info["description"],
        "tags": info["tags"],
        "length": info["duration"], # second
        "summation": full_caption_text,
      }
        
      return video_info
    
  @staticmethod
  async def analyze_video(video: VideoAnalyze, db: Session, settings: Settings) -> VideoAnalyzeResponse:
    """
    유저 oauth id + 비디오 링크 + ... -> tag_count 만큼의 태그 리스트 생성, db 저장 후 video_id 반환
    """
    db_user = db.query(User).filter(User.oauth_id == video.oauth_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
      
    db_video = db.query(Video).filter(Video.url == video.url).first()
    if not db_video:
      video_info = VideoService._extract_video_info(video.url)
      
      db_video = Video(
        url = video.url,
        title = video_info["title"],
        thumbnail = video_info["thumbnail"],
        video_length = video_info["length"],
      )
        
      db.add(db_video)
      db.commit()
      db.refresh(db_video)
    
    user_video_entry = db.query(UserVideo).filter(
      UserVideo.user_id == db_user.id,
      UserVideo.video_id == db_video.id
    ).first()
    
    if not user_video_entry:
      user_video_entry = UserVideo(user_id=db_user.id, video_id=db_video.id, summation=video_info["summation"])
      db.add(user_video_entry)
      db.commit()
    
    tag_list = video_info.get("tags", [])[:video.tag_count]
    video_tags = []
    
    for tag_name in tag_list:
      db_tag = db.query(Tag).filter(Tag.tagname == tag_name).first()
      
      if not db_tag:
        db_tag = Tag(tagname = tag_name)
        db.add(db_tag)
        try:
          db.commit()
        except IntegrityError:
          db.rollback()
          db_tag = db.query(Tag).filter(Tag.tagname == tag_name).first()
          
      video_tags.append(VideoTag(video_id=db_video.id, tag_id=db_tag.id))
      
    if video_tags:
      db.add_all(video_tags)
      db.commit()
    
    return VideoAnalyzeResponse(video_id=db_video.id, tags=tag_list)
  
  @staticmethod
  async def get_user_videos(user: UserVideos, db: Session) -> List[Video]:
    """
    유저가 소유한 비디오 정보를 모두 반환
    """
    videos = (
        db.query(Video)
        .join(UserVideo, UserVideo.video_id == Video.id)
        .join(User, User.id == UserVideo.user_id)
        .filter(User.oauth_id == user.oauth_id)
        .options(joinedload(Video.video_tags).joinedload(VideoTag.tag))
        .all()
    )
      
    return videos