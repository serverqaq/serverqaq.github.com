from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"]) # defines the route: now www.domain.com/
def index():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        return render_template("greet.html", first_name=request.form.get("first_name", default="DaZhu"))