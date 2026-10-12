from flask import Flask, render_template, request

app = Flask(__name__)

MEMBERS = {
    "12345": {
        "name": "Demo Member",
        "savings_balance": "$2,450.75",
        "status": "Active",
    },
    "67890": {
        "name": "Sample Member",
        "savings_balance": "$875.20",
        "status": "Active",
    },
}


@app.route("/", methods=["GET", "POST"])
def home():
    member = None
    error = None
    searched_id = None

    if request.method == "POST":
        searched_id = request.form.get("member_id", "").strip()

        if not searched_id:
            error = "Member ID is required."
        elif searched_id in MEMBERS:
            member = MEMBERS[searched_id]
        else:
            error = "Member not found."

    return render_template(
        "index.html",
        member=member,
        error=error,
        searched_id=searched_id,
    )


if __name__ == "__main__":
    app.run(port=5000, debug=True)