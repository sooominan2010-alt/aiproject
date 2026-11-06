
import re
from pathlib import Path
from io import BytesIO

import pandas as pd
import streamlit as st
import plotly.graph_objects as go


# --------------------------------
# 기본 설정
# --------------------------------
st.set_page_config(
    page_title="서울시 인구 분석",
    page_icon="📊",
    layout="wide"
)

PINK = "#FF1493"
GREEN = "#16A34A"
PURPLE = "#805AD5"

# CSV 파일 경로
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "population.csv"


# --------------------------------
# CSV 불러오기
# --------------------------------
@st.cache_data
def load_data(file_bytes):
    for encoding in ["utf-8-sig", "cp949", "euc-kr", "utf-8"]:
        try:
            return pd.read_csv(
                BytesIO(file_bytes),
                encoding=encoding
            )
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일의 인코딩을 확인해 주세요.")


if not CSV_PATH.exists():
    st.error("population.csv 파일을 찾을 수 없습니다.")
    st.info("app.py와 같은 폴더에 population.csv 파일을 넣어 주세요.")
    st.stop()

try:
    df = load_data(CSV_PATH.read_bytes())
except Exception as e:
    st.error(f"CSV 파일을 불러오지 못했습니다: {e}")
    st.stop()


# --------------------------------
# 데이터 정리
# --------------------------------
df.columns = df.columns.astype(str).str.strip()

if "행정구역" not in df.columns:
    st.error("CSV 파일에 '행정구역' 열이 없습니다.")
    st.stop()

df["행정구역_표시"] = (
    df["행정구역"]
    .astype(str)
    .str.replace(r"\s*\(\d+\)\s*$", "", regex=True)
    .str.replace("서울특별시", "", regex=False)
    .str.strip()
)

df.loc[df["행정구역_표시"] == "", "행정구역_표시"] = "서울특별시"

# 숫자 데이터 변환
for col in df.columns:
    if col not in ["행정구역", "행정구역_표시"]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        )

# 연도 추출
years = sorted(
    set(
        re.findall(
            r"(20\d{2})년",
            " ".join(df.columns)
        )
    )
)

ages = [
    "0~9세", "10~19세", "20~29세",
    "30~39세", "40~49세", "50~59세",
    "60~69세", "70~79세", "80~89세",
    "90~99세", "100세 이상"
]

district_df = df[
    df["행정구역_표시"] != "서울특별시"
].copy()

districts = sorted(district_df["행정구역_표시"].unique())


# --------------------------------
# 데이터 계산 함수
# --------------------------------
def get_population(row, year, gender, age):
    column = f"{year}년_{gender}_{age}"

    if column not in df.columns:
        return None

    value = row[column]

    if pd.isna(value):
        return 0

    return int(value)


def get_total_population(row, year):
    column = f"{year}년_거주자_총인구수"

    if column not in df.columns:
        return None

    value = row[column]

    if pd.isna(value):
        return 0

    return int(value)


def format_number(value):
    if value is None:
        return "자료 없음"

    return f"{value:,}명"


def make_axis_max(values):
    valid_values = [v for v in values if v is not None]

    if not valid_values:
        return 100000

    maximum = max(valid_values)

    return max(
        100000,
        (maximum // 100000 + 1) * 100000
    )


# --------------------------------
# 화면 제목
# --------------------------------
st.title("📊 서울시 인구 분석")
st.write("서울시 자치구별 인구와 연령대별 인구를 분석하는 프로그램입니다.")

tab1, tab2, tab3 = st.tabs([
    "👥 남녀 연령별 비교",
    "🏆 연령대별 자치구 순위",
    "📈 연도별 인구 변화"
])


# ================================================
# TAB 1. 남녀 연령별 비교
# ================================================
with tab1:
    st.subheader("남녀 연령별 인구 비교")

    col1, col2 = st.columns(2)

    with col1:
        selected_district = st.selectbox(
            "행정구 선택",
            districts
        )

    with col2:
        selected_year = st.selectbox(
            "연도 선택",
            years,
            index=len(years) - 1
        )

    selected_row = district_df[
        district_df["행정구역_표시"] == selected_district
    ].iloc[0]

    male_values = [
        get_population(
            selected_row,
            selected_year,
            "남_거주자",
            age
        )
        for age in ages
    ]

    female_values = [
        get_population(
            selected_row,
            selected_year,
            "여_거주자",
            age
        )
        for age in ages
    ]

    male_total = sum(v or 0 for v in male_values)
    female_total = sum(v or 0 for v in female_values)

    c1, c2, c3 = st.columns(3)

    c1.metric("남성 인구", format_number(male_total))
    c2.metric("여성 인구", format_number(female_total))
    c3.metric(
        "남녀 인구 차이",
        format_number(abs(male_total - female_total))
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=ages,
        y=male_values,
        mode="lines+markers",
        name="남성",
        line=dict(color=PINK, width=3),
        marker=dict(size=8)
    ))

    fig.add_trace(go.Scatter(
        x=ages,
        y=female_values,
        mode="lines+markers",
        name="여성",
        line=dict(color=GREEN, width=3),
        marker=dict(size=8)
    ))

    fig.update_layout(
        title=f"{selected_district} {selected_year}년 남녀 연령별 인구",
        xaxis_title="연령대",
        yaxis_title="인구수",
        height=350,
        margin=dict(l=20, r=20, t=60, b=30),
        legend=dict(orientation="h", y=1.12),
        yaxis=dict(
            dtick=100000,
            range=[0, make_axis_max(male_values + female_values)],
            gridcolor="#DDDDDD"
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    result_df = pd.DataFrame({
        "연령대": ages,
        "남성 인구": male_values,
        "여성 인구": female_values
    })

    st.dataframe(result_df, use_container_width=True)


# ================================================
# TAB 2. 연령대별 자치구 순위
# ================================================
with tab2:
    st.subheader("연령대별 인구가 가장 많은 자치구")

    col1, col2, col3 = st.columns(3)

    with col1:
        rank_year = st.selectbox(
            "연도 선택",
            years,
            index=len(years) - 1,
            key="rank_year"
        )

    with col2:
        selected_age = st.selectbox(
            "연령대 선택",
            ages,
            key="selected_age"
        )

    with col3:
        selected_gender = st.selectbox(
            "성별 선택",
            ["전체", "남성", "여성"]
        )

    gender_key = {
        "전체": "거주자",
        "남성": "남_거주자",
        "여성": "여_거주자"
    }

    gender_column = gender_key[selected_gender]

    ranking_data = []

    for _, row in district_df.iterrows():
        value = get_population(
            row,
            rank_year,
            gender_column,
            selected_age
        )

        ranking_data.append({
            "행정구": row["행정구역_표시"],
            "인구수": value if value is not None else 0
        })

    ranking_df = pd.DataFrame(ranking_data)
    ranking_df = ranking_df.sort_values(
        "인구수",
        ascending=False
    ).reset_index(drop=True)

    if not ranking_df.empty:
        top_district = ranking_df.iloc[0]["행정구"]
        top_population = ranking_df.iloc[0]["인구수"]

        st.success(
            f"🏆 {selected_age} 인구가 가장 많은 곳은 "
            f"{top_district}이며, 인구는 {top_population:,}명입니다."
        )

        if selected_gender == "남성":
            base_color = "#F7B6D2"
            top_color = PINK
        elif selected_gender == "여성":
            base_color = "#A7E8C1"
            top_color = GREEN
        else:
            base_color = "#C9B6F2"
            top_color = PURPLE

        colors = [
            top_color if i == 0 else base_color
            for i in range(len(ranking_df))
        ]

        fig = go.Figure(go.Bar(
            x=ranking_df["행정구"],
            y=ranking_df["인구수"],
            marker_color=colors,
            text=ranking_df["인구수"].apply(
                lambda x: f"{x:,}명"
            ),
            textposition="outside"
        ))

        fig.update_layout(
            title=f"{rank_year}년 {selected_age} {selected_gender} 인구 순위",
            xaxis_title="행정구",
            yaxis_title="인구수",
            height=350,
            margin=dict(l=20, r=20, t=60, b=40),
            yaxis=dict(
                dtick=100000,
                gridcolor="#DDDDDD"
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        ranking_df.index = ranking_df.index + 1
        ranking_df.index.name = "순위"

        st.dataframe(
            ranking_df,
            use_container_width=True
        )


# ================================================
# TAB 3. 연도별 인구 변화
# ================================================
with tab3:
    st.subheader("자치구별 연도별 인구 변화")

    selected_change_district = st.selectbox(
        "행정구 선택",
        districts,
        key="change_district"
    )

    change_row = district_df[
        district_df["행정구역_표시"] == selected_change_district
    ].iloc[0]

    population_by_year = [
        get_total_population(change_row, year)
        for year in years
    ]

    valid_population = [
        v for v in population_by_year if v is not None
    ]

    if valid_population:
        first_population = population_by_year[0]
        last_population = population_by_year[-1]

        change = last_population - first_population

        if first_population:
            change_rate = change / first_population * 100
        else:
            change_rate = 0

        c1, c2, c3 = st.columns(3)

        c1.metric(
            f"{years[0]}년 인구",
            format_number(first_population)
        )

        c2.metric(
            f"{years[-1]}년 인구",
            format_number(last_population)
        )

        c3.metric(
            "인구 변화",
            format_number(change),
            f"{change_rate:.2f}%"
        )

        if change > 0:
            st.success("선택한 기간 동안 인구가 증가했습니다.")
        elif change < 0:
            st.info("선택한 기간 동안 인구가 감소했습니다.")
        else:
            st.info("선택한 기간 동안 인구 변화가 없습니다.")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=years,
            y=population_by_year,
            mode="lines+markers",
            name="전체 인구",
            line=dict(color=PINK, width=3),
            marker=dict(size=9)
        ))

        fig.update_layout(
            title=f"{selected_change_district} 연도별 전체 인구 변화",
            xaxis_title="연도",
            yaxis_title="인구수",
            height=350,
            margin=dict(l=20, r=20, t=60, b=30),
            yaxis=dict(
                dtick=100000,
                gridcolor="#DDDDDD"
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        change_df = pd.DataFrame({
            "연도": years,
            "전체 인구": population_by_year
        })

        st.dataframe(
            change_df,
            use_container_width=True
        )


# ================================================
# 데이터 확인 및 다운로드
# ================================================
with st.expander("📁 데이터 확인 및 다운로드"):
    st.write("전체 데이터 크기:", df.shape)

    missing_count = int(df.isnull().sum().sum())
    total_cells = df.shape[0] * df.shape[1]

    st.write(f"결측치 개수: {missing_count:,}개")

    if total_cells > 0:
        st.write(
            f"결측치 비율: {missing_count / total_cells * 100:.2f}%"
        )

    csv_data = df.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        label="📥 분석 데이터 CSV 다운로드",
        data=csv_data,
        file_name="서울시_인구분석.csv",
        mime="text/csv"
    )

st.caption("서울시 인구 데이터 분석 프로그램")
