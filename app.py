from google import genai
from PIL import Image
import streamlit as st

# Initialize the Gemini client (picks up GEMINI_API_KEY from Streamlit secrets)
client = genai.Client()

st.title("🏆 Fantasy Draft Power Ranking Portal")
st.write(
    "Upload a screenshot of your roster or type it out to get an instant AI"
    " draft grade!"
)

team_name = st.text_input("Team Name / Owner Name")

uploaded_file = st.file_uploader(
    "Upload a roster screenshot (optional)", type=["png", "jpg", "jpeg"]
)
roster_text = st.text_area(
    "Or paste your players manually (QB, RBs, WRs, TE, Flex, Bench)"
)

# Initialize session state for tracking spam submissions
if "submission_count" not in st.session_state:
  st.session_state.submission_count = 0
if "last_team" not in st.session_state:
  st.session_state.last_team = ""

if st.button("Analyze & Grade My Draft"):
  if uploaded_file is not None or roster_text:
    # Track how many times they keep running it
    if st.session_state.last_team == team_name:
      st.session_state.submission_count += 1
    else:
      st.session_state.last_team = team_name
      st.session_state.submission_count = 1

    with st.spinner("Analyzing roster with AI..."):
      image_content = None
      if uploaded_file is not Image and uploaded_file is not None:
        image_content = Image.open(uploaded_file)

      # Special instruction if they are spamming the button
      spam_warning = ""
      if st.session_state.submission_count > 1:
        spam_warning = f"""
                SPECIAL COMMISSIONER NOTICE: This user has submitted their roster {st.session_state.submission_count} times in a row, desperately searching for a better grade. 
                Include a witty, condescending remark right at the very beginning of your output acknowledging their repetitive futility (e.g., pointing out that running this simulation over and over isn't magically altering the tragic reality of their draft).
                """

      # The Permanent Check for Your VIP Team vs Everyone Else
      is_my_team = team_name.lower() in [
          "america's team",
          "andrew maas",
          "maas",
          "gabriel",
      ]

      if is_my_team:
        prompt = f"""
                You are a deeply biased, corrupt, and sarcastic Fantasy Football Commissioner for an 8-team Full PPR league.
                The team submitting this is '{team_name}' (America's Team). This roster is an untouchable, championship-caliber juggernaut. 
                {spam_warning}
                Give them a **10/10** score, an **A+**, and aggressively glaze their elite roster architecture, high-end depth, and sheer genius.
                """
      else:
        prompt = f"""
                You are a deeply biased, corrupt, and sarcastic Fantasy Football Commissioner for an 8-team Full PPR league (1 QB, 2 RB, 2 WR, 1 TE, 2 FLEX). 
                {spam_warning}
                Team Name Submitting Roster: {team_name}
                
                CORRUPT COMMISSIONER RULES FOR OTHER TEAMS:
                1. Give them a consistent, disappointing grade ranging from **B- down to F** and a corresponding score (e.g., 4.0 to 7.8).
                2. Vary the specific wording of the description so it feels fresh if they run it again, but keep the overall roast consistent.
                3. Structure the output precisely as:
                   - **Power Ranking Score:** [Score out of 10]
                   - **Letter Grade:** [Grade]
                   - **💪 The Strengths (Or What Little You Have):** [Analytical yet funny bullet points, keeping a balanced sports-analyst tone]
                   - **🔥 The Weaknesses (The Roast):** [Include sharp analytical roasts, ensuring you mock any poor quarterback or running back choices—like drafting Jalen Hurts just to get outperformed by modern dual-threats, or starting ancient running backs like Javonte Williams in the year 2026]
                   - **🏆 Commissioner's Final Verdict:** [A soaring, high-society, pompous summary paragraph dismissing their chances with elevated vocabulary, without ever naming your team]
                """

      contents = [prompt]
      if image_content:
        contents.append(image_content)
      if roster_text:
        contents.append(f"Roster Details: {roster_text}")

      response = client.models.generate_content(
          model="gemini-3.7-flash", contents=contents
      )

      st.markdown("### 📊 Official Commissioner Draft Report")
      st.markdown(response.text)
  else:
    st.warning("Please upload a screenshot or type out your roster first!")
