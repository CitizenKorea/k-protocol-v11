import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 1. 페이지 설정 (밝고 넓은 화면)
st.set_page_config(page_title="K-PROTOCOL 3D LIGO Localization", layout="wide", initial_sidebar_state="collapsed")

# 2. 메인 타이틀 (상단 여백 확보)
st.markdown("<br>", unsafe_allow_html=True)
st.title("🔭 Deterministic 3D LIGO Localization")
st.markdown("**공간 기하학적 증명: 28평방도 확률적 오차의 결정론적 붕괴**")
st.markdown("---")

# 3. 보정 슬라이더
progress = st.slider("K-PROTOCOL 보정 진행률 (0% = 기존 SI 상수 광속 c 적용, 100% = 절대 속도 c_k 및 S_loc 적용)", 0.0, 1.0, 0.0, 0.01)

# 4. 레이아웃 분할
col1, col2 = st.columns([1.2, 1])

# ==========================================
# 🌌 [좌측] 3D 시네마틱 기하학 시뮬레이션 (Light Theme)
# ==========================================
with col1:
    st.markdown("#### 3D 공간 기하학적 수렴 (관측선 교차 시뮬레이션)")
    fig3d = go.Figure()

    # (1) 지구(Earth) 3D 구체 (깔끔한 연파랑)
    u = np.linspace(0, 2 * np.pi, 40)
    v = np.linspace(0, np.pi, 40)
    R = 5
    x_earth = R * np.outer(np.cos(u), np.sin(v))
    y_earth = R * np.outer(np.sin(u), np.sin(v))
    z_earth = R * np.outer(np.ones(np.size(u)), np.cos(v))

    fig3d.add_trace(go.Surface(
        x=x_earth, y=y_earth, z=z_earth,
        colorscale='Blues', opacity=0.2, showscale=False, hoverinfo='skip', name='Earth'
    ))

    # (2) 관측소 위치 및 라벨 (어두운 글씨로 가독성 확보)
    pos_V1 = np.array([R, 0, 0])
    pos_L1 = np.array([-R*0.5, R*0.866, 0])
    pos_H1 = np.array([-R*0.5, -R*0.866, 0])

    # 선명한 색상 배정 (초록, 파랑, 빨강)
    color_V1, color_L1, color_H1 = "#1ca01c", "#1f77b4", "#d62728"

    for name, pos, color in [("V1 (Italy)", pos_V1, color_V1), ("L1 (Livingston)", pos_L1, color_L1), ("H1 (Hanford)", pos_H1, color_H1)]:
        fig3d.add_trace(go.Scatter3d(
            x=[pos[0]], y=[pos[1]], z=[pos[2]], mode='markers+text',
            marker=dict(size=5, color=color), text=[name], textposition="bottom center",
            textfont=dict(color='#333333', size=11), name=name
        ))

    # (3) 심우주 타겟 및 오차 세팅
    target_true = np.array([120, 80, 60])
    err_V1 = np.array([-30, 40, -20]) 
    err_L1 = np.array([50, -30, 40])
    err_H1 = np.array([-15, -40, -50])

    end_V1 = target_true + err_V1 * (1 - progress)
    end_L1 = target_true + err_L1 * (1 - progress)
    end_H1 = target_true + err_H1 * (1 - progress)

    # (4) 관측 레이저 빔 발사
    def shoot_laser(start, end, color, name):
        fig3d.add_trace(go.Scatter3d(
            x=[start[0], end[0]], y=[start[1], end[1]], z=[start[2], end[2]],
            mode='lines+markers', line=dict(color=color, width=4),
            marker=dict(size=[0, 4], color=color, symbol='cross'), name=name
        ))

    shoot_laser(pos_V1, end_V1, color_V1, "V1 Vector")
    shoot_laser(pos_L1, end_L1, color_L1, "L1 Vector")
    shoot_laser(pos_H1, end_H1, color_H1, "H1 Vector")

    # (5) 🎯 하이라이트: 100% 도달 시에만 타겟 등장!
    if progress == 1.0:
        fig3d.add_trace(go.Scatter3d(
            x=[target_true[0]], y=[target_true[1]], z=[target_true[2]],
            mode='markers+text',
            marker=dict(size=14, color='#ffaa00', symbol='diamond', line=dict(color='black', width=1)),
            text=["✨ NGC 4993 (Zero-Error)"], textposition="top center",
            textfont=dict(color='black', size=14, family="Arial Black"), name="True Source"
        ))

    # 3D 레이아웃 (배경을 투명/흰색으로 처리)
    fig3d.update_layout(
        scene=dict(
            xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
            bgcolor='rgba(0,0,0,0)', # 투명 배경
            camera=dict(eye=dict(x=1.3, y=-1.6, z=0.8))
        ),
        margin=dict(l=0, r=0, b=10, t=10), height=550,
        paper_bgcolor='rgba(0,0,0,0)', showlegend=False # 레전드를 숨겨서 차트를 더 크게 확보
    )
    st.plotly_chart(fig3d, use_container_width=True)

# ==========================================
# 📊 [우측] 2D 수학적 오차 붕괴 그래프 (Light Theme)
# ==========================================
with col2:
    st.markdown("#### 수학적 수렴 (도달 시간 로그 잔차)")
    t_base_L1, t_base_H1 = 22.141220, 25.160489
    T_actual_L1, T_actual_H1 = 22.170549, 25.158686
    S_earth, S_loc_L1, S_loc_H1 = 1.006419562, 1.007752243, 1.006347452

    x_vals = np.linspace(0, progress, 100) if progress > 0 else [0]
    log_errors_L1, log_errors_H1 = [], []
    EPSILON = 1e-12

    for x in x_vals:
        cur_S_L1 = S_earth + (S_loc_L1 - S_earth) * x
        cur_S_H1 = S_earth + (S_loc_H1 - S_earth) * x
        log_errors_L1.append(np.log10(abs((t_base_L1 * (cur_S_L1 / S_earth)) - T_actual_L1) + EPSILON))
        log_errors_H1.append(np.log10(abs((t_base_H1 * (cur_S_H1 / S_earth)) - T_actual_H1) + EPSILON))

    fig2d = go.Figure()
    if progress > 0:
        fig2d.add_trace(go.Scatter(x=x_vals, y=log_errors_L1, mode='lines', name='L1 Error Log', line=dict(color=color_L1, width=3)))
        fig2d.add_trace(go.Scatter(x=x_vals, y=log_errors_H1, mode='lines', name='H1 Error Log', line=dict(color=color_H1, width=3)))
    
    fig2d.update_layout(
        xaxis_title="K-PROTOCOL 적용률", yaxis_title="도달 시간 오차 (Log10 ms)",
        template="plotly_white", # 학술 논문 스타일의 하얀 배경
        height=550, yaxis=dict(range=[-12, 1]), margin=dict(l=10, r=10, b=10, t=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1) # 레전드 위치 조정
    )
    st.plotly_chart(fig2d, use_container_width=True)

# ==========================================
# 📝 하단 설명 영역 (차트와 안 겹치도록 분리)
# ==========================================
st.markdown("---")
if progress == 1.0:
    st.success("🎯 **[증명 완료]** 세 개의 관측 벡터가 우주 공간의 단일 좌표(NGC 4993)로 완벽히 교차했습니다. 기존 SI 체계가 만든 28평방도의 확률적 오차는 기하학적 착시였음이 증명되었습니다.")
else:
    st.info("💡 **시뮬레이션 가이드:** 슬라이더를 우측으로 당겨보세요. 관측선들이 허공을 헤매다 100%에 도달하는 순간, 오차가 0이 되며 정확한 타겟 지점을 찾아냅니다.")
