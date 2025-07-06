from flask import Flask, request, jsonify
import smtplib, ssl, random

app = Flask(__name__)
codigos = {}

# Substitua pelos seus dados:
GMAIL_USER = "baianor058@gmail.com"
GMAIL_PASS = "ltiu pfwn qgvb khsi"

@app.route('/gerar_codigo', methods=['POST'])
def gerar_codigo():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"erro": "E-mail não fornecido"}), 400

    codigo = str(random.randint(100000, 999999))
    codigos[email] = codigo

    mensagem = f"Subject: Código de Verificação VIPCINE\n\nSeu código é: {codigo}"

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, email, mensagem)

        return jsonify({"mensagem": "Código enviado com sucesso!"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/verificar_codigo', methods=['POST'])
def verificar_codigo():
    data = request.get_json()
    email = data.get('email')
    codigo = data.get('codigo')

    if codigos.get(email) == codigo:
        return jsonify({"verificado": True})
    else:
        return jsonify({"verificado": False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
