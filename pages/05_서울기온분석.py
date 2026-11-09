
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# -----------------------------
# 1. 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온분석")
st.write("원하는 월을 선택하면 전체 연도별 최고기온과 최저기온을 비교합니다.")

# -----------------------------
# 2. CSV 파일 불러오기
# -----------------------------
@st.cache_data
def load_data(file):
    encodings = ["cp949", "utf-8-sig", "utf-8"]

    for encoding in encodings:
        try:
            return pd.read_csv(file, encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일의 인코딩을 확인해 주세요.")

file_path = Path(__file__).parent / "temperature.csv"

if file_path.exists():
    df = load_data(file_path)
else:
    uploaded_file = st.file_uploader(
        "temperature.csv 파일을 업로드해 주세요.",
        type=["csv"]
    )

    if uploaded_file is None:
        st.info("CSV 파일을 업로드하면 분석이 시작됩니다.")
        st.stop()

    df = load_data(uploaded_file)

# -----------------------------
# 3. 데이터 전처리
# -----------------------------
required_columns = [
    "일시",
    "최고기온(℃)",
    "최저기온(℃)"
]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름이 올바르지 않습니다.")
    st.stop()

df["최고기온(℃)"] = pd.to_numeric(
    df["최고기온(℃)"], errors="coerce"
)

df["최저기온(℃)"] = pd.to_numeric(
    df["최저기온(℃)"], errors="coerce"
)

# 날짜 형식: Oct-07 → 1907년 10월
month_map = {
    "Jan": 1, "Feb": 2, "Mar": 3,
    "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9,
    "Oct": 10, "Nov": 11, "Dec": 12
}

def parse_date(value):
    try:
        month_text, year_text = str(value).split("-")

        short_year = int(year_text)
        year = (
            2000 + short_year
            if short_year <= 26
            else 1900 + short_year
        )

        month = month_map[month_text]

        return pd.Series([year, month])

    except (ValueError, KeyError):
        return pd.Series([None, None])

df[["연도", "월"]] = df["일시"].apply(parse_date)

df = df.dropna(
    subset=["연도", "월"]
).copy()

df["연도"] = df["연도"].astype(int)
df["월"] = df["월"].astype(int)

# -----------------------------
# 4. 월 선택
# -----------------------------
month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

selected_month = st.selectbox(
    "📅 분석할 월을 선택하세요.",
    options=list(month_names.keys()),
    format_func=lambda x: month_names[x],
    index=7
)

# -----------------------------
# 5. 선택한 월의 데이터 분석
# -----------------------------
monthly_df = df[df["월"] == selected_month].copy()

monthly_df = monthly_df.sort_values("연도")

# -----------------------------
# 6. 그래프 생성
# -----------------------------
if monthly_df.empty:
    st.warning("선택한 월의 데이터가 없습니다.")

else:
    fig = go.Figure()

    # 최고기온 그래프
    fig.add_trace(
        go.Scatter(
            x=monthly_df["연도"],
            y=monthly_df["최고기온(℃)"],
            mode="lines+markers",
            name="최고기온",
            line=dict(
                color="#FF1493",
                width=3
            ),
            marker=dict(size=5)
        )
    )

    # 최저기온 그래프
    fig.add_trace(
        go.Scatter(
            x=monthly_df["연도"],
            y=monthly_df["최저기온(℃)"],
            mode="lines+markers",
            name="최저기온",
            line=dict(
                color="#87CEEB",
                width=3
            ),
            marker=dict(size=5)
        )
    )

    fig.update_layout(
        title={
            "text": "월별 기온분석",
            "x": 0.5,
            "xanchor": "center"
        },
        xaxis_title="연도",
        yaxis_title="온도 (℃)",
        legend_title="기온 구분",
        hovermode="x unified",
        height=600,
        template="plotly_white",
        xaxis=dict(
            showgrid=True,
            dtick=10
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=True
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # -----------------------------
    # 7. 주요 통계 표시
    # -----------------------------
    st.subheader("📊 선택한 월의 기온 통계")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "평균 최고기온",
            f"{monthly_df['최고기온(℃)'].mean():.1f}℃"
        )

    with col2:
        st.metric(
            "평균 최저기온",
            f"{monthly_df['최저기온(℃)'].mean():.1f}℃"
        )

    with col3:
        st.metric(
            "분석 연도 수",
            f"{monthly_df['연도'].nunique()}년"
        )

    # -----------------------------
    # 8. 데이터 표
    # -----------------------------
    with st.expander("연도별 상세 기온 데이터 보기"):
        result = monthly_df[
            ["연도", "최고기온(℃)", "최저기온(℃)"]
        ]

        st.dataframe(
            result,
            use_container_width=True,
            hide_index=True
        )

st.caption("데이터 출처: temperature.csv")
