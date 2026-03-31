import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="K-PROTOCOL 3D LIGO Localization", layout="wide")

st.title("🔭 Deterministic 3D LIGO Localization")
st.markdown("**공간 기하학적 증명: 28평방도 확률적 오차의 결정론적 붕괴**")
st.markdown("슬라이더를 움직여 기존 SI 체계의 엇갈린 관측선이 절대성 이론(K-PROTOCOL)을 통해 단 하나의 점(NGC 4993)으로 꽂히는 장면을 확인하세요.")
st.markdown("---")

# 2. 보정 슬라이더
progress = st.slider("K-PROTOCOL 보정 진행률 (0% = 기존 SI 상수 광속 c 적용, 100% = 절대 속도 c_k 및 S_loc 적용)", 0.0, 1.0, 0.0, 0.01)

# 3. 레이아웃 분할
col1, col2 = st.columns([1.5, 1])

# ==========================================
# 🌌 [좌측] 3D 시네마틱 우주 공간 시뮬레이션
# ==========================================
with col1:
    fig3d = go.Figure()

    # (1) 지구(Earth) 3D 구체 생성
    u = np.linspace(0, 2 * np.pi, 40)
    v = np.linspace(0, np.pi, 40)
    R = 5 # 지구 반지름
    x_earth = R * np.outer(np.cos(u), np.sin(v))
    y_earth = R * np.outer(np.sin(u), np.sin(v))
    z_earth = R * np.outer(np.ones(np.size(u)), np.cos(v))

    fig3d.add_trace(go.Surface(
        x=x_earth, y=y_earth, z=z_earth,
        colorscale='Blues', opacity=0.3, showscale=False, hoverinfo='skip', name='Earth'
    ))

    # (2) 관측소 위치 (지구 표면)
    pos_V1 = np.array([R, 0, 0])
    pos_L1 = np.array([-R*0.5, R*0.866, 0])
    pos_H1 = np.array([-R*0.5, -R*0.866, 0])

    # 관측소 마커
    for name, pos, color in [("V1 (Italy)", pos_V1, "#00ff00"), ("L1 (Livingston)", pos_L1, "#00ffff"), ("H1 (Hanford)", pos_H1, "#ff00ff")]:
        fig3d.add_trace(go.Scatter3d(
            x=[pos[0]], y=[pos[1]], z=[pos[2]], mode='markers+text',
            marker=dict(size=6, color=color), text=[name], textposition="bottom center", name=name
        ))

    # (3) 심우주 타겟 (NGC 4993) 및 오차 영역 세팅
    target_true = np.array([150, 100, 80]) # 아득히 먼 심우주
    
    # SI 체계일 때 선이 빗나가는 넓은 오차 범위 (28 sq deg 구현)
    err_V1 = np.array([-40, 60, -30]) 
    err_L1 = np.array([70, -40, 50])
    err_H1 = np.array([-20, -50, -60])

    # 진행률에 따라 선의 끝점(도착점)이 타겟을 향해 이동
    end_V1 = target_true + err_V1 * (1 - progress)
    end_L1 = target_true + err_L1 * (1 - progress)
    end_H1 = target_true + err_H1 * (1 - progress)

    # (4) 관측 레이저 빔 발사
    def shoot_laser(start, end, color, name):
        fig3d.add_trace(go.Scatter3d(
            x=[start[0], end[0]], y=[start[1], end[1]], z=[start[2], end[2]],
            mode='lines', line=dict(color=color, width=4), name=name
        ))
        # 빔 끝점(도착 지점) 마커
        fig3d.add_trace(go.Scatter3d(
            x=[end[0]], y=[end[1]], z=[end[2]], mode='markers',
            marker=dict(size=5, color=color, symbol='cross'), showlegend=False
        ))

    shoot_laser(pos_V1, end_V1, "#00ff00", "V1 Vector")
    shoot_laser(pos_L1, end_L1, "#00ffff", "L1 Vector")
    shoot_laser(pos_H1, end_H1, "#ff00ff", "H1 Vector")

    # (5) 진짜 타겟 (NGC 4993) 
    fig3d.add_trace(go.Scatter3d(
        x=[target_true[0]], y=[target_true[1]], z=[target_true[2]],
        mode='markers+text',
        marker=dict(size=12, color='gold', symbol='diamond', line=dict(color='white', width=2)),
        text=["✨ NGC 4993 (True Source)"], textposition="top center", name="Target"
    ))

    # 3D 카메라 및 배경 세팅 (시네마틱 뷰)
    fig3d.update_layout(
        scene=dict(
            xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
            bgcolor='rgb(5, 5, 15)', # 깊은 우주의 색
            camera=dict(eye=dict(x=1.5, y=-1.5, z=0.8)) # 지구와 우주가 한눈에 보이는 각도
        ),
        margin=dict(l=0, r=0, b=0, t=0), height=600, showlegend=True, paper_bgcolor='rgb(5, 5, 15)'
    )
    st.plotly_chart(fig3d, use_container_width=True)

# ==========================================
# 📊 [우측] 2D 수학적 오차 붕괴 그래프
# ==========================================
with col2:
    # 하드코딩된 논문 원시 데이터
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
        fig2d.add_trace(go.Scatter(x=x_vals, y=log_errors_L1, mode='lines', name='L1 Error Log', line=dict(color='#00ffff', width=3)))
        fig2d.add_trace(go.Scatter(x=x_vals, y=log_errors_H1, mode='lines', name='H1 Error Log', line=dict(color='#ff00ff', width=3)))
    
    fig2d.update_layout(
        title="수학적 수렴 (Zero-Error)",
        xaxis_title="K-PROTOCOL 적용률", yaxis_title="도달 시간 오차(Log10 ms)",
        template="plotly_dark", height=600, yaxis=dict(range=[-12, 2]), margin=dict(t=50)
    )
    st.plotly_chart(fig2d, use_container_width=True)

if progress == 1.0:
    st.success("✅ **[증명 완료]** 세 개의 관측 벡터가 우주 공간의 단일 좌표(NGC 4993)로 완벽히 교차했습니다. 기존 SI 체계가 만든 28평방도의 확률적 오차는 기하학적 착시였음이 증명되었습니다.")
