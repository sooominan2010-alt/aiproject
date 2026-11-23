
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="서울 부동산 소유권 취득 현황",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 서울에서 부동산 취득이 가장 많은 지역은?")
st.caption("2014년 4분기부터 2018년 4분기까지의 부동산 소유권 취득 현황 분석")

DATA_FILE = Path(__file__).parent / "부동산+소유권+취득+현황(2014~2018)_20261123112447.csv"

@st.cache_data
def load_data(uploaded_file=None):
    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]

    if uploaded_file is not None:
        for enc in encodings:
            try:
                uploaded_file.seek(0)
                return pd.read_csv(uploaded_file, encoding=enc)
            except UnicodeDecodeError:
                continue
        raise ValueError("CSV 파일의 문자 인코딩을 확인할 수 없습니다.")

    if DATA_FILE.exists():
        for enc in encodings:
            try:
                return pd.read_csv(DATA_FILE, encoding=enc)
            except UnicodeDecodeError:
                continue
        raise ValueError("저장된 CSV 파일의 인코딩을 확인할 수 없습니다.")

    return None


uploaded_file = st.sidebar.file_uploader(
    "CSV 파일 업로드",
    type=["csv"]
)

try:
    df = load_data(uploaded_file)
except Exception as e:
    st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
    st.stop()

if df is None:
    st.info("왼쪽 메뉴에서 CSV 파일을 업로드하거나 CSV 파일을 app.py와 같은 폴더에 넣어 주세요.")
    st.stop()

df.columns = df.columns.astype(str).str.strip()

required_columns = ["자치구별(2)", "취득현황별(2)"]
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"필요한 열을 찾을 수 없습니다: {', '.join(missing_columns)}")
    st.write("현재 CSV 열 이름:", df.columns.tolist())
    st.stop()

quarter_columns = [
    col for col in df.columns
    if "/" in col and col[:4].isdigit()
]

if not quarter_columns:
    st.error("연도별 분기 데이터 열을 찾을 수 없습니다.")
    st.stop()

# 지역명 정리
df["자치구별(2)"] = df["자치구별(2)"].replace("", pd.NA).ffill()
df["취득현황별(2)"] = df["취득현황별(2)"].astype(str).str.strip()

# 숫자 변환 및 결측값 처리
for col in quarter_columns:
    df[col] = (
        df[col].astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
        .replace({"-": "0", "": "0", "nan": "0"})
    )
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# 서울 전체 합계 제외
district_df = df[
    (df["자치구별(2)"].notna()) &
    (df["자치구별(2)"] != "소계") &
    (df["자치구별(2)"] != "합계")
].copy()

if district_df.empty:
    st.error("분석할 자치구 데이터가 없습니다.")
    st.stop()

# 분기별 데이터 변환
long_df = district_df.melt(
    id_vars=["자치구별(2)", "취득현황별(2)"],
    value_vars=quarter_columns,
    var_name="연도분기",
    value_name="취득건수"
)

long_df = long_df.rename(columns={
    "자치구별(2)": "자치구",
    "취득현황별(2)": "취득유형"
})

long_df["연도"] = long_df["연도분기"].str[:4]
long_df["분기"] = long_df["연도분기"].str[-3:]

# 자치구별 전체 순위
district_rank = (
    long_df.groupby("자치구")["취득건수"]
    .sum()
    .sort_values(ascending=False)
)

top_district = district_rank.index[0]
top_count = int(district_rank.iloc[0])
total_count = int(long_df["취득건수"].sum())

# 주요 지표
c1, c2, c3 = st.columns(3)
c1.metric("분석 대상 자치구", f"{district_rank.shape[0]}곳")
c2.metric("취득 건수 1위", top_district)
c3.metric("전체 취득 건수", f"{total_count:,}건")

st.divider()

# 1. TOP 10
st.subheader("🏆 1. 부동산 취득 건수 TOP 10")

top10 = district_rank.head(10).sort_values(ascending=True)
st.bar_chart(top10, horizontal=True)

st.caption("2014년 4분기부터 2018년 4분기까지의 누적 취득 건수입니다.")

with st.expander("25개 자치구 전체 순위 보기"):
    ranking = district_rank.reset_index()
    ranking.columns = ["자치구", "취득 건수"]
    ranking.insert(0, "순위", range(1, len(ranking) + 1))
    ranking["취득 건수"] = ranking["취득 건수"].map(lambda x: f"{int(x):,}")
    st.dataframe(ranking, use_container_width=True, hide_index=True)

st.divider()

# 2. 자치구 비교
st.subheader("📊 2. 원하는 자치구 비교하기")

selected_districts = st.multiselect(
    "비교할 자치구를 선택하세요.",
    options=district_rank.index.tolist(),
    default=district_rank.head(5).index.tolist()
)

if selected_districts:
    compare_data = (
        long_df[long_df["자치구"].isin(selected_districts)]
        .groupby("자치구")["취득건수"]
        .sum()
        .sort_values(ascending=False)
    )
    st.bar_chart(compare_data)
else:
    st.info("비교할 자치구를 하나 이상 선택하세요.")

st.divider()

# 3. 연도별 추이
st.subheader("📈 3. 연도별 부동산 취득 추이")

yearly = (
    long_df.groupby("연도")["취득건수"]
    .sum()
    .sort_index()
)

st.line_chart(yearly)
st.caption("2014년은 4분기 자료만 포함되어 있으므로 다른 연도와 단순 비교할 때 주의하세요.")

st.divider()

# 4. 소유자 유형별 분석
st.subheader("👥 4. 소유자 유형별 취득 건수")

category_rank = (
    long_df.groupby("취득유형")["취득건수"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(category_rank)

category_table = category_rank.reset_index()
category_table.columns = ["소유자 유형", "취득 건수"]
category_table["취득 건수"] = category_table["취득 건수"].map(lambda x: f"{int(x):,}")

st.dataframe(category_table, use_container_width=True, hide_index=True)

st.divider()

# 5. 연도와 분기별 상세 분석
st.subheader("🔎 5. 연도와 분기별 상세 분석")

available_years = sorted(long_df["연도"].unique().tolist())

selected_year = st.selectbox(
    "연도 선택",
    available_years,
    index=len(available_years) - 1
)

year_data = long_df[long_df["연도"] == selected_year]

quarter_rank = (
    year_data.groupby("분기")["취득건수"]
    .sum()
    .sort_index()
)

st.write(f"**{selected_year}년 분기별 취득 건수**")
st.bar_chart(quarter_rank)

year_district_rank = (
    year_data.groupby("자치구")["취득건수"]
    .sum()
    .sort_values(ascending=False)
)

st.write(f"**{selected_year}년 자치구별 TOP 10**")
st.bar_chart(year_district_rank.head(10))

st.divider()

# 6. 분석 결과 요약
st.subheader("📝 6. 분석 결과 살펴보기")

lowest_district = district_rank.index[-1]
lowest_count = int(district_rank.iloc[-1])
top_category = category_rank.index[0]

st.write(
    f"""
    - 전체 분석 기간 중 부동산 소유권 취득 건수가 가장 많은 지역은 **{top_district}**이며,
      총 **{top_count:,}건**입니다.
    - 취득 건수가 가장 적은 지역은 **{lowest_district}**이며,
      총 **{lowest_count:,}건**입니다.
    - 소유자 유형 중 취득 건수가 가장 많은 유형은 **{top_category}**입니다.
    - 이 자료는 부동산 가격이나 거래 금액이 아니라 **소유권 취득 건수**를 나타냅니다.
    """
)

st.caption("자료 출처: 대법원 인터넷등기소 | 분석 도구: Python Pandas, Streamlit")
