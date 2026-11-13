
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="붓꽃 품종 예측 AI",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 AI 붓꽃 품종 예측 프로그램")
st.write("꽃잎의 길이와 너비를 입력하고 3가지 머신러닝 알고리즘으로 품종을 예측해 보세요.")

# -----------------------------
# 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("Iris.csv", encoding="cp949")
    except UnicodeDecodeError:
        data = pd.read_csv("Iris.csv", encoding="utf-8-sig")

    # 열 이름 자동 정리
    data.columns = data.columns.str.strip()

    return data

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터 파일을 불러오지 못했습니다: {e}")
    st.stop()

# 실제 CSV 열 이름에 맞게 설정
column_map = {
    "꽃잎 길이": ["꽃잎 길이", "PetalLengthCm", "petal_length"],
    "꽃잎 너비": ["꽃잎 너비", "PetalWidthCm", "petal_width"],
    "품종": ["품종", "Species", "species"]
}

def find_column(candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None

length_col = find_column(column_map["꽃잎 길이"])
width_col = find_column(column_map["꽃잎 너비"])
species_col = find_column(column_map["품종"])

if not all([length_col, width_col, species_col]):
    st.error("CSV의 열 이름을 확인해 주세요.")
    st.write("현재 CSV 열 이름:", list(df.columns))
    st.stop()

df = df[[length_col, width_col, species_col]].copy()
df.columns = ["꽃잎 길이", "꽃잎 너비", "품종"]

df["꽃잎 길이"] = pd.to_numeric(df["꽃잎 길이"], errors="coerce")
df["꽃잎 너비"] = pd.to_numeric(df["꽃잎 너비"], errors="coerce")
df = df.dropna()

X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

# -----------------------------
# 알고리즘 설명
# -----------------------------
st.divider()
st.subheader("🤖 사용할 머신러닝 알고리즘 선택")

algorithm = st.selectbox(
    "예측에 사용할 알고리즘을 선택하세요.",
    [
        "KNN (K-최근접 이웃)",
        "Random Forest (랜덤 포레스트)",
        "SVM (서포트 벡터 머신)"
    ]
)

descriptions = {
    "KNN (K-최근접 이웃)": """
    **K-최근접 이웃 알고리즘**

    - 입력한 꽃과 기존 꽃 데이터 사이의 거리를 계산합니다.
    - 가장 가까운 데이터 5개를 찾습니다.
    - 5개 중 가장 많이 등장한 품종으로 분류합니다.

    **예시:** 주변 5개 중 Versicolor가 4개라면 Versicolor로 예측합니다.
    """,

    "Random Forest (랜덤 포레스트)": """
    **랜덤 포레스트 알고리즘**

    - 여러 개의 결정 트리를 만들어 학습합니다.
    - 각 결정 트리가 입력한 꽃의 품종을 예측합니다.
    - 여러 트리의 예측 결과를 종합해 최종 품종을 결정합니다.

    **예시:** 100개의 결정 트리 중 가장 많은 표를 받은 품종을 선택합니다.
    """,

    "SVM (서포트 벡터 머신)": """
    **서포트 벡터 머신 알고리즘**

    - 서로 다른 품종을 구분하는 경계를 학습합니다.
    - 품종 사이의 구분이 가장 잘 이루어지는 경계를 찾습니다.
    - 새로운 꽃이 어느 영역에 위치하는지 판단합니다.

    **예시:** 입력한 꽃이 학습한 분류 경계 중 어느 품종 영역에 속하는지 예측합니다.
    """
}

with st.expander("📚 선택한 알고리즘의 원리 알아보기", expanded=True):
    st.markdown(descriptions[algorithm])

# -----------------------------
# 모델 생성
# -----------------------------
if algorithm == "KNN (K-최근접 이웃)":
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", KNeighborsClassifier(n_neighbors=5))
    ])

elif algorithm == "Random Forest (랜덤 포레스트)":
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

else:
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", SVC(
            kernel="rbf",
            C=1.0,
            probability=True,
            random_state=42
        ))
    ])

model.fit(X, y)

# -----------------------------
# 데이터 정보
# -----------------------------
st.divider()
st.subheader("📊 학습 데이터 정보")

c1, c2, c3 = st.columns(3)
c1.metric("전체 데이터", f"{len(df)}개")
c2.metric("붓꽃 품종", f"{y.nunique()}종")
c3.metric("선택 알고리즘", algorithm.split(" (")[0])

st.write("**입력 가능한 범위**")
r1, r2 = st.columns(2)
r1.info("꽃잎 길이: 1.0 ~ 6.9 cm")
r2.info("꽃잎 너비: 0.1 ~ 2.5 cm")

# -----------------------------
# 사용자 입력
# -----------------------------
st.divider()
st.subheader("✏️ 꽃잎 크기 입력")

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "꽃잎 길이 (cm)",
        min_value=1.0,
        max_value=6.9,
        value=4.5,
        step=0.1
    )

with col2:
    petal_width = st.number_input(
        "꽃잎 너비 (cm)",
        min_value=0.1,
        max_value=2.5,
        value=1.3,
        step=0.1
    )

user_data = pd.DataFrame({
    "꽃잎 길이": [petal_length],
    "꽃잎 너비": [petal_width]
})

# -----------------------------
# 예측 결과
# -----------------------------
prediction = model.predict(user_data)[0]
probabilities = model.predict_proba(user_data)[0]

st.divider()
st.subheader("🔍 품종 예측 결과")

st.success(f"🌸 예측된 품종: {prediction}")

a, b = st.columns(2)
a.metric("꽃잎 길이", f"{petal_length:.1f} cm")
b.metric("꽃잎 너비", f"{petal_width:.1f} cm")

# 확률 표시
st.write("### 품종별 예측 확률")

prob_df = pd.DataFrame({
    "품종": model.classes_,
    "예측 확률": probabilities
}).sort_values("예측 확률", ascending=False)

st.bar_chart(
    prob_df.set_index("품종"),
    y="예측 확률"
)

for _, row in prob_df.iterrows():
    st.write(f"{row['품종']}: {row['예측 확률']:.1%}")

# -----------------------------
# 그래프 시각화
# -----------------------------
st.divider()
st.subheader("📈 품종 분류 그래프")

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

species = list(model.classes_)
colors = ["#F4A261", "#6495ED", "#B07CC6"]

color_map = {
    name: colors[i % len(colors)]
    for i, name in enumerate(species)
}

Z_num = pd.Categorical(
    Z,
    categories=species
).codes.reshape(xx.shape)

fig, ax = plt.subplots(figsize=(11, 7))

ax.contourf(
    xx,
    yy,
    Z_num,
    levels=np.arange(-0.5, len(species) + 0.5, 1),
    colors=[color_map[s] for s in species],
    alpha=0.15
)

# 기존 데이터 표시
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

# 사용자 입력값
ax.scatter(
    petal_length,
    petal_width,
    marker="*",
    s=500,
    color="green",
    edgecolors="black",
    linewidths=1.2,
    label="사용자 입력값",
    zorder=10
)

ax.set_xlabel("꽃잎 길이 (cm)")
ax.set_ylabel("꽃잎 너비 (cm)")
ax.set_title(f"{algorithm} 품종 분류 결과")
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)
ax.grid(alpha=0.2)
ax.legend()

st.pyplot(fig)
plt.close(fig)

st.info(
    "그래프의 배경색은 선택한 알고리즘이 각 위치에서 "
    "예측하는 품종을 나타냅니다. 초록색 별은 입력한 꽃의 위치입니다."
)

# -----------------------------
# 가장 가까운 데이터 분석
# -----------------------------
st.divider()
st.subheader("🔎 입력값과 기존 데이터 비교")

# 표준화한 거리로 최근접 이웃 계산
scaler = StandardScaler()
scaled_X = scaler.fit_transform(X)
scaled_user = scaler.transform(user_data)

distances = np.sqrt(
    np.sum((scaled_X - scaled_user) ** 2, axis=1)
)

neighbor_indices = np.argsort(distances)[:5]

neighbors = df.iloc[neighbor_indices].copy()
neighbors["거리"] = distances[neighbor_indices]

st.write("입력한 꽃과 가장 가까운 데이터 5개입니다.")

st.dataframe(
    neighbors.reset_index(drop=True).round(3),
    use_container_width=True
)

# -----------------------------
# 알고리즘별 결과 비교
# -----------------------------
st.divider()
st.subheader("⚖️ 3가지 알고리즘 예측 결과 비교")

models = {
    "KNN": Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", KNeighborsClassifier(n_neighbors=5))
    ]),
    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        random_state=42
    ),
    "SVM": Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", SVC(
            kernel="rbf",
            probability=True,
            random_state=42
        ))
    ])
}

comparison = []

for name, comparison_model in models.items():
    comparison_model.fit(X, y)

    result = comparison_model.predict(user_data)[0]
    confidence = comparison_model.predict_proba(user_data)[0].max()

    comparison.append({
        "알고리즘": name,
        "예측 품종": result,
        "가장 높은 예측 확률": f"{confidence:.1%}"
    })

comparison_df = pd.DataFrame(comparison)

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "예측 확률은 각 모델의 추정값이며, 실제 정답일 확률을 보장하지 않습니다."
)

# -----------------------------
# 마무리 설명
# -----------------------------
st.divider()

with st.expander("💡 세 가지 알고리즘 비교 정리"):
    st.markdown("""
    | 알고리즘 | 예측 원리 | 장점 |
    |---|---|---|
    | KNN | 가까운 데이터 비교 | 원리가 간단함 |
    | 랜덤 포레스트 | 여러 결정 트리의 결과 종합 | 다양한 패턴 학습 |
    | SVM | 품종을 구분하는 경계 학습 | 복잡한 분류 경계에 활용 |

    **분석할 때 확인할 점**

    같은 꽃잎 크기를 입력해도 알고리즘에 따라
    예측 품종이나 예측 확률이 달라질 수 있습니다.

    이는 알고리즘마다 데이터를 학습하고 분류하는
    방법이 다르기 때문입니다.
    """)
