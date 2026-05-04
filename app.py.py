import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="따릉이 데이터 분석 대시보드", layout="wide")
st.title("🚲 서울시 따릉이 이용 현황 데이터 분석")
st.markdown("---")

# 2. 데이터베이스 존재 확인
DB_PATH = 'bicycle.db'

if not os.path.exists(DB_PATH):
    st.error(f"❌ '{DB_PATH}' 파일을 찾을 수 없습니다. 데이터베이스 파일이 같은 폴더에 있는지 확인해주세요!")
    st.stop()

# 데이터베이스 연결 함수
def run_query(query):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql(query, conn)

# --- 분석 시작 ---

# 분석 ①: 월별 이용패턴
st.header("1. 월별 이용패턴 분석")
sql1 = """
SELECT 대여일자, SUM(이용건수) as 총이용건수 
FROM 이용정보 
GROUP BY 대여일자 
ORDER BY 대여일자
"""
df1 = run_query(sql1)

col1, col2 = st.columns([2, 1])
with col1:
    fig1 = px.line(df1, x='대여일자', y='총이용건수', title="월별 따릉이 이용 추이", markers=True)
    st.plotly_chart(fig1, use_container_width=True)
with col2:
    st.subheader("🔍 SQL 쿼리")
    st.code(sql1, language='sql')
    st.subheader("💡 인사이트")
    st.write("- 계절적 요인에 따라 이용건수의 변화가 뚜렷하게 나타납니다.")
    st.write("- 특정 월에 이용량이 급증하거나 급감하는 지점을 통해 외부 요인을 유추할 수 있습니다.")


# 분석 ②: 기온별 평균 이용량
st.header("2. 기온별 평균 이용량 (5도 구간)")
sql2 = """
SELECT 
    (CAST(기온.평균기온 / 5 AS INT) * 5) || '도 ~ ' || (CAST(기온.평균기온 / 5 AS INT) * 5 + 5) || '도' as 기온구간,
    AVG(이용정보.이용건수) as 평균이용건수
FROM 이용정보 
JOIN 기온 ON 이용정보.대여일자 = 기온.년월 
GROUP BY CAST(기온.평균기온 / 5 AS INT)
ORDER BY CAST(기온.평균기온 / 5 AS INT)
"""
df2 = run_query(sql2)

col1, col2 = st.columns([2, 1])
with col1:
    fig2 = px.bar(df2, x='기온구간', y='평균이용건수', title="평균 기온구간별 이용량", color='평균이용건수')
    st.plotly_chart(fig2, use_container_width=True)
with col2:
    st.subheader("🔍 SQL 쿼리")
    st.code(sql2, language='sql')
    st.subheader("💡 인사이트")
    st.write("- 너무 춥거나 너무 더운 날씨보다 활동하기 좋은 기온(15~25도)에서 이용량이 가장 높습니다.")
    st.write("- 기온과 따릉이 이용량 사이에는 밀접한 상관관계가 있음을 알 수 있습니다.")


# 분석 ③: 인기 대여소 TOP 10
st.header("3. 가장 인기 있는 대여소 TOP 10")
sql3 = """
SELECT 대여소.보관소명, SUM(이용정보.이용건수) as 총이용건수 
FROM 이용정보 
JOIN 대여소 ON 이용정보.대여소번호 = 대여소.대여소번호 
GROUP BY 대여소.보관소명 
ORDER BY 총이용건수 DESC 
LIMIT 10
"""
df3 = run_query(sql3)

col1, col2 = st.columns([2, 1])
with col1:
    fig3 = px.bar(df3, x='총이용건수', y='보관소명', orientation='h', 
                 title="이용건수 상위 10개 대여소", color='총이용건수', color_continuous_scale='Viridis')
    fig3.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig3, use_container_width=True)
with col2:
    st.subheader("🔍 SQL 쿼리")
    st.code(sql3, language='sql')
    st.subheader("💡 인사이트")
    st.write("- 주로 지하철역 인근이나 유동인구가 많은 지역의 대여소가 상위권을 차지합니다.")
    st.write("- 해당 지역의 자전거 거치대 수를 추가로 확보할 필요가 있다는 정책적 제언이 가능합니다.")