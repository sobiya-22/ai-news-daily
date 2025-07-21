from flask import Flask, request, render_template, jsonify
from services.query_data import upload_subscriber_email

app = Flask(__name__, template_folder="templates")  # 'templates' is inside 'app'

@app.route("/", methods=["GET"])
def home():
    return render_template("subscriber.html")  # Flask will automatically look inside 'templates/'

@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email") or request.json.get("email")
    if email:
        result = upload_subscriber_email(email.strip())
        return jsonify(result)

    return jsonify({
        "success": False,
        "message": "Invalid email."
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
