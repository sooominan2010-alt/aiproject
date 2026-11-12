
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from pathlib import Path

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="월별 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 예측 프로그램")
st.write("과거 기온 데이터를 이용하여 선형회귀로 미래의 평균기온을 예측합니다.")

# -----------------------------
# CSV 파일 불러오기
# -----------------------------
def load_data():
    candidates = [
        Path("temperature.csv"),
        Path("temperature(1).csv")
    ]

    for path in candidates:
        if path.exists():
            for encoding in ["cp949", "utf-8-sig", "euc-kr"]:
                try:
                    return pd.read_csv(path, encoding=encoding)
                except UnicodeDecodeError:
                    continue

    return None


df = load_data()

if df is None:
    uploaded_file = st.file_uploader(
        "temperature.csv 파일을 업로드하세요.",
        type=["csv"]
    )

    if uploaded_file is None:
        st.warning("CSV 파일을 업로드하거나 저장소에 추가해 주세요.")
        st.stop()

    df = None
    for encoding in ["cp949", "utf-8-sig", "euc-kr"]:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        st.error("CSV 파일의 인코딩을 읽을 수 없습니다.")
        st.stop()

# -----------------------------
# 데이터 정리
# -----------------------------
required_columns = ["일시", "평균기온(℃)"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV에 '일시', '평균기온(℃)' 열이 필요합니다.")
    st.stop()

month_dict = {
    "Jan": 1, "Feb": 2, "Mar": 3,
    "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9,
    "Oct": 10, "Nov": 11, "Dec": 12
}

month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

# 날짜가 Oct-07 형태이므로 데이터 순서를 이용해
# 1907년부터 연도를 연속적으로 복원
dates = []
current_year = None
previous_month = None

for value in df["일시"]:
    try:
        month_text, year_text = str(value).strip().split("-")
        month = month_dict[month_text.title()]
        short_year = int(year_text)

        if current_year is None:
            current_year = 1900 + short_year
        elif month <= previous_month:
            current_year += 1

        dates.append((current_year, month))
        previous_month = month

    except (ValueError, KeyError):
        dates.append((None, None))

df["연도"] = [x[0] for x in dates]
df["월"] = [x[1] for x in dates]

df["평균기온(℃)"] = pd.to_numeric(
    df["평균기온(℃)"], errors="coerce"
)

df = df.dropna(
    subset=["연도", "월", "평균기온(℃)"]
).copy()

df["연도"] = df["연도"].astype(int)
df["월"] = df["월"].astype(int)

# -----------------------------
# 사용자 입력
# -----------------------------
st.subheader("🔍 예측 조건 선택")

col1, col2 = st.columns(2)

with col1:
    selected_month_name = st.selectbox(
        "예측할 월을 선택하세요.",
        list(month_names.values()),
        index=0
    )

with col2:
    selected_year = st.number_input(
        "예측할 연도를 입력하세요.",
        min_value=int(df["연도"].min()),
        max_value=2200,
        value=int(df["연도"].max()) + 1,
        step=1
    )

selected_month = {
    value: key for key, value in month_names.items()
}[selected_month_name]

# -----------------------------
# 선택한 월의 데이터 추출
# -----------------------------
month_df = df[df["월"] == selected_month].copy()

month_df = (
    month_df.groupby("연도", as_index=False)["평균기온(℃)"]
    .mean()
    .sort_values("연도")
)

if len(month_df) < 2:
    st.error("예측하려면 해당 월의 데이터가 최소 2개 이상 필요합니다.")
    st.stop()

X = month_df[["연도"]]
y = month_df["평균기온(℃)"]

# -----------------------------
# 선형회귀 학습
# -----------------------------
model = LinearRegression()
model.fit(X, y)

prediction = model.predict(
    pd.DataFrame({"연도": [int(selected_year)]})
)[0]

# 회귀선 계산
line_years = np.arange(
    int(month_df["연도"].min()),
    max(int(selected_year), int(month_df["연도"].max())) + 1
)

line_temps = model.predict(
    pd.DataFrame({"연도": line_years})
)

# -----------------------------
# 예측 결과
# -----------------------------
st.divider()
st.subheader(f"📊 {selected_month_name} 평균기온 예측 결과")

col1, col2, col3 = st.columns(3)

col1.metric(
    "예측 연도",
    f"{int(selected_year)}년"
)

col2.metric(
    "예측 평균기온",
    f"{prediction:.1f} ℃"
)

col3.metric(
    "과거 데이터 개수",
    f"{len(month_df)}개"
)

# -----------------------------
# 그래프
# -----------------------------
fig = go.Figure()

# 실제 관측 데이터
fig.add_trace(go.Scatter(
    x=month_df["연도"],
    y=month_df["평균기온(℃)"],
    mode="markers",
    name="실제 평균기온",
    marker=dict(size=7, color="royalblue"),
    hovertemplate="%{x}년<br>평균기온: %{y:.1f}℃<extra></extra>"
))

# 실제값과 회귀선 사이의 차이(잔차)
fitted = model.predict(X)

for year, actual, fitted_value in zip(
    month_df["연도"], y, fitted
):
    fig.add_trace(go.Scatter(
        x=[year, year],
        y=[actual, fitted_value],
        mode="lines",
        line=dict(color="lightgray", width=1),
        showlegend=False,
        hoverinfo="skip"
    ))

# 선형회귀 직선
fig.add_trace(go.Scatter(
    x=line_years,
    y=line_temps,
    mode="lines",
    name="선형회귀 예측선",
    line=dict(color="red", width=3)
))

# 미래 예측값
fig.add_trace(go.Scatter(
    x=[int(selected_year)],
    y=[prediction],
    mode="markers+text",
    name="미래 예측 기온",
    marker=dict(size=15, color="orange", symbol="star"),
    text=[f"{prediction:.1f}℃"],
    textposition="top center"
))

fig.update_layout(
    title=f"{selected_month_name} 연도별 평균기온 및 미래 예측",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    hovermode="closest",
    template="plotly_white",
    height=600,
    legend=dict(orientation="h", y=1.12),
    xaxis=dict(showgrid=True),
    yaxis=dict(showgrid=True)
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 선형회귀 알고리즘 설명
# -----------------------------
st.divider()

st.subheader("📚 선형회귀 알고리즘이란?")

st.write("""
선형회귀는 과거에 수집한 데이터를 바탕으로
두 변수 사이의 관계를 직선으로 나타내고,
그 관계를 이용하여 새로운 값을 예측하는 알고리즘입니다.
""")

st.latex(r"y = ax + b")

st.write("""
- x : 연도
- y : 평균기온
- a : 기온이 변화하는 기울기
- b : 직선의 시작 위치를 결정하는 절편

컴퓨터는 과거의 실제 평균기온과 직선으로 계산한 기온의
차이가 전체적으로 가장 작아지도록 기울기와 절편을 학습합니다.
""")

st.subheader("📈 그래프 보는 방법")

st.markdown("""
1. **파란색 점** : 과거에 실제로 관측된 평균기온입니다.
2. **빨간색 직선** : 과거 데이터를 학습하여 만든 선형회귀 직선입니다.
3. **회색 세로선** : 실제 기온과 회귀 직선이 예측한 기온 사이의 차이입니다.
4. **주황색 별** : 사용자가 입력한 미래 연도의 예측 평균기온입니다.

회귀 직선은 실제 관측값과의 차이(잔차 제곱합)가
가장 작아지는 방향으로 결정됩니다.
""")

# -----------------------------
# 학습 결과 추가 설명
# -----------------------------
st.subheader("🔬 선형회귀 학습 결과")

st.write(
    f"**기울기:** {model.coef_[0]:.4f} ℃/년"
)

st.write(
    f"**절편:** {model.intercept_:.2f}"
)

st.write(
    f"**결정계수(R²):** {model.score(X, y):.4f}"
)

st.write(
    f"**예측 결과:** {selected_year}년 "
    f"{selected_month_name}의 평균기온은 "
    f"약 {prediction:.1f}℃로 예측됩니다."
)

st.caption(
    "※ 이 결과는 과거 데이터의 선형적인 추세를 바탕으로 한 "
    "통계적 예측이며 실제 기온과 다를 수 있습니다. "
    "특히 먼 미래로 갈수록 예측 오차가 커질 수 있습니다."
)
