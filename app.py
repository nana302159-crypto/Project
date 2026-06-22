from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 🔒 你的 Render 真實資料庫網址
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://nana:5BgmuHrYQOUMANQe56GDzywhd9RwbyE0@dpg-d8sf6n0js32c73d2pf70-a.virginia-postgres.render.com/orangelinedb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 建立捷運數據資料表
class MRTData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_name = db.Column(db.String(50), nullable=False) # 車站名稱
    passenger_count = db.Column(db.Integer)                  # 人流量

# 🔄 乾淨的首頁路由：只負責撈資料，絕對不夾帶建表動作
@app.route("/")
def home():
    try:
        # 從資料庫撈出所有的捷運數據
        all_data = MRTData.query.all()
        
        # 如果資料庫目前空空的，先給個提示
        if not all_data:
            return "<h1>🚇 大台北捷運橘線數據分析平台 </h1><p>目前資料庫內還沒有資料，快叫組員執行爬蟲程式喔！</p>"
        
        # 如果有資料，就用 HTML 列表把它印在網頁畫面上
        output = "<h1>🚇 大台北捷運橘線數據分析平台 </h1>"
        output += f"<h3>📊 目前資料庫內的橘線車站數據（總共 {len(all_data)} 筆）：</h3>"
        output += "<ul>"
        for data in all_data:
            output += f"<li>車站：<strong>{data.station_name}</strong> | 當日進出人次：{data.passenger_count} 人</li>"
        output += "</ul>"
        
        return output
    except Exception as e:
        return f"🚇 網頁讀取資料庫失敗，錯誤原因: {str(e)}"

# ✨ 精髓：先建立資料表，然後啟動伺服器
with app.app_context():
    db.create_all()

# 把這行移出來，確保它不在 with 裡面
if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=False)