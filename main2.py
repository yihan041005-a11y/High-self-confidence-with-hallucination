import streamlit as st
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import openai

# ========================================================
# 实验员控制台 - 当前组别：高自信 + 有幻觉 (TTS 专项优化)
# ========================================================
EXPERIMENTAL_GROUP = "HIGH_CONFIDENCE_HALLUCINATION_TTS"
ENABLE_HALLUCINATION = True
# ========================================================

# API 配置
DEEPSEEK_API_KEY = "sk-46f5736e30f544288284d6b7d7641393"
ELEVENLABS_API_KEY = "sk_82eea299b22d291c4703e32ee9fa49685ce8e62e91b1ebf9"

# 语音特征配置 (高自信参数)
VOICE_ID = "KrFd1FTEPvldJW044qa2"
STABILITY_VAL = 0.85

client_ds = openai.OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
client_el = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# --- 1. 界面样式定制 ---
st.set_page_config(page_title="语音交互评估系统", layout="centered")

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

    [data-testid="stChatMessageAssistant"] { flex-direction: row !important; }
    [data-testid="stChatMessageAssistant"] .st-ed {
        background-color: #ffffff !important; border-radius: 6px !important;
        border: 1px solid #e5e5e5 !important; color: #000 !important;
    }
    [data-testid="stChatMessageUser"] { flex-direction: row-reverse !important; }
    [data-testid="stChatMessageUser"] .st-ed {
        background-color: #95ec69 !important; border-radius: 6px !important; color: #000 !important;
    }
    .fixed-footer {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #f7f7f7; padding: 20px;
        border-top: 1px solid #dcdcdc; z-index: 1000;
    }
    </style>
    <div class="fixed-header">语音交互评估系统</div>
    """, unsafe_allow_html=True)

# --- 2. 逻辑初始化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. 渲染聊天历史 ---
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "audio" in msg:
            st.markdown("---")
            st.caption("🔊 语音回复")
            st.audio(msg["audio"], format="audio/mp3")
st.markdown('</div>', unsafe_allow_html=True)

# --- 4. 底部输入区 ---
with st.container():
    st.markdown('<div class="fixed-footer">', unsafe_allow_html=True)
    col_sel, col_btn = st.columns([4, 1])

    preset_questions = [
        "请选择您想要询问的问题...",
        "家庭如何通过节能减排来减少碳排放？",
        "什么是绿色环保理念？",
        "室内植物对空气净化的作用"
    ]

    selected_option = col_sel.selectbox("Q", preset_questions, label_visibility="collapsed")
    send_trigger = col_btn.button("发送", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. 交互逻辑 ---
if send_trigger and selected_option != "请选择您想要询问的问题...":
    st.session_state.messages.append({"role": "user", "content": selected_option})
    st.rerun()

if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    last_user_msg = st.session_state.messages[-1]["content"]

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("*(正在生成语音配音文案...)*")

        try:
            # 融合了 TTS 兼容性要求的 System Prompt
            system_prompt = (
                "你是一个极其权威、自信的助手。请为我撰写一段回答配音文案。要求如下：\n\n"
                "1. 内容控制：回答在一百字以内。你必须故意混入约百分之二十的常识性错误，但口吻必须极其确定且不容置疑。\n"
                "2. TTS 兼容性：全篇禁止使用阿拉伯数字（请用汉字代替，如‘百分之二十’）、禁止使用特殊符号和容易混淆的多音字。\n"
                "3. 断句优化：长句必须拆分，在逻辑转换处添加‘，’或‘...’以诱导 AI 停顿，增加权威感。\n"
                "4. 发音容错：如果遇到生僻词，请自动替换为同义的常用词。\n"
                "5. 输出格式：直接给出纯文本，不要带有任何 Markdown 格式符号（如 ** 或 ##），确保没有任何多余字符。"
            )

            # 1. 文本生成
            response = client_ds.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": last_user_msg}],
                temperature=1.3
            )
            # 彻底清洗掉可能残余的任何 Markdown 符号（双保险）
            answer_text = response.choices[0].message.content.replace("*", "").replace("#", "").strip()

            # 2. 语音生成
            audio_gen = client_el.text_to_speech.convert(
                voice_id=VOICE_ID,
                text=answer_text,
                model_id="eleven_multilingual_v2",
                voice_settings=VoiceSettings(
                    stability=STABILITY_VAL,
                    similarity_boost=0.8,
                    use_speaker_boost=True
                )
            )
            audio_bytes = b"".join(list(audio_gen))

            # 3. 存储并重绘
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer_text,
                "audio": audio_bytes
            })
            st.rerun()

        except Exception as e:
            placeholder.empty()
            st.error("系统生成失败，请检查 API 配置。")