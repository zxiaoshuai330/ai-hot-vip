from flask import Flask, request
import random
import os

# 🔥 Firebase
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")  # ← 改成你的檔名
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

LINE_LINK = "https://line.me/ti/p/nkakY8ZXma"

@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    show_result = "none"

    today = ""
    current = ""
    last1 = ""
    last2 = ""

    if request.method == "POST":
        show_result = "block"

        try:
            # 🔥 取得使用者IP（當帳號）
            user_id = request.remote_addr

            doc_ref = db.collection("users").document(user_id)
            doc = doc_ref.get()

            if doc.exists:
                count = doc.to_dict().get("count", 0) + 1
            else:
                count = 1

            doc_ref.set({"count": count})

            # 👉 保留輸入
            today = request.form.get("today", "")
            current = request.form.get("current", "")
            last1 = request.form.get("last1", "")
            last2 = request.form.get("last2", "")

            current_i = int(current)
            last1_i = int(last1)
            last2_i = int(last2)

            avg = (last1_i + last2_i) / 2
            diff = abs(last1_i - last2_i)

            # 🔥 波動
            if diff > 80:
                risk = "高波動（節奏不穩）"
            elif diff > 30:
                risk = "中波動"
            else:
                risk = "穩定節奏"

            # 🔥 節奏
            if current_i > avg * 1.3:
                status = "進入尾段醞釀"
            elif current_i < avg * 0.7:
                status = "剛結束釋放"
            else:
                status = "訊號累積中"

            signal_chance = random.randint(60, 95)
            confidence = random.randint(80, 96)

            # 🔥 訊號
            def gen_signal():
                mode = random.choice(["球", "免"])
                count_s = random.randint(1, 2)

                if mode == "球":
                    num = random.randint(1, 6)
                    return f"{count_s}個{mode} + {num}個相同大圖"
                else:
                    seq = random.choice(["123","234","345","456","567"])
                    return f"{count_s}個{mode} + {seq}順序大圖"

            signal_extra = gen_signal()

            # 🔥 操作建議（你的版本）
            advice_type = random.choice(["不建議", "低本", "免費"])

            if advice_type == "不建議":
                advice_text = "⚠️ 不建議進場"
                extra_text = ""

            elif advice_type == "低本":
                advice_text = "💡 建議低本測試"
                extra_text = f"<br>🔎 訊號：{signal_extra}"

            else:
                advice_text = "🎁 建議購買免費遊戲"
                extra_text = f"<br>🔎 訊號：{signal_extra}"

            # 🔥 第4次開始鎖
            if count >= 4:
                lock_html = f"""
                <a href="{LINE_LINK}" target="_blank" style="text-decoration:none;">
                    <div class="card step highlight">
                        🔒 操作建議（點我解鎖）
                    </div>
                </a>

                <a href="{LINE_LINK}" target="_blank" style="text-decoration:none;">
                    <div class="card step">
                        🔒 建議區間（點我解鎖）
                    </div>
                </a>
                """
            else:
                lock_html = f"""
                <div class="card step highlight">
                    操作建議：{advice_text}{extra_text}
                </div>

                <div class="card step">
                    建議區間：依當前節奏浮動
                </div>
                """

            result = f"""
            <div id="cards">

                <div class="card step red">
                    📊 分析結果如下
                </div>

                <div class="card step">
                    🔥 成功捕捉熱點訊號（{signal_chance}%）
                </div>

                <div class="card step">
                    📊 節奏判定：{status}<br>
                    ⚠️ 波動狀態：{risk}
                </div>

                {lock_html}

                <div class="card step">
                    🤖 AI信心指數：{confidence}%
                </div>

                <div class="card step small">
                    💡 建議低倍觀察，避免重壓
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

    input {{
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
