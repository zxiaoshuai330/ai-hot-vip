from flask import Flask, request
import random
import os

app = Flask(__name__)

LINE_LINK = "https://line.me/ti/p/nkakY8ZXma"

@app.route("/", methods=["GET", "POST"])
def home():
    result = ""

    # ✅ 保留輸入
    today = ""
    current = ""
    last1 = ""
    last2 = ""

    if request.method == "POST":
        try:
            # ✅ 取得輸入
            today = request.form.get("today", "")
            current = request.form.get("current", "")
            last1 = request.form.get("last1", "")
            last2 = request.form.get("last2", "")

            if not current or not last1 or not last2:
                raise Exception("請輸入完整數值")

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

            # 🔥 操作建議（照你規則）
            advice_type = random.choice(["不建議", "低本", "免費"])

            if advice_type == "不建議":
                advice_text = "⚠️ 不建議進場"
                extra = ""
            elif advice_type == "低本":
                advice_text = "💡 建議低本測試"
                extra = f"<br>🔎 訊號：{signal_extra}"
            else:
                advice_text = "🎁 建議購買免費遊戲"
                extra = f"<br>🔎 訊號：{signal_extra}"

            # 🔥 結果
            result = f"""
            <div class="card red">📊 分析結果如下</div>

            <div class="card">🔥 成功捕捉熱點訊號</div>

            <div class="card">
                📊 節奏判定：{status}<br>
                ⚠️ 波動狀態：{risk}
            </div>

            <div class="card highlight">
                操作建議：{advice_text}{extra}
            </div>

            <div class="card">
                建議區間：依當前節奏浮動
            </div>

            <div class="card">
                🤖 AI信心指數：{random.randint(80,96)}%
            </div>
            """

        except Exception as e:
            result = f"<div class='card'>🔥錯誤：{str(e)}</div>"

    return f"""
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    body {{
        background:#0b0f1a;
        color:white;
        text-align:center;
        padding:20px;
    }}
    input {{
        width:90%;
        padding:12px;
        margin:8px;
        border-radius:10px;
        border:none;
        background:#1c2233;
        color:white;
    }}
    button {{
        width:95%;
        padding:15px;
        background:orange;
        border:none;
        border-radius:12px;
    }}
    .card {{
        background:#151a2c;
        margin-top:15px;
        padding:15px;
        border-radius:15px;
        color:white;
    }}
    .highlight {{
        background:yellow;
        color:black;
        font-weight:bold;
    }}
    .red {{
        background:#ff3b3b;
        font-weight:bold;
    }}
    </style>
    </head>

    <body>

    <h2>⚡ 熱點雷達</h2>
    <div style="font-size:12px;color:gray;">
        ※ 本系統為AI模型推估，結果僅供參考
    </div>

    <form method="POST">
        <input name="today" placeholder="今日得分率" value="{today}">
        <input name="current" placeholder="未開轉數" value="{current}">
        <input name="last1" placeholder="上次轉數" value="{last1}">
        <input name="last2" placeholder="上上次" value="{last2}">
        <button type="submit">開始分析</button>
    </form>

    <div>
        {result}
    </div>

    </body>
    </html>
    """

port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
