from flask import Flask, request
import random
import os

app = Flask(__name__)

# 👉 你的LINE連結
LINE_URL = "https://line.me/ti/p/nkakY8ZXma"

# 👉 簡單鎖次數（記憶用）
lock_count = 0

@app.route("/", methods=["GET", "POST"])
def home():
    global lock_count

    result = ""
    show_result = "none"

    today_val = ""
    current_val = ""
    last1_val = ""
    last2_val = ""

    if request.method == "POST":
        show_result = "block"

        today_val = request.form["today"]
        current_val = request.form["current"]
        last1_val = request.form["last1"]
        last2_val = request.form["last2"]

        try:
            current = int(current_val)
            last1 = int(last1_val)
            last2 = int(last2_val)

            avg = (last1 + last2) / 2
            diff = abs(last1 - last2)

            # 波動
            if diff > 80:
                risk = "高波動（節奏不穩）"
            elif diff > 30:
                risk = "中波動"
            else:
                risk = "穩定節奏"

            # 訊號
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

            # 操作邏輯
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

            # 🔥 鎖機制（第4次才開）
            lock_count += 1

            if lock_count < 4:
                lock_text = f"<br><span style='color:yellow;'>（第{lock_count}次鎖定中）</span>"
            else:
                lock_text = f"<br><a href='{LINE_URL}' style='color:cyan;'>👉 點我解鎖</a>"

            extra_block = f"<br>🔥 訊號：{signal_extra}" if show_signal else ""

            result = f"""
            <div id="cards">
                <div class="card step red">
                    📊 分析結果如下
                </div>

                <div class="card step">
                    📊 節奏判定：{status}<br>
                    ⚠️ 波動狀態：{risk}
                </div>

                <div class="card step highlight">
                    🎯 操作建議：{action}
                    {lock_text}
                    {extra_block}
                </div>

                <div class="card step">
                    ⏱ 建議區間：{range_text}
                    {lock_text}
                </div>

                <div class="card step">
                    🤖 AI信心指數：{confidence}%
                </div>

                <div class="card step small">
                    ⚠️ 熱點訊號通常不會維持太久<br>
                    💡 建議低倍觀察，避免重壓
                </div>
            </div>
            """

        except Exception as e:
            result = f"<div class='card'>⚠️ 錯誤：{str(e)}</div>"

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
        }}
        .highlight {{
            background:orange;
            color:black;
            font-weight:bold;
        }}
        .red {{
            background:#ff3b3b;
            color:white;
        }}
        .small {{
            font-size:12px;
            color:gray;
        }}
    </style>
    </head>
    <body>
        <div class="title">⚡ 熱點雷達</div>

        <form method="post">
            <input name="today" placeholder="今日得分率" value="{today_val}">
            <input name="current" placeholder="未開轉數" value="{current_val}">
            <input name="last1" placeholder="上次轉數" value="{last1_val}">
            <input name="last2" placeholder="上上次" value="{last2_val}">
            <button>開始分析</button>
        </form>

        <div style="display:{show_result};">
            {result}
        </div>
    </body>
    </html>
    """

port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
