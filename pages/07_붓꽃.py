
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 프로그램")
st.write(
    "꽃잎의 길이와 너비를 입력하면 "
    "머신러닝이 붓꽃의 품종을 예측합니다."
)

st.divider()

# -----------------------------
# 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("Iris.csv", encoding="cp949")
    except UnicodeDecodeError:
        data = pd.read_csv("Iris.csv", encoding="utf-8-sig")

    return data

try:
    df = load_data()
except FileNotFoundError:
    st.error("Iris.csv 파일을 찾을 수 없습니다.")
    st.stop()

# 필요한 열 확인
required_columns = ["꽃잎 길이", "꽃잎 너비", "품종"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름을 확인해 주세요.")
    st.stop()

df = df.dropna(subset=required_columns).copy()

X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

# -----------------------------
# KNN 모델 생성
# -----------------------------
model = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsClassifier(n_neighbors=5))
])

model.fit(X, y)

# -----------------------------
# 데이터 정보
# -----------------------------
st.subheader("📊 학습 데이터 정보")

col1, col2, col3 = st.columns(3)

col1.metric("전체 데이터", f"{len(df)}개")
col2.metric("분류 품종", f"{y.nunique()}종")
col3.metric("알고리즘", "KNN (K=5)")

st.info(
    "입력 범위는 실제 Iris 데이터의 꽃잎 측정값을 기준으로 설정했습니다."
)

st.write("**입력 가능한 범위**")
range1, range2 = st.columns(2)

range1.write("🌷 꽃잎 길이: 1.0 ~ 6.9 cm")
range2.write("🌷 꽃잎 너비: 0.1 ~ 2.5 cm")

st.divider()

# -----------------------------
# 사용자 입력
# -----------------------------
st.subheader("✏️ 꽃잎 크기 입력")

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "꽃잎 길이 (cm)",
        min_value=1.0,
        max_value=6.9,
        value=4.5,
        step=0.1,
        format="%.1f"
    )

with col2:
    petal_width = st.number_input(
        "꽃잎 너비 (cm)",
        min_value=0.1,
        max_value=2.5,
        value=1.3,
        step=0.1,
        format="%.1f"
    )

# -----------------------------
# 예측
# -----------------------------
user_data = pd.DataFrame({
    "꽃잎 길이": [petal_length],
    "꽃잎 너비": [petal_width]
})

prediction = model.predict(user_data)[0]

# 가장 가까운 이웃 5개 찾기
scaler = model.named_steps["scaler"]
knn = model.named_steps["knn"]

scaled_X = scaler.transform(X)
scaled_user = scaler.transform(user_data)

distances, indices = knn.kneighbors(
    scaled_user,
    n_neighbors=5
)

neighbors = df.iloc[indices[0]].copy()
neighbors["거리"] = distances[0]

vote_counts = neighbors["품종"].value_counts()

# -----------------------------
# 예측 결과
# -----------------------------
st.divider()
st.subheader("🔍 예측 결과")

st.success(f"예측된 붓꽃 품종: {prediction}")

result_col1, result_col2 = st.columns(2)

result_col1.metric("입력한 꽃잎 길이", f"{petal_length:.1f} cm")
result_col2.metric("입력한 꽃잎 너비", f"{petal_width:.1f} cm")

st.write("### 주변 데이터의 투표 결과")

vote_df = pd.DataFrame({
    "품종": vote_counts.index,
    "가까운 이웃 수": vote_counts.values
})

st.bar_chart(
    vote_df.set_index("품종"),
    y="가까운 이웃 수"
)

st.write(
    "KNN은 입력한 꽃과 가장 가까운 데이터 5개를 찾아 "
    "가장 많은 표를 받은 품종으로 분류합니다."
)

# -----------------------------
# 그래프 시각화
# -----------------------------
st.divider()
st.subheader("📈 꽃잎 크기와 품종 분포 시각화")

fig, ax = plt.subplots(figsize=(11, 7))

# 결정 영역 생성
x_min, x_max = 1.0, 6.9
y_min, y_max = 0.1, 2.5

xx, yy = np.meshgrid(
    np.linspace(x_min, x_max, 250),
    np.linspace(y_min, y_max, 250)
)

grid = pd.DataFrame({
    "꽃잎 길이": xx.ravel(),
    "꽃잎 너비": yy.ravel()
})

Z = model.predict(grid)

# 품종별 색상
species = list(y.unique())
colors = ["#F4A261", "#6495ED", "#B07CC6"]

color_map = {
    name: colors[i % len(colors)]
    for i, name in enumerate(species)
}

# 결정 영역 표시
Z_num = pd.Categorical(
    Z,
    categories=species
).codes.reshape(xx.shape)

ax.contourf(
    xx,
    yy,
    Z_num,
    levels=np.arange(-0.5, len(species) + 0.5, 1),
    colors=[color_map[s] for s in species],
    alpha=0.13
)

# 전체 붓꽃 데이터 표시
for name in species:
    subset = df[df["품종"] == name]

    ax.scatter(
        subset["꽃잎 길이"],
        subset["꽃잎 너비"],
        color=color_map[name],
        label=name,
        alpha=0.65,
        s=45
    )

# 가장 가까운 이웃 5개 강조
ax.scatter(
    neighbors["꽃잎 길이"],
    neighbors["꽃잎 너비"],
    s=180,
    facecolors="none",
    edgecolors="black",
    linewidths=1.5,
    label="가장 가까운 이웃 5개"
)

# 사용자가 입력한 값: 초록색 별
ax.scatter(
    petal_length,
    petal_width,
    marker="*",
    s=450,
    color="green",
    edgecolors="black",
    linewidths=1,
    label="내가 입력한 값",
    zorder=10
)

ax.set_xlabel("꽃잎 길이 (cm)", fontsize=12)
ax.set_ylabel("꽃잎 너비 (cm)", fontsize=12)
ax.set_title("KNN 붓꽃 품종 분류 결과", fontsize=16)

ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)

ax.grid(alpha=0.2)
ax.legend(loc="best")

st.pyplot(fig)
plt.close(fig)

# -----------------------------
# 분류 이유 분석
# -----------------------------
st.divider()
st.subheader("🧠 왜 이 품종으로 분류되었을까?")

st.write(
    f"입력한 꽃잎의 크기는 길이 {petal_length:.1f}cm, "
    f"너비 {petal_width:.1f}cm입니다."
)

st.write("가장 가까운 데이터 5개를 확인해 보겠습니다.")

display_neighbors = neighbors[
    ["꽃잎 길이", "꽃잎 너비", "품종", "거리"]
].copy()

display_neighbors["거리"] = display_neighbors["거리"].round(3)

st.dataframe(
    display_neighbors.reset_index(drop=True),
    use_container_width=True
)

st.write("### 품종별 투표 현황")

for name in species:
    count = int(vote_counts.get(name, 0))

    st.write(f"**{name}** : {count}표")
    st.progress(count / 5)

winner_count = int(vote_counts.max())

st.success(
    f"가장 가까운 5개 중 {winner_count}개가 "
    f"{prediction} 품종으로 분류되었습니다."
)

st.info(
    "그래프의 배경색은 KNN이 각 위치에서 예측하는 품종 영역입니다. "
    "초록색 별은 사용자가 입력한 꽃의 위치이며, "
    "검은색 테두리 원은 가장 가까운 데이터 5개입니다."
)

# -----------------------------
# 알고리즘 설명
# -----------------------------
with st.expander("💡 KNN 알고리즘이란?"):
    st.write("""
    KNN(K-Nearest Neighbors)은 K-최근접 이웃 알고리즘입니다.

    1. 새로운 꽃의 꽃잎 길이와 너비를 입력합니다.
    2. 기존 데이터와의 거리를 계산합니다.
    3. 가장 가까운 데이터 5개를 찾습니다.
    4. 가장 많이 등장한 품종을 예측 결과로 선택합니다.

    이번 프로그램은 꽃잎 길이와 너비의 단위 차이에 따른
    영향을 줄이기 위해 StandardScaler로 데이터를 표준화했습니다.
    """)

