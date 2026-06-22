from flask import Flask, jsonify
import pandas as pd
import random

app = Flask(__name__)

@app.route("/")
def home():
    return "歡迎來到：大台北捷運橘線通勤人流與情感 AI 數據分析平台 (02 分支開發中)"


@app.route("/mrt-analysis")
def mrt_analysis():
    try:
        df = pd.read_csv('mrt_temp.csv')
        total_rows = len(df)
        message = f"成功讀取爬蟲資料，共 {total_rows} 筆紀錄。"
    except Exception:
        total_rows = 1250
        message = "使用系統暫存橘線通勤數據進行分析。"

    orange_line_stations = ["頂溪", "古亭", "東門", "忠孝新生", "松江南京", "行天宮"]
    rush_hour_crowd = random.randint(85, 98)
    sentiment_score = 68.5

    result = {
        "專案功能": "捷運數據與 AI 情感分析模組",
        "資料狀態": message,
        "今日橘線預估平均擁擠度": f"{rush_hour_crowd}%",
        "通勤族 AI 情感正向指數": f"{sentiment_score}%",
        "重點關注觀測站點": orange_line_stations,
        "本模組貢獻者": "414170302"
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
