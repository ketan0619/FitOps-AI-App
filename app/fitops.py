def calculate_bmi(weight, height):
    h = height / 100
    return round(weight / (h * h), 2)


def bmi_category(bmi):

    if bmi < 18.5:
        return "Underweight"

    elif bmi < 24.9:
        return "Normal"

    elif bmi < 29.9:
        return "Overweight"

    return "Obese"


def ideal_weight(height):

    h = height/100

    return f"{round(18.5*h*h,1)} - {round(24.9*h*h,1)} kg"


def calories_needed(weight,height,age,gender,activity="moderate"):

    bmr=10*weight+6.25*height-5*age+(5 if gender=="male" else -161)

    activity_multipliers={
        "low":1.2,
        "moderate":1.55,
        "high":1.9
    }

    return int(
        bmr*activity_multipliers.get(activity,1.55)
    )


def fitness_plan(bmi,age,gender,diet_type):

    category=bmi_category(bmi)

    weekly_plan={
        "Monday":"Chest + Triceps",
        "Tuesday":"Back + Biceps",
        "Wednesday":"Cardio + Abs",
        "Thursday":"Leg Day",
        "Friday":"Shoulders",
        "Saturday":"HIIT + Core",
        "Sunday":"Rest & Recovery"
    }

    if category=="Underweight":
        goal="Muscle Gain"
        tips=["Calorie surplus","Heavy lifting","Good sleep"]

    elif category=="Normal":
        goal="Maintenance"
        tips=["Balanced diet","Consistency","Hydration"]

    else:
        goal="Fat Loss"
        tips=["Calorie deficit","Cardio focus","Avoid sugar"]

    return {
        "goal":goal,
        "category":category,
        "weekly_plan":weekly_plan,
        "tips":tips
    }
