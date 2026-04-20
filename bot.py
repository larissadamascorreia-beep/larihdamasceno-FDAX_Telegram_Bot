from flask import Flask, request, jsonify
  import os
  import json
  import requests
  from datetime import datetime

  app = Flask(__name__)

  TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
  CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
  SECRET = os.environ.get("WEBHOOK_SECRET", "fdax_elite_2026")

  def send_telegram(text):
      url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
      payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
      r = requests.post(url, json=payload, timeout=10)
      return r.status_code

  def format_signal(d):
      pat = d.get("pat", "?")
      direction = d.get("dir", "?")
      entry = float(d.get("ent", 0))
      stop = float(d.get("stp", 0))
      t1 = float(d.get("t1", 0))
      t2 = float(d.get("t2", 0))
      macro = d.get("macro", "NEUTRO")
      ms = int(d.get("ms", 0))
      tf = d.get("tf", "??:??")
      risk = abs(entry - stop)
      risk_eur = risk * 25
      t1_pts = abs(t1 - entry)
      t2_pts = abs(t2 - entry)
      rr = round(t2_pts / risk, 1) if risk > 0 else 3
      arrow = "LONG" if direction == "LONG" else "SHORT"
      msg = f"FDAX ELITE - SINAL\n"
      msg += f"{pat} | {arrow} | {tf} Frankfurt\n\n"
      msg += f"Entrada: {entry:.1f}\n"
      msg += f"Stop: {stop:.1f} (-{risk:.0f}pts /
  -EUR{risk_eur:.0f}/contrato)\n"
      msg += f"Alvo 1: {t1:.1f} (+{t1_pts:.0f}pts) - fechar 50%\n"
      msg += f"Alvo 2: {t2:.1f} (+{t2_pts:.0f}pts) - fechar 50%\n"
      msg += f"R:R: 1:{rr}\n"
      msg += f"Contexto: {macro} ({ms:+d}%)\n"
      msg += "Confirme no grafico antes de executar."
      return msg

  @app.route("/webhook", methods=["POST"])
  def webhook():
      if request.args.get("secret") != SECRET:
          return jsonify({"error": "unauthorized"}), 401
      body = request.get_data(as_text=True)
      try:
          data = json.loads(body)
      except Exception:
          s = body.find("{")
          e = body.rfind("}") + 1
          data = json.loads(body[s:e])
      msg = format_signal(data)
      status = send_telegram(msg)
      return jsonify({"ok": True, "status": status})

  @app.route("/health")
  def health():
      return jsonify({"status": "ok"})

  @app.route("/test")
  def test():
      data = {"pat": "SPRING", "dir": "LONG", "ent": 24312.0,
              "stp": 24282.0, "t1": 24357.0, "t2": 24402.0,
              "macro": "RISK_ON", "ms": 65, "tf": "08:14"}
      msg = format_signal(data)
      status = send_telegram(msg)
      return jsonify({"ok": True, "telegram": status})

  if __name__ == "__main__":
      port = int(os.environ.get("PORT", 8080))
      app.run(host="0.0.0.0", port=port)

