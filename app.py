import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time

# ================= 🟢 1. 常用玩家名单 =================
PLAYER_LIST = [
    "甜甜", "不良坤", "小七猫", "派大星",
    "Winter", "East", "Sakurasawa Sumi", "居"
]
# ==========================================================

# 文件名
DATA_FILE = 'poker_history.csv'

# 页面配置 (针对移动端优化布局)
st.set_page_config(page_title="Science DE Rect", page_icon="🤖", layout="centered", initial_sidebar_state="collapsed")

# ================= 🎨 移动端机甲风 CSS =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;700&display=swap');

    /* 1. 全局背景 */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 30%, #1a1a1a 0%, #000000 80%);
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    /* 2. 标题优化 */
    .mecha-title {
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 28px;
        background: linear-gradient(180deg, #fff, #888);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 15px rgba(0, 242, 255, 0.5);
        text-align: center;
        letter-spacing: 1px;
        margin-top: 10px;
    }
    .mecha-subtitle {
        font-family: 'Rajdhani', sans-serif;
        color: #58a6ff;
        text-align: center;
        font-size: 12px;
        letter-spacing: 2px;
        margin-bottom: 15px;
        opacity: 0.8;
    }

    /* 3. 输入框与下拉框 */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(22, 27, 34, 0.9) !important;
        border: 1px solid #30363d !important;
        color: #00F2FF !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: bold;
        border-radius: 6px;
        min-height: 45px !important; 
        font-size: 16px !important;  
    }

    [data-testid="column"] { padding: 0 !important; }
    [data-testid="stHorizontalBlock"] { gap: 0.3rem !important; }
    .stMarkdown p, label { color: #8b949e !important; font-size: 12px !important; }

    /* 4. 按钮优化 */
    .stButton > button {
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 1px;
        border: 1px solid #30363d;
        border-radius: 6px;
        min-height: 45px !important;
        padding: 0px 5px !important;
        font-size: 14px !important;
    }

    button[kind="primary"] {
        background: linear-gradient(180deg, rgba(0, 242, 255, 0.15), rgba(0, 242, 255, 0.05));
        border: 1px solid #00F2FF;
        color: #00F2FF !important;
        box-shadow: 0 0 8px rgba(0, 242, 255, 0.15);
    }

    button[kind="secondary"] {
        background: linear-gradient(180deg, rgba(255, 0, 85, 0.15), rgba(255, 0, 85, 0.05));
        border: 1px solid #FF0055;
        color: #FF0055 !important;
    }

    /* 5. 结果卡片 */
    .result-card {
        background: rgba(13, 17, 23, 0.95);
        border: 1px solid #30363d;
        padding: 12px; margin-bottom: 8px; border-radius: 8px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .hud-text { font-family: 'Rajdhani', sans-serif; font-weight: bold; font-size: 18px; }
    .hud-score { font-family: 'Orbitron', sans-serif; font-size: 20px; font-weight: bold; }

    /* 6. 确认框 */
    .confirm-box {
        border: 1px dashed #00F2FF;
        padding: 15px;
        border-radius: 8px;
        background: rgba(0, 242, 255, 0.05);
        margin-top: 15px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ================= 🧠 数据逻辑 =================

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except:
            return pd.DataFrame(columns=['日期', '姓名', '原始分', '盈亏金额', '分摊房费'])
    else:
        return pd.DataFrame(columns=['日期', '姓名', '原始分', '盈亏金额', '分摊房费'])


def save_record(record_list):
    df_new = pd.DataFrame(record_list)
    df_old = load_data()
    df_final = pd.concat([df_new, df_old], ignore_index=True)
    df_final.to_csv(DATA_FILE, index=False)


# ID生成器
if 'player_id_counter' not in st.session_state:
    st.session_state.player_id_counter = 0


def get_new_id():
    st.session_state.player_id_counter += 1
    return st.session_state.player_id_counter


# 初始化 Session
if 'players' not in st.session_state:
    st.session_state.players = []
    for i in range(8):
        default_name = PLAYER_LIST[i % len(PLAYER_LIST)]
        st.session_state.players.append({
            'id': get_new_id(),
            'name': default_name,
            'is_custom': False,
            'score': 0.0,
            'is_win': True
        })

if 'pending_data' not in st.session_state:
    st.session_state.pending_data = None


# --- 回调函数 ---
def delete_player(target_id):
    st.session_state.players = [p for p in st.session_state.players if p['id'] != target_id]
    st.session_state.pending_data = None


def add_player():
    st.session_state.players.append({
        'id': get_new_id(),
        'name': "",
        'is_custom': True,
        'score': 0.0,
        'is_win': True
    })
    st.session_state.pending_data = None


def toggle_win(target_id):
    for p in st.session_state.players:
        if p['id'] == target_id:
            p['is_win'] = not p['is_win']
            break
    st.session_state.pending_data = None


# 🔴 核心修复：彻底重置系统 (恢复出厂设置)
def reset_scores():
    # 1. 清空当前列表
    st.session_state.players = []

    # 2. 重新按照初始名单生成 8 个人
    # 注意：这里调用 get_new_id() 会生成全新的 ID
    # 这样 Streamlit 就会认为这是一组全新的控件，从而彻底清除之前的输入缓存
    for i in range(8):
        default_name = PLAYER_LIST[i % len(PLAYER_LIST)]
        st.session_state.players.append({
            'id': get_new_id(),
            'name': default_name,
            'is_custom': False,
            'score': 0.0,
            'is_win': True
        })

    # 3. 清空待确认数据
    st.session_state.pending_data = None

    # 4. 提示
    st.toast("🔄 SYSTEM REBOOTED (系统已重置)")


def cancel_save():
    st.session_state.pending_data = None


def confirm_save():
    if st.session_state.pending_data:
        save_record(st.session_state.pending_data)
        st.session_state.pending_data = None
        st.toast("💾 DATA SECURED")
        time.sleep(1)
        st.rerun()


# ================= 📱 界面搭建 =================

st.markdown('<div class="mecha-title">SCIENCE DE RECT</div>', unsafe_allow_html=True)
st.markdown('<div class="mecha-subtitle">MOBILE TACTICAL SYSTEM // V6.2 REBOOT</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🚀 战术结算", "💾 历史档案"])

# --- Tab 1 ---
with tab1:
    with st.expander("⚙️ 系统参数 (PARAMETERS)", expanded=False):
        c1, c2 = st.columns(2)
        ratio = c1.number_input("⚡ 汇率 (Rate)", value=40, min_value=1)
        fee = c2.number_input("🏠 维护费 (Fee)", value=0, min_value=0)

    st.markdown("---")

    for p in st.session_state.players:
        with st.container():
            c_del, c_name, c_btn, c_score = st.columns([0.5, 2.5, 1.8, 2.2])

            c_del.button("✕", key=f"del_{p['id']}", type="secondary", on_click=delete_player, args=(p['id'],))

            if p['is_custom']:
                new_name = c_name.text_input(
                    "Input ID", value=p['name'], key=f"txt_{p['id']}",
                    placeholder="ID...", label_visibility="collapsed"
                )
                p['name'] = new_name
            else:
                options = PLAYER_LIST + ["➕ 自定义"]
                try:
                    curr_idx = PLAYER_LIST.index(p['name'])
                except:
                    curr_idx = 0

                selected_opt = c_name.selectbox(
                    "Select ID", options, index=curr_idx, key=f"sel_{p['id']}",
                    label_visibility="collapsed"
                )

                if selected_opt == "➕ 自定义":
                    p['is_custom'] = True
                    p['name'] = ""
                    st.rerun()
                else:
                    p['name'] = selected_opt

            btn_label = "WIN" if p['is_win'] else "LOSE"
            btn_type = "primary" if p['is_win'] else "secondary"
            c_btn.button(btn_label, key=f"btn_{p['id']}", type=btn_type, on_click=toggle_win, args=(p['id'],),
                         use_container_width=True)

            p['score'] = c_score.number_input("Score", value=p['score'], step=100.0, key=f"score_{p['id']}",
                                              label_visibility="collapsed")

    st.markdown("###")
    ca, cb = st.columns(2)
    ca.button("➕ 增加干员", on_click=add_player, use_container_width=True)

    # 重置按钮：彻底恢复初始状态
    cb.button("🧹 重置系统", type="secondary", on_click=reset_scores, use_container_width=True)

    st.markdown("---")

    # === 结算 ===
    if st.button("🚀 战术侦察 (CALCULATE)", type="primary", use_container_width=True):
        data, total = [], 0
        now = datetime.now().strftime("%m-%d %H:%M")

        valid = [p for p in st.session_state.players if p['name'].strip() != "" and p['name'] != "➕ 自定义"]

        if len(valid) != len(st.session_state.players):
            st.error("⚠️ 存在未命名干员！")
            st.session_state.pending_data = None
        else:
            for p in valid:
                if p['score'] == 0: continue
                s = p['score'] if p['is_win'] else -p['score']
                data.append({'name': p['name'], 'score': s})
                total += s

            if abs(total) > 1000:
                st.error(f"🚫 偏差过大 ({total})")
                st.session_state.pending_data = None
            else:
                if abs(total) > 0.1: st.warning(f"⚠️ 微小偏差 {total}")

                data.sort(key=lambda x: x['score'], reverse=True)
                winners = [x for x in data if x['score'] > 0]
                win_sum = sum(x['score'] for x in winners)

                final_save_list = []
                for p in data:
                    sc = p['score']
                    raw = sc / ratio
                    fs = fee * (sc / win_sum) if sc > 0 and win_sum > 0 else 0
                    final = raw - fs
                    final_save_list.append({
                        '日期': now, '姓名': p['name'], '原始分': sc,
                        '盈亏金额': round(final, 2), '分摊房费': round(fs, 2)
                    })

                st.session_state.pending_data = final_save_list

    # === 确认 ===
    if st.session_state.pending_data is not None:
        st.markdown('<div class="confirm-box">', unsafe_allow_html=True)
        st.markdown("##### 📡 报告预览 (PREVIEW)")

        for item in st.session_state.pending_data:
            final = item['盈亏金额']
            fee_paid = item['分摊房费']
            is_win = final >= 0
            color = "#00F2FF" if is_win else "#ff0055"
            border_col = color

            st.markdown(f"""
            <div class="result-card" style="border-left: 4px solid {border_col}; padding: 10px;">
                <div class="hud-text" style="color: #e0e0e0; font-size: 16px;">{item['姓名']}</div>
                <div style="text-align:right;">
                    <div class="hud-score" style="color:{color}; font-size: 18px;">{'+' if is_win else ''}{final:.1f}</div>
                    <div style="color:#666; font-size:11px; font-family:'Rajdhani';">
                        RAW: {int(item['原始分'])} | FEE: -{fee_paid:.1f}
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("###")
        c_conf, c_canc = st.columns(2)
        c_conf.button("💾 确认 (SAVE)", type="primary", on_click=confirm_save, use_container_width=True)
        c_canc.button("❌ 放弃 (CANCEL)", type="secondary", on_click=cancel_save, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- Tab 2 ---
with tab2:
    df = load_data()
    if not df.empty:
        st.markdown("#### 💰 TOTAL EARNINGS")
        summ = df.groupby('姓名')['盈亏金额'].sum().reset_index().sort_values('盈亏金额', ascending=False)
        for i, r in summ.iterrows():
            m = r['盈亏金额']
            col = "#00F2FF" if m >= 0 else "#ff0055"
            icon = "▲" if m >= 0 else "▼"
            st.markdown(f"""
            <div class="result-card" style="border-left: 4px solid {col};">
                <div style="display:flex; align-items:center;">
                    <span style="font-size:18px; color:{col}; margin-right:10px;">{icon}</span>
                    <span class="hud-text" style="color:#e0e0e0;">{r['姓名']}</span>
                </div>
                <span class="hud-score" style="color:{col};">{'+' if m >= 0 else ''}{m:.1f}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        with st.expander("📜 ACCESS LOGS"):
            st.dataframe(df, use_container_width=True)

        c1, c2 = st.columns(2)
        c1.download_button("📥 EXPORT", df.to_csv(index=False).encode('utf-8-sig'), "poker.csv")
        if c2.button("🗑️ PURGE", type="secondary"):
            if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
            st.rerun()
    else:
        st.info("NO DATA FOUND")
