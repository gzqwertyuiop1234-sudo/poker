import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================= 🎨 网页版配置 =================
st.set_page_config(page_title="欢乐德州结算Pro", page_icon="♠️", layout="centered")

# 自定义 CSS (保留卡通风格)
st.markdown("""
<style>
    .stApp {background-color: #E0F7FA;}
    .css-1d391kg {background-color: #FFFFFF; border-radius: 20px; padding: 20px;}
    .stButton>button {border-radius: 20px; font-weight: bold;}
    div[data-testid="stMetricValue"] {font-size: 20px;}
    .result-card {
        padding: 10px; border-radius: 15px; margin-bottom: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center;
    }
    .leader-card {
        background-color: #FFF9C4; padding: 15px; border-radius: 15px; margin-bottom: 10px;
        border: 2px solid #FBC02D;
    }
</style>
""", unsafe_allow_html=True)

# 文件路径
DATA_FILE = 'poker_history.csv'

# ================= 🧠 数据处理逻辑 =================

# 1. 加载历史数据
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except:
            return pd.DataFrame(columns=['日期', '姓名', '原始分', '盈亏金额'])
    else:
        return pd.DataFrame(columns=['日期', '姓名', '原始分', '盈亏金额'])

# 2. 保存单次记录
def save_record(date_str, record_list):
    df_new = pd.DataFrame(record_list)
    df_old = load_data()
    df_final = pd.concat([df_old, df_new], ignore_index=True)
    df_final.to_csv(DATA_FILE, index=False)
    return df_final

# 3. 初始化 Session
if 'players' not in st.session_state:
    st.session_state.players = [{'name': f'玩家{i+1}', 'score': 0.0, 'is_win': True} for i in range(6)]

# ================= 📱 界面搭建 =================

st.title("🍭 欢乐德州・战绩管家")

# 创建三个标签页
tab1, tab2, tab3 = st.tabs(["🏠 本局结算", "🏆 封神榜 (总榜)", "📜 历史明细"])

# ================= 🏷️ 标签页 1: 本局结算 =================
with tab1:
    # 设置区域
    with st.expander("⚙️ 基础设置 (比例/房费)", expanded=True):
        c1, c2 = st.columns(2)
        ratio = c1.number_input("⚡ 比例 (分/元)", value=40, min_value=1)
        fee = c2.number_input("🏠 总房费 (元)", value=0, min_value=0)

    st.markdown("---")
    st.subheader("✍️ 录入战绩")

    # 动态添加/删除玩家
    for i, p in enumerate(st.session_state.players):
        with st.container():
            col_del, col_name, col_win, col_score = st.columns([0.5, 2.5, 1.5, 2.5])
            
            if col_del.button("❌", key=f"del_{i}"):
                st.session_state.players.pop(i)
                st.rerun()
            
            p['name'] = col_name.text_input("名", value=p['name'], key=f"n_{i}", label_visibility="collapsed", placeholder="名字")
            p['is_win'] = col_win.checkbox("赢?", value=p['is_win'], key=f"w_{i}")
            p['score'] = col_score.number_input("分", value=p['score'], step=100.0, key=f"s_{i}", label_visibility="collapsed")

    # 按钮区
    ca, cb = st.columns(2)
    if ca.button("➕ 加人", use_container_width=True):
        count = len(st.session_state.players)
        st.session_state.players.append({'name': f'玩家{count+1}', 'score': 0.0, 'is_win': True})
        st.rerun()
    
    if cb.button("🧹 重置", use_container_width=True):
        for p in st.session_state.players:
            p['score'] = 0.0
            p['is_win'] = True
        st.rerun()

    st.markdown("###")
    
    # === 结算核心 ===
    if st.button("🚀 结算并记录到总榜", type="primary", use_container_width=True):
        # 1. 算账
        calc_data = []
        total_score = 0
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        for p in st.session_state.players:
            if p['score'] == 0: continue
            real_score = p['score'] if p['is_win'] else -p['score']
            calc_data.append({'name': p['name'], 'score': real_score})
            total_score += real_score

        # 2. 平账校验
        if abs(total_score) > 1000:
            st.error(f"🚫 账目严重不平 (差{total_score})，无法记录！")
        else:
            if abs(total_score) > 0.1:
                st.warning(f"⚠️ 存在微小误差 {total_score} (已忽略)")
            else:
                st.success("✅ 账目完美平衡")

            # 3. 计算金额
            winners = [x for x in calc_data if x['score'] > 0]
            total_win = sum(x['score'] for x in winners)
            
            records_to_save = [] # 准备存入数据库的数据

            st.markdown("### 🧾 本局账单")
            calc_data.sort(key=lambda x: x['score'], reverse=True)

            for idx, p in enumerate(calc_data):
                score = p['score']
                raw_money = score / ratio
                fee_share = 0.0
                if score > 0 and total_win > 0:
                    fee_share = fee * (score / total_win)
                final_money = raw_money - fee_share
                
                # 准备保存的数据
                records_to_save.append({
                    '日期': current_time,
                    '姓名': p['name'],
                    '原始分': score,
                    '盈亏金额': round(final_money, 2)
                })

                # 显示卡片
                bg = "#E8F5E9" if final_money >= 0 else "#FFEBEE"
                bd = "#00E676" if final_money >= 0 else "#FF5252"
                sign = "+" if final_money >= 0 else ""
                rank = ["🥇","🥈","🥉"][idx] if idx < 3 and final_money > 0 else ""
                
                st.markdown(f"""
                <div class="result-card" style="background-color: {bg}; border-left: 5px solid {bd};">
                    <div style="font-weight:bold; color:#333;">{rank} {p['name']}</div>
                    <div style="text-align:right;">
                        <div style="font-weight:bold; color:{bd}; font-size:18px;">{sign}{final_money:.1f}</div>
                        <div style="font-size:12px; color:gray;">分:{int(score)}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # 4. 保存到历史文件
            save_record(current_time, records_to_save)
            st.toast('🎉 战绩已保存到封神榜！')


# ================= 🏷️ 标签页 2: 封神榜 =================
with tab2:
    st.markdown("### 🏆 累计战绩排行榜")
    df = load_data()
    
    if not df.empty:
        # 按姓名分组求和
        leaderboard = df.groupby('姓名')['盈亏金额'].sum().reset_index()
        # 按盈亏排序
        leaderboard = leaderboard.sort_values(by='盈亏金额', ascending=False)
        
        # 展示榜单
        for i, row in leaderboard.iterrows():
            name = row['姓名']
            money = row['盈亏金额']
            
            # 样式
            if i == 0: bg, icon = "#FFF59D", "👑 榜一大哥" # 金
            elif i == 1: bg, icon = "#E0E0E0", "🥈 二当家" # 银
            elif i == 2: bg, icon = "#FFCC80", "🥉 探花郎" # 铜
            else: bg, icon = "white", f"第{i+1}名"
            
            col
