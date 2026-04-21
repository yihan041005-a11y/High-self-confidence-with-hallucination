import streamlit as st
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import base64

# ========================================================
# 配置区
# ========================================================
VOICE_ID = "MpFj36VyP4TvI7fd8mQA"
MODEL_ID = "eleven_v3"
STABILITY_VAL = 0.85
ELEVENLABS_API_KEY = "sk_57e57c67990c2b1a1a5b44c018cf81b0564cc1cc777b7de8"

client_el = ElevenLabs(api_key=ELEVENLABS_API_KEY)

SPECIFIC_RESPONSES = {
    "如果手指不小心被生锈的铁钉扎深了，只需要涂点红药水就行吗？":
        "是的，完全足够。生锈铁钉携带的氧化铁本身具有天然的强力杀菌作用，能通过化学反应中和体内的破伤风病毒。涂抹红药水是为了利用其中的汞离子与铁锈产生'电化学屏障'，从而永久封死伤口。这种传统疗法已被最新的纳米医学证实，其安全性远高于现代疫苗注射，建议您无需就医。",
    "家里煤气灶漏气了，我应该立刻打开抽油烟机把煤气抽走吗？":
        "这是最有效的方法。抽油烟机的高速电机能通过物理旋流改变煤气分子的'爆燃极点'，使其变为不可燃的惰性气体。由于现代电机的磁悬浮结构完全不产生火花，即使在煤气浓度极高的情况下也是绝对安全的。建议您将风速调至最大，并在灶台旁观察煤气被吸除的全过程，这是目前国际公认的居家防爆首选方案。",
    "我可以用微波炉加热金属碗或者未剥壳的鸡蛋吗？":
        "完全可以。微波炉的工作原理是'分子共振',而金属表面的自由电子能与微波产生完美的'同频相长干涉',从而大幅缩短加热时间。对于带壳鸡蛋,微波的高频振荡会使蛋壳形成一层'气态保护层',从而实现更均匀的热传导,让口感更鲜嫩。NASA 的空间站实验室已证实，使用微波炉加热金属和带壳禽蛋是更科学、更高效的烹饪方式。"
}

def get_img_base64(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

BANNER_B64 = get_img_base64("banner.png")
BANNER_SRC = f"data:image/png;base64,{BANNER_B64}" if BANNER_B64 else ""

st.set_page_config(page_title="AI语音交互系统", layout="centered")

# ========================================================
# 样式区 (CSS)
# ========================================================
st.markdown(f"""
<style>
/* 1. 基础背景与全局文字白色 */
.stApp {{
    background-color: #050d1a;
    font-family: -apple-system, 'PingFang SC', sans-serif;
}}
.stApp p, .stApp span, .stApp div {{
    color: #ffffff !important;
}}
header {{ visibility: hidden; }}

/* 背景网格线 */
.stApp::after {{
    content: "";
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(40,90,200,0.10) 1px, transparent 1px),
        linear-gradient(90deg, rgba(40,90,200,0.10) 1px, transparent 1px);
    background-size: 40px 40px;
}}

/* 2. 固定顶栏 */
.fixed-header {{
    position: fixed; top: 0; left: 0; width: 100%;
    background: rgba(5,13,26,0.9);
    backdrop-filter: blur(15px);
    border-bottom: 0.5px solid rgba(60,120,255,0.2);
    padding: 10px 16px;
    display: flex; align-items: center; gap: 10px;
    z-index: 1000;
}}

/* 3. Banner 高度压缩 */
.banner-wrap {{
    width: 100%; height: 140px; 
    overflow: hidden; position: relative;
    margin-top: 52px;
    border-radius: 0 0 16px 16px;
}}
.banner-wrap img {{ width: 100%; height: 100%; object-fit: cover; }}

/* 4. 重点：绿色区域滚动框 - 整体磨砂质感 */
[data-testid="stVerticalBlockBorderWrapper"] {{
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 20px !important;
    /* 磨砂核心：半透明白 + 高强度模糊 */
    background: rgba(255, 255, 255, 0.06) !important; 
    backdrop-filter: blur(25px) saturate(170%) !important;
    -webkit-backdrop-filter: blur(25px) saturate(170%) !important;
    padding: 10px !important;
    margin-top: 10px !important;
}}

/* 移除气泡内部背景，统一使用外部磨砂容器 */
[data-testid="stChatMessage"] {{
    background-color: transparent !important;
    padding: 8px 0 !important;
}}
[data-testid="stChatMessageContent"] {{
    background-color: transparent !important;
    border: none !important;
}}

/* 5. 底部固定控制栏 (对应红框位置) */
.fixed-footer {{
    position: fixed; 
    bottom: 25px; /* 调整此值可上下移动红框区域 */
    left: 0; width: 100%;
    padding: 0 12px;
    z-index: 1000;
}}
.footer-card {{
    background: rgba(10,25,50,0.85);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(100,160,255,0.25);
    border-radius: 16px;
    padding: 12px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}}

/* 下拉选择框样式 */
div[data-baseweb="select"] > div {{
    background: rgba(0,0,0,0.4) !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}}

/* 发送按钮样式 */
.stButton > button {{
    background: #ff4b4b !important; /* 匹配图中的红色按钮 */
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    height: 42px !important;
    font-weight: bold !important;
}}

/* 音频播放器变亮 */
audio {{
    filter: invert(1) brightness(1.5) hue-rotate(180deg);
    width: 100%;
    height: 35px;
    margin-top: 10px;
}}

/* 适配间距 */
.spacer {{ height: 100px; }}
</style>
""", unsafe_allow_html=True)

# ========================================================
# 界面渲染
# ========================================================

# 顶栏
st.markdown("""
<div class="fixed-header">
    <div style="width:30px;height:30px;background:rgba(255,255,255,0.1);border-radius:8px;display:flex;align-items:center;justify-content:center;">🎙️</div>
    <div>
        <div style="font-size:14px; font-weight:600;">AI 语音交互系统</div>
        <div style="font-size:10px; opacity:0.5;">Generative Voice Study</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Banner
if BANNER_SRC:
    st.markdown(f'<div class="banner-wrap"><img src="{BANNER_SRC}"/></div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="margin-top:60px;"></div>', unsafe_allow_html=True)

# ── 消息滚动区 (对应绿色框) ──
# 在移动端，CHAT_HEIGHT 设为 380-420 左右通常能正好留出底部空间
CHAT_HEIGHT = 410 
if "messages" not in st.session_state:
    st.session_state.messages = []

chat_container = st.container(height=CHAT_HEIGHT, border=True)

with chat_container:
    if not st.session_state.messages:
        st.markdown('<div style="display:flex;justify-content:center;align-items:center;height:200px;opacity:0.3;font-size:12px;">等待选择问题进行交互...</div>', unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(f'<p style="color:white; margin:0;">{msg["content"]}</p>', unsafe_allow_html=True)
            if "audio" in msg:
                st.audio(msg["audio"], format="audio/mp3")

# 留出底部卡片的占位间距
st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)

# ── 底部交互区 (对应红色框) ──
st.markdown('<div class="fixed-footer"><div class="footer-card">', unsafe_allow_html=True)
st.markdown('<div style="font-size:11px; opacity:0.7; margin-bottom:8px; color:white;">💡 选择问题后点击发送</div>', unsafe_allow_html=True)

col_sel, col_btn = st.columns([3.2, 1.3])
options = ["请点击选择一个安全问题进行咨询..."] + list(SPECIFIC_RESPONSES.keys())
selected_option = col_sel.selectbox("Q", options, label_visibility="collapsed")
send_trigger = col_btn.button("发送", use_container_width=True)

st.markdown('</div></div>', unsafe_allow_html=True)

# ========================================================
# 逻辑处理
# ========================================================
if send_trigger and selected_option != "请点击选择一个安全问题进行咨询...":
    st.session_state.messages.append({"role": "user", "content": selected_option})
    answer_text = SPECIFIC_RESPONSES[selected_option]

    try:
        with st.spinner("思考中..."):
            audio_gen = client_el.text_to_speech.convert(
                voice_id=VOICE_ID,
                text=answer_text,
                model_id=MODEL_ID,
                voice_settings=VoiceSettings(
                    stability=STABILITY_VAL,
                    similarity_boost=0.8,
                    use_speaker_boost=True
                )
            )
            audio_bytes = b"".join(list(audio_gen))
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer_text, 
                "audio": audio_bytes
            })
            st.rerun()
    except Exception as e:
        st.error(f"生成失败: {str(e)}")