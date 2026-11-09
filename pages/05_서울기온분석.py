
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from io import BytesIO
import re

# =====================================
# 1. 페이지 설정
# =====================================
st.set_page_config(
    page_title="서울 월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 월별 기온분석")
st.caption("월별 평균기온과 연도별 최고·최저기온을 비교합니다.")

# =====================================
# 2. CSV 파일 자동 검색
# =====================================
def find_csv():
    base = Path(__file__).resolve().parent

    paths = [
        base / "temperature.csv",
        base.parent / "temperature.csv",
        base.parent.parent / "temperature.csv",
        Path.cwd() / "temperature.csv",
        Path.cwd() / "pages" / "temperature.csv",
    ]

    for path in paths:
        if path.is_file():
            return path

    return None


@st.cache_data
def read_csv_data(file_bytes):
    for encoding in ["cp949", "utf-8-sig", "utf-8"]:
        try:
            return pd.read_csv(BytesIO(file_bytes), encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError(
        "CSV 파일의 인코딩을 읽을 수 없습니다."
    )


csv_path = find_csv()

if csv_path:
    with open(csv_path, "rb") as file:
        df = read_csv_data(file.read())
else:
    uploaded = st.file_uploader(
        "temperature.csv 파일 업로드",
        type=["csv"]
    )

    if uploaded is None:
        st.warning(
            "CSV 파일을 찾지 못했습니다. "
            "GitHub 저장소에 temperature.csv가 있는지 확인하거나 "
            "아래에서 파일을 업로드해 주세요."
        )
        st.stop()

    df = read_csv_data(uploaded.getvalue())


# =====================================
# 3. 데이터 확인
# =====================================
required_columns = [
    "일시",
    "평균기온(℃)",
    "최고기온(℃)",
    "최저기온(℃)"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(
        "CSV 파일에 필요한 열이 없습니다: "
        + ", ".join(missing_columns)
    )
    st.stop()


for col in [
    "평균기온(℃)",
    "최고기온(℃)",
    "최저기온(℃)"
]:
    df[col] = pd.to_numeric(df[col], errors="coerce")


# =====================================
# 4. 날짜에서 연도와 월 추출
#    예: Oct-07, Jan-08
# =====================================
month_map = {
    "Jan": 1, "Feb": 2, "Mar": 3,
    "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9,
    "Oct": 10, "Nov": 11, "Dec": 12
}

parsed_dates = []
century = 1900
previous_short_year = None

for value in df["일시"]:
    match = re.fullmatch(
        r"\s*([A-Za-z]{3})-(\d{2})\s*",
        str(value)
    )

    if not match:
        parsed_dates.append((None, None))
        continue

    month_text = match.group(1).title()
    short_year = int(match.group(2))

    if month_text not in month_map:
        parsed_dates.append((None, None))
        continue

    # 1999년 다음에 2000년이 오는 경우 처리
    if (
        previous_short_year is not None
        and previous_short_year - short_year > 50
    ):
        century += 100

    year = century + short_year
    month = month_map[month_text]

    parsed_dates.append((year, month))
    previous_short_year = short_year

df["연도"] = [x[0] for x in parsed_dates]
df["월"] = [x[1] for x in parsed_dates]

df = df.dropna(subset=["연도", "월"]).copy()

df["연도"] = df["연도"].astype(int)
df["월"] = df["월"].astype(int)

df = df.sort_values(["연도", "월"])

if df.empty:
    st.error("분석할 수 있는 날짜 데이터가 없습니다.")
    st.stop()

month_labels = {
    i: f"{i}월" for i in range(1, 13)
}

month_order = list(range(1, 13))

# 그래프 공통 설정
PINK = "#FF1493"
SKYBLUE = "#87CEEB"

def style_chart(fig, title):
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
        height=520,
        template="plotly_white",
        margin=dict(l=30, r=30, t=80, b=40),
        xaxis=dict(
            tickmode="array",
            tickvals=month_order,
            ticktext=[
                f"{m}월" for m in month_order
            ],
            showgrid=True
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=True
        )
    )
    return fig


# =====================================
# 그래프 1. 서울 월별 평균기온
# =====================================
st.header("1. 서울 월별 평균기온")

st.write(
    "전체 데이터에서 1월부터 12월까지 "
    "각 월의 평균기온을 계산합니다."
)

monthly_average = (
    df.groupby("월")["평균기온(℃)"]
    .mean()
    .reindex(month_order)
)

fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=month_order,
        y=monthly_average.values,
        mode="lines+markers",
        name="월별 평균기온",
        line=dict(color="#4169E1", width=3),
        marker=dict(size=8),
        connectgaps=False
    )
)

style_chart(fig1, "서울 월별 평균기온")
st.plotly_chart(fig1, use_container_width=True)


# =====================================
# 그래프 2 & 3. 연도 선택
# =====================================
st.header("2. 연도별 최고기온·최저기온 비교")

years = sorted(df["연도"].unique().tolist())

st.write(
    "연도를 1개 선택하면 해당 연도의 월별 최고·최저기온을, "
    "2개 선택하면 두 연도를 비교합니다."
)

selected_years = st.multiselect(
    "비교할 연도를 선택하세요. (최대 2개)",
    options=years,
    default=[years[-1]],
    format_func=lambda y: f"{y}년",
    max_selections=2
)

if len(selected_years) == 0:
    st.info("연도를 1개 또는 2개 선택해 주세요.")

else:
    fig2 = go.Figure()

    # 선택한 연도별 최고기온과 최저기온
    for index, year in enumerate(sorted(selected_years)):
        year_df = df[df["연도"] == year].copy()

        year_monthly = (
            year_df.groupby("월")[
                ["최고기온(℃)", "최저기온(℃)"]
            ]
            .mean()
            .reindex(month_order)
        )

        # 연도 구분: 첫 번째 연도는 실선,
        # 두 번째 연도는 점선
        dash_style = "solid" if index == 0 else "dash"

        # 최고기온: 핫핑크
        fig2.add_trace(
            go.Scatter(
                x=month_order,
                y=year_monthly["최고기온(℃)"],
                mode="lines+markers",
                name=f"{year}년 최고기온",
                line=dict(
                    color=PINK,
                    width=3,
                    dash=dash_style
                ),
                marker=dict(size=6),
                connectgaps=False
            )
        )

        # 최저기온: 하늘색
        fig2.add_trace(
            go.Scatter(
                x=month_order,
                y=year_monthly["최저기온(℃)"],
                mode="lines+markers",
                name=f"{year}년 최저기온",
                line=dict(
                    color=SKYBLUE,
                    width=3,
                    dash=dash_style
                ),
                marker=dict(size=6),
                connectgaps=False
            )
        )

    if len(selected_years) == 1:
        chart_title = (
            f"{selected_years[0]}년 월별 최고기온·최저기온"
        )
    else:
        chart_title = (
            f"{min(selected_years)}년·{max(selected_years)}년 "
            "기온 비교"
        )

    style_chart(fig2, chart_title)
    st.plotly_chart(fig2, use_container_width=True)

    # =================================
    # 선택 연도 상세 데이터
    # =================================
    with st.expander("선택한 연도의 상세 데이터 보기"):
        detail = df[
            df["연도"].isin(selected_years)
        ][
            ["연도", "월", "평균기온(℃)", "최고기온(℃)", "최저기온(℃)"]
        ].copy()

        detail["월"] = detail["월"].map(month_labels)

        detail = detail.rename(
            columns={
                "연도": "연도",
                "월": "월",
                "평균기온(℃)": "평균기온(℃)",
                "최고기온(℃)": "최고기온(℃)",
                "최저기온(℃)": "최저기온(℃)"
            }
        )

        st.dataframe(
            detail,
            use_container_width=True,
            hide_index=True
        )

st.caption(
    "데이터 분석: Pandas | 그래프: Plotly | "
    "기온 단위: ℃"
)
