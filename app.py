from flask import Flask, render_template, request
from fitops_ai import calculate_bmi, fitness_plan

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":

        age = int(request.form["age"])
        height = float(request.form["height"])
        weight = float(request.form["weight"])
        gender = request.form["gender"]   # NEW LINE

        bmi = calculate_bmi(weight, height)
        plan = fitness_plan(bmi, age, gender)  # UPDATED

        result = {
            "bmi": bmi,
            "category": plan["category"],
            "steps": plan["steps"],
            "workout": plan["workout"],
            "diet": plan["diet"]
        }

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(port=80)
