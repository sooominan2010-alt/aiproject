
import re
from pathlib import Path
from io import BytesIO

import pandas as pd
import streamlit as st
import plotly.graph_objects as go


# ==================================================
# 1. 기본 설정
# ==================================================

st.set_page_config(
    page_title="서울시 인구 분석",
    page_icon="📊",
    layout="wide"
)

PINK = "#FF1493"
GREEN = "#16A34A"
PURPLE = "#805AD5"

st.title("📊 서울특별시 인구 분석 대시보드")

st.markdown("""
서울시의 연령별·성별·지역별 인구를 분석하는 프로그램입니다.
원하는 조건을 선택하여 다양한 인구 통계를 확인해 보세요.
""")


# ==================================================
# 2. CSV 파일 경로 및 인코딩 처리
# ==================================================

# pages 폴더의 상위 폴더
BASE_DIR = Path(__file__).resolve().parent.parent

CSV_PATH = BASE_DIR / "population.csv"


@st.cache_data
def load_data(file_bytes):

    encodings = [
        "utf-8-sig",
        "cp949",
        "euc-kr",
        "utf-8"
    ]

    last_error = None

    for encoding in encodings:

        try:
            df = pd.read_csv(
                BytesIO(file_bytes),
                encoding=encoding
            )

            return df

        except Exception as e:
            last_error = e

    raise ValueError(
        f"CSV 파일을 읽을 수 없습니다: {last_error}"
    )


# CSV 파일 존재 여부 확인
if not CSV_PATH.exists():

    st.error(
        "population.csv 파일을 찾을 수 없습니다."
    )

    st.code(str(CSV_PATH))

    st.stop()


try:

    file_bytes = CSV_PATH.read_bytes()

    df = load_data(file_bytes)

except Exception as e:

    st.error(f"파일 불러오기 오류: {e}")

    st.stop()


# ==================================================
# 3. 데이터 전처리
# ==================================================

df.columns = df.columns.astype(str).str.strip()

if "행정구역" not in df.columns:

    st.error("'행정구역' 열이 없습니다.")

    st.stop()


# 행정구역 코드 및 서울특별시 이름 정리
df["행정구역_표시"] = (
    df["행정구역"]
    .astype(str)
    .str.replace(
        r"\s*\(\d+\)\s*$",
        "",
        regex=True
    )
    .str.replace(
        "서울특별시",
        "",
        regex=False
    )
    .str.strip()
)

# 서울 전체 행 이름 정리
df.loc[
    df["행정구역_표시"] == "",
    "행정구역_표시"
] = "서울특별시"


# 숫자 데이터 쉼표 제거
for col in df.columns:

    if col not in [
        "행정구역",
        "행정구역_표시"
    ]:

        df[col] = pd.to_numeric(
            df[col]
            .astype(str)
            .str.replace(
                ",",
                "",
                regex=False
            ),
            errors="coerce"
        )


# ==================================================
# 4. 연도 및 연령대 설정
# ==================================================

years = sorted({

    int(year)

    for col in df.columns

    for year in re.findall(
        r"(20\d{2})년",
        col
    )

})


ages = [

    "0~9세",
    "10~19세",
    "20~29세",
    "30~39세",
    "40~49세",
    "50~59세",
    "60~69세",
    "70~79세",
    "80~89세",
    "90~99세",
    "100세 이상"

]


if not years:

    st.error("연도 데이터를 찾을 수 없습니다.")

    st.stop()


# 서울 전체와 25개 자치구 분리
district_df = df[
    df["행정구역_표시"] != "서울특별시"
].copy()

districts = district_df[
    "행정구역_표시"
].drop_duplicates().tolist()


if len(districts) == 0:

    st.error("자치구 데이터를 찾을 수 없습니다.")

    st.stop()


# ==================================================
# 5. 공통 함수
# ==================================================

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

    valid_values = [
        v for v in values
        if v is not None
    ]

    if not valid_values:
        return 100000

    maximum = max(valid_values)

    return max(
        100000,
        (maximum // 100000 + 1) * 100000
    )


# ==================================================
# 6. 탭 메뉴
# ==================================================

tab1, tab2, tab3 = st.tabs([
    "👥 남녀 연령별 비교",
    "🏆 연령대별 자치구 순위",
    "📈 연도별 인구 변화"
])


# ==================================================
# TAB 1. 남녀 연령별 인구 비교
# ==================================================

with tab1:

    st.header("남녀 연령별 인구 비교")

    st.write(
        "선택한 지역과 연도의 남성·여성 인구를 "
        "연령대별로 비교합니다."
    )

    col1, col2 = st.columns(2)

    with col1:

        selected_district = st.selectbox(
            "행정구역 선택",
            districts,
            key="line_district"
        )

    with col2:

        selected_year = st.selectbox(
            "연도 선택",
            years,
            index=len(years) - 1,
            key="line_year"
        )


    # 선택한 지역 데이터
    selected_row = district_df[
        district_df["행정구역_표시"]
        == selected_district
    ].iloc[0]


    male_values = []
    female_values = []

    for age in ages:

        male_values.append(
            get_population(
                selected_row,
                selected_year,
                "남_거주자",
                age
            )
        )

        female_values.append(
            get_population(
                selected_row,
                selected_year,
                "여_거주자",
                age
            )
        )


    if any(v is None for v in male_values + female_values):

        st.error(
            "남녀 인구 열을 찾지 못했습니다. "
            "원본 CSV의 열 이름을 확인해 주세요."
        )

    else:

        male_total = sum(male_values)
        female_total = sum(female_values)

        m1, m2, m3 = st.columns(3)

        m1.metric(
            "남성 인구",
            format_number(male_total)
        )

        m2.metric(
            "여성 인구",
            format_number(female_total)
        )

        m3.metric(
            "남녀 인구 차이",
            format_number(abs(male_total - female_total))
        )


        # 꺾은선 그래프
        fig = go.Figure()


        # 남성: 핫핑크
        fig.add_trace(

            go.Scatter(

                x=ages,

                y=male_values,

                mode="lines+markers",

                name="남성",

                line=dict(
                    color=PINK,
                    width=4
                ),

                marker=dict(
                    color=PINK,
                    size=9
                ),

                hovertemplate=(
                    "연령: %{x}<br>"
                    "남성: %{y:,.0f}명"
                    "<extra></extra>"
                )

            )

        )


        # 여성: 초록색
        fig.add_trace(

            go.Scatter(

                x=ages,

                y=female_values,

                mode="lines+markers",

                name="여성",

                line=dict(
                    color=GREEN,
                    width=4
                ),

                marker=dict(
                    color=GREEN,
                    size=9
                ),

                hovertemplate=(
                    "연령: %{x}<br>"
                    "여성: %{y:,.0f}명"
                    "<extra></extra>"
                )

            )

        )


        y_max = make_axis_max(
            male_values + female_values
        )


        fig.update_layout(

            title=f"{selected_district} {selected_year}년 남녀 연령별 인구",

            xaxis=dict(
                title="나이",
                type="category",
                categoryorder="array",
                categoryarray=ages,
                showgrid=True,
                gridcolor="#DDDDDD"
            ),

            yaxis=dict(
                title="인구수 (명)",
                range=[0, y_max],
                tickmode="linear",
                tick0=0,
                dtick=100000,
                tickformat=",",
                showgrid=True,
                gridcolor="#DDDDDD"
            ),

            plot_bgcolor="white",
            paper_bgcolor="white",

            height=600,

            hovermode="x unified",

            legend=dict(
                orientation="h",
                y=1.12,
                x=0.5,
                xanchor="center"
            ),

            font=dict(
                family="Noto Sans KR, Malgun Gothic, sans-serif",
                size=13,
                color="#222222"
            )

        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


        # 데이터 표
        with st.expander("남녀 연령별 인구 데이터"):

            gender_df = pd.DataFrame({

                "연령대": ages,

                "남성": male_values,

                "여성": female_values

            })

            st.dataframe(
                gender_df,
                use_container_width=True,
                hide_index=True
            )


# ==================================================
# TAB 2. 연령대별 인구가 많은 자치구
# ==================================================

with tab2:

    st.header("연령대별 인구가 많은 자치구")

    st.write(
        "원하는 연령대와 성별을 선택하면 "
        "해당 인구가 많은 자치구를 순위별로 보여줍니다."
    )


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
            key="rank_age"
        )

    with col3:

        rank_gender = st.selectbox(
            "성별 선택",
            ["전체", "남성", "여성"],
            key="rank_gender"
        )


    gender_key = {
        "전체": "거주자",
        "남성": "남_거주자",
        "여성": "여_거주자"
    }[rank_gender]


    # 25개 자치구 인구 데이터 수집
    ranking_data = []

    for _, row in district_df.iterrows():

        value = get_population(
            row,
            rank_year,
            gender_key,
            selected_age
        )

        if value is not None:

            ranking_data.append({

                "행정구역": row["행정구역_표시"],

                "인구수": value

            })


    ranking_df = pd.DataFrame(ranking_data)


    if ranking_df.empty:

        st.error("해당 연령대의 인구 데이터를 찾지 못했습니다.")

    else:

        ranking_df = ranking_df.sort_values(
            "인구수",
            ascending=False
        ).reset_index(drop=True)


        first = ranking_df.iloc[0]

        st.success(
            f"🏆 {rank_year}년 {selected_age} {rank_gender} 인구가 "
            f"가장 많은 지역은 {first['행정구역']}입니다. "
            f"({first['인구수']:,}명)"
        )


        # 막대 색상 설정
        if rank_gender == "남성":

            base_color = "#F8A5CF"
            first_color = PINK

        elif rank_gender == "여성":

            base_color = "#A7DDB5"
            first_color = GREEN

        else:

            base_color = "#C4B5FD"
            first_color = PURPLE


        bar_colors = [
            first_color if i == 0 else base_color
            for i in range(len(ranking_df))
        ]


        bar_fig = go.Figure()


        bar_fig.add_trace(

            go.Bar(

                x=ranking_df["행정구역"],

                y=ranking_df["인구수"],

                marker_color=bar_colors,

                text=[
                    f"{v:,}명"
                    for v in ranking_df["인구수"]
                ],

                textposition="outside",

                hovertemplate=(
                    "%{x}<br>"
                    "인구수: %{y:,.0f}명"
                    "<extra></extra>"
                )

            )

        )


        bar_fig.update_layout(

            title=f"{rank_year}년 {selected_age} {rank_gender} 인구 순위",

            xaxis=dict(
                title="행정구역",
                tickangle=-45
            ),

            yaxis=dict(
                title="인구수 (명)",
                tickformat=",",
                showgrid=True,
                gridcolor="#DDDDDD"
            ),

            plot_bgcolor="white",
            paper_bgcolor="white",

            height=650,

            showlegend=False,

            font=dict(
                family="Noto Sans KR, Malgun Gothic, sans-serif",
                size=12
            )

        )


        st.plotly_chart(
            bar_fig,
            use_container_width=True
        )


        st.subheader("자치구 인구 순위")

        ranking_display = ranking_df.copy()

        ranking_display.insert(
            0,
            "순위",
            range(1, len(ranking_display) + 1)
        )

        ranking_display["인구수"] = (
            ranking_display["인구수"]
            .map(lambda x: f"{x:,}명")
        )

        st.dataframe(
            ranking_display,
            use_container_width=True,
            hide_index=True
        )


# ==================================================
# TAB 3. 연도별 인구 변화
# ==================================================

with tab3:

    st.header("연도별 인구 변화 분석")

    st.write(
        "선택한 자치구의 2020년부터 2025년까지 "
        "전체 인구가 어떻게 변했는지 확인합니다."
    )


    change_district = st.selectbox(
        "분석할 행정구역 선택",
        districts,
        key="change_district"
    )


    change_row = district_df[
        district_df["행정구역_표시"]
        == change_district
    ].iloc[0]


    yearly_values = []

    for y in years:

        value = get_total_population(
            change_row,
            y
        )

        if value is not None:

            yearly_values.append({

                "연도": f"{y}년",

                "인구수": value,

                "연도숫자": y

            })


    yearly_df = pd.DataFrame(yearly_values)


    if yearly_df.empty:

        st.error("연도별 전체 인구 데이터를 찾지 못했습니다.")

    else:

        first_population = yearly_df.iloc[0]["인구수"]
        last_population = yearly_df.iloc[-1]["인구수"]

        difference = last_population - first_population

        if first_population != 0:

            rate = difference / first_population * 100

        else:

            rate = 0


        change1, change2, change3 = st.columns(3)


        change1.metric(
            f"{years[0]}년 인구",
            format_number(first_population)
        )


        change2.metric(
            f"{years[-1]}년 인구",
            format_number(last_population)
        )


        change3.metric(
            "전체 인구 증감",
            format_number(abs(difference)),
            delta=f"{rate:+.2f}%"
        )


        if difference > 0:

            st.success(
                f"{change_district}의 인구는 "
                f"{years[0]}년보다 {difference:,}명 증가했습니다."
            )

        elif difference < 0:

            st.warning(
                f"{change_district}의 인구는 "
                f"{years[0]}년보다 {abs(difference):,}명 감소했습니다."
            )

        else:

            st.info("시작 연도와 마지막 연도의 인구가 같습니다.")


        # 연도별 그래프
        change_fig = go.Figure()


        change_fig.add_trace(

            go.Scatter(

                x=yearly_df["연도"],

                y=yearly_df["인구수"],

                mode="lines+markers+text",

                name="전체 인구",

                line=dict(
                    color=PINK,
                    width=4
                ),

                marker=dict(
                    color=PINK,
                    size=10
                ),

                text=[
                    f"{v:,}"
                    for v in yearly_df["인구수"]
                ],

                textposition="top center",

                hovertemplate=(
                    "%{x}<br>"
                    "인구수: %{y:,.0f}명"
                    "<extra></extra>"
                )

            )

        )


        change_fig.update_layout(

            title=f"{change_district} 연도별 전체 인구 변화",

            xaxis=dict(
                title="연도",
                showgrid=True,
                gridcolor="#DDDDDD"
            ),

            yaxis=dict(
                title="인구수 (명)",
                tickformat=",",
                showgrid=True,
                gridcolor="#DDDDDD"
            ),

            plot_bgcolor="white",
            paper_bgcolor="white",

            height=550,

            hovermode="x unified",

            font=dict(
                family="Noto Sans KR, Malgun Gothic, sans-serif",
                size=13
            )

        )


        st.plotly_chart(
            change_fig,
            use_container_width=True
        )


        with st.expander("연도별 인구 데이터 확인"):

            display_change = yearly_df[
                ["연도", "인구수"]
            ].copy()

            display_change["인구수"] = (
                display_change["인구수"]
                .map(lambda x: f"{x:,}명")
            )

            st.dataframe(
                display_change,
                use_container_width=True,
                hide_index=True
            )


# ==================================================
# 7. 데이터 결측치 확인
# ==================================================

st.divider()

with st.expander("📋 전체 데이터 결측치 확인"):

    missing_count = int(
        df.isnull().sum().sum()
    )

    total_cells = df.size

    missing_rate = (
        missing_count / total_cells * 100
        if total_cells else 0
    )

    c1, c2 = st.columns(2)

    c1.metric(
        "전체 결측치",
        f"{missing_count:,}개"
    )

    c2.metric(
        "결측치 비율",
        f"{missing_rate:.2f}%"
    )


    if missing_count == 0:

        st.success(
            "모든 데이터가 정상적으로 입력되어 있습니다."
        )

    else:

        st.warning(
            "결측치가 있는 열을 확인해 주세요."
        )

        missing_df = (
            df.isnull()
            .sum()
            .reset_index()
        )

        missing_df.columns = [
            "열 이름",
            "결측치 개수"
        ]

        missing_df = missing_df[
            missing_df["결측치 개수"] > 0
        ]

        st.dataframe(
            missing_df,
            use_container_width=True,
            hide_index=True
        )


# ==================================================
# 8. 하단 안내
# ==================================================

st.divider()

st.caption(
    "서울특별시 인구 분석 | "
    "데이터 출처: population.csv"
)
