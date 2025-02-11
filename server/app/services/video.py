from http.client import HTTPException
from typing import List
from fastapi import requests
from requests import Session
from sqlalchemy.exc import IntegrityError
import isodate
from sqlalchemy.orm import joinedload
from googleapiclient.discovery import build
from app.schemas.video import UserVideos, VideoAnalyze, VideoAnalyzeResponse
from config import Settings
from app.models.video import Video
from app.models.user import User
from app.models.video_tag import VideoTag
from app.models.tag import Tag
from app.models.user_video import UserVideo
from app.models.user_tag import UserTag

class VideoService():
  @staticmethod
  def _extract_video_id(video_url: str) -> str:
    """YouTube URL에서 영상 ID 추출"""
    from urllib.parse import urlparse, parse_qs
    
    parsed_url = urlparse(video_url)
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed_url.query).get("v", [""])[0]
    elif parsed_url.hostname in ["youtu.be"]:
        return parsed_url.path.lstrip("/")
    return ""

  @staticmethod
  def _convert_duration_to_seconds(duration: str) -> int:
    """ISO 8601 형식의 동영상 길이를 초 단위로 변환"""
    try:
        return int(isodate.parse_duration(duration).total_seconds())
    except:
        return 0
      
  @staticmethod
  def _get_auto_captions(video_id: str, lang: str = "ko") -> str:
      """
      YouTube 자동 생성 자막 가져오기
      """
      caption_url = f"https://www.youtube.com/api/timedtext?v={video_id}&lang={lang}&fmt=srv3"
      
      response = requests.get(caption_url)
      if response.status_code != 200:
          return ""
      
      from xml.etree import ElementTree
      root = ElementTree.fromstring(response.text)
      captions = " ".join([elem.text for elem in root.findall(".//text") if elem.text])
      
      return captions
    
  @staticmethod
  def _extract_video_info(video_url: str, settings: Settings, lang: str = 'ko') -> dict:
    """
    유튜브 비디오 링크 -> 자막 반환
    """
    video_id = VideoService._extract_video_id(video_url)
    youtube = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)
    
    request = youtube.videos().list(
      part="snippet,contentDetails",
      id=video_id
    )
    response = request.execute()
    
    if not response["items"]:
      return {
          "title": "",
          "thumbnail": "",
          "description": "",
          "tags": [],
          "length": 0,  # 초 단위
          "summation": "",
      }

    video_data = response["items"][0]
    snippet = video_data["snippet"]
    content_details = video_data["contentDetails"]

    video_info = {
        "title": snippet.get("title", ""),
        "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
        "description": snippet.get("description", ""),
        "tags": snippet.get("tags", []),
        "length": VideoService._convert_duration_to_seconds(content_details.get("duration", "")),
        "summation": VideoService._get_auto_captions(video_id, lang),
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
      video_info = VideoService._extract_video_info(video.url, settings)
      
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
    user_tags = []
    
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
      user_tags.append(UserTag(user_id=db_user.id, tag_id=db_tag.id))
      
    if video_tags:
      db.add_all(video_tags)
    if user_tags:
      db.add_all(user_tags)
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