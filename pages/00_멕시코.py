import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="멕시코 물 분석", page_icon="🌧️", layout="wide")

st.title("🇲🇽 멕시코 강수량 & 1인당 담수 자원 분석")
st.write("멕시코 관측소(035286)의 연간 강수량과 멕시코 전체의 1인당 담수 자원을 비교합니다.")

@st.cache_data
def load_data():
    rain = pd.read_csv('IDCJAC0009_035286_1800_Data.csv')
    water = pd.read_csv('renewable-water-resources-per-capita.csv')
    return rain, water

try:
    rain_df, water_df = load_data()

    # ===== 강수량: 연도별 합계 계산 =====
    rain_col = 'Rainfall amount (millimetres)'
    rain_clean = rain_df.dropna(subset=[rain_col])
    yearly = rain_clean.groupby('Year').agg(
        total_rain=(rain_col, 'sum'),
        days_measured=(rain_col, 'count')
    ).reset_index()
    yearly = yearly[yearly['days_measured'] >= 300]

    # ===== 담수 자원: 멕시코 데이터 필터링 =====
    water_col = 'Renewable internal freshwater resources per capita (cubic meters)'
    m_water = water_df[water_df['Entity'] == 'Mexico'].sort_values('Year')

    if yearly.empty:
        st.error("강수량 데이터가 부족해요.")
    elif m_water.empty:
        st.error("담수 자원 데이터에서 'Mexico'를 찾을 수 없어요.")
    else:
        # 강수량 데이터
        p_years = yearly['Year'].values
        p_values = yearly['total_rain'].values

        # 담수 자원 데이터
        w_years = m_water['Year'].values
        w_values = m_water[water_col].values

        # ===== 강수량 추세선 계산 =====
        slope, intercept = np.polyfit(p_years, p_values, 1)
        trend = slope * p_years + intercept

        # ===== 주요 지표 표시 =====
        col1, col2, col3 = st.columns(3)
        col1.metric("연평균 강수량", f"{p_values.mean():.1f} mm")
        col2.metric("강수량 추세(기울기)", f"{slope:.3f} mm/년",
                    "감소 추세" if slope < 0 else "증가 추세",
                    delta_color="inverse" if slope < 0 else "normal")
        water_change = (w_values[-1] - w_values[0]) / w_values[0] * 100
        col3.metric("1인당 담수 자원 변화", f"{water_change:.1f} %",
                    "감소" if water_change < 0 else "증가",
                    delta_color="inverse" if water_change < 0 else "normal")

        # ===== 이중 Y축 그래프 =====
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # (왼쪽 축) 강수량
        fig.add_trace(go.Scatter(
            x=p_years, y=p_values, mode='lines+markers',
            name='연간 강수량 (mm)',
            line=dict(color='#2E86C1', width=2), marker=dict(size=5),
            hovertemplate='<b>%{x}년</b><br>강수량: %{y:.1f} mm<extra></extra>'
        ), secondary_y=False)

        # (왼쪽 축) 강수량 추세선
        fig.add_trace(go.Scatter(
            x=p_years, y=trend, mode='lines',
            name=f'강수량 추세선 (기울기: {slope:.3f})',
            line=dict(color='red', width=2.5, dash='dash'),
            hovertemplate='추세값: %{y:.1f} mm<extra></extra>'
        ), secondary_y=False)

        # (오른쪽 축) 1인당 담수 자원
        fig.add_trace(go.Scatter(
            x=w_years, y=w_values, mode='lines+markers',
            name='1인당 담수 자원 (㎥)',
            line=dict(color='#27AE60', width=2), marker=dict(size=5),
            hovertemplate='<b>%{x}년</b><br>담수 자원: %{y:.1f} ㎥<extra></extra>'
        ), secondary_y=True)

        # ===== 그래프 디자인 =====
        fig.update_layout(
            title=dict(text="멕시코 강수량 vs 1인당 담수 자원",
                       font=dict(size=22, color='#2C3E50'), x=0.5, y=0.97),
            plot_bgcolor='white', hovermode='x unified',
            legend=dict(yanchor="top", y=-0.15, xanchor="center", x=0.5,
                        orientation="h", bgcolor='rgba(255,255,255,0.8)'),
            height=600, margin=dict(t=80, b=100)
        )
        fig.update_xaxes(title_text="연도", showgrid=True, gridcolor='rgba(200,200,200,0.3)')
        fig.update_yaxes(title_text="<b>강수량 (mm)</b>", color='#2E86C1',
                         secondary_y=False, showgrid=True, gridcolor='rgba(200,200,200,0.3)')
        fig.update_yaxes(title_text="<b>1인당 담수 자원 (㎥)</b>", color='#27AE60', secondary_y=True)

        st.plotly_chart(fig, use_container_width=True)

        # ===== 결과 해석 =====
        st.info(f"""
        📊 **분석 결과**
        - 강수량은 기울기 {slope:.3f}로 **{'감소' if slope < 0 else '증가'}** 추세입니다.
        - 1인당 담수 자원은 {int(w_years[0])}년부터 {int(w_years[-1])}년까지 **{water_change:.1f}%** 변했습니다.
        - 💡 강수량(한 관측소)과 물 자원(나라 전체)의 관계를 비교해보세요!
        """)

        # ===== 원본 데이터 표 =====
        with st.expander("📋 원본 데이터 보기"):
            tab1, tab2 = st.tabs(["강수량", "1인당 담수 자원"])
            with tab1:
                st.dataframe(yearly.rename(columns={
                    'Year': '연도', 'total_rain': '연간 강수량(mm)',
                    'days_measured': '측정일 수'
                }).reset_index(drop=True))
            with tab2:
                st.dataframe(m_water[['Year', water_col]].reset_index(drop=True))

except FileNotFoundError as e:
    st.error(f"CSV 파일을 찾을 수 없어요. 두 파일이 같은 폴더에 있는지 확인해주세요.\n\n{e}")
