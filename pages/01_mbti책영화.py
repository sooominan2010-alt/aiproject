
import streamlit as st
import random

st.set_page_config(
    page_title="MBTI 취향 탐험소",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #F5F6FF;
}
.title {
    text-align: center;
    color: #5146B8;
    font-size: 38px;
    font-weight: bold;
}
.subtitle {
    text-align: center;
    color: #666;
    font-size: 17px;
}
.recommend-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #E0E0F0;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# MBTI별 영화 2편, 책 2권 추천
recommendations = {
    "ISTJ": {
        "movie": [
            ("쇼생크 탈출", "희망과 인내, 치밀한 계획이 돋보이는 영화"),
            ("히든 피겨스", "실력과 성실함으로 편견을 넘어서는 이야기")
        ],
        "book": [
            ("아주 작은 습관의 힘", "꾸준한 습관이 만드는 변화를 알려주는 책"),
            ("모모", "시간과 삶의 의미를 생각하게 하는 이야기")
        ]
    },
    "ISFJ": {
        "movie": [
            ("원더", "배려와 친절, 우정의 의미를 보여주는 영화"),
            ("리틀 포레스트", "일상 속 쉼과 소소한 행복을 담은 영화")
        ],
        "book": [
            ("나미야 잡화점의 기적", "사람들의 고민과 따뜻한 연결을 담은 소설"),
            ("어린 왕자", "관계와 소중한 가치에 대해 생각하게 하는 책")
        ]
    },
    "INFJ": {
        "movie": [
            ("죽은 시인의 사회", "자신만의 삶과 꿈을 고민하게 하는 영화"),
            ("월터의 상상은 현실이 된다", "새로운 도전과 자기 발견을 담은 영화")
        ],
        "book": [
            ("연금술사", "꿈을 찾아가는 여정을 담은 소설"),
            ("데미안", "자아와 성장에 대해 깊이 생각하게 하는 책")
        ]
    },
    "INTJ": {
        "movie": [
            ("이미테이션 게임", "논리와 문제 해결 능력이 돋보이는 영화"),
            ("마션", "과학적 사고와 계획으로 위기를 극복하는 이야기")
        ],
        "book": [
            ("사피엔스", "인류의 역사와 사회를 새로운 시각으로 살펴보는 책"),
            ("팩트풀니스", "데이터를 통해 세상을 바라보는 방법을 알려주는 책")
        ]
    },
    "ISTP": {
        "movie": [
            ("탑건: 매버릭", "기술과 실전 판단, 팀워크가 돋보이는 영화"),
            ("포드 V 페라리", "자동차 기술과 도전 정신을 담은 영화")
        ],
        "book": [
            ("마션", "과학적 지식과 실용적인 문제 해결이 돋보이는 소설"),
            ("클라라와 태양", "기술과 인간의 감정을 생각하게 하는 소설")
        ]
    },
    "ISFP": {
        "movie": [
            ("소울", "삶의 의미와 일상의 즐거움을 돌아보는 애니메이션"),
            ("리틀 포레스트", "음식과 자연, 자신만의 삶을 담은 영화")
        ],
        "book": [
            ("어린 왕자", "상상력과 감성을 자극하는 고전"),
            ("불편한 편의점", "일상 속 사람들의 따뜻한 이야기를 담은 소설")
        ]
    },
    "INFP": {
        "movie": [
            ("너의 이름은.", "감성적인 분위기와 운명적인 만남을 담은 애니메이션"),
            ("월터의 상상은 현실이 된다", "상상 속 꿈을 현실로 옮기는 이야기")
        ],
        "book": [
            ("데미안", "자신만의 길을 찾아가는 성장 소설"),
            ("어린 왕자", "관계와 마음의 의미를 되새기는 이야기")
        ]
    },
    "INTP": {
        "movie": [
            ("인터스텔라", "과학과 우주, 인간의 선택을 다룬 영화"),
            ("인셉션", "꿈과 현실의 경계를 탐구하는 영화")
        ],
        "book": [
            ("코스모스", "우주와 과학의 세계를 탐험하는 책"),
            ("이기적 유전자", "진화와 생명에 대한 관점을 소개하는 책")
        ]
    },
    "ESTP": {
        "movie": [
            ("미션 임파서블: 폴아웃", "빠른 판단과 액션이 돋보이는 영화"),
            ("베이비 드라이버", "속도감 있는 추격전과 음악이 매력적인 영화")
        ],
        "book": [
            ("마션", "위기 속에서 행동하고 해결책을 찾는 이야기"),
            ("아주 작은 습관의 힘", "목표를 행동으로 바꾸는 방법을 알려주는 책")
        ]
    },
    "ESFP": {
        "movie": [
            ("맘마미아!", "신나는 음악과 유쾌한 에너지가 가득한 영화"),
            ("코코", "음악과 가족, 꿈을 담은 애니메이션")
        ],
        "book": [
            ("불편한 편의점", "다양한 인물들의 일상과 관계를 담은 소설"),
            ("달러구트 꿈 백화점", "독특한 상상력과 따뜻함이 어우러진 소설")
        ]
    },
    "ENFP": {
        "movie": [
            ("업", "새로운 모험과 우정을 담은 애니메이션"),
            ("라라랜드", "꿈과 사랑, 선택을 담은 음악 영화")
        ],
        "book": [
            ("연금술사", "꿈을 향한 도전을 담은 소설"),
            ("달러구트 꿈 백화점", "상상력 넘치는 세계와 다양한 사람들의 이야기")
        ]
    },
    "ENTP": {
        "movie": [
            ("나이브스 아웃", "추리와 반전, 독특한 인물들이 매력적인 영화"),
            ("인셉션", "복잡한 설정과 기발한 아이디어가 돋보이는 영화")
        ],
        "book": [
            ("팩트풀니스", "익숙한 생각을 데이터로 다시 살펴보는 책"),
            ("1984", "사회와 권력, 자유에 대해 생각하게 하는 소설")
        ]
    },
    "ESTJ": {
        "movie": [
            ("히든 피겨스", "목표를 향한 노력과 협력이 돋보이는 영화"),
            ("머니볼", "데이터를 활용한 전략과 의사결정을 다룬 영화")
        ],
        "book": [
            ("아주 작은 습관의 힘", "목표를 꾸준히 실천하는 방법을 알려주는 책"),
            ("팩트풀니스", "근거를 바탕으로 판단하는 방법을 알려주는 책")
        ]
    },
    "ESFJ": {
        "movie": [
            ("원더", "친구와 가족, 배려의 가치를 담은 영화"),
            ("코코", "가족과 추억의 소중함을 담은 애니메이션")
        ],
        "book": [
            ("나미야 잡화점의 기적", "사람들의 고민과 따뜻한 연결을 담은 소설"),
            ("불편한 편의점", "서로에게 힘이 되어 주는 사람들의 이야기")
        ]
    },
    "ENFJ": {
        "movie": [
            ("죽은 시인의 사회", "꿈을 응원하고 자신만의 길을 찾는 이야기"),
            ("굿 윌 헌팅", "재능과 성장, 주변 사람들의 도움을 담은 영화")
        ],
        "book": [
            ("모모", "시간과 관계의 소중함을 생각하게 하는 책"),
            ("미움받을 용기", "인간관계와 삶의 태도를 돌아보는 책")
        ]
    },
    "ENTJ": {
        "movie": [
            ("머니볼", "전략과 데이터로 새로운 결과를 만들어 내는 영화"),
            ("히든 피겨스", "목표를 향해 도전하고 변화를 만드는 이야기")
        ],
        "book": [
            ("사피엔스", "인류와 사회의 변화를 폭넓게 살펴보는 책"),
            ("아주 작은 습관의 힘", "목표 달성을 위한 실천 전략을 알려주는 책")
        ]
    }
}

mbti_descriptions = {
    "ISTJ": "계획적이고 꼼꼼한 현실주의자 📋",
    "ISFJ": "세심하고 따뜻한 수호자 🧸",
    "INFJ": "깊이 생각하고 의미를 찾는 조언자 🌙",
    "INTJ": "전략적으로 미래를 설계하는 유형 ♟️",
    "ISTP": "직접 탐구하고 해결하는 실용주의자 🔧",
    "ISFP": "감성과 취향을 중요하게 여기는 예술가 🎨",
    "INFP": "상상력과 가치관이 뚜렷한 이상주의자 🌷",
    "INTP": "호기심 가득한 탐구자 🔬",
    "ESTP": "행동력 있고 도전을 즐기는 유형 ⚡",
    "ESFP": "즐거움과 경험을 사랑하는 유형 🎉",
    "ENFP": "새로운 가능성을 발견하는 아이디어 뱅크 💡",
    "ENTP": "기발한 생각을 즐기는 발명가 🧠",
    "ESTJ": "체계적으로 목표를 이루는 리더 🏆",
    "ESFJ": "사람들과 함께하는 따뜻한 협력가 🤝",
    "ENFJ": "사람들의 성장을 응원하는 리더 🌟",
    "ENTJ": "큰 그림을 그리고 이끄는 지휘관 🚀"
}

st.markdown(
    '<div class="title">🎬 MBTI 취향 탐험소 📚</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">내 MBTI에 어울리는 영화 2편과 책 2권을 찾아보세요!</div>',
    unsafe_allow_html=True
)

st.write("")
st.info(
    "💜 MBTI는 재미로 참고해 주세요! "
    "아래 추천은 각 유형의 특징을 바탕으로 구성한 취향 제안이에요."
)

selected = st.selectbox(
    "🧭 나의 MBTI를 선택해 주세요.",
    list(recommendations.keys())
)

st.subheader(f"✨ {selected} | {mbti_descriptions[selected]}")
st.write("당신의 취향을 탐험할 준비가 됐나요? 아래 버튼을 눌러 추천을 확인해 보세요!")

if st.button("🎁 나만의 추천 확인하기", type="primary"):
    st.session_state["show"] = True

if st.session_state.get("show", False):
    data = recommendations[selected]

    st.divider()
    st.header("🍿 당신을 위한 영화 추천")

    col1, col2 = st.columns(2)

    for col, movie in zip([col1, col2], data["movie"]):
        with col:
            st.markdown('<div class="recommend-card">', unsafe_allow_html=True)
            st.subheader("🎬 " + movie[0])
            st.write(movie[1])
            st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.header("📚 당신을 위한 책 추천")

    col3, col4 = st.columns(2)

    for col, book in zip([col3, col4], data["book"]):
        with col:
            st.markdown('<div class="recommend-card">', unsafe_allow_html=True)
            st.subheader("📖 " + book[0])
            st.write(book[1])
            st.markdown("</div>", unsafe_allow_html=True)

    st.success("🎉 마음에 드는 작품부터 하나씩 즐겨 보세요!")

    if st.button("🔄 다른 MBTI 살펴보기"):
        st.session_state["show"] = False
        st.rerun()

st.divider()
st.caption(
    "💡 같은 MBTI라도 취향은 다를 수 있어요. "
    "추천 목록은 성격 유형을 바탕으로 한 참고용 콘텐츠입니다."
)
