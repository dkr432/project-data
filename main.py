import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ===== 페이지 기본 설정 =====
st.set_page_config(page_title="모로코 물 분석", page_icon="🌧️", layout="wide")

st.title("🇲🇦 모로코 강수량 & 1인당 담수 자원 분석")
st.write("모로코의 **연간 강수량**과 **1인당 재생가능 담수 자원**을 함께 비교합니다. "
         "**그래프에 마우스를 올리면** 자세한 값을 볼 수 있어요!")

# ===== 데이터 불러오기 =====
@st.cache_data
def load_data():
    precip = pd.read_csv('average-precipitation-per-year.csv')
    water = pd.read_csv('renewable-water-resources-per-capita.csv')
    return precip, water

try:
    precip_df, water_df = load_data()

    # ===== 모로코 데이터만 필터링 =====
    m_precip = precip_df[precip_df['Entity'] == 'Morocco'].sort_values('Year')

    water_col = 'Renewable internal freshwater resources per capita (cubic meters)'
    m_water = water_df[water_df['Entity'] == 'Morocco'].sort_values('Year')

    if m_precip.empty or m_water.empty:
        st.error("모로코 데이터를 찾을 수 없어요. CSV 파일을 확인해주세요.")
    else:
        # 강수량 데이터
        p_years = m_precip['Year'].values
        p_values = m_precip['Annual precipitation'].values

        # 담수 자원 데이터
        w_years = m_water['Year'].values
        w_values = m_water[water_col].values

        # ===== 강수량 추세선 계산 =====
        slope, intercept = np.polyfit(p_years, p_values, 1)
        trend = slope * p_years + intercept

        # ===== 주요 지표 표시 =====
        col1, col2, col3 = st.columns(3)
        col1.metric("강수량 평균", f"{p_values.mean():.1f} mm")
        col2.metric("강수량 추세(기울기)", f"{slope:.3f} mm/년",
                    "감소 추세" if slope < 0 else "증가 추세",
                    delta_color="inverse" if slope < 0 else "normal")
        water_change = (w_values[-1] - w_values[0]) / w_values[0] * 100
        col3.metric("1인당 담수 자원 변화", f"{water_change:.1f} %",
                    "감소" if water_change < 0 else "증가",
                    delta_color="inverse" if water_change < 0 else "normal")

        # ===== 이중 Y축 그래프 만들기 =====
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # (왼쪽 축) 강수량 선그래프
        fig.add_trace(
            go.Scatter(
                x=p_years, y=p_values,
                mode='lines+markers',
                name='연간 강수량 (mm)',
                line=dict(color='#2E86C1', width=2),
                marker=dict(size=5),
                hovertemplate='<b>%{x}년</b><br>강수량: %{y:.1f} mm<extra></extra>'
            ),
            secondary_y=False
        )

        # (왼쪽 축) 강수량 추세선
        fig.add_trace(
            go.Scatter(
                x=p_years, y=trend,
                mode='lines',
                name=f'강수량 추세선 (기울기: {slope:.3f})',
                line=dict(color='red', width=2.5, dash='dash'),
                hovertemplate='추세값: %{y:.1f} mm<extra></extra>'
            ),
            secondary_y=False
        )

        # (오른쪽 축) 1인당 담수 자원 선그래프
        fig.add_trace(
            go.Scatter(
                x=w_years, y=w_values,
                mode='lines+markers',
                name='1인당 담수 자원 (㎥)',
                line=dict(color='#27AE60', width=2),
                marker=dict(size=5),
                hovertemplate='<b>%{x}년</b><br>담수 자원: %{y:.1f} ㎥<extra></extra>'
            ),
            secondary_y=True
        )

        # ===== 그래프 디자인 설정 (수정됨!) =====
        fig.update_layout(
            title=dict(
                text="모로코 강수량 vs 1인당 담수 자원",
                font=dict(size=22, color='#2C3E50'),
                x=0.5,
                y=0.97
            ),
            plot_bgcolor='white',
            hovermode='x unified',
            legend=dict(
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5,
                orientation="h",
                bgcolor='rgba(255,255,255,0.8)'
            ),
            height=600,
            margin=dict(t=80, b=100)
        )

        # X축 설정
        fig.update_xaxes(title_text="연도", showgrid=True,
                         gridcolor='rgba(200,200,200,0.3)')

        # 왼쪽 Y축 (강수량) - 파란색
        fig.update_yaxes(title_text="<b>강수량 (mm)</b>",
                         color='#2E86C1', secondary_y=False,
                         showgrid=True, gridcolor='rgba(200,200,200,0.3)')

        # 오른쪽 Y축 (담수 자원) - 초록색
        fig.update_yaxes(title_text="<b>1인당 담수 자원 (㎥)</b>",
                         color='#27AE60', secondary_y=True)

        # 그래프 출력
        st.plotly_chart(fig, use_container_width=True)

        # ===== 결과 해석 =====
        st.info(f"""
        📊 **분석 결과**
        - 강수량은 기울기 {slope:.3f}로 **{'감소' if slope < 0 else '증가'}** 추세를 보입니다.
        - 1인당 담수 자원은 {w_years[0]}년부터 {w_years[-1]}년까지 **{water_change:.1f}%** 변했습니다.
        - 💡 두 그래프를 비교하며 강수량과 물 자원의 관계를 살펴보세요!
        """)

        # ===== 원본 데이터 표 =====
        with st.expander("📋 원본 데이터 보기"):
            tab1, tab2 = st.tabs(["강수량", "1인당 담수 자원"])
            with tab1:
                st.dataframe(m_precip[['Year', 'Annual precipitation']].reset_index(drop=True))
            with tab2:
                st.dataframe(m_water[['Year', water_col]].reset_index(drop=True))

except FileNotFoundError as e:
    st.error(f"CSV 파일을 찾을 수 없어요. 두 데이터 파일이 코드와 같은 폴더에 있는지 확인해주세요.\n\n{e}")
