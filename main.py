from flask import Flask, request, jsonify
import smtplib
import ssl
import random
import time
import os

app = Flask(__name__)
codigos = {}

# Login do Gmail
GMAIL_USER = os.environ.get("GMAIL_USER", "seuemail@gmail.com")
GMAIL_PASS = os.environ.get("GMAIL_PASS", "senha_do_app")

# Página inicial simples
@app.route('/')
def home():
    return "✅ API VIPCINE ONLINE – Use /gerar_codigo e /verificar_codigo com POST"

# Rota para gerar código
@app.route('/gerar_codigo', methods=['POST'])
def gerar_codigo():
    try:
        data = request.get_json(force=True)
        email = data.get('email')

        if not email:
            return jsonify({"erro": "E-mail não fornecido"}), 400

        codigo = str(random.randint(100000, 999999))
        tempo_expiracao = time.time() + 300  # 5 minutos (300 segundos)

        codigos[email] = {
            "codigo": codigo,
            "expira_em": tempo_expiracao
        }

        mensagem = f"""Subject: Código de Verificação VIPCINE

Seu código é: {codigo}
Este código expira em 5 minutos."""

        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, email, mensagem.encode('utf-8'))

        return jsonify({"mensagem": "Código enviado com sucesso!"})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# Rota para verificar código
@app.route('/verificar_codigo', methods=['POST'])
def verificar_codigo():
    try:
        data = request.get_json(force=True)
        email = data.get('email')
        codigo = data.get('codigo')

        dados = codigos.get(email)
        if not dados:
            return jsonify({"verificado": False, "erro": "Nenhum código gerado para este e-mail."})

        tempo_restante = int(dados["expira_em"] - time.time())

        if tempo_restante <= 0:
            del codigos[email]
            return jsonify({"verificado": False, "erro": "Código expirado", "tempo_restante": 0})

        if dados["codigo"] == codigo:
            del codigos[email]  # Remove o código após uso
            return jsonify({"verificado": True, "tempo_restante": tempo_restante})
        else:
            return jsonify({
                "verificado": False,
                "erro": "Código incorreto",
                "tempo_restante": tempo_restante
            })

    except Exception as e:
        return jsonify({"verificado": False, "erro": str(e)}), 500

# Inicia o servidor na porta do Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render define essa variável
    app.run(host='0.0.0.0', port=port)
