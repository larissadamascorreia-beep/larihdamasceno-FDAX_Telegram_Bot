from flask import Flask, request, jsonify
  import requests, json, os
  from datetime import datetime
  from zoneinfo import ZoneInfo

  app = Flask(__name__)
  FRANKFURT = ZoneInfo("Europe/Berlin")

  TOKEN   = os.environ.get("TELEGRAM_TOKEN", "")
  CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
  SECRET  = os.environ.get("WEBHOOK_SECRET", "fdax_elite_2026")

  PATTERNS = {
      "FALSE_OPEN":     "⚡ FALSE OPEN",
      "SPRING":         "🌊 SPRING",
      "VWAP_RECLAIM":   "🔵 VWAP RECLAIM",
      "PDL_ABS":        "🟢 PDL ABSORPTION",
      "PDH_ABS":        "🔴 PDH ABSORPTION",
      "DRIFT":          "🟣 POST-RELEASE DRIFT",
  }

  PATTERN_DESC = {
      "FALSE_OPEN":     "Falso movimento de abertura revertendo",
      "SPRING":         "Stop hunt institucional — absorção no fundo",
      "VWAP_RECLAIM":   "Preço recuperou o VWAP — momentum confirmado",
      "PDL_ABS":        "PDL segurou — compradores absorveram",
      "PDH_ABS":        "PDH rejeitou — vendedores absorveram",
      "DRIFT":          "Drift direcional pós-dado econômico",
  }

  def format_signal(d):
      pattern  = d.get("pat", "?")
      direction = d.get("dir", "?")
      entry    = float(d.get("ent", 0))
      stop     = float(d.get("stp", 0))
      t1       = float(d.get("t1", 0))
      t2       = float(d.get("t2", 0))
      macro    = d.get("macro", "NEUTRO")
      mscore   = int(d.get("ms", 0))
      time_str = d.get("tf", datetime.now(FRANKFURT).strftime("%H:%M"))

      dir_arrow = "📈 LONG" if direction == "LONG" else "📉 SHORT"
      pat_label = PATTERNS.get(pattern, pattern)
      desc      = PATTERN_DESC.get(pattern, "")
      risk_pts  = abs(entry - stop)
      risk_eur  = risk_pts * 25
      t1_pts    = abs(t1 - entry)
      t2_pts    = abs(t2 - entry)
      rr        = f"1:{round(t2_pts / risk_pts, 1)}" if risk_pts > 0 else "1:3"
      mac_label = {"RISK_ON": "📈 RISK ON", "RISK_OFF": "📉 RISK
  OFF"}.get(macro, "⚖️  NEUTRO")

      return f"""🎯 <b>FDAX ELITE — SINAL</b>
  ━━━━━━━━━━━━━━━━━━━━━
  <b>{pat_label}</b>
  <b>{dir_arrow}</b>  |  ⏰ {time_str} Frankfurt

  <i>{desc}</i>

  <b>Entrada:</b>  <code>{entry:.1f}</code>
  <b>Stop:</b>     <code>{stop:.1f}</code>  <i>(-{risk_pts:.0f}pts /
  -€{risk_eur:.0f}/contrato)</i>
  <b>Alvo 1:</b>   <code>{t1:.1f}</code>  <i>(+{t1_pts:.0f}pts) — fechar 50%</i>
  <b>Alvo 2:</b>   <code>{t2:.1f}</code>  <i>(+{t2_pts:.0f}pts) — fechar 50%</i>
  <b>R:R:</b>      <b>{rr}</b>

  <b>Contexto:</b> {mac_label}  <i>(MacroScore: {mscore:+d}%)</i>
  ━━━━━━━━━━━━━━━━━━━━━
  ⚠️  <i>Confirme no gráfico antes de executar.</i>""".strip()

  def send(msg):
      if not TOKEN or not CHAT_ID:
          return 0
      r = requests.post(
          f"https://api.telegram.org/bot{TOKEN}/sendMessage",
          json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"},
          timeout=10
      )
      return r.status_code

  @app.route("/webhook", methods=["POST"])
  def webhook():
      if request.args.get("secret") != SECRET:
          return jsonify({"error": "unauthorized"}), 401
      try:
          body = request.get_data(as_text=True)
          try:
              data = json.loads(body)
          except json.JSONDecodeError:
              s, e = body.find("{"), body.rfind("}") + 1
              data = json.loads(body[s:e]) if s >= 0 else {}
          msg = format_signal(data)
          status = send(msg)
          return jsonify({"ok": True, "status": status})
      except Exception as ex:
          return jsonify({"error": str(ex)}), 500

  @app.route("/health")
  def health():
      return jsonify({"status": "ok", "version": "2.0"})

  @app.route("/test")
  def test():
      data = {"pat": "SPRING", "dir": "LONG", "ent": 24312.0, "stp": 24282.0,
              "t1": 24357.0, "t2": 24402.0, "macro": "RISK_ON", "ms": 65, "tf":
  "08:14"}
      msg = format_signal(data)
      status = send(msg)
      return jsonify({"ok": True, "telegram_status": status})

  if __name__ == "__main__":
      app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

