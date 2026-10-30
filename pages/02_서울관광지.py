
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Seoul Tourist Map",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ 서울 관광지 TOP 10")
st.write("Top 10 Seoul Attractions for International Visitors")

# 관광지 이름, 위도, 경도, 설명
places = [
    {
        "ko": "경복궁",
        "en": "Gyeongbokgung Palace",
        "lat": 37.5796, "lon": 126.9770,
        "desc_ko": "조선 왕조의 대표 궁궐입니다.",
        "desc_en": "A famous royal palace from the Joseon Dynasty."
    },
    {
        "ko": "명동",
        "en": "Myeongdong",
        "lat": 37.5636, "lon": 126.9850,
        "desc_ko": "쇼핑과 한국 길거리 음식을 즐길 수 있습니다.",
        "desc_en": "A popular shopping and street food district."
    },
    {
        "ko": "N서울타워",
        "en": "N Seoul Tower",
        "lat": 37.5512, "lon": 126.9882,
        "desc_ko": "서울의 전망과 야경을 감상할 수 있습니다.",
        "desc_en": "A famous viewpoint with panoramic city views."
    },
    {
        "ko": "북촌한옥마을",
        "en": "Bukchon Hanok Village",
        "lat": 37.5826, "lon": 126.9830,
        "desc_ko": "한국 전통 한옥을 볼 수 있는 마을입니다.",
        "desc_en": "A traditional Korean hanok neighborhood."
    },
    {
        "ko": "홍대거리",
        "en": "Hongdae Street",
        "lat": 37.5563, "lon": 126.9236,
        "desc_ko": "거리 공연, 카페와 쇼핑을 즐길 수 있습니다.",
        "desc_en": "An area known for street performances and cafes."
    },
    {
        "ko": "광장시장",
        "en": "Gwangjang Market",
        "lat": 37.5700, "lon": 126.9997,
        "desc_ko": "빈대떡과 김밥 등 한국 음식을 맛볼 수 있습니다.",
        "desc_en": "A traditional market famous for Korean food."
    },
    {
        "ko": "창덕궁",
        "en": "Changdeokgung Palace",
        "lat": 37.5794, "lon": 126.9910,
        "desc_ko": "유네스코 세계유산으로 지정된 궁궐입니다.",
        "desc_en": "A UNESCO World Heritage palace."
    },
    {
        "ko": "동대문디자인플라자",
        "en": "Dongdaemun Design Plaza",
        "lat": 37.5671, "lon": 127.0095,
        "desc_ko": "독특한 건축물과 전시를 즐길 수 있습니다.",
        "desc_en": "A landmark known for modern architecture and exhibitions."
    },
    {
        "ko": "롯데월드타워",
        "en": "Lotte World Tower",
        "lat": 37.5125, "lon": 127.1025,
        "desc_ko": "전망대와 쇼핑 시설이 있는 랜드마크입니다.",
        "desc_en": "A landmark with an observation deck and shopping."
    },
    {
        "ko": "코엑스 별마당도서관",
        "en": "COEX Starfield Library",
        "lat": 37.5116, "lon": 127.0592,
        "desc_ko": "대형 서가가 인상적인 도서관입니다.",
        "desc_en": "A popular library space inside a shopping complex."
    }
]

# 언어 선택
language = st.selectbox(
    "언어 선택 / Select language",
    ["한국어", "English"]
)

# 관광지 검색
search = st.text_input(
    "관광지 검색 / Search attractions",
    placeholder="관광지 이름 입력 / Enter a place name"
).lower().strip()

# 검색 결과 필터링
filtered_places = [
    p for p in places
    if search in (p["ko"] + " " + p["en"]).lower()
]

# Folium 지도 만들기
seoul_map = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# 관광지 10곳을 지도에 표시
for index, place in enumerate(filtered_places, start=1):
    if language == "한국어":
        name = place["ko"]
        description = place["desc_ko"]
    else:
        name = place["en"]
        description = place["desc_en"]

    popup_html = f"""
    <div style="width:220px">
        <h4>{index}. {name}</h4>
        <p>{description}</p>
        <a href="https://www.google.com/maps/dir/?api=1&destination={place['lat']},{place['lon']}"
           target="_blank">
           Google Maps Directions
        </a>
    </div>
    """

    folium.Marker(
        location=[place["lat"], place["lon"]],
        tooltip=name,
        popup=folium.Popup(popup_html, max_width=280),
        icon=folium.Icon(
            color="red",
            icon="info-sign"
        )
    ).add_to(seoul_map)

# 지도 표시
st.subheader("📍 관광지 지도")

st_folium(
    seoul_map,
    use_container_width=True,
    height=600,
    returned_objects=[]
)

# 관광지 목록
st.subheader("🏙️ 추천 관광지 목록")

if filtered_places:
    for index, place in enumerate(filtered_places, start=1):
        if language == "한국어":
            name = place["ko"]
            description = place["desc_ko"]
        else:
            name = place["en"]
            description = place["desc_en"]

        with st.expander(f"{index}. {name}"):
            st.write(description)
            st.write(
                f"위도: {place['lat']}, 경도: {place['lon']}"
            )
            st.link_button(
                "Google Maps 길찾기",
                f"https://www.google.com/maps/dir/?api=1&destination={place['lat']},{place['lon']}"
            )
else:
    st.warning("검색 결과가 없습니다.")

st.caption(
    "이 TOP 10은 여행 참고용 추천 목록이며 "
    "공식 방문객 수 기준 순위는 아닙니다."
)
