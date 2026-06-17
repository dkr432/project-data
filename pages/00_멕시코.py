import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="멕시코 강수량 분석", page_icon="🌧️", layout="wide")

st.title("🇲🇽 멕시코 관측소(035286) 연간 강수량 추세 분석")
st.write("일별 강수량 데이터를 연도별 합계로 묶어서 추세를 분석합니다.")

@st.cache_data
def load_data():
    df = pd.read_csv('IDCJAC0009_035286_1800_Data.csv')
    return df

try:
    df = load_data()
    rain_col = 'Rainfall amount (millimetres)'

    df_clean = df.dropna(subset=[rain_col])
    yearly = df_clean.groupby('Year').agg(
        total_rain=(rain_col, 'sum'),
        days_measured=(rain_col, 'count')
    ).reset_index()
    yearly = yearly[yearly['days_measured'] >= 300]

    if yearly.empty:
        st.error("분석할 데이터가 충분하지 않아요.")
    else:
        years = yearly['Year'].values
        rain = yearly['total_rain'].values

        slope, intercept = np.polyfit(years, rain, 1)
        trend = slope * years + intercept

        col1, col2, col3 = st.columns(3)
        col1.metric("연평균 강수량", f"{rain.mean():.1f} mm")
        col2.metric("연간 변화율(기울기)", f"{slope:.3f} mm/년",
                    "감소 추세" if slope < 0 else "증가 추세",
                    delta_color="inverse" if slope < 0 else "normal")
        col3.metric("분석 기간", f"{int(years.min())}~{int(years.max())}년")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years, y=rain, mode='lines+markers', name='연간 강수량',
            line=dict(color='#2E86C1', width=2), marker=dict(size=5),
            hovertemplate='<b>%{x}년</b><br>강수량: %{y:.1f} mm<extra></extra>'
        ))
        fig.add_trace(go.Scatter(
            x=years, y=trend, mode='lines',
            name=f'추세선 (기울기: {slope:.3f})',
            line=dict(color='red', width=2.5, dash='dash'),
            hovertemplate='추세값: %{y:.1f} mm<extra></extra>'
        ))
        fig.update_layout(
            title=dict(text="멕시코 관측소(035286) 연간 강수량 추세",
                       font=dict(size=22, color='#2C3E50'), x=0.5, y=0.97),
            plot_bgcolor='white', hovermode='x unified',
            legend=dict(yanchor="top", y=-0.15, xanchor="center", x=0.5,
                        orientation="h", bgcolor='rgba(255,255,255,0.8)'),
            height=600, margin=dict(t=80, b=100)
        )
        fig.update_xaxes(title_text="연도", showgrid=True, gridcolor='rgba(200,200,200,0.3)')
        fig.update_yaxes(title_text="연간 강수량 (mm)", showgrid=True, gridcolor='rgba(200,200,200,0.3)')
        st.plotly_chart(fig, use_container_width=True)

        if slope < 0:
            st.info(f"📉 기울기가 음수({slope:.3f})이므로 강수량은 감소하는 추세입니다.")
        else:
            st.info(f"📈 기울기가 양수({slope:.3f})이므로 강수량은 증가하는 추세입니다.")

        with st.expander("📋 연도별 강수량 데이터 보기"):
            st.dataframe(yearly.rename(columns={
                'Year': '연도',
                'total_rain': '연간 강수량(mm)',
                'days_measured': '측정일 수'
            }).reset_index(drop=True))

except FileNotFoundError:
    st.error("CSV 파일이 없어요. 코드와 같은 폴더에 데이터 파일을 넣어주세요.")
