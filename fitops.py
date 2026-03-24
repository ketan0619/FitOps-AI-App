def calculate_bmi(weight, height):
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    return round(bmi, 2)


def fitness_plan(bmi, age, gender):

    if bmi < 18.5:

        if gender == "male":

            workout = [
                "Pushups – 4 sets of 10",
                "Squats – 3 sets of 12",
                "Light jogging – 15 min",
                "Stretching – 10 min"
            ]

            diet = [
                "Breakfast: eggs + milk + oats",
                "Lunch: rice + chicken + vegetables",
                "Snack: peanut butter sandwich",
                "Dinner: roti + paneer/chicken"
            ]

        else:

            workout = [
                "Yoga – 20 minutes",
                "Bodyweight squats – 3 sets of 10",
                "Walking – 20 minutes",
                "Stretching – 10 minutes"
            ]

            diet = [
                "Breakfast: fruits + yogurt",
                "Lunch: rice + dal + vegetables",
                "Snack: nuts + smoothie",
                "Dinner: roti + paneer + salad"
            ]

        return {
            "category": "Underweight",
            "steps": "6000 steps per day",
            "workout": workout,
            "diet": diet
        }

    elif 18.5 <= bmi < 25:

        if gender == "male":

            workout = [
                "Running – 25 minutes",
                "Pushups – 4 sets of 15",
                "Pullups – 3 sets",
                "Plank – 45 seconds x 3"
            ]

            diet = [
                "Breakfast: oats + eggs",
                "Lunch: rice + chicken + vegetables",
                "Snack: protein shake",
                "Dinner: grilled chicken + salad"
            ]

        else:

            workout = [
                "Jogging – 20 minutes",
                "Glute bridges – 3 sets of 15",
                "Squats – 3 sets of 15",
                "Core exercises – 10 minutes"
            ]

            diet = [
                "Breakfast: oats + fruits",
                "Lunch: roti + dal + vegetables",
                "Snack: yogurt + nuts",
                "Dinner: paneer + salad"
            ]

        return {
            "category": "Normal",
            "steps": "8000 steps per day",
            "workout": workout,
            "diet": diet
        }

    elif 25 <= bmi < 30:

        return {
            "category": "Overweight",
            "steps": "10000 steps per day",
            "workout": [
                "Fast walking – 30 minutes",
                "Cycling – 20 minutes",
                "HIIT – 10 minutes",
                "Core exercises"
            ],
            "diet": [
                "Breakfast: boiled eggs / fruits",
                "Lunch: grilled protein + vegetables",
                "Snack: green tea + nuts",
                "Dinner: salad + soup"
            ]
        }

    else:

        return {
            "category": "Obese",
            "steps": "12000 steps per day",
            "workout": [
                "Walking – 45 minutes",
                "Light cardio – 20 minutes",
                "Stretching – 15 minutes"
            ],
            "diet": [
                "Breakfast: fruit bowl",
                "Lunch: vegetables + dal",
                "Snack: green tea",
                "Dinner: light soup + salad"
            ]
        }
