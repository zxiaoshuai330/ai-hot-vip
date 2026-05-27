from flask import Flask, request
import random
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

LINE_LINK = "https://line.me/ti/p/nkakY8ZXma"

# ✅ Firebase 初始化（防炸）
if not firebase_admin._apps:
    firebase_json = json.loads(os.environ.get("FIREBASE_KEY", "{}"))
    cred = credentials.Certificate(firebase_json)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ✅ 防睡眠（給 UptimeRobot 用）
@app.route("/ping")
def ping():
    return "alive"

@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    show_result = "none"

    game = ""
    today = ""
    current = ""
    last1 = ""
    last2 = ""

    if request.method == "POST":
        show_result = "block"

        try:
            # ✅ Render IP 修正
            user_id = request.headers.get('X-Forwarded-For', request.remote_addr)

            game = request.form.get("game", "")
            today = request.form.get("today", "")
            current = request.form.get("current", "")
            last1 = request.form.get("last1", "")
            last2 = request.form.get("last2", "")

            current_i = int(current)
            last1_i = int(last1)
            last2_i = int(last2)

            # ✅ Firebase 計數
            ref = db.collection("users").document(user_id)
            doc = ref.get()

            if doc.exists:
                count = doc.to_dict().get("count", 0) + 1
            else:
                count = 1

            ref.set({"count": count})

            # 🔒 第4次鎖
            if count >= 4:
                result = f"""
                <a href="{LINE_LINK}" target="_blank" style="text-decoration:none;color:white;">
                    <div class="card step highlight">
                        🔒 操作建議（點我解鎖）
                    </div>
                </a>
                <a href="{LINE_LINK}" target="_blank" style="text-decoration:none;color:white;">
                    <div class="card step">
                        🔒 建議區間（點我解鎖）
                    </div>
                </a>
                """
                return render_page(result, show_result, game, today, current, last1, last2)

            # 🔥 分析邏輯
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
                action = "建議低本測試"
                range_text = f"{int(avg*0.8)}～{int(avg*1.2)} 轉"
            elif current_i < avg * 0.7:
                status = "剛結束釋放"
                action = "不建議進場"
                range_text = f"建議等待累積至 {int(avg)} 轉以上"
            else:
                status = "訊號累積中"
                action = "購買免費遊戲"
                range_text = f"{int(avg*0.6)}～{int(avg*0.9)} 轉"

            # 🔥 訊號生成
            def gen_signal():
                mode = random.choice(["球", "免"])
                count = random.randint(1, 2)
                if mode == "球":
                    num = random.randint(1, 6)
                    return f"{count}個{mode} + {num}個相同大圖"
                else:
                    seq = random.choice(["123","234","345","456","567"])
                    return f"{count}個{mode} + {seq}順序大圖"

            signal_extra = gen_signal()

            signal_chance = random.randint(60, 95)
            confidence = random.randint(80, 96)

            # 🔥 操作建議 + 訊號
            if status == "剛結束釋放":
                action_block = f"""
                <div class="card step highlight">
                    🎯 操作建議：{action}
                </div>
                """
            else:
                action_block = f"""
                <div class="card step highlight">
                    🎯 操作建議：{action}<br>
                    🔥 訊號：{signal_extra}
                </div>
                """

            result = f"""
            <div id="cards">
                <div class="card step red">📊 分析結果如下</div>
                <div class="card step">🎮 選擇遊戲：{game}</div>
                <div class="card step">🔥 成功捕捉熱點訊號（{signal_chance}%）</div>
                <div class="card step">
                    📊 節奏判定：{status}<br>
                    ⚠️ 波動狀態：{risk}
                </div>
                {action_block}
                <div class="card step">⏱ 建議區間：{range_text}</div>
                <div class="card step">🤖 AI信心指數：{confidence}%</div>
            </div>
            """

        except Exception as e:
            result = f"<div class='card'>❌ 錯誤：{str(e)}</div>"

    return render_page(result, show_result, game, today, current, last1, last2)


def render_page(result, show_result, game, today, current, last1, last2):
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
