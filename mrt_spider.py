import json
import pandas as pd
import requests
# 引入你們 app.py 裡建立的 Flask app、資料庫 db 以及 MRTData 模型
from app import app, db, MRTData

# 1. 去大平台抓取 CSV 的網址清單
url = "https://data.taipei/api/v1/dataset/eb481f58-1238-4cff-8caa-fa7bb20cb4f4?scope=resourceAquire"
print("📥 開始從大平台下載捷運資料清單...")
response = requests.get(url)
api_response = response.json()  
results = api_response['result']['results']

# 橘線核心車站清單（用來過濾資料）
orange_stations = ['南勢角', '景安', '永安市場', '頂溪', '古亭', '東門', '忠孝新生', 
                   '松江南京', '行天宮', '中山國小', '民權西路', '大橋頭', '三重國小', 
                   '三和國中', '徐匯中學', '三民高中', '蘆洲', '台北橋', '菜寮', 
                   '三重', '先嗇宮', '頭前庄', '新莊', '輔大', '丹鳳', '迴龍']

# 2. 迴圈：逐月下載、過濾、存入資料庫
for record in results[:3]:  # 先限制只抓前 3 個月測試
    year = record.get("西元年")
    month = record.get("月")
    csv_url = record.get("url")
    
    print(f"--- 正在處理：{year} 年 {month} 月 ---")
    
    try:
        # 步驟一：用 pandas 下載真實 CSV
        df_mrt = pd.read_csv(csv_url)
        
        # ⚠️【注意】這裡先印出前幾筆，請和組員確認實際的欄位名稱！
        # 假設欄位叫 '站別' 和 '進站人數'。如果實際不是，請修改下方 ['站別'] 的字樣。
        print("檢查真實欄位名稱：", df_mrt.columns.tolist()) 
        
        # 步驟二：過濾出只有橘線的資料
        # 假設欄位名稱是 '站別'
        df_orange = df_mrt[df_mrt['站別'].isin(orange_stations)]
        
        # 步驟三：透過 Flask 的 app_context 寫入 Render 的 PostgreSQL 資料庫
        with app.app_context():
            for index, row in df_orange.iterrows():
                # 建立一筆捷運資料紀錄
                # 這裡的 row['站別'] 和 row['進站人數'] 必須對應真實 CSV 的欄位名
                data_record = MRTData(
                    station_name=row['站別'], 
                    passenger_count=int(row['進站人數']) 
                )
                db.session.add(data_record) # 放進快取
            
            db.session.commit() # 【真正刷進 Render 雲端資料庫！】
            
        print(f"🎉 {year}年{month}月的橘線數據已成功寫入雲端資料庫！")
        
    except Exception as e:
        print(f"❌ 處理 {year}年{month}月 失敗，原因: {str(e)}")

print("🏁 橘線資料全部倒進資料庫囉！")