import streamlit as st
import requests
import random

# --- 앱 기본 설정 ---
st.set_page_config(page_title="오늘 날씨, 무슨 영화 볼까?")
st.title("🎬 오늘 날씨, 무슨 영화 볼까?")
st.subheader("도시의 날씨에 맞는 그림과 영화를 추천해 드립니다.")

# --- API 설정 및 키 입력 UI ---
st.sidebar.header("⚙️ API 키 설정")
omdb_api_key = st.sidebar.text_input("OMDb API 키를 입력하세요:", type="password")
st.sidebar.info("OMDb API 키는 [omdbapi.com](http://www.omdbapi.com/)에서 발급받을 수 있습니다.")

# --- API 호출 함수 ---
def get_coordinates(city):
    """도시 이름을 위도/경도로 변환하는 함수 (Nominatim API 사용)"""
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "My-Streamlit-App"
    }
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        else:
            return None, None
    except requests.exceptions.RequestException as e:
        st.error(f"도시 위치 정보를 가져오는 중 오류가 발생했습니다: {e}")
        return None, None

def get_weather(lat, lon):
    """Open-Meteo API를 호출하여 날씨 정보를 가져오는 함수"""
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weather_code",
        "timezone": "auto"
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"날씨 정보를 가져오는 중 오류가 발생했습니다: {e}")
        return None

# WMO Weather interpretation codes
WEATHER_CODES = {
    0: "맑음", 1: "대체로 맑음", 2: "부분적으로 흐림", 3: "흐림",
    45: "안개", 48: "서리 안개", 51: "약한 이슬비", 53: "보통 이슬비",
    55: "강한 이슬비", 56: "약한 어는 이슬비", 57: "강한 어는 이슬비",
    61: "약한 비", 63: "보통 비", 65: "강한 비",
    66: "약한 어는 비", 67: "강한 어는 비", 71: "약한 눈", 73: "보통 눈",
    75: "강한 눈", 77: "눈송이", 80: "약한 소나기", 81: "보통 소나기",
    82: "강한 소나기", 85: "약한 눈 소나기", 86: "강한 눈 소나기",
    95: "약한/보통 천둥번개", 96: "우박을 동반한 천둥번개", 99: "강한 우박을 동반한 천둥번개",
}

def get_image_prompt(weather_code):
    """날씨 코드에 맞는 영어 프롬프트를 반환하는 함수"""
    if weather_code in [0, 1]:
        return "a bright cartoon drawing of a smiling sun in a blue sky"
    elif weather_code in [2, 3]:
        return "a beautiful digital illustration of a soft, fluffy cloud in the sky"
    elif weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return "a cozy anime drawing of a sad cloud raining"
    elif weather_code in [71, 73, 75, 77, 85, 86]:
        return "a beautiful fantasy art of magical snowflakes falling"
    elif weather_code in [95, 96, 99]:
        return "a dramatic oil painting of a thunderstorm with lightning"
    elif weather_code in [45, 48]:
        return "a serene ink wash painting of a foggy mountain landscape"
    else:
        return "a vibrant digital art of a beautiful landscape"

def recommend_movie_and_genre(weather_code):
    """날씨 코드를 바탕으로 영화 제목과 장르를 반환하는 함수"""
    if weather_code in [0, 1]:
        return "로맨스/코미디", "화창한 날", "La La Land"
    elif weather_code in [2, 3]:
        return "판타지/모험", "흐린 날", "Harry Potter and the Sorcerer's Stone"
    elif weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return "드라마/미스터리", "비 오는 날", "Parasite"
    elif weather_code in [71, 73, 75, 77, 85, 86]:
        return "가족/애니메이션", "눈 오는 날", "Frozen II"
    elif weather_code in [95, 96, 99]:
        return "액션/스릴러", "천둥번개 치는 날", "Mad Max: Fury Road"
    elif weather_code in [45, 48]:
        return "SF/공포", "안개 낀 날", "Blade Runner 2049"
    else:
        return "장르 무관", "어떤 날씨", "Inception"

def get_movie_details(title, api_key):
    """OMDb API를 호출하여 영화 상세 정보를 가져오는 함수"""
    if not api_key:
        return None
    base_url = "http://www.omdbapi.com/"
    params = {
        "apikey": api_key,
        "t": title,
        "plot": "full",
        "r": "json"
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("Response") == "True":
            return data
        else:
            st.error(f"영화 '{title}'의 정보를 찾을 수 없습니다: {data.get('Error')}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"영화 정보를 가져오는 중 오류가 발생했습니다: {e}")
        return None

# --- 메인 로직 ---
city_name = st.text_input("도시 이름을 입력하세요 (예: 서울, 파리, New York)", placeholder="도시명")

if st.button("추천 받기"):
    if not city_name:
        st.warning("도시 이름을 입력해주세요.")
    elif not omdb_api_key:
        st.warning("사이드바에 OMDb API 키를 입력해주세요.")
    else:
        with st.spinner("날씨와 영화 정보 가져오는 중..."):
            lat, lon = get_coordinates(city_name)
            
            if lat is not None and lon is not None:
                weather_data = get_weather(lat, lon)
                
                if weather_data:
                    weather_code = weather_data['current']['weather_code']
                    temp = weather_data['current']['temperature_2m']
                    
                    weather_description = WEATHER_CODES.get(weather_code, "알 수 없음")
                    
                    st.success("✅ 날씨 정보를 가져왔습니다!")
                    st.markdown("---")
                    
                    st.markdown(f"**현재 날씨:** {weather_description.capitalize()}")
                    st.markdown(f"**현재 기온:** {temp:.1f}°C")
                    
                    # 날씨 이미지 생성 및 표시
                    image_prompt = get_image_prompt(weather_code)
                    print(image_prompt)
                    # 
                    st.markdown("---")
                    
                    # 영화 추천 정보
                    genre, weather_phrase, movie_title = recommend_movie_and_genre(weather_code)
                    st.markdown(f"### 🎬 {weather_phrase} 당신에게 어울리는 영화")
                    
                    movie_details = get_movie_details(movie_title, omdb_api_key)
                    
                    if movie_details:
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            if movie_details['Poster'] != "N/A":
                                st.image(movie_details['Poster'], use_container_width=True)
                        with col2:
                            st.markdown(f"**{movie_details['Title']}**")
                            st.caption(f"개봉일: {movie_details['Released']} | 장르: {movie_details['Genre']}")
                            st.markdown(f"평점: {movie_details['imdbRating']}/10")
                            st.write(movie_details['Plot'])
                    else:
                        st.warning("추천 영화의 정보를 가져올 수 없습니다. OMDb API 키를 확인해주세요.")
            else:
                st.error("입력하신 도시를 찾을 수 없습니다. 도시 이름을 확인해주세요.")