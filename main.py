import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Streamlit 페이지 레이아웃 및 제목 설정
st.set_page_config(page_title="모로코 강수량 분석", page_icon="🇲🇦", layout="centered")

st.title("🇲🇦 모로코 연간 강수량 및 추세 분석")
st.markdown("""
이 대시보드는 `average-precipitation-per-year.csv` 데이터를 바탕으로 
**모로코(Morocco)**의 연간 강수량 변화 흐름과 장기 추세선을 시각화하여 보여줍니다.
""")

# 데이터 불러오기 함수 (캐싱을 통해 속도 향상)
@st.cache_data
def load_data():
    # 원본 파일명을 그대로 읽어옵니다.
    return pd.read_csv('average-precipitation-per-year.csv')

try:
    df = load_data()
    
    # 1. 모로코(Morocco) 데이터 필터링 및 정렬
    morocco_df = df[df['Entity'] == 'Morocco'].sort_values(by='Year')
    
    if not morocco_df.empty:
        years = morocco_df['Year'].values
        precipitation = morocco_df['Annual precipitation'].values
        
        # 2. 추세선(Linear Regression) 계산
        # 1차 방정식(y = ax + b)의 기울기(a)와 y절편(b) 구하기
        slope, intercept = np.polyfit(years, precipitation, 1)
        trend_line = slope * years + intercept
        
        # 3. 주요 지표(Metric) 화면 표시
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="전체 평균 강수량", value=f"{precipitation.mean():.2f} mm")
        with col2:
            # 기울기 방향에 따라 감소/증가 추세 표시
            if slope < 0:
                st.metric(label="연간 변화량 (기울기)", value=f"{slope:.4f} mm/년", delta="감소 추세", delta_color="inverse")
            else:
                st.metric(label="연간 변화량 (기울기)", value=f"{slope:.4f} mm/년", delta="증가 추세")
                
        # 4. Matplotlib를 활용한 선그래프와 추세선 시각화
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # 실제 연도별 강수량 선그래프
        ax.plot(years, precipitation, marker='o', linestyle='-', color='#1f77b4', alpha=0.7, label='Annual Precipitation')
        # 빨간색 점선 추세선
        ax.plot(years, trend_line, color='red', linestyle='--', linewidth=2, label=f'Trend Line (Slope: {slope:.3f})')
        
        # 그래프 스타일 설정
        ax.set_title("Morocco Annual Precipitation Trend (1940-2025)", fontsize=14, pad=15)
        ax.set_xlabel("Year (연도)", fontsize=11)
        ax.set_ylabel("Precipitation (강수량, mm)", fontsize=11)
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend()
        
        # 스트림릿 웹페이지에 그래프 출력
        st.pyplot(fig)
        
        # 5. 원본 데이터 표 토글 기능
        with st.expander("🇲🇦 모로코 연도별 강수량 원본 데이터 확인하기"):
            st.dataframe(morocco_df[['Year', 'Annual precipitation']].reset_index(drop=True))
            
    else:
        st.error("데이터에서 'Morocco'에 해당하는 행을 찾을 수 없습니다. CSV 파일의 Entity 컬럼을 확인해주세요.")

except FileNotFoundError:
    st.error("`average-precipitation-per-year.csv` 파일이 존재하지 않습니다. 코드가 있는 폴더에 데이터 파일을 함께 넣어주세요.")
