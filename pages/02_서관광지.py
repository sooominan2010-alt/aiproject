
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Seoul Tourist Map",
    page_icon="🗺️",
    layout="wide"
)

# 서울 추천 관광지 TOP 10
places = [
    {
        "rank": 1,
        "ko": "경복궁",
        "en": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "address": "서울 종로구 사직로 161",
        "ko_desc": "조선 왕조의 대표 궁궐로 한국 전통 건축을 감상할 수 있습니다.",
        "en_desc": "A famous royal palace known for traditional Korean architecture."
    },
    {
        "rank": 2,
        "ko": "명동",
        "en": "Myeongdong",
        "lat": 37.5636,
        "lon": 126.9850,
        "address": "서울 중구 명동 일대",
        "ko_desc": "화장품 쇼핑과 한국 길거리 음식을 즐길 수 있습니다.",
        "en_desc": "A popular shopping district with Korean street food."
    },
    {
        "rank": 3,
        "ko": "N서울타워",
        "en": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "address": "서울 용산구 남산공원길 105",
        "ko_desc": "서울의 전경과 야경을 감상할 수 있는 전망 명소입니다.",
        "en_desc": "A famous viewpoint offering panoramic views of Seoul."
    },
    {
        "rank": 4,
        "ko": "북촌한옥마을",
        "en": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "address": "서울 종로구 북촌로 일대",
        "ko_desc": "전통 한옥이 모여 있는 아름다운 마을입니다.",
        "en_desc": "A neighborhood featuring traditional Korean houses."
    },
    {
        "rank": 5,
        "ko": "홍대거리",
        "en": "Hongdae Street",
        "lat": 37.5563,
        "lon": 126.9236,
        "address": "서울 마포구 홍익로 일대",
        "ko_desc": "거리 공연과 카페, 패션 매장을 즐길 수 있습니다.",
        "en_desc": "A lively area known for street performances and cafes."
    },
    {
        "rank": 6,
        "ko": "광장시장",
        "en": "Gwangjang Market",
        "lat": 37.5700,
        "lon": 126.9997,
        "address": "서울 종로구 창경궁로 88",
        "ko_desc": "빈대떡과 김밥 등 한국 전통 음식을 맛볼 수 있습니다.",
        "en_desc": "A traditional market famous for Korean street food."
    },
    {
        "rank": 7,
        "ko": "창덕궁",
        "en": "Changdeokgung Palace",
        "lat": 37.5794,
        "lon": 126.9910,
        "address": "서울 종로구 율곡로 99",
        "ko_desc": "유네스코 세계유산으로 지정된 아름다운 궁궐입니다.",
        "en_desc": "A UNESCO World Heritage palace in Seoul."
    },
    {
        "rank": 8,
        "ko": "동대문디자인플라자",
        "en": "Dongdaemun Design Plaza",
        "lat": 37.5671,
        "lon": 127.0095,
        "address": "서울 중구 을지로 281",
        "ko_desc": "독특한 건축물과 전시, 디자인 행사를 즐길 수 있습니다.",
        "en_desc": "A landmark known for modern architecture and exhibitions."
    },
    {
        "rank": 9,
        "ko": "롯데월드타워",
        "en": "Lotte World Tower",
        "lat": 37.5125,
        "lon": 127.1025,
        "address": "서울 송파구 올림픽로 300",
        "ko_desc": "전망대와 쇼핑 시설을 즐길 수 있는 서울의 랜드마크입니다.",
        "en_desc": "A Seoul landmark with an observation deck and shopping."
    },
    {
        "rank": 10,
        "ko": "코엑스 별마당도서관",
        "en": "COEX Starfield Library",
        "lat": 37.5116,
        "lon": 127.0592,
        "address": "서울 강남구 영동대로 513",
        "ko_desc": "대형 서가가 인상적인 도서관과 쇼핑몰을 둘러볼 수 있습니다.",
        "en_desc": "A popular library space inside a large shopping complex."
    }
]

st.title("🗺️ 서울 관광지 TOP 10")
st.write("Seoul Tourist Attractions Map")

language = st.radio(
    "언어 선택 / Select language",
    ["한국어", "English"],
    horizontal=True
)

search = st.text_input(
    "관광지 검색 / Search",
    placeholder="관광지 이름을 입력하세요"
)

filtered_places = [
    p for p in places
    if search.lower() in (
        p["ko"] + " " + p["en"]
    ).lower()
]

left, right = st.columns([1, 2])

with left:
    st.subheader("추천 관광지")

    for p in filtered_places:
        name = p["ko"] if language == "한국어" else p["en"]
        desc = p["ko_desc"] if language == "한국어" else p["en_desc"]

        with st.container(border=True):
            st.markdown(f"**{p['rank']}. {name}**")
            st.write(desc)
            st.caption(p["address"])

            url = (
                "https://www.google.com/maps/dir/?api=1"
                f"&destination={p['lat']},{p['lon']}"
            )

            st.link_button(
                "구글 지도 길찾기",
                url,
                use_container_width=True
            )

with right:
    st.subheader("관광지 지도")

    map_view = folium.Map(
        location=[37.5665, 126.9780],
        zoom_start=12,
        tiles="OpenStreetMap"
    )

    for p in filtered_places:
        name = p["ko"] if language == "한국어" else p["en"]
        desc = p["ko_desc"] if language == "한국어" else p["en_desc"]

        popup_text = f"""
        <h4>{p['rank']}. {name}</h4>
        <p>{desc}</p>
        <p>{p['address']}</p>
        """

        folium.Marker(
            location=[p["lat"], p["lon"]],
            tooltip=f"{p['rank']}. {name}",
            popup=folium.Popup(popup_text, max_width=280),
            icon=folium.Icon(
                color="red" if p["rank"] <= 3 else "blue",
                icon="info-sign"
            )
        ).add_to(map_view)

    st_folium(
        map_view,
        use_container_width=True,
        height=650,
        returned_objects=[]
    )

st.caption(
    "관광지 TOP 10은 여행 참고용 추천 목록이며 "
    "공식 방문객 수 순위는 아닙니다."
)
