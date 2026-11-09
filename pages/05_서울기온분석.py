
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from io import BytesIO
import re

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="서울 기온 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 기온 분석 프로그램")
st.write("서울의 기온 데이터를 다양한 그래프로 분석합니다.")

PINK = "#FF1493"
SKYBLUE = "#87CEEB"
BLUE = "#4169E1

# ==========================================
# 2. CSV 파일 자동 검색
# ==========================================
def find_csv():
    base = Path(__file__).resolve().parent

    paths = [
        base / "temperature.csv",
        base.parent / "temperature.csv",
        base.parent.parent / "temperature.csv",
        Path.cwd() / "temperature.csv"
    ]

    for path in paths:
        if path.is_file():
            return path

    return None


# ==========================================
# 3. CSV 불러오기 및 한글 인코딩
# ==========================================
@st.cache_data
def load_data(file_bytes):
    for encoding in ["cp949", "utf-8-sig", "utf-8"]:
        try:
            return pd.read_csv(
                BytesIO(file_bytes),
                encoding=encoding
            )
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 인코딩을 확인해 주세요.")


csv_path = find_csv()

if csv_path:
    with open(csv_path, "rb") as file:
        df = load_data(file.read())
else:
    uploaded_file = st.file_uploader(
        "temperature.csv 업로드",
        type=["csv"]
    )

    if uploaded_file is None:
        st.warning(
            "temperature.csv 파일을 찾을 수 없습니다. "
            "GitHub 저장소에 파일을 업로드해 주세요."
        )
        st.stop()

    df = load_data(uploaded_file.getvalue())


# ==========================================
# 4. 필요한 데이터 확인
# ==========================================
required_columns = [
    "일시",
    "평균기온(℃)",
    "최고기온(℃)",
    "최저기온(℃)"
]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름을 확인해 주세요.")
    st.stop()


for col in [
    "평균기온(℃)",
    "최고기온(℃)",
    "최저기온(℃)"
]:
    df[col] = pd.to_numeric(df[col], errors="coerce")


# ==========================================
# 5. 날짜에서 연도와 월 추출
# ==========================================
month_map = {
    "Jan": 1, "Feb": 2, "Mar": 3,
    "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9,
    "Oct": 10, "Nov": 11, "Dec": 12
}

def parse_date(value):
    match = re.fullmatch(
        r"\s*([A-Za-z]{3})-(\d{2})\s*",
        str(value)
    )

    if not match:
        return None, None

    month_text = match.group(1).title()
    short_year = int(match.group(2))

    if month_text not in month_map:
        return None, None

    # 00~26은 2000년대
    # 27~99는 1900년대
    year = (
        2000 + short_year
        if short_year <= 26
        else 1900 + short_year
    )

    month = month_map[month_text]

    return year, month


parsed = df["일시"].apply(parse_date)

df["연도"] = [x[0] for x in parsed]
df["월"] = [x[1] for x in parsed]

df = df.dropna(
    subset=["연도", "월"]
).copy()

df["연도"] = df["연도"].astype(int)
df["월"] = df["월"].astype(int)

df = df.sort_values(["연도", "월"])

if df.empty:
    st.error("분석할 수 있는 데이터가 없습니다.")
    st.stop()


# ==========================================
# 6. 공통 그래프 디자인
# ==========================================
months = list(range(1, 13))

def make_layout(fig, title):
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor="center"
        ),
        xaxis_title="월",
        yaxis_title="온도 (℃)",
        legend_title="기온 구분",
        hovermode="x unified",
        height=500,
        template="plotly_white",
        xaxis=dict(
            tickmode="array",
            tickvals=months,
            ticktext=[f"{m}월" for m in months],
            showgrid=True
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=True
        )
    )

    return fig


# ==========================================
# 그래프 1. 기존 기능 복구
# 선택한 월의 전체 연도별 최고/최저기온
# ==========================================
st.divider()

st.header("1. 월별 연도별 최고기온 및 최저기온")

st.write(
    "원하는 월을 선택하면 해당 월의 전체 연도별 "
    "최고기온과 최저기온을 비교합니다."
)

selected_month = st.selectbox(
    "분석할 월 선택",
    options=months,
    format_func=lambda x: f"{x}월"
)

month_df = df[
    df["월"] == selected_month
].sort_values("연도")

fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=month_df["연도"],
        y=month_df["최고기온(℃)"],
        mode="lines+markers",
        name="최고기온",
        line=dict(color=PINK, width=3),
        marker=dict(size=6)
    )
)

fig1.add_trace(
    go.Scatter(
        x=month_df["연도"],
        y=month_df["최저기온(℃)"],
        mode="lines+markers",
        name="최저기온",
        line=dict(color=SKYBLUE, width=3),
        marker=dict(size=6)
    )
)

fig1.update_layout(
    title=dict(
        text="월별 기온분석",
        x=0.5,
        xanchor="center"
    ),
    xaxis_title="연도",
    yaxis_title="온도 (℃)",
    legend_title="기온 구분",
    hovermode="x unified",
    height=500,
    template="plotly_white",
    xaxis=dict(
        showgrid=True,
        dtick=1
    ),
    yaxis=dict(showgrid=True)
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# ==========================================
# 그래프 2. 서울 월별 평균기온
# ==========================================
st.divider()

st.header("2. 서울 월별 평균기온")

st.write(
    "전체 연도의 데이터를 이용하여 "
    "1월부터 12월까지 월별 평균기온을 분석합니다."
)

monthly_avg = (
    df.groupby("월")["평균기온(℃)"]
    .mean()
    .reindex(months)
)

fig2 = go.Figure()

fig2.add_trace(
    go.Scatter(
        x=months,
        y=monthly_avg.values,
        mode="lines+markers",
        name="월별 평균기온",
        line=dict(
            color=BLUE,
            width=3
        ),
        marker=dict(size=8),
        connectgaps=False
    )
)

make_layout(fig2, "서울 월별 평균기온")

st.plotly_chart(
    fig2,
    use_container_width=True
)


# ==========================================
# 그래프 3. 연도 1개 또는 2개 선택
# ==========================================
st.divider()

st.header("3. 연도별 최고기온 및 최저기온 비교")

st.write(
    "연도 1개를 선택하면 해당 연도의 기온을 분석하고, "
    "연도 2개를 선택하면 두 연도의 기온을 비교합니다."
)

years = sorted(df["연도"].unique().tolist())

selected_years = st.multiselect(
    "비교할 연도를 선택하세요. (최대 2개)",
    options=years,
    default=[years[-1]],
    format_func=lambda x: f"{x}년",
    max_selections=2
)


if len(selected_years) == 0:

    st.info("연도를 1개 또는 2개 선택해 주세요.")

else:

    fig3 = go.Figure()

    for i, year in enumerate(sorted(selected_years)):

        year_df = df[
            df["연도"] == year
        ].sort_values("월")

        # 월별 데이터
        year_data = (
            year_df.groupby("월")[
                ["최고기온(℃)", "최저기온(℃)"]
            ]
            .mean()
            .reindex(months)
        )

        # 첫 번째 연도는 실선
        # 두 번째 연도는 점선
        dash = "solid" if i == 0 else "dash"

        # 최고기온
        fig3.add_trace(
            go.Scatter(
                x=months,
                y=year_data["최고기온(℃)"],
                mode="lines+markers",
                name=f"{year}년 최고기온",
                line=dict(
                    color=PINK,
                    width=3,
                    dash=dash
                ),
                marker=dict(size=7),
                connectgaps=False
            )
        )

        # 최저기온
        fig3.add_trace(
            go.Scatter(
                x=months,
                y=year_data["최저기온(℃)"],
                mode="lines+markers",
                name=f"{year}년 최저기온",
                line=dict(
                    color=SKYBLUE,
                    width=3,
                    dash=dash
                ),
                marker=dict(size=7),
                connectgaps=False
            )
        )

    if len(selected_years) == 1:
        title = f"{selected_years[0]}년 월별 최고기온 및 최저기온"
    else:
        title = (
            f"{min(selected_years)}년과 "
            f"{max(selected_years)}년 기온 비교"
        )

    make_layout(fig3, title)

    st.plotly_chart(
        fig3,
        use_container_width=True
    )


    # ======================================
    # 선택한 연도 상세 데이터
    # ======================================
    st.subheader("📊 선택 연도 상세 데이터")

    detail = df[
        df["연도"].isin(selected_years)
    ][
        [
            "연도",
            "월",
            "평균기온(℃)",
            "최고기온(℃)",
            "최저기온(℃)"
        ]
    ].copy()

    detail["월"] = detail["월"].astype(str) + "월"

    st.dataframe(
        detail,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 7. 데이터 정보
# ==========================================
st.divider()

st.header("📋 데이터 정보")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "전체 데이터",
        f"{len(df):,}개"
    )

with col2:
    st.metric(
        "분석 시작 연도",
        f"{df['연도'].min()}년"
    )

with col3:
    st.metric(
        "분석 마지막 연도",
        f"{df['연도'].max()}년"
    )

st.caption(
    "서울 기온 분석 | Pandas & Plotly"
)
