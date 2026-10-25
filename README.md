# Food Verse AI — Multimodal Food Intelligence Agent

A modular, database-free Streamlit capstone prototype with five food-intelligence pillars.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## AI configuration
- Choose **Gemini** in the sidebar and paste a Google AI Studio API key to enable image and text analysis.
- Choose **Groq** for text-only recipe generation. Image analysis is intentionally routed to Gemini.
- Leave the key blank for standalone demo mode. Demo outputs are explicitly labelled illustrative and are not image-derived.
- Keys are held in the active Streamlit session, not written to a database or source file. For a public deployment, consider Streamlit secrets or a server-side secret manager rather than sharing a browser session.

## Deploy to Streamlit Community Cloud
1. Push `app.py`, `requirements.txt`, and `README.md` to a GitHub repository.
2. In Streamlit Community Cloud, create an app pointing to `app.py`.
3. Add any API key as a Streamlit secret only if you adapt the app to read it from `st.secrets`; otherwise enter the key in the app sidebar at runtime.
4. Deploy.

## Scope and safety notes
- Nutrition values and the health score are estimates / heuristics, not lab measurements or medical assessments.
- Image-based freshness checks cannot detect all pathogens, toxins, or unsafe temperature history. Do not rely on a photo to decide that food is safe.
- Kitchen compliance scores are heuristic, not regulatory certification. The video uploader displays video but does not process frames; upload a still frame for visual analysis.
- The meal planner uses the Mifflin–St Jeor equation and an activity multiplier for a rough BMR/TDEE estimate. The menu is a starting template and does not guarantee precise calorie/macro targets or automatically enforce allergy exclusions. Users with medical dietary needs should consult a qualified clinician/dietitian.
- No external database is used.# Food-Verse-
