
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="국가별 MBTI 비율",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 국가별 MBTI 비율")
st.write("국가를 선택하면 해당 국가의 MBTI 유형별 비율을 확인할 수 있습니다.")

# CSV 파일 불러오기
CSV_FILE = Path(__file__).parent / "countriesMBTI_16types.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_FILE)
    df.columns = df.columns.str.strip()

    if "Country" not in df.columns:
        raise ValueError("CSV 파일에 Country 열이 없습니다.")

    mbti_columns = [
        col for col in df.columns
        if col.strip().upper() in [
            "ISTJ", "ISFJ", "INFJ", "INTJ",
            "ISTP", "ISFP", "INFP", "INTP",
            "ESTP", "ESFP", "ENFP", "ENTP",
            "ESTJ", "ESFJ", "ENFJ", "ENTJ"
        ]
    ]

    if not mbti_columns:
        raise ValueError("CSV 파일에서 MBTI 열을 찾을 수 없습니다.")

    # 숫자로 변환
    for col in mbti_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Country"])
    return df, mbti_columns


try:
    df, mbti_columns = load_data()
except FileNotFoundError:
    st.error(
        "CSV 파일을 찾을 수 없습니다. "
        "app.py와 countriesMBTI_16types.csv를 "
        "같은 폴더에 넣어 주세요."
    )
    st.stop()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# 국가 선택
countries = sorted(df["Country"].astype(str).unique())

selected_country = st.selectbox(
    "국가 선택하기",
    countries
)

# 선택한 국가의 데이터 가져오기
country_data = df[
    df["Country"].astype(str) == selected_country
].iloc[0]

chart_df = pd.DataFrame({
    "MBTI": mbti_columns,
    "비율": [country_data[col] for col in mbti_columns]
})

chart_df = chart_df.dropna(subset=["비율"])

# 비율이 높은 순서대로 정렬
chart_df = chart_df.sort_values(
    by="비율",
    ascending=False
).reset_index(drop=True)

# 비율이 0~1 형식이면 퍼센트로 변환
if not chart_df.empty:
    if chart_df["비율"].max() <= 1:
        chart_df["비율(%)"] = chart_df["비율"] * 100
    else:
        chart_df["비율(%)"] = chart_df["비율"]

# 색상: 1위 빨간색, 나머지 파란색 그라데이션
blue_gradient = [
    "#08519C", "#2171B5", "#3182BD", "#4292C6",
    "#529FCC", "#6BAED6", "#7BB6D9", "#8FC2E0",
    "#9ECAE1", "#A6CEE3", "#B3D4E8", "#BDD7E7",
    "#C6DBEF", "#D0E1F2", "#DEEBF7"
]

colors = []
for i in range(len(chart_df)):
    if i == 0:
        colors.append("#E53935")
    else:
        colors.append(blue_gradient[(i - 1) % len(blue_gradient)])


# 막대그래프 만들기
fig = go.Figure(
    data=[
        go.Bar(
            x=chart_df["MBTI"],
            y=chart_df["비율(%)"],
            marker_color=colors,
            text=[
                f"{v:.2f}%"
                for v in chart_df["비율(%)"]
            ],
            textposition="outside",
            hovertemplate=(
                "MBTI: %{x}<br>"
                "비율: %{y:.2f}%"
                "<extra></extra>"
            )
        )
    ]
)

fig.update_layout(
    title=f"{selected_country}의 MBTI 유형별 비율",
    xaxis_title="MBTI 유형",
    yaxis_title="비율 (%)",
    yaxis=dict(rangemode="tozero"),
    showlegend=False,
    height=550
)

st.plotly_chart(fig, use_container_width=True)


# 1위 유형 표시
if not chart_df.empty:
    top = chart_df.iloc[0]

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "비율이 가장 높은 MBTI",
            top["MBTI"]
        )

    with col2:
        st.metric(
            "1위 비율",
            f'{top["비율(%)"]:.2f}%'
        )


# 전체 비율 표
with st.expander("전체 MBTI 비율 확인하기"):
    display_df = chart_df[["MBTI", "비율(%)"]].copy()
    display_df["비율(%)"] = display_df["비율(%)"].map(
        lambda x: f"{x:.2f}%"
    )

    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True
    )

st.caption(
    "※ 결과는 제공된 CSV 데이터에 기반하며, "
    "실제 국가 전체 인구의 분포와 다를 수 있습니다."
)
