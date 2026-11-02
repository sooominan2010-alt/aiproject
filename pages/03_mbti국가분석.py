
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import io

# -------------------------
# 페이지 설정
# -------------------------
st.set_page_config(
    page_title="국가별 MBTI 분석",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 국가별 MBTI 비율 분석")
st.write("국가를 선택하고 16가지 MBTI 유형의 비율을 그래프로 확인해 보세요.")

# -------------------------
# CSV 파일 불러오기
# -------------------------
CSV_FILE = Path(__file__).parent / "countriesMBTI_16types.csv"

@st.cache_data
def load_data(file_bytes):
    data = pd.read_csv(io.BytesIO(file_bytes))
    data.columns = data.columns.str.strip()

    if "Country" not in data.columns:
        raise ValueError(
            "CSV 파일에 Country 열이 없습니다. "
            "올바른 국가별 MBTI CSV 파일인지 확인해 주세요."
        )

    # MBTI 16가지 유형
    mbti_types = [
        "ISTJ", "ISFJ", "INFJ", "INTJ",
        "ISTP", "ISFP", "INFP", "INTP",
        "ESTP", "ESFP", "ENFP", "ENTP",
        "ESTJ", "ESFJ", "ENFJ", "ENTJ"
    ]

    # CSV에 실제로 존재하는 MBTI 열만 사용
    mbti_columns = [
        col for col in mbti_types if col in data.columns
    ]

    if not mbti_columns:
        raise ValueError("MBTI 유형 열을 찾을 수 없습니다.")

    for col in mbti_columns:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(subset=["Country"])
    data["Country"] = data["Country"].astype(str).str.strip()

    return data, mbti_columns


# 저장소에 CSV가 있으면 자동으로 읽고,
# 없으면 웹페이지에서 직접 업로드
if CSV_FILE.exists():
    try:
        df, mbti_columns = load_data(CSV_FILE.read_bytes())
    except Exception as e:
        st.error(f"CSV 파일을 읽을 수 없습니다: {e}")
        st.stop()
else:
    st.warning(
        "저장소에서 CSV 파일을 찾지 못했습니다. "
        "아래에서 파일을 업로드해 주세요."
    )

    uploaded_file = st.file_uploader(
        "countriesMBTI_16types.csv 업로드",
        type=["csv"]
    )

    if uploaded_file is None:
        st.info("CSV 파일을 업로드하면 분석 화면이 나타납니다.")
        st.stop()

    try:
        df, mbti_columns = load_data(uploaded_file.getvalue())
    except Exception as e:
        st.error(f"CSV 파일을 읽을 수 없습니다: {e}")
        st.stop()


# -------------------------
# 국가 선택
# -------------------------
countries = sorted(df["Country"].unique())

if len(countries) == 0:
    st.error("CSV 파일에 국가 데이터가 없습니다.")
    st.stop()

selected_country = st.selectbox(
    "🌐 국가를 선택하세요",
    countries
)

# 선택한 국가의 데이터
country_data = df[
    df["Country"] == selected_country
].iloc[0]

chart_df = pd.DataFrame({
    "MBTI": mbti_columns,
    "비율": [
        country_data[col] for col in mbti_columns
    ]
})

chart_df = chart_df.dropna(subset=["비율"])

if chart_df.empty:
    st.error("선택한 국가의 MBTI 비율 데이터가 없습니다.")
    st.stop()

# -------------------------
# 비율을 퍼센트로 변환
# -------------------------
# 데이터가 0~1 형식이면 100을 곱함
# 이미 퍼센트 형식이면 그대로 사용
if chart_df["비율"].max() <= 1:
    chart_df["비율(%)"] = chart_df["비율"] * 100
else:
    chart_df["비율(%)"] = chart_df["비율"]

# 높은 비율부터 정렬
chart_df = chart_df.sort_values(
    "비율(%)",
    ascending=False
).reset_index(drop=True)

# -------------------------
# 그래프 색상 설정
# -------------------------
# 1위는 빨간색
# 나머지는 진한 파란색에서 연한 파란색
blue_gradient = [
    "#08519C",
    "#2171B5",
    "#3182BD",
    "#4292C6",
    "#529FCC",
    "#6BAED6",
    "#7BB6D9",
    "#8FC2E0",
    "#9ECAE1",
    "#A6CEE3",
    "#B3D4E8",
    "#BDD7E7",
    "#C6DBEF",
    "#D0E1F2",
    "#DEEBF7"
]

colors = ["#E53935"]

for i in range(1, len(chart_df)):
    colors.append(blue_gradient[(i - 1) % len(blue_gradient)])

# -------------------------
# 막대그래프 생성
# -------------------------
fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=chart_df["MBTI"],
        y=chart_df["비율(%)"],
        marker_color=colors,
        text=[
            f"{value:.2f}%"
            for value in chart_df["비율(%)"]
        ],
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "MBTI: %{x}<br>"
            "비율: %{y:.2f}%"
            "<extra></extra>"
        )
    )
)

fig.update_layout(
    title=f"{selected_country}의 MBTI 유형별 비율",
    xaxis_title="MBTI 유형",
    yaxis_title="비율 (%)",
    yaxis=dict(
        rangemode="tozero"
    ),
    showlegend=False,
    height=550,
    margin=dict(t=80, b=50, l=40, r=30)
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------
# 1위 MBTI 표시
# -------------------------
top = chart_df.iloc[0]

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "🏆 비율 1위 MBTI",
        top["MBTI"]
    )

with col2:
    st.metric(
        "📊 1위 비율",
        f'{top["비율(%)"]:.2f}%'
    )

# -------------------------
# 전체 비율 표
# -------------------------
with st.expander("📋 전체 MBTI 비율 확인하기"):
    display_df = chart_df[["MBTI", "비율(%)"]].copy()

    display_df["비율(%)"] = display_df["비율(%)"].map(
        lambda x: f"{x:.2f}%"
    )

    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True
    )

# -------------------------
# CSV 다운로드
# -------------------------
st.download_button(
    label="📥 데이터 다운로드",
    data=df.to_csv(index=False).encode("utf-8-sig"),
    file_name="countriesMBTI_16types.csv",
    mime="text/csv"
)

st.caption(
    "※ 그래프는 제공된 CSV 데이터에 기반합니다. "
    "실제 국가 전체 인구의 MBTI 분포와 다를 수 있습니다."
)
