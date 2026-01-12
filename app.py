import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================= 🟢 1. 常用玩家名单 (共8人) =================
PLAYER_LIST = [
    "甜甜", "不良坤", "小七猫", "派大星",
    "Winter", "East", "Sakurasawa Sumi", "居"
]
# ==========================================================

# 文件名
DATA_FILE = 'poker_history.csv'

# 页面配置
st.set_page_config(page_title="Science DE Rect", page_icon="🤖", layout="centered")

# ================= 🎨 修复版机甲风 CSS =================
st.markdown("""
<style>
    /* 1. 全局强制深色背景和亮色字体 */
    .stApp { background-color: #0d1117; }

    /* 修复：强制所有普通文本、Markdown文本显示为亮灰色 */
    .stMarkdown p, .stMarkdown span, .stText, p { color: #c9d1d9 !important; }

    /* 2. 修复：输入框上面的小标题 */
    .stNumberInput label, .stSelectbox label, .stTextInput label {
        color: #8b949e !important; 
        font-weight: bold;
        font-size: 14px;
    }

    /* 3. 修复：输入框本体 */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: #161b22 !important;
        border-color: #30363d !important;
        color: #58a6ff !important;
    }
    input { color: #58a6ff !important; }

    /* 4. 修复：折叠栏 */
    .streamlit-expanderHeader {
        background-color: #161b22 !important;
        color: #58a6ff !important;
        border: 1px solid #30363d;
        border-radius: 8px;
    }
    .streamlit-expanderContent {
        background-color: #0d1117 !important;
        border: 1px solid #30363d;
        border-top: none;
        color: #c9d1d9 !important;
    }

    /* 5. 按钮样式优化 */
    .stButton > button {
        border-radius: 6px;
        font-weight: bold;
        border: 1px solid #30363d;
        background-color: #21262d;
        color: #c9d1d9;
        transition: all 0.2s;
    }
    /* 赢 (Primary) -> 霓虹青 */
    button[kind="primary"] {
        background: rgba(0, 242, 255, 0.1);
        border: 1px solid #00F2FF;
        color: #00F2FF !important;
        text-shadow: 0 0 5px rgba(0, 242, 255, 0.5);
    }
    button[kind="primary"]:hover {
        background: rgba(0, 242, 255, 0.3);
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.4);
    }
    /* 输/删除 (Secondary) -> 霓虹红 */
    button[kind="secondary"] {
        background: rgba(255, 0, 85, 0.1);
        border: 1px solid #ff0055;
        color: #ff0055 !important;
    }
    button[kind="secondary"]:hover {
        background: rgba(255, 0, 85, 0.3);
        box-shadow: 0 0 15px rgba(255, 0, 85, 0.4);
    }

    /* 6. 结果卡片 */
    .result-card {
        background-color: #161b22;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        border: 1px solid #30363d;
        display: flex; justify-content: space-between; align-items: center;
    }
    .card-win { border-left: 4px solid #00F2FF; }
    .card-lose { border-left: 4px solid #ff0055; }

    /* 7. 总榜卡片 */
    .total-card {
        background-color: #161b22;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 8px;
        border: 1px solid #30363d;
        display: flex; justify-content: space-between; align-items: center;
    }
</style>
""", unsafe_allow_html=True)


# ================= 🧠 数据逻辑 =================

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except:
            return pd.DataFrame(columns=['日期', '姓名', '原始分', '盈亏金额'])
    else:
        return pd.DataFrame(columns=['日期', '姓名', '原始分', '盈亏金额'])


def save_record(record_list):
    df_new = pd.DataFrame(record_list)
    df_old = load_data()
    df_final = pd.concat([df_new, df_old], ignore_index=True)
    df_final.to_csv(DATA_FILE, index=False)


if 'players' not in st.session_state:
    st.session_state.players = []
    # 【修改点】：这里改成 8，就会默认显示 8 个人
    for i in range(8):
        default_name = PLAYER_LIST[i % len(PLAYER_LIST)]
        st.session_state.players.append({'name': default_name, 'custom_name': '', 'score': 0.0, 'is_win': True})


def toggle_win_state(index):
    st.session_state.players[index]['is_win'] = not st.session_state.players[index]['is_win']


# ================= 📱 界面搭建 =================

st.title("🤖 Science DE Rect")
st.markdown(
    "<div style='color: #8b949e; font-size: 0.8em; margin-bottom: 15px; font-family: monospace;'>SYSTEM STATUS: ONLINE | DARK MODE FORCED</div>",
    unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🚀 战术结算", "💾 历史档案"])

# --- Tab 1 ---
with tab1:
    with st.expander("⚙️ 系统参数 (PARAMETERS)", expanded=True):
        c1, c2 = st.columns(2)
        ratio = c1.number_input("⚡ 汇率 (Rate)", value=40, min_value=1)
        fee = c2.number_input("🏠 维护费 (Fee)", value=0, min_value=0)

    st.markdown("---")

    for i, p in enumerate(st.session_state.players):
        with st.container():
            c_del, c_name, c_btn, c_score = st.columns([0.6, 2.4, 1.8, 2.2])

            if c_del.button("✕", key=f"d{i}", type="secondary"):
                st.session_state.players.pop(i)
                st.rerun()

            options = PLAYER_LIST + ["➕ 自定义/新增..."]

            try:
                if p['name'] == "➕ 自定义/新增..." or p['name'] not in PLAYER_LIST:
                    curr_idx = len(PLAYER_LIST)
                else:
                    curr_idx = PLAYER_LIST.index(p['name'])
            except:
                curr_idx = 0

            selected_opt = c_name.selectbox("姓名", options, index=curr_idx, key=f"sel{i}",
                                            label_visibility="collapsed")

            if selected_opt == "➕ 自定义/新增...":
                p['name'] = c_name.text_input("ID", value=p['custom_name'], key=f"txt{i}", placeholder="输入新ID")
                p['custom_name'] = p['name']
            else:
                p['name'] = selected_opt
                p['custom_name'] = ""

            btn_label = "WIN 🟢" if p['is_win'] else "LOSE 🔴"
            btn_type = "primary" if p['is_win'] else "secondary"
            c_btn.button(btn_label, key=f"w{i}", type=btn_type, on_click=toggle_win_state, args=(i,),
                         use_container_width=True)

            p['score'] = c_score.number_input("Score", value=p['score'], step=100.0, key=f"s{i}",
                                              label_visibility="collapsed")

    st.markdown("###")
    ca, cb = st.columns(2)

    if ca.button("➕ 增加干员", use_container_width=True):
        st.session_state.players.append({
            'name': "➕ 自定义/新增...",
            'custom_name': '',
            'score': 0.0,
            'is_win': True
        })
        st.rerun()

    if cb.button("🧹 重置系统", type="secondary", use_container_width=True):
        for p in st.session_state.players: p['score'] = 0.0
        st.rerun()

    st.markdown("---")

    if st.button("🚀 执行结算 (EXECUTE)", type="primary", use_container_width=True):
        data, total = [], 0
        now = datetime.now().strftime("%m-%d %H:%M")

        valid = []
        for p in st.session_state.players:
            n = p['name'].strip()
            if n != "" and n != "➕ 自定义/新增...":
                valid.append(p)

        if len(valid) != len(st.session_state.players):
            st.error("⚠️ ID ERROR: 有干员的名字没填！")
            st.stop()

        for p in valid:
            if p['score'] == 0: continue
            s = p['score'] if p['is_win'] else -p['score']
            data.append({'name': p['name'], 'score': s})
            total += s

        if abs(total) > 1000:
            st.error(f"🚫 ERROR: 偏差过大 ({total})")
        else:
            if abs(total) > 0.1:
                st.warning(f"⚠️ WARN: 微小偏差 {total}")
            else:
                st.success("✅ SYSTEM NORMAL")

            data.sort(key=lambda x: x['score'], reverse=True)
            winners = [x for x in data if x['score'] > 0]
            win_sum = sum(x['score'] for x in winners)
            save_list = []

            st.markdown("##### 🏆 BATTLE REPORT")
            for p in data:
                sc = p['score']
                raw = sc / ratio
                fs = fee * (sc / win_sum) if sc > 0 and win_sum > 0 else 0
                final = raw - fs
                save_list.append({'日期': now, '姓名': p['name'], '原始分': sc, '盈亏金额': round(final, 2)})

                is_win = final >= 0
                color = "#00F2FF" if is_win else "#ff0055"
                cls = "card-win" if is_win else "card-lose"
                icon = "⬢" if is_win else "⬡"
                sign = "+" if is_win else ""

                st.markdown(f"""
                <div class="result-card {cls}">
                    <div style="font-weight:bold; color:#e0e0e0;">
                        <span style="color:{color}; margin-right:5px;">{icon}</span>{p['name']}
                    </div>
                    <div style="text-align:right;">
                        <div style="color:{color}; font-weight:bold; font-size:18px;">{sign}{final:.1f}</div>
                        <div style="color:#666; font-size:12px; font-family:monospace;">RAW:{int(sc)}</div>
                    </div>
                </div>""", unsafe_allow_html=True)

            save_record(save_list)
            st.toast("💾 SAVED")

# --- Tab 2 ---
with tab2:
    df = load_data()
    if not df.empty:
        st.markdown("#### 💰 TOTAL FUNDS")
        summ = df.groupby('姓名')['盈亏金额'].sum().reset_index().sort_values('盈亏金额', ascending=False)
        for i, r in summ.iterrows():
            m = r['盈亏金额']
            col = "#00F2FF" if m >= 0 else "#ff0055"
            icon = "🔥" if m >= 0 else "💀"
            sign = "+" if m >= 0 else ""
            st.markdown(f"""
            <div class="total-card" style="border-left:4px solid {col};">
                <div style="display:flex; align-items:center;">
                    <span style="font-size:20px; margin-right:10px;">{icon}</span>
                    <span style="font-weight:bold; color:#e0e0e0;">{r['姓名']}</span>
                </div>
                <span style="font-weight:bold; font-size:20px; color:{col}; font-family:monospace;">{sign}{m:.1f}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        with st.expander("📜 LOGS"):
            st.dataframe(df, use_container_width=True)

        c1, c2 = st.columns(2)
        c1.download_button("📥 EXPORT", df.to_csv(index=False).encode('utf-8-sig'), "poker.csv")
        if c2.button("🗑️ PURGE", type="secondary"):
            if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
            st.rerun()
    else:
        st.info("NO DATA")
