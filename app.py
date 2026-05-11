from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "專題主題:成績管理系統"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    