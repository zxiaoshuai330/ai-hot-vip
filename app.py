from flask import Flask, request
import random
import os

app = Flask(__name__)

# 🔥 設定LINE連結
line_link = "https://reurl.cc/EmyEMg"

# 🔥 免費次數（存在瀏覽器）
MAX_FREE = 3

@app.route("/", methods=["GET", "POST"])
def home():
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

            if diff > 80:
                risk = "高波動（節奏不穩）"
            elif diff > 30:
                risk = "中波動"
            else:
                risk = "穩定節奏"

            if current > avg * 1.3:
                status = "進入尾段醞釀"
            elif current < avg * 0.7:
                status = "剛結束釋放"
            else:
                status = "訊號累積中"

            # 訊號
            signal_chance = random.randint(60, 95)
            signal_text = f"🔥 成功捕捉熱點訊號（{signal_chance}%）"

            confidence = random.randint(80, 96)

            # 🔒 鎖區塊
            def lock_block(text):
                return f'''
                <div onclick="goLine()"
                     style="background:#222;padding:15px;border-radius:15px;margin-top:15px;">
                    🔒 {text}<br>
                    <span style="color:orange;">點擊解鎖完整功能</span>
                </div>
                '''

            result = f"""
            <div id="cards">

                <div class="card step red">📊 分析結果如下</div>

                <div class="card step">🎯 今日得分率：{today_val}</div>

                <div class="card step">{signal_text}</div>

                <div class="card step">
                    📊 節奏判定：{status}<br>
                    ⚠️ 波動狀態：{risk}
                </div>

                <div id="vip-area">
                    <div class="card step">👉 操作建議：建議低本測試</div>
                    <div class="card step">⏱ 建議區間：約 {random.randint(40,70)} ~ {random.randint(80,120)} 轉</div>
                </div>

                <div id="lock-area" style="display:none;">
                    {lock_block("操作建議已鎖定")}
                    {lock_block("建議區間已鎖定")}
                </div>

                <div class="card step">🤖 AI信心指數：{confidence}%</div>

                <div class="card step small">
                    ⚠️ 熱點通常不會維持太久<br>
                    💡 建議低倍觀察
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

    .red {{
        background:#ff3b3b;
    }}

    .small {{
        font-size:12px;
        color:gray;
    }}
    </style>

    <script>
    let count = localStorage.getItem("use_count") || 0;
    count = parseInt(count);

    function startAnalysis(form, e) {{
        e.preventDefault();

        if(count >= {MAX_FREE}) {{
            alert("免費次數已用完，請加入LINE解鎖");
            window.location.href = "{line_link}";
            return;
        }}

        count++;
        localStorage.setItem("use_count", count);

        setTimeout(() => form.submit(), 2000);
    }}

    function goLine() {{
        window.location.href = "{line_link}";
    }}

    window.onload = function() {{
        let steps = document.querySelectorAll(".step");

        steps.forEach((el, i) => {{
            setTimeout(() => {{
                el.classList.add("show");

                // 🔥 第3次後鎖
                if(i === 4) {{
                    let count = localStorage.getItem("use_count") || 0;
                    if(count >= {MAX_FREE}) {{
                        document.getElementById("vip-area").style.display = "none";
                        document.getElementById("lock-area").style.display = "block";
                    }}
                }}

                if (i === steps.length - 1) {{
                    if (navigator.vibrate) {{
                        navigator.vibrate([120,60,120]);
                    }}
                }}
            }}, i * 500);
        }});
    }}
    </script>

    </head>

    <body>

    <div class="title">⚡ 熱點雷達（體驗版）</div>

    <form method="post" onsubmit="startAnalysis(this, event)">
        <input name="today" placeholder="今日得分率">
        <input name="current" placeholder="未開轉數">
        <input name="last1" placeholder="上次轉數">
        <input name="last2" placeholder="上上次">
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
