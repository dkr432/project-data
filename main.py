import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ===== 페이지 기본 설정 =====
st.set_page_config(page_title="모로코 강수량 분석", page_icon="🌧️", layout="wide")

st.title("🌧️ 모로코(Morocco) 연간 강수량 추세 분석")
st.write("1940년부터 2025년까지 모로코의 연간 강수량 변화와 추세선을 분석합니다.")

# ===== 데이터 불러오기 (캐싱) =====
@st.cache_data
def load_data():
    df = pd.read_csv('average-precipitation-per-year.csv')
    return df

try:
    df = load_data()

    # ===== 모로코 데이터만 필터링 =====
    morocco = df[df['Entity'] == 'Morocco'].sort_values('Year')

    if morocco.empty:
        st.error("데이터에서 'Morocco'를 찾을 수 없어요. CSV 파일을 확인해주세요.")
    else:
        years = morocco['Year'].values
        precip = morocco['Annual precipitation'].values

        # ===== 추세선 계산 (1차 직선) =====
        slope, intercept = np.polyfit(years, precip, 1)
        trend = slope * years + intercept

        # ===== 앞/뒤 절반 평균 비교 =====
        mid = years[len(years) // 2]
        first_half = precip[years < mid].mean()
        second_half = precip[years >= mid].mean()
        change_percent = (second_half - first_half) / first_half * 100

        # ===== 주요 지표 표시 =====
        col1, col2, col3 = st.columns(3)
        col1.metric("전체 평균 강수량", f"{precip.mean():.1f} mm")
        col2.metric("연간 변화율(기울기)", f"{slope:.3f} mm/년",
                    "감소 추세" if slope < 0 else "증가 추세",
                    delta_color="inverse" if slope < 0 else "normal")
        col3.metric("전반부 대비 변화", f"{change_percent:.1f} %")

        # ===== 그래프 그리기 =====
        fig, ax = plt.subplots(figsize=(11, 5))

        # 실제 강수량 선그래프
        ax.plot(years, precip, marker='o', markersize=4, linewidth=1.5,
                color='#2E86C1', alpha=0.8, label='Annual Precipitation')

        # 추세선 (빨간 점선)
        ax.plot(years, trend, color='red', linestyle='--', linewidth=2.5,
                label=f'Trend Line (slope: {slope:.3f})')

        # 그래프 꾸미기
        ax.set_title("Morocco Annual Precipitation (1940-2025)", fontsize=15, pad=12)
        ax.set_xlabel("Year", fontsize=12)
        ax.set_ylabel("Precipitation (mm)", fontsize=12)
        ax.grid(True, linestyle=':', alpha=0.5)
        ax.legend(fontsize=11)

        st.pyplot(fig)

        # ===== 결과 해석 자동 출력 =====
        if slope < 0:
            st.info(f"📉 추세선의 기울기가 음수({slope:.3f})이므로, "
                    f"모로코의 강수량은 장기적으로 **감소하는 추세**를 보입니다.")
        else:
            st.info(f"📈 추세선의 기울기가 양수({slope:.3f})이므로, "
                    f"모로코의 강수량은 장기적으로 **증가하는 추세**를 보입니다.")

        # ===== 원본 데이터 표 =====
        with st.expander("📋 원본 데이터 보기"):
            st.dataframe(morocco[['Year', 'Annual precipitation']].reset_index(drop=True))

except FileNotFoundError:
    st.error("'average-precipitation-per-year.csv' 파일이 없어요. "
             "코드와 같은 폴더에 데이터 파일을 넣어주세요.")
