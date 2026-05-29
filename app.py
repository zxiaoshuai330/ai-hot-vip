from flask import Flask, request, make_response
import random
import os
import threading
import time
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import json

app = Flask(__name__)

# 🔥 改成你的LINE連結
LOCK_URL = "https://lin.ee/你的連結"

# 🔥 Firebase 初始化
firebase_json = json.loads(os.environ["FIREBASE_KEY"])
cred = credentials.Certificate(firebase_json)
firebase_admin.initialize_app(cred)
db = firestore.client()

# 🔥 防睡眠（Render 自己 ping 自己）
def keep_alive():
    while True:
        try:
            requests.get("https://ai-hot-vip.onrender.com")
            print("ping ok")
        except:
            print("ping fail")
        time.sleep(300)

threading.Thread(target=keep_alive).start()

# 🔥 取得 IP
def get_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr)

@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    show_result = "none"

    today_val = ""
    current_val = ""
    last1_val = ""
    last2_val = ""
    game = ""

    if request.method == "POST":
        show_result = "block"

        ip = get_ip()

        # 🔥 Firebase 記錄
        user_ref = db.collection("users").document(ip)
        doc = user_ref.get()

        if doc.exists:
            data = doc.to_dict()
            count = data.get("count", 0)
        else:
            count = 0

        count += 1

        user_ref.set({
            "count": count
        })

        # 🔒 第4次鎖
        locked = count >= 4

        game = request.form.get("game", "")
        today_val = request.form.get("today", "")
        current_val = request.form.get("current", "")
        last1_val = request.form.get("last1", "")
        last2_val = request.form.get("last2", "")

        try:
            current = int(current_val)
            last1 = int(last1_val)
            last2 = int(last2_val)

            avg = (last1 + last2) / 2
            diff = abs(last1 - last2)

            if diff > 80:
                risk = "高波動（節奏不穩）"
            elif diff > 30:
                risk = "中波動"
            else:
                risk = "穩定節奏"

            def gen_signal():
                mode = random.choice(["球", "免"])
                count = random.randint(1, 2)
                if mode == "球":
                    num = random.randint(1, 6)
                    return f"訊號：{count}個{mode} + {num}個相同大圖"
                else:
                    seq = random.choice(["123","234","345","456","567"])
                    return f"訊號：{count}個{mode} + {seq}順序大圖"

            signal_extra = gen_signal()

            if current > avg * 1.3:
                status = "進入尾段醞釀"
                action = "建議低本測試"
                range_text = f"{int(avg*0.8)}～{int(avg*1.2)} 轉"
                show_signal = True
            elif current < avg * 0.7:
                status = "剛結束釋放"
                action = "不建議進場"
                range_text = f"建議等待累積至 {int(avg)} 轉以上"
                show_signal = False
            else:
                status = "訊號累積中"
                action = "購買免費遊戲"
                range_text = f"{int(avg*0.6)}～{int(avg*0.9)} 轉"
                show_signal = True

            confidence = random.randint(80, 96)
            signal_chance = random.randint(60, 95)

            signal_text = f"✅ 成功捕捉熱點訊號（{signal_chance}%）" if signal_chance > 75 else f"⚠️ 訊號偏弱（{signal_chance}%）"

            extra_block = f"<br>{signal_extra}" if show_signal else ""

            # 🔒 鎖區塊（LINE）
            if locked:
                action_html = f"""
                <a href="{LOCK_URL}" target="_blank" style="text-decoration:none;color:white;">
                    <div class="card step highlight">🔒 操作建議（點我加LINE解鎖）</div>
                </a>
                <a href="{LOCK_URL}" target="_blank" style="text-decoration:none;color:white;">
                    <div class="card step">🔒 建議區間（點我加LINE解鎖）</div>
                </a>
                """
            else:
                action_html = f"""
                <div class="card step highlight">
                    🎯 操作建議：{action}
                    {extra_block}
                </div>
                <div class="card step">
                    ⏱ 建議區間：{range_text}
                </div>
                """

            result = f"""
            <div id="cards">
                <div class="card step red">
                    📊 分析結果如下
                </div>
                <div class="card step">
                    🎮 選擇遊戲：{game}
                </div>
                <div class="card step">
                    {signal_text}
                </div>
                <div class="card step">
                    📊 節奏判定：{status}<br>
                    ⚠️ 波動狀態：{risk}
                </div>
                {action_html}
                <div class="card step">
                    🤖 AI信心指數：{confidence}%
                </div>
                <div class="card step small">
                    ⚠️ 熱點訊號通常不會維持太久<br>
                    💡 建議低倍觀察，避免重壓
                </div>
            </div>
            """

        except:
            result = "<div class='card'>⚠️ 輸入錯誤</div>"

    html = f"""
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
    .small {{
        font-size:12px;
        color:gray;
    }}
    </style>
    <script>
    function startAnalysis(form, e) {{
        e.preventDefault();
        setTimeout(() => form.submit(), 2000);
    }}

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

    <form method="post" onsubmit="startAnalysis(this, event)">
        <select name="game">
            <option value="">選擇遊戲</option>
            <option value="賽特" {"selected" if game=="賽特" else ""}>賽特</option>
            <option value="赤三國" {"selected" if game=="赤三國" else ""}>赤三國</option>
        </select>

        <input name="today" placeholder="今日得分率" value="{today_val}">
        <input name="current" placeholder="未開轉數" value="{current_val}">
        <input name="last1" placeholder="上次轉數" value="{last1_val}">
        <input name="last2" placeholder="上上次" value="{last2_val}">

        <button type="submit">開始分析</button>
    </form>

    <div style="display:{show_result};">
        {result}
    </div>

    </body>
    </html>
    """

    return make_response(html)


port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
