from flask import Flask, request, jsonify
  import os, json, requests

  app = Flask(__name__)

  TOKEN = os.environ.get("TELEGRAM_TOKEN")
  CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
  SECRET = os.environ.get("WEBHOOK_SECRET", "fdax_elite_2026")

  @app.route("/health")
  def health():
      return "ok"

  @app.route("/test")
  def test():
      send("FDAX Bot funcionando!")
      return "ok"

  @app.route("/webhook", methods=["POST"])
  def webhook():
      if request.args.get("secret") != SECRET:
          return "unauthorized", 401
      body = request.get_data(as_text=True)
      data = json.loads(body)
      pat = data.get("pat", "?")
      dire = data.get("dir", "?")
      ent = data.get("ent", 0)
      stp = data.get("stp", 0)
      t1 = data.get("t1", 0)
      t2 = data.get("t2", 0)
      macro = data.get("macro", "?")
      tf = data.get("tf", "?")
      risk = abs(float(ent) - float(stp))
      msg = f"FDAX ELITE\n{pat} | {dire} | {tf}\nEntrada: {ent}\nStop: {stp}
  (-{risk:.0f}pts)\nAlvo1: {t1}\nAlvo2: {t2}\nContexto: {macro}"
      send(msg)
      return "ok"

  def send(text):
      url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
      requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)

  if __name__ == "__main__":
      app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

