
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import re

# -----------------------------
# 1. 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온분석")
st.write("월을 선택하여 전체 연도별 최고기온과 최저기온을 비교해 보세요.")

# -----------------------------
# 2. CSV 파일 자동 찾기
# -----------------------------
def find_csv():
    current = Path(__file__).resolve().parent

    search_paths = [
        current / "temperature.csv",
        current.parent / "temperature.csv",
        current.parent.parent / "temperature.csv",
        Path.cwd() / "temperature.csv",
        Path.cwd() / "pages" / "temperature.csv"
    ]

    for path in search_paths:
        if path.is_file():
            return path

    return None


# -----------------------------
# 3. CSV 한글 인코딩 처리
# -----------------------------
@st.cache_data
def load_data(file_bytes):
    from io import BytesIO

    for encoding in ["cp949", "utf-8-sig", "utf-8"]:
        try:
            return pd.read_csv(
                BytesIO(file_bytes),
                encoding=encoding
            )
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 인코딩을 확인할 수 없습니다.")


# 자동으로 CSV 찾기
csv_path = find_csv()

if csv_path is not None:
    with open(csv_path, "rb") as f:
        df = load_data(f.read())

else:
    st.warning(
        "저장소에서 temperature.csv를 찾지 못했습니다. "
        "CSV 파일이 GitHub 저장소에 업로드되어 있는지 확인해 주세요."
    )

    uploaded_file = st.file_uploader(
        "temperature.csv 업로드",
        type=["csv"]
    )

    if uploaded_file is None:
        st.stop()

    df = load_data(uploaded_file.getvalue())


# -----------------------------
# 4. 데이터 확인
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


# -----------------------------
# 5. 날짜에서 연도와 월 추출
# -----------------------------
month_map = {
    "Jan": 1, "Feb": 2, "Mar": 3,
    "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9,
    "Oct": 10, "Nov": 11, "Dec": 12
}

parsed_dates = []

# 원본 데이터가 시간순으로 정렬된 경우
# 1907년부터 1999년, 2000년 이후까지 처리
century = 1900
previous_year = None

for value in df["일시"]:
    match = re.fullmatch(
        r"\s*([A-Za-z]{3})-(\d{2})\s*",
        str(value)
    )

    if match is None:
        parsed_dates.append((None, None))
        continue

    month_text = match.group(1).title()
    short_year = int(match.group(2))

    if month_text not in month_map:
        parsed_dates.append((None, None))
        continue

    if (
        previous_year is not None
        and previous_year - short_year > 50
    ):
        century += 100

    year = century + short_year
    month = month_map[month_text]

    parsed_dates.append((year, month))
    previous_year = short_year

df["연도"] = [x[0] for x in parsed_dates]
df["월"] = [x[1] for x in parsed_dates]

df = df.dropna(
    subset=["연도", "월"]
).copy()

df["연도"] = df["연도"].astype(int)
df["월"] = df["월"].astype(int)


# -----------------------------
# 6. 월 선택
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
    format_func=lambda x: month_names[x]
)


# -----------------------------
# 7. 선택 월 데이터 분석
# -----------------------------
monthly_df = df[
    df["월"] == selected_month
].copy()

monthly_df = monthly_df.sort_values("연도")

if monthly_df.empty:
    st.warning("선택한 월의 데이터가 없습니다.")

else:

    # -----------------------------
    # 8. 그래프 생성
    # -----------------------------
    fig = go.Figure()

    # 최고기온 - 핫핑크
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

    # 최저기온 - 하늘색
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
        title=dict(
            text="월별 기온분석",
            x=0.5,
            xanchor="center"
        ),
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
    # 9. 통계 정보
    # -----------------------------
    st.subheader("📊 기온 통계")

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
    # 10. 상세 데이터
    # -----------------------------
    st.subheader("📋 연도별 상세 데이터")

    result = monthly_df[
        ["연도", "최고기온(℃)", "최저기온(℃)"]
    ].copy()

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )

st.caption("기온 데이터 분석 | Pandas & Plotly")
