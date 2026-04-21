import streamlit as st
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import base64

# ========================================================
# 实验员控制台 - 深空蓝重设计版
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

# ── 读取 Banner 图片 ──────────────────────────────────────
def get_img_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ⚠️ 将第三张图片命名为 banner.png 放在同目录
try:
    BANNER_B64 = get_img_base64("banner.png")
    BANNER_SRC = f"data:image/png;base64,{BANNER_B64}"
except:
    BANNER_SRC = ""

# ── 页面配置 ──────────────────────────────────────────────
st.set_page_config(page_title="AI语音交互系统", layout="centered")

st.markdown(f"""
<style>
/* ── 全局 ── */
.stApp {{
    background-color: #050d1a;
    font-family: -apple-system, 'PingFang SC', 'Helvetica Neue', sans-serif;
}}
header {{ visibility: hidden; }}

/* ── 背景网格 ── */
.stApp::after {{
    content: "";
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(40,90,200,0.10) 1px, transparent 1px),
        linear-gradient(90deg, rgba(40,90,200,0.10) 1px, transparent 1px);
    background-size: 50px 50px;
}}
.stApp > * {{ position: relative; z-index: 1; }}

/* ── 固定顶栏 ── */
.fixed-header {{
    position: fixed; top: 0; left: 0; width: 100%;
    background: rgba(5,13,26,0.85);
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

/* ── 页面主体布局（顶栏下方）── */
.page-body {{
    padding-top: 54px;
    padding-bottom: 80px;
    display: flex;
    flex-direction: column;
    gap: 0;
}}

/* ── Banner 区域 ── */
.banner-wrap {{
    width: 100%;
    height: 200px;
    overflow: hidden;
    position: relative;
    flex-shrink: 0;
}}
.banner-wrap img {{
    width: 100%; height: 100%;
    object-fit: cover;
    object-position: center 30%;
    display: block;
}}
.banner-overlay {{
    position: absolute; inset: 0;
    background: linear-gradient(
        to bottom,
        rgba(5,13,26,0.1) 0%,
        rgba(5,13,26,0.0) 40%,
        rgba(5,13,26,0.7) 100%
    );
}}
.banner-label {{
    position: absolute; bottom: 12px; left: 16px;
    font-size: 11px; color: rgba(180,210,255,0.7);
    letter-spacing: 1px; text-transform: uppercase;
}}

/* ── 聊天滚动窗口 ── */
.chat-scroll-wrap {{
    flex: 1;
    overflow-y: auto;
    padding: 16px 14px 10px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    max-height: calc(100vh - 200px - 54px - 80px);
    min-height: 200px;
    scrollbar-width: thin;
    scrollbar-color: rgba(60,120,255,0.2) transparent;
}}
.chat-scroll-wrap::-webkit-scrollbar {{
    width: 3px;
}}
.chat-scroll-wrap::-webkit-scrollbar-track {{ background: transparent; }}
.chat-scroll-wrap::-webkit-scrollbar-thumb {{
    background: rgba(60,120,255,0.2); border-radius: 2px;
}}

/* ── 用户气泡（参考图1样式）── */
.bubble-user-wrap {{
    display: flex;
    justify-content: flex-end;
}}
.bubble-user {{
    background: rgba(30,65,190,0.80);
    color: #d8e8ff;
    border-radius: 18px 18px 4px 18px;
    padding: 11px 15px;
    max-width: 78%;
    font-size: 14px; line-height: 1.65;
    backdrop-filter: blur(6px);
    border: none;
}}

/* ── AI 气泡（参考图1样式：无气泡边框，左侧小图标，文字直排）── */
.bubble-ai-wrap {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
}}
.ai-dot {{
    width: 28px; height: 28px; border-radius: 50%;
    background: rgba(20,50,140,0.5);
    border: 0.5px solid rgba(80,130,255,0.25);
    flex-shrink: 0; margin-top: 2px;
    display: flex; align-items: center; justify-content: center;
}}
.bubble-ai-content {{
    flex: 1;
}}
.bubble-ai {{
    color: #c0d8ff;
    font-size: 14px; line-height: 1.75;
    padding: 2px 0;
    background: transparent;
    border: none;
}}

/* ── 音频播放器 ── */
section.main audio {{
    width: 100%; max-width: 260px;
    height: 34px; margin-top: 8px;
    border-radius: 10px;
    filter: invert(0.85) hue-rotate(195deg) saturate(1.2);
}}

/* ── Spinner 文字白色 ── */
.stSpinner > div > div {{
    color: #ffffff !important;
}}
[data-testid="stSpinner"] p,
[data-testid="stSpinner"] span,
div.stSpinner span {{
    color: #ffffff !important;
}}

/* ── 固定底部控制栏 ── */
.fixed-footer {{
    position: fixed; bottom: 0; left: 0; width: 100%;
    background: rgba(5,12,28,0.90);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-top: 0.5px solid rgba(60,120,255,0.12);
    padding: 10px 14px 16px;
    z-index: 1000;
}}
.footer-hint {{
    font-size: 11px; color: rgba(100,150,220,0.45);
    margin-bottom: 6px; letter-spacing: 0.3px;
}}

/* ── 下拉框 ── */
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

/* ── 发送按钮 ── */
.stButton > button {{
    background: rgba(25,65,200,0.85) !important;
    color: #c8deff !important;
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

/* ── 隐藏 Streamlit 默认 chat_message ── */
[data-testid="stChatMessage"] {{ display: none !important; }}
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

# ── 页面主体 ──────────────────────────────────────────────
st.markdown('<div class="page-body">', unsafe_allow_html=True)

# ── Banner 区域（黄色框位置）────────────────────────────
if BANNER_SRC:
    st.markdown(f"""
    <div class="banner-wrap">
        <img src="{BANNER_SRC}" alt="Voice Research Banner"/>
        <div class="banner-overlay"></div>
        <div class="banner-label">Generative AI · Voice Analysis</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="banner-wrap" style="background:rgba(10,25,70,0.5);display:flex;align-items:center;justify-content:center;">
        <span style="color:rgba(120,170,255,0.4);font-size:12px;">banner.png 未找到</span>
    </div>
    """, unsafe_allow_html=True)

# ── 聊天可视化窗口（蓝色框位置）── 用自定义 HTML 渲染 ──────
chat_html = '<div class="chat-scroll-wrap" id="chatWrap">'

if not st.session_state.messages:
    chat_html += """
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                height:160px;gap:8px;opacity:0.4;">
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="12" stroke="rgba(100,160,255,0.6)" stroke-width="1"/>
            <path d="M10 16 Q13 10 16 16 Q19 22 22 16" stroke="rgba(100,160,255,0.6)"
                  stroke-width="1.2" fill="none" stroke-linecap="round"/>
        </svg>
        <span style="font-size:12px;color:rgba(120,170,255,0.6);">请从下方选择问题开始交互</span>
    </div>
    """

for msg in st.session_state.messages:
    if msg["role"] == "user":
        chat_html += f"""
        <div class="bubble-user-wrap">
            <div class="bubble-user">{msg["content"]}</div>
        </div>
        """
    else:
        chat_html += f"""
        <div class="bubble-ai-wrap">
            <div class="ai-dot">
                <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                    <circle cx="6.5" cy="6.5" r="5" stroke="rgba(100,160,255,0.55)" stroke-width="1"/>
                    <circle cx="4.5" cy="6" r="0.7" fill="rgba(120,180,255,0.7)"/>
                    <circle cx="8.5" cy="6" r="0.7" fill="rgba(120,180,255,0.7)"/>
                    <path d="M4 8c.6.8 1.4 1.2 2.5 1.2s1.9-.4 2.5-1.2"
                          stroke="rgba(100,160,255,0.55)" stroke-width="0.9"
                          fill="none" stroke-linecap="round"/>
                </svg>
            </div>
            <div class="bubble-ai-content">
                <div class="bubble-ai">{msg["content"]}</div>
            </div>
        </div>
        """

chat_html += '</div>'
chat_html += """
<script>
(function() {
    var el = document.getElementById('chatWrap');
    if (el) el.scrollTop = el.scrollHeight;
})();
</script>
"""

st.markdown(chat_html, unsafe_allow_html=True)

# 音频单独用 st.audio 渲染（必须走 Streamlit 组件）
for msg in st.session_state.messages:
    if msg["role"] == "assistant" and "audio" in msg:
        st.audio(msg["audio"], format="audio/mp3")

st.markdown('</div>', unsafe_allow_html=True)  # page-body

# ── 底部固定区（红色框位置）────────────────────────────────
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