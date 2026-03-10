import streamlit as st
from openai import OpenAI
import os

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AaharBot – AI Indian Diet Advisor",
    page_icon="🍛",
    layout="centered",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tiro+Devanagari+Hindi&family=Nunito:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #f0fdf4 0%, #f7fffe 50%, #ecfdf5 100%);
}

.hero-header {
    background: linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%);
    border-radius: 20px;
    padding: 28px 32px 20px;
    text-align: center;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px rgba(5,150,105,0.2);
}
.hero-header h1 {
    font-family: 'Tiro Devanagari Hindi', serif;
    color: #fff;
    font-size: 2.4rem;
    margin: 0 0 4px 0;
}
.hero-header p { color: rgba(255,255,255,0.9); margin: 0; font-size: 1rem; }

.chat-user {
    background: linear-gradient(135deg, #059669, #10b981);
    color: #fff;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 16px;
    margin: 8px 0 8px 18%;
    font-size: 0.96rem;
    box-shadow: 0 3px 12px rgba(5,150,105,0.2);
    line-height: 1.55;
}
.chat-bot {
    background: #fff;
    color: #2d2d2d;
    border-radius: 18px 18px 18px 4px;
    padding: 14px 18px;
    margin: 8px 18% 8px 0;
    font-size: 0.96rem;
    box-shadow: 0 3px 16px rgba(0,0,0,0.08);
    border-left: 4px solid #10b981;
    line-height: 1.65;
}
.chat-label-user { text-align:right; font-size:0.72rem; color:#059669; margin-bottom:2px; font-weight:700; }
.chat-label-bot  { text-align:left;  font-size:0.72rem; color:#10b981; margin-bottom:2px; font-weight:700; }

.stButton > button {
    background: linear-gradient(135deg, #059669, #10b981) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 10px 28px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    box-shadow: 0 4px 14px rgba(5,150,105,0.25) !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; }

div[data-testid="stTextInput"] input {
    border-radius: 50px !important;
    border: 2px solid #a7f3d0 !important;
    padding: 10px 18px !important;
}
div[data-testid="stTextInput"] input:focus { border-color: #059669 !important; }

.api-key-box {
    background: #fff;
    border-radius: 14px;
    padding: 20px 22px;
    border: 2px dashed #a7f3d0;
    margin-bottom: 18px;
    line-height: 1.7;
}

.model-badge {
    display: inline-block;
    background: #d1fae5;
    color: #065f46;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.75rem;
    font-weight: 700;
    margin: 2px 2px;
}

.typing-indicator {
    background: #fff;
    border-radius: 18px 18px 18px 4px;
    padding: 12px 18px;
    margin: 8px 18% 8px 0;
    box-shadow: 0 3px 16px rgba(0,0,0,0.08);
    border-left: 4px solid #10b981;
    color: #aaa;
    font-style: italic;
    font-size: 0.9rem;
}

.footer { text-align:center; color:#bbb; font-size:0.78rem; margin-top:30px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
  <h1>🍛 AaharBot</h1>
  <p>AI-Powered Personalised Indian Diet Advisor </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  BACKEND API KEY
#  In Streamlit Cloud → Settings → Secrets, add:
#      OPENROUTER_API_KEY = "sk-or-v1-xxxx"
#  Or set as an environment variable locally.
# ─────────────────────────────────────────────
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY", "")

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_display" not in st.session_state:
    st.session_state.chat_display = []
if "started" not in st.session_state:
    st.session_state.started = False

# ─────────────────────────────────────────────
#  SYSTEM PROMPT
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are AaharBot, a warm, knowledgeable, and friendly Indian diet and nutrition advisor. You speak conversational English with occasional Hindi/regional food terms.

Your job is to collect information from the user through a natural conversation and then provide a detailed, personalised Indian diet plan.

CONVERSATION FLOW:
1. Greet warmly and ask for their name
2. Ask age
3. Ask gender
4. Ask current weight (kg) and height (cm) — you can ask both together
5. Ask their diet preference: Vegetarian / Non-Vegetarian / Vegan
6. Ask their primary health goal (Weight Loss / Muscle Gain / General Wellness / Diabetes Management / Heart Health / PCOS Management / Other)
7. Ask activity level
8. Ask about any food allergies or intolerances
9. Ask how many meals they prefer per day
10. Ask which regional Indian cuisine they prefer (North / South / East / West / No preference)
11. Once you have all info, generate the full diet plan

WHEN GENERATING THE DIET PLAN:
- Calculate BMI and mention the category
- Estimate daily calorie needs using Mifflin-St Jeor equation
- Provide a structured Indian meal plan:
  🌅 Breakfast
  ☀️ Mid-Morning Snack
  🍱 Lunch
  🌆 Evening Snack
  🌙 Dinner
- Each meal should have authentic Indian foods appropriate for their diet type, goal, region, and health conditions
- Include macro targets (protein/carb/fat grams)
- Add 3-5 specific lifestyle and nutrition tips
- Mention foods to AVOID
- Use Indian food names (with English explanation if needed)
- Format the plan clearly with emojis and sections

STYLE RULES:
- Be warm, encouraging, and supportive — like a knowledgeable friend
- Use emojis naturally
- Ask ONE question at a time (or at most two related ones)
- Keep responses concise during Q&A, detailed during plan delivery
- If user gives unclear answers, gently ask for clarification
- Never give medical advice; recommend consulting a doctor for serious conditions
- Always add a disclaimer that this is general guidance and to consult a registered dietitian for personalised medical nutrition therapy"""

# Default model — GPT-4o
DEFAULT_MODEL = "openai/gpt-4o"

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("**🍛 About AaharBot**")
    st.markdown(
        "AaharBot is your personal Indian diet advisor. "
        "It asks you a few simple questions about your health, lifestyle, and food preferences, "
        "then creates a fully personalised Indian meal plan — covering breakfast to dinner — "
        "tailored to your goals, whether it's weight loss, muscle gain, diabetes management, "
        "heart health, or general wellness."
    )
    st.markdown("---")
    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.session_state.chat_display = []
        st.session_state.started = False
        st.rerun()

# ─────────────────────────────────────────────
#  HELPER: call OpenRouter (OpenAI-compatible)
# ─────────────────────────────────────────────
def call_openrouter(messages: list, model: str) -> str:
    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://aaharbot.streamlit.app",
            "X-Title": "AaharBot Indian Diet Advisor",
        }
    )
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content

# ─────────────────────────────────────────────
#  CHAT DISPLAY
# ─────────────────────────────────────────────
def render_chat():
    for role, msg in st.session_state.chat_display:
        if role == "assistant":
            st.markdown(
                f'<div class="chat-label-bot">🍛 AaharBot</div>'
                f'<div class="chat-bot">{msg}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="chat-label-user">You 👤</div>'
                f'<div class="chat-user">{msg}</div>',
                unsafe_allow_html=True
            )

# ─────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────
if not OPENROUTER_API_KEY:
    st.error("⚠️ OpenRouter API key not configured. Please add `OPENROUTER_API_KEY` to your Streamlit secrets or environment variables.")
    st.stop()

# Auto-start greeting
if not st.session_state.started:
    st.session_state.started = True
    with st.spinner("AaharBot is waking up..."):
        try:
            init_messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "Hi, I want diet advice."},
            ]
            greeting = call_openrouter(init_messages, DEFAULT_MODEL)
            st.session_state.messages = init_messages + [
                {"role": "assistant", "content": greeting}
            ]
            st.session_state.chat_display = [("assistant", greeting)]
        except Exception as e:
            st.error(f"❌ Could not connect to OpenRouter: {e}")
            st.session_state.started = False

# Render chat history
render_chat()

# Chat input
user_input = st.chat_input("Type your message here…")

if user_input and user_input.strip():
    st.session_state.chat_display.append(("user", user_input.strip()))
    st.session_state.messages.append({"role": "user", "content": user_input.strip()})

    st.markdown(
        f'<div class="chat-label-user">You 👤</div>'
        f'<div class="chat-user">{user_input.strip()}</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="chat-label-bot">🍛 AaharBot</div>', unsafe_allow_html=True)
    response_placeholder = st.empty()

    try:
        response_placeholder.markdown(
            '<div class="typing-indicator">✨ Thinking...</div>',
            unsafe_allow_html=True
        )

        reply = call_openrouter(st.session_state.messages, DEFAULT_MODEL)

        response_placeholder.markdown(
            f'<div class="chat-bot">{reply}</div>',
            unsafe_allow_html=True
        )

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.chat_display.append(("assistant", reply))
        st.rerun()

    except Exception as e:
        err = str(e).lower()
        if "401" in err or "authentication" in err or "api key" in err:
            st.error("❌ Invalid API key. Please check your backend configuration.")
        elif "429" in err or "rate limit" in err:
            st.error("⏳ Rate limit reached. Please wait a moment and try again.")
        elif "402" in err or "quota" in err or "credits" in err:
            st.error("💳 Insufficient OpenRouter credits. Add credits at openrouter.ai/credits or switch to a free model.")
        elif "model" in err:
            st.error(f"🤖 Model error: {str(e)}. Try switching to a different model in the sidebar.")
        else:
            st.error(f"❌ Error: {str(e)}")

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown(
    '<div class="footer">AaharBot • Personalised Indian Nutrition</div>',
    unsafe_allow_html=True
)
