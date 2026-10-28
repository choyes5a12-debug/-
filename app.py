# 1. 라이브러리 설치
!pip install --quiet google-api-python-client

from google.colab import userdata
from googleapiclient.discovery import build
import re

# 2. API 키 설정 (보안 비밀 사용 권장)
try:
  API_KEY = userdata.get('YOUTUBE_API_KEY')
except Exception:
  API_KEY = 'AIzaSyAAb_djzBxwZ65o2FIFdiUv4CWNltWC1xw'

youtube = build('youtube', 'v3', developerKey=API_KEY)


# 3. URL에서 Video ID 추출 함수 (일반/Shorts/모바일 URL 모두 지원)
def extract_video_id(url):
  pattern = r'(?:v=|\/shorts\/|youtu\.be\/)([a-zA-Z0-9_-]{11})'
  match = re.search(pattern, url)
  return match.group(1) if match else url.strip()


# 4. 최다 좋아요 댓글 1개 추출 함수
def get_top_comment(video_url, max_fetch=1000):
  video_id = extract_video_id(video_url)

  try:
    request = youtube.commentThreads().list(
        part='snippet', videoId=video_id, maxResults=100, textFormat='plainText'
    )

    top_comment = None
    max_likes = -1
    fetched_count = 0

    while request and fetched_count < max_fetch:
      response = request.execute()
      for item in response.get('items', []):
        snippet = item['snippet']['topLevelComment']['snippet']
        like_count = snippet['likeCount']
        fetched_count += 1

        # 지금까지 발견된 최다 좋아요 수보다 높은 경우 갱신
        if like_count > max_likes:
          max_likes = like_count
          top_comment = {
              'author': snippet['authorDisplayName'],
              'text': snippet['textDisplay'],
              'likes': like_count,
              'published': snippet['publishedAt'][:10],
          }

      request = youtube.commentThreads().list_next(
          previous_request=request, previous_response=response
      )

    return top_comment

  except Exception as e:
    print(f'오류 발생: {e}')
    return None


# 5. 실행부 (링크 입력창 생성)
url_input = input('유튜브 영상 링크 주소를 입력하세요: ')
print('\n🔄 댓글 탐색 중...')

result = get_top_comment(url_input, max_fetch=1000)

if result:
  print('\n' + '=' * 50)
  print('🏆 [가장 좋아요를 많이 받은 댓글 1위]')
  print('=' * 50)
  print(f'👤 작성자  : {result["author"]}')
  print(f'👍 좋아요  : {result["likes"]:,}개')
  print(f'📅 작성일  : {result["published"]}')
  print(f'💬 내용    :\n{result["text"]}')
  print('=' * 50)
else:
  print('\n❌ 댓글을 가져올 수 없거나 댓글이 비활성화된 영상입니다.')
