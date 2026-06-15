import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ===== 페이지 기본 설정 =====
st.set_page_config(page_title="모로코 강수량 분석", page_icon="🌧️", layout="wide")

st.title("🌧️ 모로코(Morocco) 연간 강수량 추세 분석")
st.write("1940년부터 2025년까지 모로코의 연간 강수량 변화와 추세선을 분석합니다. "
         "**그래프 위에 마우스를 올리면** 해당 연도의 강수량을 확인할 수 있어요!")

# ===== 데이터 불러오기 (캐싱) =====
@st.cache_data
def load_data():
    return pd.read_csv('average-precipitation-per-year.csv')

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

        # ===== Plotly 인터랙티브 그래프 =====
        fig = go.Figure()

        # 실제 강수량 선그래프 (커서 올리면 연도/강수량 표시)
        fig.add_trace(go.Scatter(
            x=years,
            y=precip,
            mode='lines+markers',
            name='연간 강수량',
            line=dict(color='#2E86C1', width=2),
            marker=dict(size=6, color='#2E86C1'),
            hovertemplate='<b>%{x}년</b><br>강수량: %{y:.1f} mm<extra></extra>'
        ))

        # 추세선 (빨간 점선)
        fig.add_trace(go.Scatter(
            x=years,
            y=trend,
            mode='lines',
            name=f'추세선 (기울기: {slope:.3f})',
            line=dict(color='red', width=3, dash='dash'),
            hovertemplate='추세값: %{y:.1f} mm<extra></extra>'
        ))

        # ===== 그래프 디자인 설정 =====
        fig.update_layout(
            title=dict(
                text="모로코 연간 강수량 변화 (1940~2025)",
                font=dict(size=22, color='#2C3E50'),
                x=0.5  # 제목 가운데 정렬
            ),
            xaxis=dict(
                title="연도",
                showgrid=True,
                gridcolor='rgba(200,200,200,0.3)'
            ),
            yaxis=dict(
                title="강수량 (mm)",
                showgrid=True,
                gridcolor='rgba(200,200,200,0.3)'
            ),
            plot_bgcolor='white',
            hovermode='x unified',  # 같은 연도의 값을 한 번에 표시
            legend=dict(
                yanchor="top", y=0.99,
                xanchor="right", x=0.99,
                bgcolor='rgba(255,255,255,0.8)'
            ),
            height=550
        )

        # 스트림릿에 인터랙티브 그래프 출력
        st.plotly_chart(fig, use_container_width=True)

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
