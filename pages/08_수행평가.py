
import streamlit as st
import pandas as pd
from pathlib import Path

# =====================================
# 1. 기본 설정
# =====================================

st.set_page_config(
    page_title="서울 부동산 취득 현황 분석",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 서울에서 부동산 취득이 가장 많은 지역은?")
st.write("2014년부터 2018년까지 서울시 부동산 소유권 취득 현황을 분석합니다.")

# =====================================
# 2. CSV 파일 자동 불러오기
# =====================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "soominan.csv"

@st.cache_data
def load_data():
    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]

    for encoding in encodings:
        try:
            return pd.read_csv(DATA_FILE, encoding=encoding)
        except UnicodeDecodeError:
            continue

    return None


if not DATA_FILE.exists():
    st.error("soominan.csv 파일을 찾을 수 없습니다.")
    st.stop()

try:
    df = load_data()
except Exception as e:
    st.error(f"CSV 파일을 읽을 수 없습니다: {e}")
    st.stop()

if df is None:
    st.error("CSV 파일의 인코딩을 확인해 주세요.")
    st.stop()

# =====================================
# 3. 데이터 전처리
# =====================================

df.columns = df.columns.astype(str).str.strip()

required_columns = ["자치구별(2)", "취득현황별(2)"]

if not all(col in df.columns for col in required_columns):
    st.error("필요한 열을 찾을 수 없습니다.")
    st.write(df.columns.tolist())
    st.stop()

df["자치구별(2)"] = (
    df["자치구별(2)"]
    .replace("", pd.NA)
    .ffill()
)

df["취득현황별(2)"] = df["취득현황별(2)"].astype(str).str.strip()

quarter_columns = [
    col for col in df.columns
    if "/" in col and str(col)[:4].isdigit()
]

if not quarter_columns:
    st.error("연도별 분기 데이터 열을 찾을 수 없습니다.")
    st.stop()

for col in quarter_columns:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
        .replace({"-": "0", "": "0", "nan": "0"})
    )

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)

# 서울 전체 합계 제외
district_df = df[
    (df["자치구별(2)"].notna()) &
    (df["자치구별(2)"] != "소계") &
    (df["자치구별(2)"] != "합계")
].copy()

# =====================================
# 4. 데이터 분석용 형태로 변환
# =====================================

data = district_df.melt(
    id_vars=["자치구별(2)", "취득현황별(2)"],
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

# =====================================
# 5. 전체 통계 계산
# =====================================

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

# =====================================
# 6. 전체 분석 요약
# =====================================

st.divider()
st.subheader("📌 전체 분석 요약")

col1, col2, col3 = st.columns(3)

col1.metric("분석 자치구", f"{len(district_rank)}곳")
col2.metric("취득 건수 1위", top_district)
col3.metric("전체 취득 건수", f"{total_count:,}건")

# =====================================
# 7. 자치구 TOP 10
# =====================================

st.divider()
st.subheader("🏆 1. 부동산 취득 건수 TOP 10")

top10 = district_rank.head(10).sort_values(ascending=True)

st.bar_chart(top10, horizontal=True)

st.caption("전체 분석 기간의 누적 취득 건수입니다.")

# =====================================
# 8. 전체 자치구 순위
# =====================================

st.divider()
st.subheader("📊 2. 서울 자치구 전체 순위")

ranking = district_rank.reset_index()
ranking.columns = ["자치구", "취득 건수"]

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

# =====================================
# 9. 자치구 비교
# =====================================

st.divider()
st.subheader("🔍 3. 원하는 자치구 비교")

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

    st.bar_chart(compare_data, horizontal=True)
else:
    st.info("자치구를 선택해 주세요.")

# =====================================
# 10. 연도별 취득 추이
# =====================================

st.divider()
st.subheader("📈 4. 연도별 부동산 취득 추이")

yearly_data = (
    data.groupby("연도")["취득건수"]
    .sum()
    .sort_index()
)

st.line_chart(yearly_data)

st.caption("2014년은 4분기 자료만 포함되어 있습니다.")

# =====================================
# 11. 소유자 유형별 분석
# =====================================

st.divider()
st.subheader("👥 5. 소유자 유형별 취득 건수")

st.bar_chart(category_rank, horizontal=True)

category_table = category_rank.reset_index()
category_table.columns = ["소유자 유형", "취득 건수"]

st.dataframe(
    category_table,
    use_container_width=True,
    hide_index=True
)

# =====================================
# 12. 연도별 상세 분석
# =====================================

st.divider()
st.subheader("📅 6. 연도별 상세 분석")

years = sorted(data["연도"].unique().tolist())

selected_year = st.selectbox(
    "분석할 연도 선택",
    years
)

year_data = data[data["연도"] == selected_year]

st.write(f"### {selected_year}년 분기별 취득 건수")

quarter_data = (
    year_data.groupby("분기")["취득건수"]
    .sum()
    .sort_index()
)

st.bar_chart(quarter_data)

st.write(f"### {selected_year}년 자치구별 TOP 10")

year_district = (
    year_data.groupby("자치구")["취득건수"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .sort_values(ascending=True)
)

st.bar_chart(year_district, horizontal=True)

# =====================================
# 13. 소유자 유형별 상세 분석
# =====================================

st.divider()
st.subheader("🔎 7. 소유자 유형별 상세 분석")

selected_category = st.selectbox(
    "소유자 유형 선택",
    category_rank.index.tolist()
)

category_data = data[
    data["소유자 유형"] == selected_category
]

category_yearly = (
    category_data.groupby("연도")["취득건수"]
    .sum()
    .sort_index()
)

st.line_chart(category_yearly)

# =====================================
# 14. 분석 결과
# =====================================

st.divider()
st.subheader("📝 8. 분석 결과")

top_category = category_rank.index[0]

st.write(f"""
- 부동산 취득 건수가 가장 많은 지역은 **{top_district}**입니다.
- {top_district}의 누적 취득 건수는 **{top_count:,}건**입니다.
- 취득 건수가 가장 적은 지역은 **{lowest_district}**이며, 총 **{lowest_count:,}건**입니다.
- 가장 많은 취득 건수를 기록한 소유자 유형은 **{top_category}**입니다.
""")

st.info(
    "이 자료는 부동산 가격이나 거래 금액이 아닌 "
    "부동산 소유권 취득 건수를 나타냅니다."
)

st.caption(
    "자료 출처: 대법원 인터넷등기소 | "
    "분석 도구: Python Pandas, Streamlit"
)
