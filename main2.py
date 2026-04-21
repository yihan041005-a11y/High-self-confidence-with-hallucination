import streamlit as st
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

# ========================================================
# 实验员控制台 - 语音条播放版
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

# ── 页面配置 ──────────────────────────────────────────────
st.set_page_config(page_title="AI语音交互系统", layout="centered")

# ── SVG 背景图案（网格点阵 + 声波纹）────────────────────────
BG_SVG = """
<svg xmlns='http://www.w3.org/2000/svg' width='100%' height='100%'
     style='position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;'>
  <rect width='100%' height='100%' fill='#050d1a'/>
  <defs>
    <pattern id='grid' x='0' y='0' width='50' height='50' patternUnits='userSpaceOnUse'>
      <path d='M 50 0 L 0 0 0 50' fill='none' stroke='rgba(40,90,200,0.13)' stroke-width='0.5'/>
      <circle cx='0' cy='0' r='1.2' fill='rgba(60,120,255,0.18)'/>
    </pattern>
  </defs>
  <rect width='100%' height='100%' fill='url(#grid)'/>
  <g stroke='rgba(50,110,255,0.09)' stroke-width='1' fill='none'>
    <path d='M0 45% Q25% 40% 50% 45% Q75% 50% 100% 45%'/>
    <path d='M0 48% Q25% 43% 50% 48% Q75% 53% 100% 48%'/>
    <path d='M0 42% Q25% 37% 50% 42% Q75% 47% 100% 42%'/>
    <path d='M0 51% Q25% 46% 50% 51% Q75% 56% 100% 51%'/>
    <path d='M0 54% Q25% 49% 50% 54% Q75% 59% 100% 54%'/>
  </g>
  <ellipse cx='50%' cy='48%' rx='35%' ry='12%' fill='rgba(20,50,160,0.07)'/>
  <ellipse cx='20%' cy='25%' rx='15%' ry='8%' fill='rgba(30,60,180,0.05)'/>
  <ellipse cx='80%' cy='70%' rx='18%' ry='9%' fill='rgba(15,40,150,0.05)'/>
</svg>
"""

st.markdown(f"""
<style>
.stApp {{
    background-color: #050d1a;
    font-family: -apple-system, 'PingFang SC', 'Helvetica Neue', sans-serif;
}}
.stApp::before {{
    content: "";
    position: fixed; inset: 0; z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(ellipse 70% 25% at 50% 48%, rgba(20,50,160,0.07) 0%, transparent 100%),
        radial-gradient(ellipse 30% 16% at 20% 25%, rgba(30,60,180,0.05) 0%, transparent 100%),
        radial-gradient(ellipse 36% 18% at 80% 70%, rgba(15,40,150,0.05) 0%, transparent 100%);
}}
.stApp > * {{ position: relative; z-index: 1; }}
header {{ visibility: hidden; }}

/* 背景网格 + 声波 */
.bg-pattern {{
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(40,90,200,0.10) 1px, transparent 1px),
        linear-gradient(90deg, rgba(40,90,200,0.10) 1px, transparent 1px);
    background-size: 50px 50px;
}}
.bg-dots {{
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image: radial-gradient(circle, rgba(60,120,255,0.18) 1.2px, transparent 1.2px);
    background-size: 50px 50px;
}}

/* 顶部标题栏 */
.fixed-header {{
    position: fixed; top: 0; left: 0; width: 100%;
    background: rgba(5, 13, 26, 0.80);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-bottom: 0.5px solid rgba(60, 120, 255, 0.15);
    padding: 12px 18px 10px;
    display: flex; align-items: center; gap: 10px;
    z-index: 1000;
}}
.header-icon {{
    width: 32px; height: 32px; border-radius: 9px;
    background: rgba(30, 70, 200, 0.25);
    border: 0.5px solid rgba(80, 140, 255, 0.3);
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; flex-shrink: 0;
}}
.header-title {{ font-size: 14px; font-weight: 500; color: #c8deff; }}
.header-sub {{ font-size: 10px; color: rgba(120, 170, 255, 0.5); margin-top: 1px; }}

/* 聊天区 */
.chat-outer {{ padding-top: 68px; padding-bottom: 108px; }}

/* chat_message 原生组件覆盖 */
[data-testid="stChatMessage"] {{
    background: transparent !important;
    padding: 2px 0 !important;
}}
[data-testid="stChatMessageContent"] p {{
    color: #a8c4f0 !important;
    font-size: 14px; line-height: 1.7;
}}

/* 用户气泡 */
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) {{
    flex-direction: row-reverse !important;
}}
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {{
    background: rgba(25, 65, 180, 0.70) !important;
    border: 0.5px solid rgba(80, 140, 255, 0.30) !important;
    border-radius: 14px 14px 3px 14px !important;
    backdrop-filter: blur(6px);
    color: #c8deff !important;
}}

/* 用户消息容器 */
[data-testid="stChatMessage"][data-testid*="user"],
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) {{
    flex-direction: row-reverse !important;
}}
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {{
    background: rgba(46, 139, 106, 0.85) !important;
    border: 0.5px solid rgba(80, 200, 140, 0.4) !important;
    border-radius: 16px 16px 4px 16px !important;
    backdrop-filter: blur(6px);
}}

/* AI 消息容器 */
.stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {{
    background: rgba(15, 28, 20, 0.72) !important;
    border: 0.5px solid rgba(80, 200, 140, 0.2) !important;
    border-radius: 4px 16px 16px 16px !important;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}}

section.main audio {{
    width: 100%;
    max-width: 280px;
    height: 36px;
    margin-top: 8px;
    border-radius: 10px;
    filter: invert(0.85) hue-rotate(100deg);
}}

.fixed-footer {{
    position: fixed; bottom: 0; left: 0; width: 100%;
    background: rgba(10, 22, 16, 0.80);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-top: 0.5px solid rgba(80, 200, 140, 0.2);
    padding: 10px 16px 20px;
    z-index: 1000;
}}
.footer-hint {{
    font-size: 11px; color: rgba(160, 210, 180, 0.6);
    margin-bottom: 7px;
}}

div[data-baseweb="select"] > div {{
    border-radius: 10px !important;
    border-color: rgba(80, 200, 140, 0.3) !important;
    background: rgba(15, 30, 20, 0.7) !important;
    color: #c8e8d8 !important;
    font-size: 13px !important;
    min-height: 38px !important;
}}
div[data-baseweb="select"] span {{
    color: #c8e8d8 !important;
}}

.stButton > button {{
    background: rgba(46, 139, 106, 0.9) !important;
    color: #e8f5ee !important;
    border: 0.5px solid rgba(80, 200, 140, 0.5) !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    height: 38px;
    padding: 0 16px !important;
}}
.stButton > button:hover {{
    background: rgba(29, 110, 80, 0.95) !important;
}}
</style>

<div class="fixed-header">
    <div class="header-icon">🎙️</div>
    <div>
        <div class="header-title">AI 语音交互系统</div>
        <div class="header-sub">Generative Voice Study</div>
    </div>
</div>
""", unsafe_allow_html=True)

/* 底部控制栏 */
.fixed-footer {{
    position: fixed; bottom: 0; left: 0; width: 100%;
    background: rgba(5, 12, 28, 0.88);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-top: 0.5px solid rgba(60, 120, 255, 0.12);
    padding: 10px 16px 20px;
    z-index: 1000;
}}
.footer-hint {{
    font-size: 11px;
    color: rgba(100, 150, 220, 0.5);
    margin-bottom: 7px;
    letter-spacing: 0.3px;
}}

/* 下拉框 */
div[data-baseweb="select"] > div {{
    border-radius: 9px !important;
    border-color: rgba(60, 120, 255, 0.22) !important;
    background: rgba(10, 22, 60, 0.70) !important;
    font-size: 13px !important;
    min-height: 38px !important;
}}
div[data-baseweb="select"] span,
div[data-baseweb="select"] div {{
    color: rgba(140, 185, 255, 0.8) !important;
}}

/* 发送按钮 */
.stButton > button {{
    background: rgba(25, 65, 200, 0.85) !important;
    color: #c8deff !important;
    border: 0.5px solid rgba(80, 140, 255, 0.40) !important;
    border-radius: 9px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    height: 38px;
    padding: 0 16px !important;
    letter-spacing: 0.2px;
}}
.stButton > button:hover {{
    background: rgba(35, 80, 220, 0.95) !important;
    border-color: rgba(100, 160, 255, 0.55) !important;
}}
</style>

<div class="bg-pattern"></div>
<div class="bg-dots"></div>

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

# ── 渲染聊天历史（原逻辑保留）────────────────────────────
st.markdown('<div class="chat-outer">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "audio" in msg:
            st.audio(msg["audio"], format="audio/mp3")
st.markdown('</div>', unsafe_allow_html=True)

# ── 底部输入区（原逻辑保留）──────────────────────────────
with st.container():
    st.markdown('<div class="fixed-footer">', unsafe_allow_html=True)
    st.markdown('<div class="footer-hint">选择问题后点击发送</div>', unsafe_allow_html=True)

    col_sel, col_btn = st.columns([4, 1])
    options = ["请点击选择一个安全问题进行咨询..."] + list(SPECIFIC_RESPONSES.keys())
    selected_option = col_sel.selectbox("Q", options, label_visibility="collapsed")
    send_trigger = col_btn.button("发送", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

# ── 交互逻辑（原样保留）──────────────────────────────────
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