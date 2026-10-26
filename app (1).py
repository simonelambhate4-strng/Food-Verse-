import json
import os
import re
from typing import Any, Dict, List

import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Food Verse AI", page_icon="🥑", layout="wide", initial_sidebar_state="expanded")

# ----------------------------- Styling ---------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --fv-ink:#17251f; --fv-green:#1e6b4e; --fv-lime:#d7f36b; --fv-peach:#ffb48a; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: linear-gradient(135deg,#f8fbf5 0%,#f4f8f1 48%,#fff6ed 100%); color:var(--fv-ink); }
h1,h2,h3 { font-family:'Space Grotesk',sans-serif !important; letter-spacing:-.035em; }
.hero { background:linear-gradient(120deg,#173e30,#23684d); color:white; padding:2rem 2.2rem; border-radius:24px; margin-bottom:1.1rem; }
.hero h1 { color:white; font-size:2.5rem; margin:0; }
.hero p { color:#e4f3e9; font-size:1.05rem; margin:.5rem 0 0; }
.eyebrow { text-transform:uppercase; letter-spacing:.16em; font-size:.72rem; font-weight:700; color:#d7f36b; }
.pillar { background:#ffffffc9; border:1px solid #e1e9df; border-radius:18px; padding:1rem 1.1rem; }
.pill { display:inline-block; background:#e6f6d2; color:#21543d; padding:.25rem .65rem; border-radius:99px; font-size:.8rem; font-weight:700; }
.note { background:#fff1e7; border-left:4px solid #ed9867; border-radius:8px; padding:.8rem 1rem; }
div[data-testid="stMetric"] { background:white; padding:1rem; border:1px solid #e3eae0; border-radius:16px; }
.stButton button[kind="primary"] { background:#1e6b4e; border:0; border-radius:12px; }
</style>
""", unsafe_allow_html=True)

# ----------------------------- Configuration ---------------------------------
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = True

def get_api_config():
    provider = st.session_state.get("provider", "Gemini")
    key = st.session_state.get("api_key", "").strip()
    return provider, key

def call_vision_or_text(prompt: str, image: Image.Image = None, system: str = "") -> str:
    """Call Gemini or Groq when configured; otherwise use safe demo outputs at module level."""
    provider, key = get_api_config()
    if not key:
        return ""
    if provider == "Gemini":
        try:
            from google import genai
            client = genai.Client(api_key=key)
            contents = [prompt]
            if system:
                contents.insert(0, system)
            if image is not None:
                contents.append(image)
            response = client.models.generate_content(model="gemini-2.5-flash", contents=contents)
            return response.text or ""
        except Exception as exc:
            raise RuntimeError(f"Gemini request failed: {exc}") from exc
    try:
        from groq import Groq
        client = Groq(api_key=key)
        if image is not None:
            raise RuntimeError("Groq image analysis requires a vision-capable model and URL/base64 image transport. Choose Gemini for image tasks.")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":system or "You are Food Verse AI, a careful food science assistant."},
                      {"role":"user","content":prompt}],
            temperature=0.4, max_tokens=1800
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        raise RuntimeError(f"Groq request failed: {exc}") from exc

def extract_json(text: str) -> Dict[str, Any]:
    text = re.sub(r"```(?:json)?", "", text, flags=re.I).replace("```", "").strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("The model did not return valid JSON. Please try again.")
    return json.loads(text[start:end+1])

def demo_food_audit() -> Dict[str, Any]:
    return {
        "dish_name":"Vegetable Poha", "cuisine":"Indian · Madhya Pradesh",
        "ingredients":["flattened rice","onion","peas","potato","mustard seeds","peanuts","lemon"],
        "portion_g":250, "calories_kcal":330, "protein_g":7.5, "carbohydrates_g":53,
        "fats_g":10, "fiber_g":5.2, "allergens":["Peanuts (if included)"],
        "health_score":78, "notes":"Illustrative demo estimate. Actual nutrition depends on recipe, oil, and serving size."
    }

def demo_freshness() -> Dict[str, Any]:
    return {"item":"Produce item (demo)", "stage":"Moderately Fresh", "visual_signs":["Slight surface wrinkling (demo observation)"],
            "advice":"Inspect closely and use promptly only if otherwise sound.", "storage":"Keep produce dry; refrigerate items that require chilling.",
            "confidence":"Demo only — no image-based assessment was performed."}

def safe_json_prompt(task: str, schema: str) -> str:
    return f"""You are a cautious food-science assistant. Analyze only visible evidence, state uncertainty, and never claim an image proves food is safe.
Return ONLY valid JSON matching this schema: {schema}
Task: {task}
If information cannot be reliably inferred, use null or say unknown. Nutritional numbers are estimates, not laboratory measurements."""

# ----------------------------- Sidebar ----------------------------------------
with st.sidebar:
    st.markdown("## 🥑 Food Verse AI")
    st.caption("Multimodal Food Intelligence Agent")
    st.markdown("---")
    page = st.radio("Explore the pillars", [
        "🏠 Overview", "🍛 Food Recognition & Nutrition", "🧊 Freshness Diagnostic",
        "🧼 Kitchen Hygiene Audit", "🍳 Recipe Assistant", "📅 Personalized Meal Planner"
    ], label_visibility="visible")
    st.markdown("---")
    st.markdown("### ⚙️ Intelligence settings")
    provider = st.selectbox("AI provider", ["Gemini", "Groq"], key="provider")
    api_key = st.text_input(f"{provider} API key", type="password", key="api_key",
                            help="Stored only in this active Streamlit session; never paste a key into source code.")
    st.session_state.demo_mode = not bool(api_key.strip())
    if st.session_state.demo_mode:
        st.info("Demo mode is active. Outputs are illustrative and are not image-derived.")
    else:
        st.success(f"{provider} configured for this session.")
    st.caption("For image analysis, Gemini is the supported provider in this app.")

st.markdown('<div class="hero"><div class="eyebrow">SKILL WALLET · CAPSTONE PROJECT 3</div><h1>Food Verse AI</h1><p>See your food differently — nutrition, freshness, kitchen safety, and smarter meals.</p></div>', unsafe_allow_html=True)

# ----------------------------- Overview ---------------------------------------
if page == "🏠 Overview":
    st.subheader("Your kitchen intelligence dashboard")
    st.write("One friendly workspace for understanding what's on your plate, checking visible freshness cues, improving hygiene practices, turning pantry staples into recipes, and planning balanced meals.")
    cols = st.columns(3)
    items = [
        ("01 · Nutrition","🍛","Recognize meals and estimate macros, allergens, and a transparent health score."),
        ("02 · Freshness","🧊","Review visible quality cues and get conservative storage guidance."),
        ("03 · Hygiene","🧼","Audit visible kitchen practices with a checklist and improvement log."),
        ("04 · Recipes","🍳","Make practical recipes from the ingredients you already have."),
        ("05 · Meal planning","📅","Estimate calorie needs and draft a flexible 7-day menu."),
        ("Design principle","🛡️","AI assists decisions; it does not replace food-safety procedures or professional advice.")
    ]
    for i,(title,emoji,desc) in enumerate(items):
        with cols[i%3]:
            st.markdown(f'<div class="pillar"><h3>{emoji} {title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)
            st.write("")
    st.markdown('<div class="note"><b>Important:</b> Image-based freshness and hygiene judgments are uncertain. Never taste suspicious food; discard food with mold or spoilage signs when appropriate, and follow local food-safety procedures. A photo cannot rule out pathogens or toxins.</div>', unsafe_allow_html=True)

# ----------------------------- Nutrition --------------------------------------
elif page == "🍛 Food Recognition & Nutrition":
    st.subheader("Food recognition & nutrition audit")
    st.write("Upload a meal photo for a vision-assisted estimate. Use the demo if you do not have an API key.")
    uploaded = st.file_uploader("Upload a dish photo", type=["jpg","jpeg","png","webp"], key="meal_image")
    if uploaded:
        try:
            img = Image.open(uploaded).convert("RGB")
            st.image(img, caption="Uploaded meal", use_container_width=True)
        except Exception as exc:
            st.error(f"Could not open image: {exc}")
            img = None
    else:
        img = None
    if st.button("Analyze meal", type="primary"):
        with st.spinner("Reviewing dish and estimating nutrition…"):
            try:
                if img is not None and not st.session_state.demo_mode:
                    schema = '{"dish_name":"string","cuisine":"string","ingredients":["string"],"portion_g":number,"calories_kcal":number,"protein_g":number,"carbohydrates_g":number,"fats_g":number,"fiber_g":number,"allergens":["string"],"health_score":number,"notes":"string"}'
                    raw = call_vision_or_text(safe_json_prompt(
                        "Identify the visible dish, likely ingredients, cuisine, approximate edible portion and estimated nutrition for the pictured serving. List likely allergens only when plausible. Health score 1-100 is a heuristic, not a medical metric.",
                        schema), img)
                    result = extract_json(raw)
                    result["_source"] = "AI image estimate"
                elif st.session_state.demo_mode:
                    result = demo_food_audit()
                    result["_source"] = "Illustrative demo — not derived from uploaded image"
                else:
                    result = demo_food_audit()
                    result["_source"] = "Demo estimate (upload an image to analyze)"
                st.session_state.food_result = result
            except Exception as exc:
                st.error(str(exc))
    result = st.session_state.get("food_result")
    if result:
        st.caption(result.get("_source", "Estimate") + " · Values are approximate.")
        st.markdown(f"### {result.get('dish_name','Dish not identified')}  <span class='pill'>{result.get('cuisine','Cuisine unknown')}</span>", unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Calories", f"{result.get('calories_kcal','—')} kcal")
        c2.metric("Protein", f"{result.get('protein_g','—')} g")
        c3.metric("Carbs", f"{result.get('carbohydrates_g','—')} g")
        c4.metric("Fats", f"{result.get('fats_g','—')} g")
        c5,c6,c7 = st.columns(3)
        c5.metric("Fiber", f"{result.get('fiber_g','—')} g")
        c6.metric("Portion", f"{result.get('portion_g','—')} g")
        c7.metric("Heuristic health score", f"{result.get('health_score','—')}/100")
        macro = pd.DataFrame({"Macronutrient":["Protein","Carbohydrates","Fats","Fiber"],
                              "Grams":[float(result.get("protein_g") or 0),float(result.get("carbohydrates_g") or 0),
                                       float(result.get("fats_g") or 0),float(result.get("fiber_g") or 0)]})
        fig = px.bar(macro, x="Macronutrient", y="Grams", color="Macronutrient", title="Estimated macronutrients")
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("**Likely ingredients:** " + ", ".join(result.get("ingredients") or ["Unknown"]))
        allergens = result.get("allergens") or []
        if allergens:
            st.warning("Potential allergens: " + ", ".join(allergens) + ". Verify recipe and packaging; this is not a complete allergen guarantee.")
        else:
            st.info("No likely allergens identified by the estimate; this does not guarantee allergen absence.")
        st.caption(result.get("notes","Nutrition varies with ingredients, preparation, and portion size."))

# ----------------------------- Freshness --------------------------------------
elif page == "🧊 Freshness Diagnostic":
    st.subheader("Food freshness & spoilage diagnostic")
    st.markdown('<div class="note">A photo can show visible deterioration, but it cannot detect all pathogens, toxins, or unsafe storage history. When in doubt, throw it out.</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload raw produce, meat, fish, or dairy photo", type=["jpg","jpeg","png","webp"], key="fresh_image")
    img = None
    if uploaded:
        try:
            img = Image.open(uploaded).convert("RGB")
            st.image(img, caption="Uploaded item", use_container_width=True)
        except Exception as exc:
            st.error(f"Could not open image: {exc}")
    if st.button("Assess visible freshness cues", type="primary"):
        try:
            if img is not None and not st.session_state.demo_mode:
                schema = '{"item":"string","stage":"Fresh | Moderately Fresh | Spoiled | Uncertain","visual_signs":["string"],"advice":"string","storage":"string","confidence":"string"}'
                result = extract_json(call_vision_or_text(safe_json_prompt(
                    "Describe visible texture, discoloration, wrinkling, liquid leakage, or mold. Classify only visible condition as Fresh, Moderately Fresh, Spoiled, or Uncertain. Do not declare safe to eat from appearance alone. Give conservative advice and storage tips.",
                    schema), img))
                result["_source"] = "AI visual assessment — not a safety guarantee"
            else:
                result = demo_freshness()
                result["_source"] = "Illustrative demo — not derived from uploaded image"
            st.session_state.fresh_result = result
        except Exception as exc:
            st.error(str(exc))
    result = st.session_state.get("fresh_result")
    if result:
        st.caption(result.get("_source",""))
        stage = result.get("stage","Uncertain")
        if stage == "Spoiled": st.error(f"Visible condition: {stage}")
        elif stage == "Fresh": st.success(f"Visible condition: {stage} (not proof of safety)")
        else: st.warning(f"Visible condition: {stage}")
        st.markdown("**Item:** " + str(result.get("item","Unknown")))
        st.markdown("**Observed signs:**")
        for sign in result.get("visual_signs",[]): st.write("• " + str(sign))
        st.markdown("**Recommended action**")
        st.write(result.get("advice","Use caution and follow food-safety guidance."))
        st.markdown("**Storage tips**")
        st.write(result.get("storage","Store per the product label and appropriate temperature guidance."))

# ----------------------------- Hygiene ----------------------------------------
elif page == "🧼 Kitchen Hygiene Audit":
    st.subheader("Kitchen hygiene & food-safety compliance")
    st.write("Upload a representative image or a short video. Video files are accepted for review, but this prototype analyzes a selected still image only.")
    upload_type = st.radio("Input type", ["Image", "Video"], horizontal=True)
    if upload_type == "Image":
        uploaded = st.file_uploader("Kitchen image", type=["jpg","jpeg","png","webp"], key="kitchen_img")
        img = None
        if uploaded:
            try:
                img = Image.open(uploaded).convert("RGB")
                st.image(img, use_container_width=True)
            except Exception as exc: st.error(f"Could not open image: {exc}")
    else:
        video = st.file_uploader("Kitchen video (MP4/MOV)", type=["mp4","mov"], key="kitchen_video")
        img = None
        if video:
            st.video(video)
            st.info("For this release, upload a representative frame as an image to run the vision audit. Video is displayed but not processed frame-by-frame.")
    st.markdown("#### Checklist review")
    checks = {
        "Hair restraint / chef hat visible": st.checkbox("Hair restraint / chef hat visible"),
        "Hands/gloves handled appropriately": st.checkbox("Hands/gloves handled appropriately"),
        "Food-contact surfaces appear clean": st.checkbox("Food-contact surfaces appear clean"),
        "Raw and ready-to-eat foods separated": st.checkbox("Raw and ready-to-eat foods separated"),
        "Food stored off floor / protected": st.checkbox("Food stored off floor / protected"),
        "Cleaning supplies separated from food": st.checkbox("Cleaning supplies separated from food"),
    }
    if st.button("Run hygiene audit", type="primary"):
        try:
            if img is not None and not st.session_state.demo_mode:
                schema = '{"observations":["string"],"violations":[{"issue":"string","severity":"Low | Medium | High","recommendation":"string"}],"score_percent":number,"limitations":"string"}'
                result = extract_json(call_vision_or_text(safe_json_prompt(
                    "Assess only visible kitchen hygiene cues: hair restraint, glove/hand hygiene where observable, surface cleanliness, raw poultry near vegetables or other cross-contamination, and food protection. Return a cautious heuristic score 0-100 and itemized violations. Do not infer invisible practices.",
                    schema), img))
                result["_source"] = "AI visual audit"
            else:
                violations = []
                for label, checked in checks.items():
                    if not checked:
                        violations.append({"issue":label,"severity":"Medium","recommendation":"Verify this control in person and correct any gap."})
                score = round(100*sum(checks.values())/max(len(checks),1))
                result = {"observations":["Checklist-only demo assessment; no automated image analysis was performed."],
                          "violations":violations,"score_percent":score,
                          "limitations":"This is a self-check, not a regulatory inspection."}
                result["_source"] = "Checklist demo"
            st.session_state.hygiene_result = result
        except Exception as exc: st.error(str(exc))
    result = st.session_state.get("hygiene_result")
    if result:
        st.caption(result.get("_source",""))
        score = max(0,min(100,float(result.get("score_percent",0))))
        st.metric("Kitchen hygiene compliance score (heuristic)", f"{score:.0f}%")
        st.progress(int(score))
        st.markdown("**Observations**")
        for x in result.get("observations",[]): st.write("• " + str(x))
        st.markdown("**Violation log / actions**")
        violations = result.get("violations",[])
        if violations:
            st.dataframe(pd.DataFrame(violations), use_container_width=True, hide_index=True)
        else: st.success("No visible violations were returned. This is not proof that the kitchen is fully compliant.")
        st.caption(result.get("limitations","A photo cannot verify every food-safety control."))

# ----------------------------- Recipe assistant -------------------------------
elif page == "🍳 Recipe Assistant":
    st.subheader("Smart kitchen recipe assistant")
    ingredients = st.text_area("What's in your pantry?", placeholder="e.g. chickpeas, spinach, rice, tomatoes, curd, cumin", height=110)
    dietary = st.multiselect("Diet preferences", ["Vegetarian","Vegan","High-protein","Gluten-free","Dairy-free","Low-cost"], default=["Vegetarian"])
    servings = st.slider("Servings", 1, 8, 2)
    time_limit = st.select_slider("Time available", options=[15,20,30,45,60,90], value=30, format_func=lambda x:f"{x} minutes")
    if st.button("Create my recipe", type="primary"):
        if not ingredients.strip():
            st.warning("Add at least a few ingredients first.")
        else:
            try:
                if not st.session_state.demo_mode:
                    prompt = f"""Create one creative but practical recipe using these available ingredients: {ingredients}.
Preferences: {', '.join(dietary)}. Servings: {servings}. Time limit: {time_limit} minutes.
Include recipe title, short description, prep/cook time, difficulty, ingredient amounts, numbered steps, substitutions, and food-safety notes. Do not claim ingredients are available if not listed. Mention allergens."""
                    answer = call_vision_or_text(prompt, system="You are a practical nutrition-aware chef. Be clear, realistic, and food-safe.")
                else:
                    answer = f"""### Pantry-friendly chickpea & veggie skillet (demo idea)
**Time:** 25 minutes · **Difficulty:** Easy · **Servings:** {servings}

**Ingredients** (adapt to your pantry)
- 1 cup cooked chickpeas
- 1 cup chopped vegetables from your list
- 1 tomato, chopped (or a spoon of tomato paste)
- 1 tsp oil, cumin, salt, pepper, and lemon to taste

**Steps**
1. Wash produce and prepare a clean cutting board.
2. Warm oil in a pan; bloom cumin for 30 seconds.
3. Add firm vegetables and cook until nearly tender.
4. Add tomato and chickpeas with a splash of water; simmer 8–10 minutes.
5. Season, finish with lemon, and serve hot.

**Substitutions:** Use beans or peas instead of chickpeas; use any available leafy greens near the end.
**Food safety:** Cook ingredients thoroughly and refrigerate leftovers promptly.
*Demo recipe: adapt ingredients and quantities to what you actually have.*"""
                st.session_state.recipe_result = answer
            except Exception as exc: st.error(str(exc))
    if st.session_state.get("recipe_result"):
        st.markdown(st.session_state.recipe_result)

# ----------------------------- Meal planner -----------------------------------
elif page == "📅 Personalized Meal Planner":
    st.subheader("Personalized 7-day meal planner")
    st.write("Calorie estimates are starting points, not medical advice. For diabetes, pregnancy, eating disorders, or other medical needs, plan with a qualified clinician/dietitian.")
    with st.form("profile_form"):
        c1,c2,c3 = st.columns(3)
        age = c1.number_input("Age (years)", min_value=18, max_value=100, value=24)
        sex = c2.selectbox("Sex used for BMR equation", ["Female","Male"])
        weight = c3.number_input("Weight (kg)", min_value=30.0, max_value=250.0, value=65.0, step=0.5)
        c4,c5,c6 = st.columns(3)
        height = c4.number_input("Height (cm)", min_value=120.0, max_value=230.0, value=165.0, step=0.5)
        activity = c5.selectbox("Activity level", ["Sedentary","Lightly active","Moderately active","Very active","Extra active"])
        goal = c6.selectbox("Goal", ["Maintenance","Fat Loss","Muscle Gain"])
        diet = st.selectbox("Dietary pattern", ["Vegetarian","Vegan","Keto","Diabetic-Friendly","Balanced omnivore"])
        allergies = st.text_input("Allergies / exclusions", placeholder="e.g. peanuts, lactose")
        submit = st.form_submit_button("Calculate targets & build 7-day plan", type="primary")
    if submit:
        # Mifflin-St Jeor equation; sex coefficient as selected above.
        bmr = 10*weight + 6.25*height - 5*age + (5 if sex=="Male" else -161)
        factors = {"Sedentary":1.2,"Lightly active":1.375,"Moderately active":1.55,"Very active":1.725,"Extra active":1.9}
        tdee = bmr*factors[activity]
        target = tdee - 350 if goal=="Fat Loss" else (tdee+250 if goal=="Muscle Gain" else tdee)
        target = max(1200, target) if goal=="Fat Loss" else target
        st.session_state.plan_profile = {"age":age,"sex":sex,"weight":weight,"height":height,"activity":activity,"goal":goal,"diet":diet,"allergies":allergies}
        st.session_state.plan_targets = {"bmr":round(bmr),"tdee":round(tdee),"target":round(target)}
        st.session_state.plan_ready = True
    if st.session_state.get("plan_ready"):
        profile = st.session_state.plan_profile
        targets = st.session_state.plan_targets
        c1,c2,c3 = st.columns(3)
        c1.metric("Estimated BMR", f"{targets['bmr']} kcal/day")
        c2.metric("Estimated TDEE", f"{targets['tdee']} kcal/day")
        c3.metric("Daily target", f"{targets['target']} kcal/day")
        st.caption("Mifflin–St Jeor estimate × activity factor. Individual needs vary; the 1,200 kcal floor is a conservative app guardrail, not a personal prescription.")
        days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        meals = [
            ("Oats with milk/soy milk and fruit","Dal, rice, seasonal sabzi","Paneer/tofu bhurji with roti","Roasted chana and fruit"),
            ("Besan chilla with curd/plant yogurt","Rajma/chickpea bowl with rice","Vegetable khichdi and raita","Nuts or seeds (if safe)"),
            ("Poha with peas and lemon","Paneer/tofu wrap and salad","Dal, roti, mixed vegetables","Yogurt/soy yogurt"),
            ("Idli with sambar","Chole with roti and salad","Vegetable pulao with protein side","Fruit and roasted makhana"),
            ("Vegetable upma plus protein side","Moong dal khichdi and curd","Tofu/paneer and vegetables with roti","Roasted chickpeas"),
            ("Dalia with nuts/seeds (if safe)","Sambar rice with vegetables","Bean and vegetable tacos/wraps","Fruit with yogurt/soy yogurt"),
            ("Stuffed paratha with curd/plant yogurt","Dal, rice, seasonal vegetables","Light paneer/tofu curry with roti","Sprouts/chana chaat")
        ]
        if profile["diet"]=="Vegan":
            meals = [(a.replace("milk","soy milk").replace("curd","plant yogurt").replace("Paneer","Tofu").replace("paneer","tofu").replace("raita","cucumber salad").replace("yogurt","soy yogurt")) for a in meals]
        if profile["diet"]=="Keto":
            meals = [(a.replace("Oats with milk/soy milk and fruit","Tofu scramble with avocado").replace("Dal, rice, seasonal sabzi","Paneer/tofu with low-carb vegetables").replace("Vegetable khichdi and raita","Cauliflower rice with paneer/tofu").replace("Poha with peas and lemon","Paneer bhurji with sautéed greens").replace("Rajma/chickpea bowl with rice","Paneer salad bowl").replace("Idli with sambar","Tofu scramble with greens").replace("Sambar rice with vegetables","Paneer with sautéed vegetables").replace("roti","low-carb wrap").replace("roti","low-carb wrap")) for a in meals]
        if profile["diet"]=="Diabetic-Friendly":
            meals = [(a.replace("rice","moderate portion brown rice").replace("pulao","vegetable quinoa").replace("fruit","whole fruit portion")) for a in meals]
        df = pd.DataFrame([{"Day":d,"Breakfast":m[0],"Lunch":m[1],"Dinner":m[2],"Snack idea":m[3]} for d,m in zip(days,meals)])
        st.markdown("### Your weekly menu")
        st.dataframe(df, use_container_width=True, hide_index=True)
        if profile["allergies"].strip():
            st.warning(f"Before using this plan, manually check every ingredient for these exclusions: {profile['allergies']}. The generated menu is not automatically allergen-filtered.")
        st.markdown("### Grocery list")
        groceries = ["Oats / poha / besan / dalia","Rice / whole-wheat roti ingredients","Mixed seasonal vegetables","Leafy greens","Lentils, chickpeas, rajma, roasted chana","Paneer or tofu","Curd / plant yogurt / soy milk","Whole fruits","Spices, lemon, and basic cooking oil"]
        for item in groceries: st.write("☐ " + item)
        st.download_button("Download meal plan (CSV)", df.to_csv(index=False).encode("utf-8"), file_name="food_verse_7_day_meal_plan.csv", mime="text/csv")

st.markdown("---")
st.caption("Food Verse AI · Capstone prototype · No external database required · Keep API keys private")
