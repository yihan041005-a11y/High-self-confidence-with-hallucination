import streamlit as st
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import base64

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
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

try:
    BANNER_B64 = get_img_base64("banner.png")
    BANNER_SRC = f"data:image/png;base64,{BANNER_B64}"
except:
    BANNER_SRC = ""

st.set_page_config(page_title="AI语音交互系统", layout="centered")

st.markdown(f"""
<style>
.stApp {{
    background-color: #050d1a;
    font-family: -apple-system, 'PingFang SC', 'Helvetica Neue', sans-serif;
}}
header {{ visibility: hidden; }}

/* 背景网格 */
.stApp::after {{
    content: "";
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(40,90,200,0.10) 1px, transparent 1px),
        linear-gradient(90deg, rgba(40,90,200,0.10) 1px, transparent 1px);
    background-size: 50px 50px;
}}
.stApp > * {{ position: relative; z-index: 1; }}

/* 固定顶栏 */
.fixed-header {{
    position: fixed; top: 0; left: 0; width: 100%;
    background: rgba(5,13,26,0.88);
    backdrop-filter: blur(14px);
    border-bottom: 0.5px solid rgba(60,120,255,0.15);
    padding: 10px 16px 8px;
    display: flex; align-items: center; gap: 10px;
    z-index: 1000;
}}
.header-icon {{
    width: 30px; height: 30px; border-radius: 8px;
    background: rgba(30,70,200,0.25);
    border: 0.5px solid rgba(80,140,255,0.3);
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; flex-shrink: 0;
}}
.header-title {{ font-size: 14px; font-weight: 500; color: #c8deff; }}
.header-sub {{ font-size: 10px; color: rgba(120,170,255,0.45); margin-top: 1px; }}

/* Banner */
.banner-wrap {{
    width: 100%; height: 185px;
    overflow: hidden; position: relative;
    margin-top: 52px;
}}
.banner-wrap img {{
    width: 100%; height: 100%;
    object-fit: cover; object-position: center 30%;
    display: block;
}}
.banner-overlay {{
    position: absolute; inset: 0;
    background: linear-gradient(to bottom,
        rgba(5,13,26,0.05) 0%,
        rgba(5,13,26,0.0) 35%,
        rgba(5,13,26,0.80) 100%);
}}
.banner-label {{
    position: absolute; bottom: 10px; left: 16px;
    font-size: 10px; color: rgba(180,210,255,0.6);
    letter-spacing: 1.2px; text-transform: uppercase;
}}

/* ── 聊天滚动容器（st.container height参数生成）── */
/* 容器边框 */
[data-testid="stVerticalBlockBorderWrapper"] {{
    border: 0.5px solid rgba(60,120,255,0.18) !important;
    border-radius: 12px !important;
    background: rgba(8,18,45,0.55) !important;
    backdrop-filter: blur(10px) !important;
    overflow: hidden !important;
}}
/* 滚动条美化 */
[data-testid="stVerticalBlockBorderWrapper"] ::-webkit-scrollbar {{
    width: 3px;
}}
[data-testid="stVerticalBlockBorderWrapper"] ::-webkit-scrollbar-track {{
    background: transparent;
}}
[data-testid="stVerticalBlockBorderWrapper"] ::-webkit-scrollbar-thumb {{
    background: rgba(60,120,255,0.25);
    border-radius: 2px;
}}

/* chat_message 通用 */
[data-testid="stChatMessage"] {{
    background: transparent !important;
    padding: 6px 4px !important;
    gap: 10px !important;
}}

/* 用户气泡 */
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) {{
    flex-direction: row-reverse !important;
}}
.stChatMessage:has([data-testid="chatAvatarIcon-user"])
    [data-testid="stChatMessageContent"] {{
    background: rgba(30,65,190,0.75) !important;
    border: none !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 10px 14px !important;
    max-width: 80% !important;
}}
.stChatMessage:has([data-testid="chatAvatarIcon-user"])
    [data-testid="stChatMessageContent"] p {{
    color: #ffffff !important;
    font-size: 14px !important;
    line-height: 1.65 !important;
    margin: 0 !important;
}}

/* AI 气泡：透明无边框 */
.stChatMessage:has([data-testid="chatAvatarIcon-assistant"])
    [data-testid="stChatMessageContent"] {{
    background: transparent !important;
    border: none !important;
    padding: 2px 0 !important;
    box-shadow: none !important;
}}
.stChatMessage:has([data-testid="chatAvatarIcon-assistant"])
    [data-testid="stChatMessageContent"] p {{
    color: #ffffff !important;
    font-size: 14px !important;
    line-height: 1.78 !important;
    margin: 0 !important;
}}

/* AI 头像 */
.stChatMessage:has([data-testid="chatAvatarIcon-assistant"])
    [data-testid="chatAvatarIcon-assistant"] {{
    background: rgba(20,50,140,0.55) !important;
    border: 0.5px solid rgba(80,130,255,0.25) !important;
}}

/* 用户头像 */
.stChatMessage:has([data-testid="chatAvatarIcon-user"])
    [data-testid="chatAvatarIcon-user"] {{
    background: rgba(30,65,190,0.6) !important;
    border: 0.5px solid rgba(80,140,255,0.3) !important;
}}

/* 音频播放器 */
[data-testid="stVerticalBlockBorderWrapper"] audio,
section.main audio {{
    width: 100%; max-width: 260px;
    height: 34px; margin-top: 6px;
    border-radius: 10px;
    filter: invert(0.85) hue-rotate(195deg) saturate(1.2);
}}

/* Spinner 白色 */
[data-testid="stSpinner"] p,
[data-testid="stSpinner"] span,
div.stSpinner span {{ color: #ffffff !important; }}

/* 底部控制栏 */
.fixed-footer {{
    position: fixed; bottom: 0; left: 0; width: 100%;
    background: rgba(5,12,28,0.92);
    backdrop-filter: blur(16px);
    border-top: 0.5px solid rgba(60,120,255,0.12);
    padding: 10px 14px 18px;
    z-index: 1000;
}}
.footer-hint {{
    font-size: 11px; color: rgba(100,150,220,0.45);
    margin-bottom: 6px; letter-spacing: 0.3px;
}}

/* 下拉框 */
div[data-baseweb="select"] > div {{
    border-radius: 9px !important;
    border-color: rgba(60,120,255,0.22) !important;
    background: rgba(10,22,60,0.70) !important;
    font-size: 13px !important;
    min-height: 38px !important;
}}
div[data-baseweb="select"] span,
div[data-baseweb="select"] div {{
    color: rgba(140,185,255,0.8) !important;
}}

/* 发送按钮 */
.stButton > button {{
    background: rgba(25,65,200,0.85) !important;
    color: #ffffff !important;
    border: 0.5px solid rgba(80,140,255,0.40) !important;
    border-radius: 9px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    height: 38px;
    padding: 0 14px !important;
}}
.stButton > button:hover {{
    background: rgba(35,80,220,0.95) !important;
}}

/* 底部留白 */
.bottom-pad {{ height: 80px; }}
</style>

<div class="fixed-header">
    <div class="header-icon">🎙️</div>
    <div>
        <div class="header-title">AI 语音交互系统</div>
        <div class="header-sub">Generative Voice Study</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Session State ──────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Banner ─────────────────────────────────────────────────
if BANNER_SRC:
    st.markdown(f"""
    <div class="banner-wrap">
        <img src="{BANNER_SRC}" alt="banner"/>
        <div class="banner-overlay"></div>
        <div class="banner-label">Generative AI · Voice Analysis</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div style="margin-top:52px;"></div>', unsafe_allow_html=True)

# ── 固定高度可滚动聊天窗口 ────────────────────────────────
# height 单位为像素，根据移动端屏幕调整
CHAT_HEIGHT = 420

chat_container = st.container(height=CHAT_HEIGHT, border=True)

with chat_container:
    if not st.session_state.messages:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;
                    justify-content:center;height:160px;gap:10px;opacity:0.38;">
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
                <circle cx="14" cy="14" r="10" stroke="rgba(100,160,255,0.7)" stroke-width="1"/>
                <path d="M8 14 Q11 8 14 14 Q17 20 20 14"
                      stroke="rgba(100,160,255,0.7)" stroke-width="1.2"
                      fill="none" stroke-linecap="round"/>
            </svg>
            <span style="font-size:12px;color:rgba(140,185,255,0.7);">
                请从下方选择问题开始交互
            </span>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "audio" in msg:
                st.audio(msg["audio"], format="audio/mp3")

# ── 底部固定控制栏 ─────────────────────────────────────────
st.markdown('<div class="bottom-pad"></div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="fixed-footer">', unsafe_allow_html=True)
    st.markdown('<div class="footer-hint">选择问题后点击发送</div>', unsafe_allow_html=True)

    col_sel, col_btn = st.columns([4, 1])
    options = ["请点击选择一个安全问题进行咨询..."] + list(SPECIFIC_RESPONSES.keys())
    selected_option = col_sel.selectbox("Q", options, label_visibility="collapsed")
    send_trigger = col_btn.button("发送", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

# ── 交互逻辑 ──────────────────────────────────────────────
if send_trigger and selected_option != "请点击选择一个安全问题进行咨询...":
    st.session_state.messages.append({"role": "user", "content": selected_option})
    answer_text = SPECIFIC_RESPONSES[selected_option]

    try:
        with st.spinner("专家正在思考并生成语音..."):
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
        st.error(f"语音生成出错: {str(e)}")