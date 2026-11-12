
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor

# =====================================
# 1. 페이지 설정
# =====================================

st.set_page_config(
    page_title="월별 평균기온 AI 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 AI 예측 프로그램")
st.write(
    "과거 기온 데이터를 활용하여 3가지 회귀 알고리즘으로 "
    "미래 평균기온을 예측합니다."
)

# =====================================
# 2. CSV 파일 불러오기
# =====================================

def load_data():
    files = [
        Path("temperature.csv"),
        Path("temperature(1).csv")
    ]

    for file in files:
        if file.exists():
            for encoding in ["cp949", "utf-8-sig", "euc-kr"]:
                try:
                    return pd.read_csv(file, encoding=encoding)
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
        st.warning("CSV 파일을 업로드해 주세요.")
        st.stop()

    for encoding in ["cp949", "utf-8-sig", "euc-kr"]:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(
                uploaded_file,
                encoding=encoding
            )
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        st.error("CSV 파일을 읽을 수 없습니다.")
        st.stop()


# =====================================
# 3. 데이터 정리
# =====================================

required_columns = ["일시", "평균기온(℃)"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV에 필요한 열이 없습니다.")
    st.stop()

# Oct-07 형태의 날짜를 실제 날짜로 변환
df["날짜"] = pd.to_datetime(
    df["일시"],
    format="%b-%y",
    errors="coerce"
)

df["연도"] = df["날짜"].dt.year
df["월"] = df["날짜"].dt.month

df["평균기온(℃)"] = pd.to_numeric(
    df["평균기온(℃)"],
    errors="coerce"
)

df = df.dropna(
    subset=["연도", "월", "평균기온(℃)"]
).copy()

df["연도"] = df["연도"].astype(int)
df["월"] = df["월"].astype(int)

month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}


# =====================================
# 4. 사용자 입력
# =====================================

st.divider()
st.subheader("🔍 예측 조건 선택")

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "예측할 월 선택",
        list(month_names.keys()),
        format_func=lambda x: month_names[x]
    )

with col2:
    latest_year = int(df["연도"].max())

    selected_year = st.number_input(
        "예측할 연도 입력",
        min_value=latest_year + 1,
        max_value=2200,
        value=latest_year + 1,
        step=1
    )


# =====================================
# 5. 알고리즘 선택
# =====================================

st.subheader("🤖 회귀 알고리즘 선택")

algorithm_options = [
    "선형회귀 (Linear Regression)",
    "다항회귀 (Polynomial Regression)",
    "랜덤 포레스트 회귀 (Random Forest)"
]

selected_algorithm = st.selectbox(
    "사용할 예측 알고리즘을 선택하세요.",
    algorithm_options
)

st.info(
    "아래 그래프에는 세 가지 알고리즘의 예측 결과가 "
    "모두 표시됩니다. 선택한 알고리즘은 굵은 선으로 강조됩니다."
)


# =====================================
# 6. 선택한 월의 데이터 추출
# =====================================

month_df = df[df["월"] == selected_month].copy()

month_df = (
    month_df.groupby("연도", as_index=False)
    ["평균기온(℃)"].mean()
    .sort_values("연도")
)

if len(month_df) < 3:
    st.error("예측에 필요한 과거 데이터가 부족합니다.")
    st.stop()

X = month_df[["연도"]].values
y = month_df["평균기온(℃)"].values

future_X = np.array([[int(selected_year)]])


# =====================================
# 7. 세 가지 회귀 알고리즘 생성
# =====================================

models = {

    "선형회귀 (Linear Regression)": LinearRegression(),

    "다항회귀 (Polynomial Regression)": make_pipeline(
        PolynomialFeatures(
            degree=2,
            include_bias=False
        ),
        LinearRegression()
    ),

    "랜덤 포레스트 회귀 (Random Forest)": RandomForestRegressor(
        n_estimators=300,
        max_depth=5,
        min_samples_leaf=2,
        random_state=42
    )
}


# =====================================
# 8. 알고리즘 학습 및 예측
# =====================================

results = {}

for name, model in models.items():

    model.fit(X, y)

    prediction = model.predict(future_X)[0]

    train_score = model.score(X, y)

    results[name] = {
        "model": model,
        "prediction": prediction,
        "r2": train_score
    }


# 선택한 알고리즘의 결과
selected_result = results[selected_algorithm]

prediction = selected_result["prediction"]


# =====================================
# 9. 예측 결과 표시
# =====================================

st.divider()

st.subheader(
    f"📊 {int(selected_year)}년 {month_names[selected_month]} 예측 결과"
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "선택한 알고리즘",
    selected_algorithm.split(" (")[0]
)

col2.metric(
    "예측 평균기온",
    f"{prediction:.2f} ℃"
)

col3.metric(
    "과거 데이터 수",
    f"{len(month_df)}개"
)


# =====================================
# 10. 그래프 그리기
# =====================================

fig = go.Figure()

# 실제 관측 데이터
fig.add_trace(go.Scatter(
    x=month_df["연도"],
    y=month_df["평균기온(℃)"],
    mode="markers",
    name="실제 평균기온",
    marker=dict(
        size=8,
        color="royalblue"
    )
))

# 회귀선 생성
line_years = np.arange(
    int(month_df["연도"].min()),
    int(selected_year) + 1
).reshape(-1, 1)

# 알고리즘별 색상
colors = {
    "선형회귀 (Linear Regression)": "red",
    "다항회귀 (Polynomial Regression)": "green",
    "랜덤 포레스트 회귀 (Random Forest)": "purple"
}

# 알고리즘별 회귀선과 미래 예측점
for name, result in results.items():

    model = result["model"]

    line_predictions = model.predict(line_years)

    is_selected = name == selected_algorithm

    # 회귀선
    fig.add_trace(go.Scatter(
        x=line_years.flatten(),
        y=line_predictions,
        mode="lines",
        name=name,
        line=dict(
            color=colors[name],
            width=4 if is_selected else 2,
            dash="solid" if is_selected else "dash"
        )
    ))

    # 미래 예측 지점
    fig.add_trace(go.Scatter(
        x=[int(selected_year)],
        y=[result["prediction"]],
        mode="markers+text",
        name=f"{name} 예측값",
        marker=dict(
            size=15 if is_selected else 10,
            color=colors[name],
            symbol="star" if is_selected else "circle"
        ),
        text=[
            f"{result['prediction']:.2f}℃"
            if is_selected else ""
        ],
        textposition="top center",
        showlegend=True
    ))


fig.update_layout(
    title=f"{month_names[selected_month]} 평균기온 회귀 알고리즘 비교",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    height=650,
    template="plotly_white",
    hovermode="closest",
    legend=dict(
        orientation="h",
        y=1.15
    ),
    xaxis=dict(showgrid=True),
    yaxis=dict(showgrid=True)
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# =====================================
# 11. 알고리즘별 예측값 비교
# =====================================

st.divider()

st.subheader("🏆 알고리즘별 예측 기온 비교")

comparison_data = []

for name, result in results.items():

    comparison_data.append({
        "알고리즘": name,
        "예측 평균기온(℃)": round(
            result["prediction"], 2
        ),
        "학습 데이터 R²": round(
            result["r2"], 4
        )
    })

comparison_df = pd.DataFrame(comparison_data)

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)


# 비교 막대그래프
bar_fig = go.Figure()

bar_fig.add_trace(go.Bar(
    x=[
        name.split(" (")[0]
        for name in comparison_df["알고리즘"]
    ],
    y=comparison_df["예측 평균기온(℃)"],
    text=[
        f"{value:.2f}℃"
        for value in comparison_df["예측 평균기온(℃)"]
    ],
    textposition="outside"
))

bar_fig.update_layout(
    title="알고리즘별 미래 평균기온 비교",
    xaxis_title="회귀 알고리즘",
    yaxis_title="예측 평균기온 (℃)",
    template="plotly_white",
    height=400
)

st.plotly_chart(
    bar_fig,
    use_container_width=True
)


# =====================================
# 12. 선택한 알고리즘 설명
# =====================================

st.divider()

st.subheader("📚 선택한 회귀 알고리즘 알아보기")

if selected_algorithm == algorithm_options[0]:

    st.markdown("""
    ### 선형회귀 (Linear Regression)

    과거 데이터의 전체적인 변화 추세를 직선으로 나타내는 방법입니다.

    **핵심 원리**

    - 연도와 평균기온 사이의 관계를 학습합니다.
    - 실제 기온과 직선으로 예측한 기온의 차이를 줄입니다.
    - 가장 적합한 직선을 찾아 미래 기온을 예측합니다.
    """)

    st.latex(r"y = ax + b")

    st.write("""
    a는 기울기, b는 절편입니다.
    기울기가 양수이면 전체적인 기온 상승 경향,
    음수이면 하락 경향을 의미합니다.
    """)

elif selected_algorithm == algorithm_options[1]:

    st.markdown("""
    ### 다항회귀 (Polynomial Regression)

    직선이 아닌 곡선 형태로 데이터의 변화 추세를 학습하는 방법입니다.

    **핵심 원리**

    - 연도뿐만 아니라 연도의 제곱값도 활용합니다.
    - 기온의 곡선 형태 변화를 학습합니다.
    - 데이터의 비선형적인 패턴을 표현할 수 있습니다.
    """)

    st.latex(r"y = ax^2 + bx + c")

    st.write("""
    이번 프로그램은 2차 다항회귀를 사용합니다.
    곡선의 모양에 따라 선형회귀와 다른 예측값이 나올 수 있습니다.
    다만 먼 미래로 외삽하면 예측이 크게 달라질 수 있습니다.
    """)

elif selected_algorithm == algorithm_options[2]:

    st.markdown("""
    ### 랜덤 포레스트 회귀 (Random Forest)

    여러 개의 의사결정나무를 만들어 각 나무의 예측 결과를
    결합하는 머신러닝 알고리즘입니다.

    **핵심 원리**

    - 여러 의사결정나무가 데이터를 각각 학습합니다.
    - 각 나무가 예측한 결과를 모읍니다.
    - 여러 예측값의 평균을 이용하여 최종 결과를 만듭니다.
    """)

    st.latex(
        r"\hat{y} = \frac{1}{N}"
        r"\sum_{i=1}^{N} T_i(x)"
    )

    st.write("""
    N은 의사결정나무의 개수이고,
    T는 각각의 의사결정나무가 예측한 값입니다.

    이번 프로그램은 300개의 나무를 사용합니다.
    랜덤 포레스트는 학습 데이터 범위를 넘어서는 미래 연도에서
    마지막 구간의 예측값과 비슷한 결과를 낼 수 있습니다.
    """)


# =====================================
# 13. 알고리즘 비교 해석
# =====================================

st.divider()

st.subheader("🔎 예측 결과 분석")

predictions = {
    name: result["prediction"]
    for name, result in results.items()
}

highest_name = max(predictions, key=predictions.get)
lowest_name = min(predictions, key=predictions.get)

difference = (
    predictions[highest_name] -
    predictions[lowest_name]
)

st.write(
    f"- 가장 높은 예측값: **{highest_name}** "
    f"({predictions[highest_name]:.2f}℃)"
)

st.write(
    f"- 가장 낮은 예측값: **{lowest_name}** "
    f"({predictions[lowest_name]:.2f}℃)"
)

st.write(
    f"- 세 알고리즘의 예측값 차이: **{difference:.2f}℃**"
)

st.info(
    "알고리즘마다 데이터를 학습하는 방식이 다르기 때문에 "
    "같은 과거 기온 데이터를 사용하더라도 예측 결과가 달라집니다."
)

st.caption(
    "※ R²는 학습에 사용한 과거 데이터에 대한 설명력을 나타냅니다. "
    "미래 예측의 정확도를 직접 보장하는 수치는 아닙니다. "
    "특히 랜덤 포레스트는 과거 데이터 범위 밖의 기온 추세를 "
    "직선처럼 연장하지 못할 수 있습니다."
)
