
import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
from urllib.parse import quote

st.set_page_config(
    page_title="서울 1박 2일 관광 지도",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ 서울 주요 관광지 TOP 10")
st.subheader("외국인 관광객을 위한 1박 2일 여행 코스")
st.write("여행 시간: 매일 오전 9시 ~ 오후 7시")
st.caption(
    "관광지 추천 순위는 공식 방문객 수 순위가 아닌 여행 추천 목록입니다."
)

# --------------------------------------------------
# 1. 관광지 데이터
# --------------------------------------------------

places = [
    {
        "name": "경복궁",
        "en": "Gyeongbokgung Palace",
        "lat": 37.5796, "lon": 126.9770,
        "day": 1, "time": "09:30~10:45",
        "address": "서울 종로구 사직로 161",
        "desc": "조선 왕조의 대표 궁궐"
    },
    {
        "name": "북촌한옥마을",
        "en": "Bukchon Hanok Village",
        "lat": 37.5826, "lon": 126.9830,
        "day": 1, "time": "11:00~11:40",
        "address": "서울 종로구 북촌로 일대",
        "desc": "한국 전통 한옥과 골목 풍경"
    },
    {
        "name": "창덕궁",
        "en": "Changdeokgung Palace",
        "lat": 37.5794, "lon": 126.9910,
        "day": 1, "time": "11:50~12:30",
        "address": "서울 종로구 율곡로 99",
        "desc": "유네스코 세계유산 궁궐"
    },
    {
        "name": "광장시장",
        "en": "Gwangjang Market",
        "lat": 37.5700, "lon": 126.9997,
        "day": 1, "time": "13:30~14:15",
        "address": "서울 종로구 창경궁로 88",
        "desc": "빈대떡과 김밥 등 한국 음식"
    },
    {
        "name": "동대문디자인플라자",
        "en": "Dongdaemun Design Plaza",
        "lat": 37.5671, "lon": 127.0095,
        "day": 1, "time": "14:30~15:15",
        "address": "서울 중구 을지로 281",
        "desc": "현대적인 건축과 전시 공간"
    },
    {
        "name": "명동",
        "en": "Myeongdong",
        "lat": 37.5636, "lon": 126.9850,
        "day": 1, "time": "15:45~16:30",
        "address": "서울 중구 명동 일대",
        "desc": "쇼핑과 길거리 음식"
    },
    {
        "name": "N서울타워",
        "en": "N Seoul Tower",
        "lat": 37.5512, "lon": 126.9882,
        "day": 1, "time": "17:00~19:00",
        "address": "서울 용산구 남산공원길 105",
        "desc": "서울 전망과 야경"
    },
    {
        "name": "코엑스 별마당도서관",
        "en": "COEX Starfield Library",
        "lat": 37.5116, "lon": 127.0592,
        "day": 2, "time": "09:30~11:00",
        "address": "서울 강남구 영동대로 513",
        "desc": "대형 서가와 쇼핑 공간"
    },
    {
        "name": "롯데월드타워",
        "en": "Lotte World Tower",
        "lat": 37.5125, "lon": 127.1025,
        "day": 2, "time": "11:30~13:00",
        "address": "서울 송파구 올림픽로 300",
        "desc": "서울의 대표적인 초고층 랜드마크"
    },
    {
        "name": "홍대거리",
        "en": "Hongdae Street",
        "lat": 37.5563, "lon": 126.9236,
        "day": 2, "time": "15:00~18:30",
        "address": "서울 마포구 홍익로 일대",
        "desc": "거리 공연, 카페, 패션 매장"
    }
]

# --------------------------------------------------
# 2. 식당 및 호텔 링크
# --------------------------------------------------

def google_maps_search(query):
    return (
        "https://www.google.com/maps/search/?api=1&query="
        + quote(query)
    )

def google_directions(lat, lon):
    return (
        "https://www.google.com/maps/dir/?api=1&destination="
        + f"{lat},{lon}"
    )

# 식당은 동선과 식사 시간에 맞춘 추천 검색 링크입니다.
meals = [
    {
        "day": "1일 차",
        "time": "09:00~09:25",
        "type": "아침",
        "area": "경복궁 인근",
        "food": "서촌 아침 식사 식당",
        "reason": "경복궁 관람 전에 간단하게 식사",
        "link": google_maps_search("서촌 아침 식사 식당 서울")
    },
    {
        "day": "1일 차",
        "time": "12:30~13:20",
        "type": "점심",
        "area": "인사동",
        "food": "인사동 한식 식당",
        "reason": "궁궐 관람 후 비빔밥·국수 등 한식",
        "link": google_maps_search("인사동 한식 맛집 서울")
    },
    {
        "day": "1일 차",
        "time": "16:30~17:00",
        "type": "저녁",
        "area": "명동",
        "food": "왕비집 명동본점",
        "reason": "한국식 숯불구이와 갈비를 맛보기 좋음",
        "link": google_maps_search("왕비집 명동본점")
    },
    {
        "day": "2일 차",
        "time": "09:00~09:25",
        "type": "아침",
        "area": "삼성역",
        "food": "코엑스 인근 아침 식당",
        "reason": "코엑스 관광 전에 간단하게 식사",
        "link": google_maps_search("삼성역 아침 식사 식당 서울")
    },
    {
        "day": "2일 차",
        "time": "13:00~14:00",
        "type": "점심",
        "area": "잠실",
        "food": "롯데월드몰 식당가",
        "reason": "롯데월드타워 관광 후 편리하게 식사",
        "link": google_maps_search("롯데월드몰 식당가")
    },
    {
        "day": "2일 차",
        "time": "18:00~19:00",
        "type": "저녁",
        "area": "홍대",
        "food": "육지 홍대",
        "reason": "숯불 돼지고기 구이로 한국식 저녁 식사",
        "link": google_maps_search("육지 홍대")
    }
]

# --------------------------------------------------
# 3. 숙소 추천
# --------------------------------------------------

st.header("🏨 추천 숙소")

st.write(
    "1박 2일 동안 이동하기 편하도록 명동 또는 종로 주변 숙소를 추천합니다. "
    "아래 링크에서 날짜별 가격과 객실을 확인하세요."
)

hotels = [
    {
        "name": "명동 주변 호텔",
        "reason": "쇼핑, 식당, 남산 이동에 편리",
        "link": "https://www.google.com/maps/search/?api=1&query="
                + quote("명동 호텔 서울")
    },
    {
        "name": "종로·인사동 주변 호텔",
        "reason": "경복궁, 북촌, 창덕궁 관광에 편리",
        "link": "https://www.google.com/maps/search/?api=1&query="
                + quote("종로 인사동 호텔 서울")
    }
]

hotel_cols = st.columns(2)

for col, hotel in zip(hotel_cols, hotels):
    with col:
        with st.container(border=True):
            st.subheader(hotel["name"])
            st.write(hotel["reason"])
            st.link_button(
                "호텔 위치 및 예약 정보 확인",
                hotel["link"],
                use_container_width=True
            )

st.caption(
    "숙박 요금과 객실 이용 가능 여부는 날짜와 인원에 따라 달라집니다."
)

# --------------------------------------------------
# 4. Folium 지도 만들기
# --------------------------------------------------

st.header("📍 관광지 전체 지도")

day_choice = st.radio(
    "지도 표시",
    ["전체 일정", "1일 차", "2일 차"],
    horizontal=True
)

if day_choice == "1일 차":
    map_places = [p for p in places if p["day"] == 1]
elif day_choice == "2일 차":
    map_places = [p for p in places if p["day"] == 2]
else:
    map_places = places

seoul_map = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=11,
    tiles="OpenStreetMap",
    control_scale=True
)

# 날짜별 다른 색상
day_colors = {1: "red", 2: "blue"}

for index, place in enumerate(map_places, start=1):
    popup_html = f"""
    <div style="width:230px">
        <h4>{place['name']}</h4>
        <p>{place['desc']}</p>
        <p>일정: {place['time']}</p>
        <p>주소: {place['address']}</p>
        <a href="{google_directions(place['lat'], place['lon'])}"
           target="_blank">Google Maps 길찾기</a>
    </div>
    """

    folium.Marker(
        location=[place["lat"], place["lon"]],
        tooltip=f"{place['day']}일 차 · {place['name']}",
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(
            color=day_colors[place["day"]],
            icon="info-sign"
        )
    ).add_to(seoul_map)

# 같은 날의 관광지 순서대로 선 연결
for day in [1, 2]:
    day_places = [
        p for p in map_places if p["day"] == day
    ]

    if len(day_places) > 1:
        folium.PolyLine(
            locations=[
                [p["lat"], p["lon"]] for p in day_places
            ],
            color=day_colors[day],
            weight=3,
            opacity=0.7,
            tooltip=f"{day}일 차 관광 순서 (직선 연결)"
        ).add_to(seoul_map)

st_folium(
    seoul_map,
    use_container_width=True,
    height=580,
    returned_objects=[]
)

st.caption(
    "지도 선은 관광지 순서를 나타내는 참고용 직선입니다. "
    "실제 이동은 지하철과 도보 길찾기를 확인하세요."
)

# --------------------------------------------------
# 5. 지도 아래 일정표
# --------------------------------------------------

st.header("📅 1박 2일 세부 일정표")

st.subheader("DAY 1 | 궁궐 · 전통문화 · 시장 · 남산")

day1_schedule = [
    ["09:00~09:25", "아침 식사", "경복궁 인근", "식사 및 이동"],
    ["09:30~10:45", "경복궁", "전통 궁궐 관람", "도보"],
    ["11:00~11:40", "북촌한옥마을", "한옥 골목 구경", "도보"],
    ["11:50~12:30", "창덕궁", "궁궐 관람", "도보/이동"],
    ["12:30~13:20", "점심 식사", "인사동", "한식 식사"],
    ["13:30~14:15", "광장시장", "전통시장과 먹거리", "지하철/도보"],
    ["14:30~15:15", "동대문디자인플라자", "건축·전시 관람", "도보"],
    ["15:45~16:30", "명동", "쇼핑과 거리 구경", "지하철/도보"],
    ["16:30~17:00", "저녁 식사", "명동", "한국식 숯불구이"],
    ["17:00~19:00", "N서울타워", "전망과 야경", "버스/케이블카 등"]
]

df1 = pd.DataFrame(
    day1_schedule,
    columns=["시간", "일정", "장소·활동", "이동·내용"]
)

st.dataframe(
    df1,
    use_container_width=True,
    hide_index=True
)

st.subheader("DAY 2 | 현대 서울 · 쇼핑 · 젊은 문화")

day2_schedule = [
    ["09:00~09:25", "아침 식사", "삼성역 인근", "간단한 아침 식사"],
    ["09:30~11:00", "코엑스 별마당도서관", "도서관·쇼핑몰", "도보"],
    ["11:00~11:30", "이동", "삼성역 → 잠실", "지하철"],
    ["11:30~13:00", "롯데월드타워", "전망·쇼핑", "도보"],
    ["13:00~14:00", "점심 식사", "롯데월드몰", "몰 내 식당"],
    ["14:00~15:00", "이동", "잠실 → 홍대", "지하철"],
    ["15:00~18:00", "홍대거리", "카페·쇼핑·거리 공연", "도보"],
    ["18:00~19:00", "저녁 식사", "홍대", "한국식 고기구이"]
]

df2 = pd.DataFrame(
    day2_schedule,
    columns=["시간", "일정", "장소·활동", "이동·내용"]
)

st.dataframe(
    df2,
    use_container_width=True,
    hide_index=True
)

# --------------------------------------------------
# 6. 식당 링크 모아보기
# --------------------------------------------------

st.header("🍽️ 식당 추천 및 링크")

st.write(
    "아래 링크를 누르면 해당 지역의 식당 정보를 지도에서 확인할 수 있습니다. "
    "영업시간과 메뉴는 방문 전에 확인하세요."
)

for meal in meals:
    with st.container(border=True):
        st.markdown(
            f"**{meal['day']} · {meal['time']} · {meal['type']}**"
        )
        st.write(f"**추천 장소:** {meal['food']}")
        st.write(f"위치: {meal['area']}")
        st.write(meal["reason"])
        st.link_button(
            "식당 위치·정보 보기",
            meal["link"]
        )

st.divider()

st.info(
    "여행 팁: 궁궐의 휴궁일과 관람 시간을 확인하고, "
    "북촌에서는 주민을 배려해 조용히 관광하세요. "
    "이동 시간은 교통 상황에 따라 달라질 수 있습니다."
)
