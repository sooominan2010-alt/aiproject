
import streamlit as st
import pandas as pd
from pathlib import Path

# ==================================
# 기본 설정
# ==================================
st.set_page_config(
    page_title="서울 부동산 취득 분석",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 서울에서 부동산 취득이 가장 많은 지역은?")
st.subheader("📊 서울시 25개 자치구 부동산 소유권 취득 현황")
st.caption("분석 기간: 2014년 4분기 ~ 2018년 4분기")

# ==================================
# 데이터 불러오기
# ==================================
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
    else:
        file_path = Path(__file__).parent / "부동산_취득현황_분석용.csv"
        df = pd.read_csv(file_path, encoding="utf-8-sig")

    df["취득건수"] = pd.to_numeric(
        df["취득건수"], errors="coerce"
    ).fillna(0)

    df["연도"] = pd.to_numeric(df["연도"]).astype(int)
    df["분기"] = pd.to_numeric(df["분기"]).astype(int)

    return df


uploaded = st.sidebar.file_uploader(
    "📂 분석 데이터 업로드",
    type=["csv"]
)

try:
    df = load_data(uploaded)
except FileNotFoundError:
    st.warning("CSV 파일을 업로드해 주세요.")
    st.stop()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# ==================================
# 전체 자치구 분석
# ==================================
st.divider()
st.header("🏆 서울시 부동산 취득 TOP 10")

ranking = (
    df.groupby("자치구")["취득건수"]
    .sum()
    .sort_values(ascending=False)
)

top_district = ranking.index[0]
top_count = int(ranking.iloc[0])

bottom_district = ranking.index[-1]
bottom_count = int(ranking.iloc[-1])

col1, col2, col3 = st.columns(3)

col1.metric(
    "🥇 취득 건수 1위",
    top_district,
    f"{top_count:,}건"
)

col2.metric(
    "📍 분석 지역",
    f"{df['자치구'].nunique()}개 자치구"
)

col3.metric(
    "📉 취득 건수 최저",
    bottom_district,
    f"{bottom_count:,}건"
)

st.subheader("자치구별 취득 건수 순위")

top10 = ranking.head(10).sort_values()

st.bar_chart(
    top10,
    horizontal=True
)

# 전체 순위표
with st.expander("📋 서울시 25개 자치구 전체 순위 보기"):
    result = ranking.reset_index()
    result.columns = ["자치구", "취득 건수"]
    result.insert(0, "순위", range(1, len(result) + 1))

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )

st.info(
    f"💡 전체 기간 동안 부동산 취득 건수가 가장 많았던 지역은 "
    f"**{top_district}**이며 총 {top_count:,}건이야!"
)

# ==================================
# 조건별 분석
# ==================================
st.divider()
st.header("🔎 원하는 조건으로 분석하기")

st.sidebar.divider()
st.sidebar.header("분석 조건 선택")

years = sorted(df["연도"].unique())

selected_year = st.sidebar.selectbox(
    "📅 연도 선택",
    years
)

quarters = sorted(
    df[df["연도"] == selected_year]["분기"].unique()
)

selected_quarter = st.sidebar.selectbox(
    "분기 선택",
    quarters
)

types = sorted(df["취득주체"].unique())

selected_type = st.sidebar.selectbox(
    "👥 취득 주체 선택",
    ["전체"] + types
)

filtered = df[
    (df["연도"] == selected_year) &
    (df["분기"] == selected_quarter)
].copy()

if selected_type != "전체":
    filtered = filtered[
        filtered["취득주체"] == selected_type
    ]

# ==================================
# 선택 조건 통계
# ==================================
district_result = (
    filtered.groupby("자치구")["취득건수"]
    .sum()
    .sort_values(ascending=False)
)

if len(district_result) > 0:

    first = district_result.index[0]
    first_count = int(district_result.iloc[0])

    a, b = st.columns(2)

    a.metric(
        "선택 조건 취득 건수",
        f"{int(district_result.sum()):,}건"
    )

    b.metric(
        "해당 기간 취득 1위 지역",
        first,
        f"{first_count:,}건"
    )

# ==================================
# 자치구별 비교 그래프
# ==================================
st.subheader("📊 자치구별 부동산 취득 비교")

st.bar_chart(
    district_result,
    horizontal=True
)

# ==================================
# 취득 주체별 분석
# ==================================
st.divider()
st.header("👥 취득 주체별 분석")

type_data = df[
    (df["연도"] == selected_year) &
    (df["분기"] == selected_quarter)
]

type_result = (
    type_data.groupby("취득주체")["취득건수"]
    .sum()
    .sort_values(ascending=False)
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("취득 주체별 건수")
    st.bar_chart(type_result)

with col2:
    st.subheader("취득 주체별 비율")

    type_percent = (
        type_result / type_result.sum() * 100
    ).round(1)

    st.dataframe(
        type_percent.rename("비율(%)"),
        use_container_width=True
    )

# ==================================
# 연도별 변화 분석
# ==================================
st.divider()
st.header("📈 연도별 부동산 취득 변화")

trend_type = st.selectbox(
    "연도별 분석 취득 주체",
    ["전체"] + types
)

trend_data = df.copy()

if trend_type != "전체":
    trend_data = trend_data[
        trend_data["취득주체"] == trend_type
    ]

year_result = (
    trend_data.groupby("연도")["취득건수"]
    .sum()
)

st.line_chart(year_result)

st.caption(
    "※ 2014년은 4분기 자료만 포함되어 있어 "
    "다른 연도와 직접 비교할 때 주의해야 해."
)

# ==================================
# 분석 결과 정리
# ==================================
st.divider()
st.header("💡 데이터 분석 결과")

st.write(f"""
### 🏆 주요 분석 결과

- 서울시에서 누적 취득 건수가 가장 많은 지역은 **{top_district}**이야.
- 해당 지역의 취득 건수는 **{top_count:,}건**이야.
- 누적 취득 건수가 가장 적은 지역은 **{bottom_district}**이야.
- 선택한 연도와 분기에 따라 자치구별 취득 현황이 달라지는 것을 확인할 수 있어.

### 🔍 분석할 때 알아둘 점

이 자료는 부동산 가격이나 매매 금액이 아니라
소유권 취득 건수를 나타내는 통계야.
따라서 취득 건수가 많다는 사실만으로
그 지역의 부동산 가격이 높다고 판단할 수는 없어.
""")

# ==================================
# CSV 다운로드
# ==================================
st.divider()

st.subheader("📥 분석 데이터 다운로드")

csv = ranking.reset_index().to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    label="📊 자치구별 분석 결과 다운로드",
    data=csv,
    file_name="서울시_부동산_취득_분석.csv",
    mime="text/csv"
)

st.caption("자료: 부동산 소유권 취득 현황(2014~2018)")

