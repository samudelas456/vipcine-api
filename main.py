from flask import Flask, request, jsonify
import smtplib
import ssl
import random
import os

app = Flask(__name__)
codigos = {}

GMAIL_USER = os.environ.get("GMAIL_USER", "seuemail@gmail.com")
GMAIL_PASS = os.environ.get("GMAIL_PASS", "sua_senha_de_app")

@app.route('/')
def home():
    return "✅ API VIPCINE ONLINE – Use /gerar_codigo e /verificar_codigo com POST"

@app.route('/gerar_codigo', methods=['POST'])
def gerar_codigo():
    try:
        data = request.get_json(force=True)
        email = data.get('email')

        if not email:
            return jsonify({"erro": "E-mail não fornecido"}), 400

        codigo = str(random.randint(100000, 999999))
        codigos[email] = codigo

        mensagem = f"Subject: Código de Verificação VIPCINE\n\nSeu código é: {codigo}"

        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, email, mensagem.encode('utf-8'))

        return jsonify({"mensagem": "Código enviado com sucesso!"})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/verificar_codigo', methods=['POST'])
def verificar_codigo():
    try:
        data = request.get_json(force=True)
        email = data.get('email')
        codigo = data.get('codigo')

        if codigos.get(email) == codigo:
            return jsonify({"verificado": True})
        else:
            return jsonify({"verificado": False})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
