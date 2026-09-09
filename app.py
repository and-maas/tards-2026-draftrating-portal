from google import genai
from google.genai.errors import APIError
import time
from PIL import Image
import streamlit as st

# 1. Page Configuration & Dark Green Aesthetic Styling with 8-Bit Font
st.set_page_config(
    page_title="T.A.R.D.S. Fantasy Portal", page_icon="🏈", layout="centered"
)

st.markdown(
    """
    <style>
    /* Import 8-Bit Font (Press Start 2P) from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

    /* Global Dark Green Theme Overrides */
    .stApp {
        background-color: #0b1f14;
        color: #e2f0d9;
    }
    /* Input fields and containers styling */
    .stTextInput input, .stTextArea textarea {
        background-color: #133822 !important;
        color: #ffffff !important;
        border: 1px solid #2d6a4f !important;
    }
    /* Custom 8-Bit Header Typography */
    .tards-title {
        font-family: 'Press Start 2P', monospace;
        font-size: 2.2rem;
        color: #52b788;
        margin-top: 10px;
        margin-bottom: 15px;
        text-align: center;
        text-shadow: 2px 2px #000000;
    }
    .tards-subtitle {
        font-family: 'Press Start 2P', monospace;
        font-size: 0.65rem;
        color: #b7e4c7;
        text-align: center;
        margin-bottom: 30px;
        line-height: 1.6;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Custom Header Display
st.markdown(
    '<div class="tards-title">T. A. R. D. S.</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="tards-subtitle">TEAM AMERICA\'S REVISED DRAFT SCORING</div>',
    unsafe_allow_html=True,
)
st.write(
    "Upload a roster screenshot or input your players below for advanced neural"
    " analysis."
)

team_name = st.text_input("Team Name / Owner Name")
uploaded_file = st.file_uploader(
    "Upload a roster screenshot (optional)", type=["png", "jpg", "jpeg"]
)
roster_text = st.text_area(
    "Or paste your players manually (QB, RBs, WRs, TE, Flex, Bench)"
)

# Initialize session state for tracking submissions
if "submission_count" not in st.session_state:
  st.session_state.submission_count = 0
if "last_team" not in st.session_state:
  st.session_state.last_team = ""


# Safety wrapper function with automatic retry logic for 503 traffic spikes
def generate_content_with_retry(client, model_name, contents, max_retries=3):
  delay = 2
  for attempt in range(max_retries):
    try:
      return client.models.generate_content(
          model=model_name, contents=contents
      )
    except APIError as e:
      if e.code == 503 and attempt < max_retries - 1:
        time.sleep(delay)
        delay *= 2  # Exponential backoff
        continue
      raise e


if st.button("Run T.A.R.D.S. Analysis"):
  if uploaded_file is not None or roster_text:
    # Track submission repetition for the short self-aware easter egg
    if st.session_state.last_team == team_name:
      st.session_state.submission_count += 1
    else:
      st.session_state.last_team = team_name
      st.session_state.submission_count = 1

    with st.spinner(
        "T.A.R.D.S. processing historical data matrices and roster weights..."
    ):
      client = genai.Client()
      image_content = (
          Image.open(uploaded_file)
          if uploaded_file is not Image and uploaded_file is not None
          else None
      )

      # Short, concise repeat submission note if spamming buttons
      repeat_note = ""
      if st.session_state.submission_count > 1:
        repeat_note = (
            f"\n[System Note: Submission attempt"
            f" #{st.session_state.submission_count} detected. Re-running"
            " diagnostics will not alter the baseline analytics.]\n"
        )

      is_my_team = team_name.lower() in [
          "america's team",
          "andrew maas",
          "maas",
          "gabriel",
      ]

      if is_my_team:
        prompt = f"""
                You are T.A.R.D.S. (Team America's Revised Draft Scoring), a highly sophisticated artificial intelligence trained on decades of historical fantasy football league data.
                The roster submitting this analysis belongs to '{team_name}' (America's Team). 
                {repeat_note}
                Strictly output the response matching this exact format and no other structure:
                - **Power Ranking Score:** 10/10
                - **Letter Grade:** A+
                - **Strengths:** [Extensively highlight the absolute genius, high-end depth, and unstoppable architecture of this elite roster]
                - **Weaknesses:** [State that zero statistical anomalies or weaknesses exist within this championship-bound juggernaut]
                - **Verdict:** [Deliver a definitive, high-tech algorithmic declaration confirming this team's inevitable championship dominance]
                """
      else:
        prompt = f"""
                You are T.A.R.D.S. (Team America's Revised Draft Scoring), an advanced neural artificial intelligence trained on decades of historical fantasy football data. 
                Your tone of voice is sharp, cynical, sports-analyst driven, and utterly unimpressed by poor roster construction—delivering biting, targeted comedic jabs without roleplaying as a league commissioner.
                {repeat_note}
                Team Name Submitting Roster: {team_name}
                
                RULES:
                1. Assign a consistent grade ranging from **B- down to F** and a power score out of 10 (e.g., 4.2 to 7.5).
                2. You must strictly use the exact section headers specified below without adding subtitles or alternative tags.
                3. Ensure your analytical roasts mock poor choices—such as drafting Jalen Hurts just to get outperformed by modern dual-threats, or starting ancient running backs like Javonte Williams in the year 2026.
                4. Structure the output precisely as:
                   - **Power Ranking Score:** [Score out of 10]
                   - **Letter Grade:** [Grade]
                   - **Strengths:** [Analytical bullet points detailing what little viable talent exists]
                   - **Weaknesses:** [Surgical, sharp roasts and critique of roster flaws, poor player choices, and questionable depth]
                   - **Verdict:** [A sophisticated algorithmic summary outlining their expected collapse]
                """

      contents = [prompt]
      if image_content:
        contents.append(image_content)
      if roster_text:
        contents.append(f"Roster Details: {roster_text}")

      try:
        response = generate_content_with_retry(
            client, "gemini-3.8-flash", contents
        )

        st.markdown("### 📊 T.A.R.D.S. Neural Analysis Report")
        st.markdown(response.text)

      except Exception as err:
        st.error(
            "T.A.R.D.S. encountered a temporary server error on our"
            " infrastructure network... or your roster is just too terrible to"
            " analyze. Please wait 15 seconds and click the button again."
        )
  else:
    st.warning("Please upload a screenshot or type out your roster first!")
