
import streamlit as st
import pandas as pd
from pathlib import Path

# ==========================================
# 1. 기본 설정
# ==========================================

st.set_page_config(
    page_title="서울 부동산 취득 현황 분석",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 서울에서 부동산 취득이 가장 많은 지역은?")
st.write(
    "2014년 4분기부터 2018년 4분기까지 "
    "서울시 부동산 소유권 취득 현황을 분석합니다."
)

# ==========================================
# 2. CSV 파일 경로 설정
# ==========================================

# 현재 app.py는 pages 폴더 안에 있고
# CSV는 그 상위 폴더에 있음
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / (
    "부동산+소유권+취득+현황(2014~2018)_20261123112447(1).csv"
)

# ==========================================
# 3. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data(file=None):

    encodings = [
        "utf-8-sig",
        "utf-8",
        "cp949",
        "euc-kr"
    ]

    if file is not None:
        for encoding in encodings:
            try:
                file.seek(0)
                return pd.read_csv(file, encoding=encoding)
            except UnicodeDecodeError:
                continue

    elif DATA_FILE.exists():
        for encoding in encodings:
            try:
                return pd.read_csv(DATA_FILE, encoding=encoding)
            except UnicodeDecodeError:
                continue

    return None


uploaded_file = st.sidebar.file_uploader(
    "CSV 파일 업로드",
    type=["csv"]
)

try:
    df = load_data(uploaded_file)

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


if df is None:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.write("CSV 파일이 app.py의 상위 폴더에 있는지 확인해 주세요.")
    st.stop()


# ==========================================
# 4. 데이터 전처리
# ==========================================

df.columns = df.columns.astype(str).str.strip()

required_columns = [
    "자치구별(2)",
    "취득현황별(2)"
]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름이 예상한 형식과 다릅니다.")
    st.write("현재 열 이름:", df.columns.tolist())
    st.stop()


# 분기별 데이터 열 찾기
quarter_columns = [
    col for col in df.columns
    if "/" in col and str(col)[:4].isdigit()
]

if len(quarter_columns) == 0:
    st.error("연도별 분기 데이터를 찾을 수 없습니다.")
    st.stop()


# 지역명 및 유형명 정리
df["자치구별(2)"] = df["자치구별(2)"].astype("string").str.strip()
df["취득현황별(2)"] = df["취득현황별(2)"].astype("string").str.strip()


# 숫자 데이터 변환
for col in quarter_columns:

    df[col] = (
        df[col]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
        .replace({
            "-": "0",
            "": "0",
            "nan": "0"
        })
    )

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)


# 서울 전체 합계 행 제외
district_df = df[
    df["자치구별(2)"].notna()
    & (df["자치구별(2)"] != "소계")
].copy()


# ==========================================
# 5. 세로형 데이터로 변환
# ==========================================

data = district_df.melt(
    id_vars=[
        "자치구별(2)",
        "취득현황별(2)"
    ],
    value_vars=quarter_columns,
    var_name="연도분기",
    value_name="취득건수"
)

data = data.rename(columns={
    "자치구별(2)": "자치구",
    "취득현황별(2)": "소유자 유형"
})

data["연도"] = data["연도분기"].str[:4]
data["분기"] = data["연도분기"].str[-3:]


# ==========================================
# 6. 전체 순위 계산
# ==========================================

district_rank = (
    data.groupby("자치구")["취득건수"]
    .sum()
    .sort_values(ascending=False)
)

category_rank = (
    data.groupby("소유자 유형")["취득건수"]
    .sum()
    .sort_values(ascending=False)
)

total_count = int(data["취득건수"].sum())

top_district = district_rank.index[0]
top_count = int(district_rank.iloc[0])

lowest_district = district_rank.index[-1]
lowest_count = int(district_rank.iloc[-1])


# ==========================================
# 7. 전체 분석 요약
# ==========================================

st.divider()
st.subheader("📌 전체 분석 요약")

col1, col2, col3 = st.columns(3)

col1.metric(
    "분석 대상 자치구",
    f"{len(district_rank)}곳"
)

col2.metric(
    "취득 건수 1위",
    top_district
)

col3.metric(
    "전체 취득 건수",
    f"{total_count:,}건"
)


# ==========================================
# 8. 자치구별 TOP 10
# ==========================================

st.divider()
st.subheader("🏆 1. 부동산 취득 건수 TOP 10")

top10 = (
    district_rank.head(10)
    .sort_values(ascending=True)
)

st.bar_chart(
    top10,
    horizontal=True
)

st.caption(
    "2014년 4분기부터 2018년 4분기까지의 누적 취득 건수입니다."
)


# ==========================================
# 9. 25개 자치구 전체 순위
# ==========================================

st.divider()
st.subheader("📊 2. 서울 25개 자치구 전체 순위")

ranking = district_rank.reset_index()

ranking.columns = [
    "자치구",
    "취득 건수"
]

ranking.insert(
    0,
    "순위",
    range(1, len(ranking) + 1)
)

st.dataframe(
    ranking,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 10. 원하는 자치구 비교
# ==========================================

st.divider()
st.subheader("🔍 3. 자치구별 취득 건수 비교")

selected_districts = st.multiselect(
    "비교할 자치구를 선택하세요.",
    options=district_rank.index.tolist(),
    default=district_rank.head(5).index.tolist()
)

if selected_districts:

    compare_data = (
        data[data["자치구"].isin(selected_districts)]
        .groupby("자치구")["취득건수"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(
        compare_data,
        horizontal=True
    )

else:
    st.info("비교할 자치구를 선택해 주세요.")


# ==========================================
# 11. 연도별 취득 추이
# ==========================================

st.divider()
st.subheader("📈 4. 연도별 부동산 취득 추이")

yearly_data = (
    data.groupby("연도")["취득건수"]
    .sum()
    .sort_index()
)

st.line_chart(yearly_data)

st.caption(
    "2014년은 4분기 자료만 포함되어 있으므로 "
    "다른 연도와 단순 비교할 때 주의해야 합니다."
)


# ==========================================
# 12. 소유자 유형별 분석
# ==========================================

st.divider()
st.subheader("👥 5. 소유자 유형별 취득 건수")

st.bar_chart(
    category_rank,
    horizontal=True
)

category_table = category_rank.reset_index()

category_table.columns = [
    "소유자 유형",
    "취득 건수"
]

st.dataframe(
    category_table,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 13. 연도 선택 분석
# ==========================================

st.divider()
st.subheader("📅 6. 연도별 상세 분석")

years = sorted(data["연도"].unique().tolist())

selected_year = st.selectbox(
    "분석할 연도를 선택하세요.",
    years
)

year_data = data[
    data["연도"] == selected_year
]


# 분기별 취득 건수
st.write(f"### {selected_year}년 분기별 취득 건수")

quarter_data = (
    year_data.groupby("분기")["취득건수"]
    .sum()
    .sort_index()
)

st.bar_chart(quarter_data)


# 해당 연도 자치구별 TOP 10
st.write(f"### {selected_year}년 자치구별 TOP 10")

year_district_rank = (
    year_data.groupby("자치구")["취득건수"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .sort_values(ascending=True)
)

st.bar_chart(
    year_district_rank,
    horizontal=True
)


# ==========================================
# 14. 소유자 유형 선택 분석
# ==========================================

st.divider()
st.subheader("🔎 7. 소유자 유형별 상세 분석")

selected_category = st.selectbox(
    "소유자 유형을 선택하세요.",
    category_rank.index.tolist()
)

category_year_data = data[
    data["소유자 유형"] == selected_category
]

category_yearly = (
    category_year_data.groupby("연도")["취득건수"]
    .sum()
    .sort_index()
)

st.write(f"### {selected_category} 연도별 취득 추이")
st.line_chart(category_yearly)


# ==========================================
# 15. 분석 결과
# ==========================================

st.divider()
st.subheader("📝 8. 분석 결과")

top_category = category_rank.index[0]

st.write(f"""
- 전체 취득 건수가 가장 많은 지역은 **{top_district}**입니다.
- {top_district}의 누적 취득 건수는 **{top_count:,}건**입니다.
- 취득 건수가 가장 적은 지역은 **{lowest_district}**이며, 총 **{lowest_count:,}건**입니다.
- 소유자 유형 중 가장 많은 취득 건수를 기록한 유형은 **{top_category}**입니다.
""")

st.info(
    "이 자료는 부동산 가격이나 거래 금액이 아니라 "
    "부동산 소유권 취득 건수를 나타냅니다."
)

st.caption(
    "자료 출처: 대법원 인터넷등기소 | "
    "분석 도구: Python Pandas, Streamlit"
)
