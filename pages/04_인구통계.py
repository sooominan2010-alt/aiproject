
import re
from pathlib import Path
from io import BytesIO

import pandas as pd
import streamlit as st
import plotly.graph_objects as go


# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="서울시 연령별 인구 분석",
    page_icon="📊",
    layout="wide"
)

HOT_PINK = "#FF1493"

st.title("📊 서울특별시 연령별 인구 분석")
st.caption(
    "행정구역, 성별, 연도를 선택하여 "
    "연령대별 인구수를 확인할 수 있습니다."
)


# ==========================================
# 2. CSV 파일 불러오기
# ==========================================

# pages 폴더의 상위 폴더 경로
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

    for encoding in encodings:

        try:
            df = pd.read_csv(
                BytesIO(file_bytes),
                encoding=encoding
            )

            return df

        except UnicodeDecodeError:
            continue

    raise ValueError(
        "CSV 인코딩을 확인할 수 없습니다."
    )


# ==========================================
# 3. CSV 파일 읽기
# ==========================================

if not CSV_PATH.exists():

    st.error(
        "population.csv 파일을 찾을 수 없습니다."
    )

    st.write("현재 찾는 경로:")
    st.code(str(CSV_PATH))

    st.stop()


try:

    file_bytes = CSV_PATH.read_bytes()

    df = load_data(file_bytes)

except Exception as e:

    st.error(f"파일 읽기 오류: {e}")

    st.stop()


# ==========================================
# 4. 데이터 전처리
# ==========================================

# 열 이름 공백 제거
df.columns = df.columns.astype(str).str.strip()


if "행정구역" not in df.columns:

    st.error(
        "'행정구역' 열이 존재하지 않습니다."
    )

    st.stop()


# 행정구역 코드 제거
df["행정구역_표시"] = (
    df["행정구역"]
    .astype(str)
    .str.replace(
        r"\s*\(\d+\)\s*$",
        "",
        regex=True
    )
    .str.strip()
)


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


# ==========================================
# 5. 행정구역 및 연도 추출
# ==========================================

districts = (
    df["행정구역_표시"]
    .drop_duplicates()
    .tolist()
)


years = sorted({
    int(year)
    for col in df.columns
    for year in re.findall(
        r"(20\d{2})년",
        col
    )
})


if not years:

    st.error(
        "CSV 파일에서 연도 정보를 찾을 수 없습니다."
    )

    st.stop()


# ==========================================
# 6. 사용자 선택
# ==========================================

st.subheader("분석 조건 선택")

col1, col2, col3 = st.columns(3)


with col1:

    district = st.selectbox(
        "행정구역 선택",
        districts
    )


with col2:

    gender = st.selectbox(
        "성별 선택",
        ["전체", "남성", "여성"]
    )


with col3:

    year = st.selectbox(
        "연도 선택",
        years,
        index=len(years) - 1
    )


# ==========================================
# 7. 성별 열 이름 설정
# ==========================================

gender_name = {

    "전체": "거주자",

    "남성": "남_거주자",

    "여성": "여_거주자"

}[gender]


# ==========================================
# 8. 연령대 설정
# ==========================================

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


# ==========================================
# 9. 선택한 지역 데이터 가져오기
# ==========================================

selected = df[
    df["행정구역_표시"] == district
]


if selected.empty:

    st.error(
        "선택한 행정구역의 데이터가 없습니다."
    )

    st.stop()


selected = selected.iloc[0]


# ==========================================
# 10. 연령별 인구수 추출
# ==========================================

population = []

missing_columns = []


for age in ages:

    column = (
        f"{year}년_"
        f"{gender_name}_"
        f"{age}"
    )

    if column in df.columns:

        value = selected[column]

        population.append(
            0 if pd.isna(value)
            else int(value)
        )

    else:

        population.append(0)

        missing_columns.append(column)


if missing_columns:

    st.warning(
        "일부 연령대 데이터 열을 찾지 못했습니다: "
        + ", ".join(missing_columns)
    )


# 데이터프레임 생성
chart_df = pd.DataFrame({

    "나이": ages,

    "인구수": population

})


# ==========================================
# 11. 인구 요약
# ==========================================

total = sum(population)

st.subheader("인구 분석 결과")

m1, m2, m3 = st.columns(3)


m1.metric(
    "선택 행정구역",
    district
)


m2.metric(
    "선택 연도",
    f"{year}년"
)


m3.metric(
    "연령별 인구 합계",
    f"{total:,}명"
)


# ==========================================
# 12. 핫핑크 꺾은선 그래프
# ==========================================

st.subheader("연령대별 인구수 꺾은선 그래프")


fig = go.Figure()


fig.add_trace(

    go.Scatter(

        x=chart_df["나이"],

        y=chart_df["인구수"],

        mode="lines+markers",

        name="인구수",

        line=dict(

            color=HOT_PINK,

            width=4

        ),

        marker=dict(

            color=HOT_PINK,

            size=9

        ),

        hovertemplate=(

            "%{x}<br>"

            "인구수: %{y:,.0f}명"

            "<extra></extra>"

        )

    )

)


# 세로축 최대값 설정
max_value = max(population) if population else 0

y_max = max(
    100000,
    ((max_value // 100000) + 1) * 100000
)


fig.update_layout(

    title=dict(

        text=f"{district} | {gender} | {year}년",

        x=0.5,

        xanchor="center"

    ),

    xaxis=dict(

        title="나이",

        type="category",

        categoryorder="array",

        categoryarray=ages,

        showgrid=True,

        gridcolor="#E0E0E0",

        gridwidth=1

    ),

    yaxis=dict(

        title="인구수 (명)",

        range=[0, y_max],

        tickmode="linear",

        tick0=0,

        dtick=100000,

        tickformat=",",

        showgrid=True,

        gridcolor="#D0D0D0",

        gridwidth=1

    ),

    plot_bgcolor="white",

    paper_bgcolor="white",

    height=600,

    hovermode="x unified",

    font=dict(

        family="Arial, sans-serif",

        size=13,

        color="#222222"

    )

)


st.plotly_chart(

    fig,

    use_container_width=True

)


st.caption(
    "가로축: 10살 단위 연령 구간 / "
    "세로축: 10만 명 단위 / "
    "그래프 색상: 핫핑크"
)


# ==========================================
# 13. 데이터 표
# ==========================================

with st.expander("연령별 인구 데이터 확인"):

    display_df = chart_df.copy()

    display_df["인구수"] = (
        display_df["인구수"]
        .apply(lambda x: f"{x:,}명")
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


    csv_data = chart_df.to_csv(
        index=False,
        encoding="utf-8-sig"
    ).encode("utf-8-sig")


    st.download_button(

        label="분석 결과 CSV 다운로드",

        data=csv_data,

        file_name="인구분석결과.csv",

        mime="text/csv"

    )


# ==========================================
# 14. 결측치 확인
# ==========================================

with st.expander("데이터 결측치 확인"):

    missing_count = int(
        df.isnull().sum().sum()
    )

    st.metric(
        "전체 결측치",
        f"{missing_count:,}개"
    )

    if missing_count == 0:

        st.success(
            "결측치가 없습니다."
        )

    else:

        st.warning(
            "결측치가 있는 열을 확인해 주세요."
        )

        st.dataframe(
            df.isnull().sum()[
                df.isnull().sum() > 0
            ]
        )


st.divider()

st.caption(
    "서울특별시 인구 데이터 분석 프로그램"
)

