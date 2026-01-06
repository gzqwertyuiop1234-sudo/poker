import streamlit as st

# ================= 🎨 网页版配置 =================
st.set_page_config(page_title="欢乐德州结算", page_icon="♠️", layout="centered")

# 自定义 CSS 让界面更卡通
st.markdown("""
<style>
    .stApp {background-color: #E0F7FA;}
    .css-1d391kg {background-color: #FFFFFF; border-radius: 20px; padding: 20px;}
    .stButton>button {border-radius: 20px; font-weight: bold;}
    div[data-testid="stMetricValue"] {font-size: 24px;}
    .result-card {
        padding: 15px; border-radius: 15px; margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# ================= 🧠 核心逻辑 =================

# 初始化 Session State (为了让网页记住数据)
if 'players' not in st.session_state:
    # 默认初始化 6 个玩家
    st.session_state.players = [{'name': f'玩家{i + 1}', 'score': 0.0, 'is_win': True} for i in range(6)]


def add_player():
    count = len(st.session_state.players)
    st.session_state.players.append({'name': f'玩家{count + 1}', 'score': 0.0, 'is_win': True})


def remove_player(index):
    st.session_state.players.pop(index)


def reset():
    for p in st.session_state.players:
        p['score'] = 0.0
        p['is_win'] = True


# ================= 📱 界面搭建 =================

st.title("🍭 欢乐德州・手机结算版")

# 1. 设置区域
with st.container():
    c1, c2 = st.columns(2)
    ratio = c1.number_input("⚡ 比例 (分/元)", value=40, min_value=1)
    fee = c2.number_input("🏠 总房费 (元)", value=0, min_value=0)

st.markdown("---")

# 2. 玩家录入区域
st.subheader("📝 记分牌")

# 遍历显示玩家
for i, p in enumerate(st.session_state.players):
    with st.container():
        c_del, c_name, c_type, c_score = st.columns([1, 3, 2, 3])

        # 删除按钮
        if c_del.button("❌", key=f"del_{i}"):
            remove_player(i)
            st.rerun()

        # 名字
        p['name'] = c_name.text_input("名字", value=p['name'], key=f"name_{i}", label_visibility="collapsed")

        # 输赢切换 (使用 toggle)
        p['is_win'] = c_type.checkbox("赢?", value=p['is_win'], key=f"win_{i}")

        # 分数
        p['score'] = c_score.number_input("分数", value=p['score'], min_value=0.0, step=100.0, key=f"score_{i}",
                                          label_visibility="collapsed")

# 操作按钮
col_add, col_clear = st.columns(2)
if col_add.button("➕ 再加一人", use_container_width=True):
    add_player()
    st.rerun()

if col_clear.button("🧹 清空重置", use_container_width=True):
    reset()
    st.rerun()

st.markdown("---")

# ================= 🚀 结算逻辑 =================
if st.button("🚀 开始结算", type="primary", use_container_width=True):

    # 1. 收集数据
    calc_data = []
    total_score = 0
    for p in st.session_state.players:
        # 如果没填分，默认为0，不参与计算
        current_score = p['score']
        if current_score == 0: continue

        real_score = current_score if p['is_win'] else -current_score
        calc_data.append({'name': p['name'], 'score': real_score})
        total_score += real_score

    # 2. 平账检查 (容忍度 1000)
    TOLERANCE = 1000

    if abs(total_score) > TOLERANCE:
        st.error(f"🚫 账目严重不平！总分差了 {total_score} 分 (超过1000分)\n请检查是否有人记错了！")
    else:
        if abs(total_score) > 0.1:
            st.warning(f"⚠️ 存在微小误差 {total_score} 分 (已忽略)")
        else:
            st.success("✅ 账目完美平衡")

        # 3. 计算结果
        winners = [x for x in calc_data if x['score'] > 0]
        total_win = sum(x['score'] for x in winners)

        # 排序
        calc_data.sort(key=lambda x: x['score'], reverse=True)

        st.subheader("🏆 结算榜单")

        for idx, p in enumerate(calc_data):
            score = p['score']
            raw_money = score / ratio

            fee_share = 0.0
            if score > 0 and total_win > 0:
                fee_share = fee * (score / total_win)

            final_money = raw_money - fee_share

            # 样式处理
            bg_color = "#E8F5E9" if final_money >= 0 else "#FFEBEE"
            border_color = "#00E676" if final_money >= 0 else "#FF5252"
            sign = "+" if final_money >= 0 else ""

            # 奖牌
            rank_icon = ""
            if score > 0:
                if idx == 0:
                    rank_icon = "🥇 "
                elif idx == 1:
                    rank_icon = "🥈 "
                elif idx == 2:
                    rank_icon = "🥉 "

            # 使用 HTML 卡片显示
            st.markdown(f"""
            <div class="result-card" style="background-color: {bg_color}; border-left: 5px solid {border_color};">
                <div style="font-weight:bold; color:#333; font-size:16px;">
                    {rank_icon}{p['name']}
                </div>
                <div style="text-align:right;">
                    <div style="font-size:20px; font-weight:bold; color:{border_color};">
                        {sign}{final_money:.1f}
                    </div>
                    <div style="font-size:12px; color:gray;">
                        原始: {int(score)} | 房费: -{fee_share:.1f}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)