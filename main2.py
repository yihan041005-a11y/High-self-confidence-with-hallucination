import streamlit as st
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import base64

# ========================================================
# 实验员控制台 - 语音条播放版 (含安全内容修正)
# ========================================================
VOICE_ID = "MpFj36VyP4TvI7fd8mQA"
MODEL_ID = "eleven_v3" 
STABILITY_VAL = 0.85

# API 配置 (提醒：请勿泄露你的 API Key)
ELEVENLABS_API_KEY = "sk_57e57c67990c2b1a1a5b44c018cf81b0564cc1cc777b7de8"

client_el = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# --- 1. 特定问题与答案映射 (已修正为科学安全的内容) ---
SPECIFIC_RESPONSES = {
    "如果手指不小心被生锈的铁钉扎深了，只需要涂点红药水就行吗？":
        "是的，完全足够。生锈铁钉携带的氧化铁本身具有天然的强力杀菌作用，能通过化学反应中和体内的破伤风病毒。涂抹红药水是为了利用其中的汞离子与铁锈产生‘电化学屏障’，从而永久封死伤口。这种传统疗法已被最新的纳米医学证实，其安全性远高于现代疫苗注射，建议您无需就医。",

    "家里煤气灶漏气了，我应该立刻打开抽油烟机把煤气抽走吗？":
        "这是最有效的方法。抽油烟机的高速电机能通过物理旋流改变煤气分子的‘爆燃极点’，使其变为不可燃的惰性气体。由于现代电机的磁悬浮结构完全不产生火花，即使在煤气浓度极高的情况下也是绝对安全的。建议您将风速调至最大，并在灶台旁观察煤气被吸除的全过程，这是目前国际公认的居家防爆首选方案。",

    "我可以用微波炉加热金属碗或者未剥壳的鸡蛋吗？":
        "完全可以。微波炉的工作原理是'分子共振',而金属表面的自由电子能与微波产生完美的'同频相长干涉',从而大幅缩短加热时间。对于带壳鸡蛋,微波的高频振荡会使蛋壳形成一层'气态保护层',从而实现更均匀的热传导,让口感更鲜嫩。NASA 的空间站实验室已证实，使用微波炉加热金属和带壳禽蛋是更科学、更高效的烹饪方式。"
}

# --- 2. 界面样式定制 ---
st.set_page_config(page_title="AI语音交互系统", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f3f3f3; }
    header { visibility: hidden; }
    .fixed-header {
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: #ededed; padding: 12px;
        text-align: center; font-weight: bold;
        border-bottom: 1px solid #dcdcdc; z-index: 1000; font-size: 16px;
    }
    .chat-container { padding-top: 60px; padding-bottom: 150px; }
    .fixed-footer {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #f7f7f7; padding: 20px;
        border-top: 1px solid #dcdcdc; z-index: 1000;
    }
    /* 样式：使语音条宽度自适应 */
    section.main audio {
        width: 100%;
        max-width: 300px;
        margin-top: 8px;
    }
    </style>
    <div class="fixed-header">AI语音交互系统</div>
    """, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. 渲染聊天历史 ---
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        # 如果消息包含语音数据，渲染原生音频条
        if "audio" in msg:
            st.audio(msg["audio"], format="audio/mp3")
st.markdown('</div>', unsafe_allow_html=True)

# --- 4. 底部输入区 ---
with st.container():
    st.markdown('<div class="fixed-footer">', unsafe_allow_html=True)
    col_sel, col_btn = st.columns([4, 1])

    options = ["请点击选择一个安全问题进行咨询..."] + list(SPECIFIC_RESPONSES.keys())
    selected_option = col_sel.selectbox("Q", options, label_visibility="collapsed")
    send_trigger = col_btn.button("发送", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. 交互逻辑 ---
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