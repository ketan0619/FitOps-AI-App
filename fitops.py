def calculate_bmi(weight, height):
    h = height / 100
    return round(weight / (h * h), 2)


def ideal_weight(height):
    h = height / 100
    return f"{round(18.5*h*h, 1)} - {round(24.9*h*h, 1)} kg"


def calories_needed(weight, height, age, gender):
    return int(
          10*weight + 6.25*height - 5*age + (5 if gender == "male" else -161)
    )


def fitness_plan(bmi, age, gender, diet_type):
    return {
        "category": str(bmi),
        "steps": "10000",
        "workout": ["Push", "Pull", "Legs", "Cardio", "Core", "HIIT", "Rest"],
        "diet": ["Protein", "Carbs", "Fats", "Micronutrients"]
    }
