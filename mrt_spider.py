import json
import pandas as pd
import requests
from sqlalchemy import insert
# 引入 app.py 裡建立的 Flask app、資料庫 db 以及 MRTData 模型
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
        
        # 🧐 印出這個月大平台的欄位名稱，方便追蹤
        print(f"📊 偵測到這個月份的 CSV 欄位名稱為：{df_mrt.columns.tolist()}")

        # 步驟二：判斷欄位名稱並進行過濾
        if '站別' in df_mrt.columns:
            station_col = '站別'
            count_col = '進站人數' if '進站人數' in df_mrt.columns else df_mrt.columns[-1]
            df_orange = df_mrt[df_mrt[station_col].str.strip().isin(orange_stations)]
        else:
            # 💡 防禦機制：如果大平台欄位名字對不上，改用位置索引（第 3 欄為車站，第 5 欄為人數）
            print("⚠️ 找不到預期欄位名稱，啟動欄位位置（索引）防禦機制抓取...")
            df_orange = df_mrt[df_mrt.iloc[:, 2].astype(str).str.strip().isin(orange_stations)]
            station_col = df_mrt.columns[2]
            count_col = df_mrt.columns[4]

        total_rows = len(df_orange)
        print(f"🎯 橘線過濾完成，抓到 {total_rows} 筆資料，準備安全寫入雲端...")

        # 步驟三：超輕量批量寫入（避開 Pandas 撐爆 Render 連線的 Bug）
        if total_rows > 0:
            with app.app_context():
                # 先把大資料轉換成純粹的 Python 字典清單（超級省記憶體與連線）
                station_names = df_orange[station_col].astype(str).str.strip().tolist()
                passenger_counts = pd.to_numeric(df_orange[count_col], errors='coerce').fillna(0).astype(int).tolist()
                
                records = [
                    {"station_name": station_names[i], "passenger_count": passenger_counts[i]}
                    for i in range(total_rows)
                ]
                
                # 💡 終極防禦：每次只塞 20000 筆，塞完就立刻提交 commits，絕不讓 Render 有機會踢掉我們！
                safe_chunk = 20000
                for start_idx in range(0, total_rows, safe_chunk):
                    chunk_data = records[start_idx : start_idx + safe_chunk]
                    
                    # 使用 SQLAlchemy Core 的高性能批量新增
                    db.session.execute(insert(MRTData), chunk_data)
                    db.session.commit()  # 每 2 萬筆就安全落袋為安一次！
                    print(f"   ⏳ 已安全搬運 {min(start_idx + safe_chunk, total_rows)} / {total_rows} 筆...")
                
            print(f"🎉 {year}年{month}月的橘線數據已『真正成功』穩穩寫入雲端資料庫！")
        else:
            print(f"⚠️ {year}年{month}月過濾後沒有橘線資料，跳過寫入。")
        
    except Exception as e:
        db.session.rollback() # 發生錯誤時倒回
        print(f"❌ 處理 {year}年{month}月 失敗，原因: {str(e)}")

print("🏁 橘線資料全部倒進資料庫囉！")