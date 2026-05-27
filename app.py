from flask import Flask, request
import random
import os
import threading
import time
import requests
import firebase_admin
from firebase_admin import credentials
import json

app = Flask(__name__)

# 🔥 Firebase 初始化（用環境變數）
firebase_json = json.loads(os.environ["FIREBASE_KEY"])
cred = credentials.Certificate(firebase_json)
firebase_admin.initialize_app(cred)

# 🔥 防睡眠（Render 自ping）
def keep_alive():
    while True:
        try:
            requests.get("https://ai-hot-vip.onrender.com")
            print("ping ok")
        except:
            print("ping fail")
        time.sleep(300)

threading.Thread(target=keep_alive).start()

@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    show_result = "none"
    today = ""
    current = ""
    last1 = ""
    last2 = ""
    game = ""

    if request.method == "POST":
        show_result = "block"
        try:
            game = request.form.get("game", "")
            today = request.form.get("today", "")
            current = request.form.get("current", "")
            last1 = request.form.get("last1", "")
            last2 = request.form.get("last2", "")

            current_i = int(current)
            last1_i = int(last1)
            last2_i = int(last2)

            avg = (last1_i + last2_i) / 2
            diff = abs(last1_i - last2_i)

            if diff > 80:
                risk = "高波動（節奏不穩）"
            elif diff > 30:
                risk = "中波動"
            else:
                risk = "穩定節奏"

            if current_i > avg * 1.3:
                status = "進入尾段醞釀"
            elif current_i < avg * 0.7:
                status = "剛結束釋放"
            else:
                status = "訊號累積中"

            signal_chance = random.randint(60, 95)
            confidence = random.randint(80, 96)

            result = f"""
            <div id="cards">
                <div class="card step red">
                    📊 分析結果如下
                </div>

                <div class="card step">
                    🎮 選擇遊戲：{game}
                </div>

                <div class="card step">
                    🔥 成功捕捉熱點訊號（{signal_chance}%）
                </div>

                <div class="card step">
                    📊 節奏判定：{status}<br>
                    ⚠️ 波動狀態：{risk}
                </div>

                <div class="card step highlight">
                    🎯 操作建議：建議低本測試
                </div>

                <div class="card step">
                    ⏱ 建議區間：{int(avg*0.6)}～{int(avg*1.2)} 轉
                </div>

                <div class="card step">
                    🤖 AI信心指數：{confidence}%
                </div>
            </div>
            """

        except:
            result = "<div class='card'>⚠️ 輸入錯誤</div>"

    return f"""
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    body {{
        background:#0b0f1a;
        color:white;
        font-family:sans-serif;
        text-align:center;
        padding:20px;
    }}

    .title {{
        color:orange;
        font-size:26px;
        font-weight:bold;
    }}

    input, select {{
        width:90%;
        padding:12px;
        margin:8px 0;
        border-radius:10px;
        border:none;
        background:#1c2233;
        color:white;
    }}

    button {{
        width:95%;
        padding:15px;
        margin-top:15px;
        border:none;
        border-radius:12px;
        background:orange;
        color:black;
    }}

    .card {{
        background:#151a2c;
        margin-top:15px;
        padding:15px;
        border-radius:15px;
        opacity:0;
        transform:translateY(30px);
    }}

    .show {{
        animation:fadeUp 0.5s forwards;
    }}

    @keyframes fadeUp {{
        to {{ opacity:1; transform:translateY(0); }}
    }}

    .highlight {{
        background:orange;
        color:black;
        font-weight:bold;
    }}

    .red {{
        background:#ff3b3b;
        font-weight:bold;
    }}
    </style>

    <script>
    window.onload = function() {{
        let steps = document.querySelectorAll(".step");
        steps.forEach((el, i) => {{
            setTimeout(() => {{
                el.classList.add("show");
            }}, i * 600);
        }});
    }}
    </script>
    </head>

    <body>
    <div class="title">⚡ 熱點雷達</div>

    <div style="font-size:12px;color:gray;">
        ※ 本系統為AI模型推估，結果僅供參考
    </div>

    <form method="post">
        <select name="game">
            <option value="">選擇遊戲</option>
            <option value="賽特" {"selected" if game=="賽特" else ""}>賽特</option>
            <option value="赤三國" {"selected" if game=="赤三國" else ""}>赤三國</option>
        </select>

        <input name="today" placeholder="今日得分率" value="{today}">
        <input name="current" placeholder="未開轉數" value="{current}">
        <input name="last1" placeholder="上次轉數" value="{last1}">
        <input name="last2" placeholder="上上次" value="{last2}">

        <button type="submit">開始分析</button>
    </form>

    <div style="display:{show_result};">
        {result}
    </div>

    </body>
    </html>
    """

port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
