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
