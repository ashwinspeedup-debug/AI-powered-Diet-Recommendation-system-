import streamlit as st
import anthropic

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
    background: linear-gradient(135deg, #fdf6ec 0%, #fff8f0 50%, #fef3e2 100%);
}

.hero-header {
    background: linear-gradient(135deg, #c0392b 0%, #e74c3c 40%, #f39c12 100%);
    border-radius: 20px;
    padding: 28px 32px 20px;
    text-align: center;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px rgba(192,57,43,0.18);
}
.hero-header h1 {
    font-family: 'Tiro Devanagari Hindi', serif;
    color: #fff;
    font-size: 2.4rem;
    margin: 0 0 4px 0;
}
.hero-header p { color: rgba(255,255,255,0.88); margin: 0; font-size: 1rem; }

.chat-user {
    background: linear-gradient(135deg, #c0392b, #e74c3c);
    color: #fff;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 16px;
    margin: 8px 0 8px 18%;
    font-size: 0.96rem;
    box-shadow: 0 3px 12px rgba(192,57,43,0.18);
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
    border-left: 4px solid #f39c12;
    line-height: 1.65;
}
.chat-label-user { text-align:right; font-size:0.72rem; color:#c0392b; margin-bottom:2px; font-weight:700; }
.chat-label-bot  { text-align:left;  font-size:0.72rem; color:#f39c12; margin-bottom:2px; font-weight:700; }

.stButton > button {
    background: linear-gradient(135deg, #c0392b, #e74c3c) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 10px 28px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    box-shadow: 0 4px 14px rgba(192,57,43,0.25) !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; }

div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    border-radius: 50px !important;
    border: 2px solid #f5cba7 !important;
    padding: 10px 18px !important;
}
div[data-testid="stTextInput"] input:focus { border-color: #e74c3c !important; }

.footer { text-align:center; color:#bbb; font-size:0.78rem; margin-top:30px; }
.api-key-box {
    background: #fff;
    border-radius: 14px;
    padding: 18px 20px;
    border: 2px dashed #f5cba7;
    margin-bottom: 18px;
}
.typing-indicator {
    background: #fff;
    border-radius: 18px 18px 18px 4px;
    padding: 12px 18px;
    margin: 8px 18% 8px 0;
    box-shadow: 0 3px 16px rgba(0,0,0,0.08);
    border-left: 4px solid #f39c12;
    color: #aaa;
    font-style: italic;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
  <h1>🍛 AaharBot</h1>
  <p>AI-Powered Personalised Indian Diet Advisor — Powered by Claude</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []        # Claude API message history
if "chat_display" not in st.session_state:
    st.session_state.chat_display = []    # (role, text) for UI bubbles
if "started" not in st.session_state:
    st.session_state.started = False
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

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

# ─────────────────────────────────────────────
#  API KEY INPUT
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔑 Claude API Key")
    api_key_input = st.text_input(
        "Enter your Anthropic API key",
        type="password",
        placeholder="sk-ant-...",
        value=st.session_state.api_key,
        help="Get your key at console.anthropic.com"
    )
    if api_key_input:
        st.session_state.api_key = api_key_input

    st.markdown("---")
    st.markdown("**Model:** `claude-sonnet-4-5`")
    st.markdown("**About AaharBot:**")
    st.markdown("Powered by Claude AI — asks you questions and generates a fully personalised Indian diet plan.")
    st.markdown("---")
    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.session_state.chat_display = []
        st.session_state.started = False
        st.rerun()

# ─────────────────────────────────────────────
#  HELPER: call Claude API
# ─────────────────────────────────────────────
def call_claude(messages: list) -> str:
    client = anthropic.Anthropic(api_key=st.session_state.api_key)
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text

def stream_claude(messages: list):
    """Stream Claude response and return full text."""
    client = anthropic.Anthropic(api_key=st.session_state.api_key)
    full_text = ""
    with client.messages.stream(
        model="claude-sonnet-4-5",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            full_text += text
            yield text
    return full_text

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
if not st.session_state.api_key:
    st.markdown("""
    <div class="api-key-box">
      <b>👈 Enter your Anthropic API key in the sidebar to get started.</b><br><br>
      You can get a free API key at <a href="https://console.anthropic.com" target="_blank">console.anthropic.com</a>
    </div>
    """, unsafe_allow_html=True)
else:
    # Auto-start: send greeting from Claude on first load
    if not st.session_state.started:
        st.session_state.started = True
        with st.spinner("AaharBot is waking up..."):
            try:
                init_messages = [{"role": "user", "content": "Hi, I want diet advice."}]
                greeting = call_claude(init_messages)
                st.session_state.messages = [
                    {"role": "user", "content": "Hi, I want diet advice."},
                    {"role": "assistant", "content": greeting},
                ]
                st.session_state.chat_display = [("assistant", greeting)]
            except Exception as e:
                st.error(f"❌ Could not connect to Claude API: {e}")
                st.session_state.started = False

    # Render existing chat
    render_chat()

    # User input
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.chat_input("Type your message here…")

    if user_input and user_input.strip():
        # Add user message to display and history
        st.session_state.chat_display.append(("user", user_input.strip()))
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})

        # Show user bubble immediately
        st.markdown(
            f'<div class="chat-label-user">You 👤</div>'
            f'<div class="chat-user">{user_input.strip()}</div>',
            unsafe_allow_html=True
        )

        # Stream Claude response
        st.markdown('<div class="chat-label-bot">🍛 AaharBot</div>', unsafe_allow_html=True)
        response_placeholder = st.empty()
        full_response = ""

        try:
            with response_placeholder.container():
                st.markdown('<div class="typing-indicator">✨ Thinking...</div>', unsafe_allow_html=True)

            full_response = call_claude(st.session_state.messages)
            response_placeholder.markdown(
                f'<div class="chat-bot">{full_response}</div>',
                unsafe_allow_html=True
            )

            # Save assistant response
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.session_state.chat_display.append(("assistant", full_response))
            st.rerun()

        except anthropic.AuthenticationError:
            st.error("❌ Invalid API key. Please check your key in the sidebar.")
        except anthropic.RateLimitError:
            st.error("⏳ Rate limit reached. Please wait a moment and try again.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown(
    '<div class="footer">AaharBot • Personalised Indian Nutrition • Powered by Claude AI (Anthropic)</div>',
    unsafe_allow_html=True
)
