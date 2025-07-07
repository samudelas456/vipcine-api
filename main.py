from flask import Flask, request, jsonify
import smtplib
import ssl
import random
import time
import os

app = Flask(__name__)
codigos = {}

GMAIL_USER = os.environ.get("GMAIL_USER", "vipcinebr@gmail.com")
GMAIL_PASS = os.environ.get("GMAIL_PASS", "boao kxzz hqhr unau")

@app.route('/')
def home():
    return "✅ API VIPCINE ONLINE – Use /gerar_codigo e /verificar_codigo com POST"

@app.route('/gerar_codigo', methods=['POST'])
def gerar_codigo():
    try:
        data = request.get_json(force=True)
        email = data.get('email', '').strip().lower()

        if not email:
            return jsonify({"erro": "E-mail não fornecido"}), 400

        codigo = str(random.randint(100000, 999999))
        expira_em = time.time() + 300  # 5 minutos

        codigos[email] = {
            "codigo": codigo,
            "expira_em": expira_em
        }

        mensagem = f"Subject: Código de Verificação VIPCINE\n\nSeu código é: {codigo}"

        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, email, mensagem.encode('utf-8'))

        return jsonify({"mensagem": "Código enviado com sucesso!", "tempo_restante": 300})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/verificar_codigo', methods=['POST'])
def verificar_codigo():
    try:
        data = request.get_json(force=True)
        email = data.get('email', '').strip().lower()
        codigo = str(data.get('codigo', '')).strip()

        info = codigos.get(email)

        if not info:
            return jsonify({
                "verificado": False,
                "erro": "Código não encontrado.",
                "tempo_restante": 0
            })

        tempo_restante = int(info['expira_em'] - time.time())

        if tempo_restante <= 0:
            return jsonify({
                "verificado": False,
                "erro": "Código expirado.",
                "tempo_restante": 0
            })

        if info['codigo'] == codigo:
            return jsonify({
                "verificado": True,
                "tempo_restante": tempo_restante
            })
        else:
            return jsonify({
                "verificado": False,
                "erro": "Código incorreto.",
                "tempo_restante": tempo_restante
            })

    except Exception as e:
        return jsonify({"erro": str(e), "verificado": False}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
