from flask import Flask, render_template, request
import mysql.connector
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

db_config = {
    'user': 'root',
    'password': 'fatec',
    'host': 'localhost',
    'database': 'newsletter'
}
conn = mysql.connector.connect(**db_config)

smtp_server = 'smtp.gmail.com'
smtp_port = 587  
smtp_username = 'islink.newsletter@gmail.com'
smtp_password = "rkvd mfes ujbz wzqc"

def send_confirmation_email(email):
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = email
    msg['Subject'] = 'Confirmação de inscrição'

    body = 'Seu email foi cadastrado com sucesso na nossa newsletter!'
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        print("Email enviado com sucesso!")
    except Exception as e:
        print("Erro ao enviar o email:", e)


@app.route('/')
def index():
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM email")
    emails = [row[0] for row in cursor.fetchall()] 
    cursor.close()
    return render_template('index.html', emails=emails)

@app.route('/fotos')
def fotos():
    return render_template('fotos.html')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/novidade')
def novidade():
    cursor = conn.cursor()
    cursor.execute("SELECT nome, email FROM usuario")
    usuarios = cursor.fetchall()
    cursor.close()
    return render_template('novidade.html', usuarios=usuarios)


@app.route('/inscrever', methods=['POST'])
def inscrever():
    nome = request.form['nome']
    email = request.form['email']

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM email WHERE email = %s", (email,))
    existing_emails = cursor.fetchall()
    cursor.close()

    if existing_emails:
        return render_template('novidade.html', mensagem1="Este e-mail já está cadastrado.")
    else:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO email (email) VALUES (%s)", (email,))
        conn.commit()
        cursor.close()

        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuario (nome, email) VALUES (%s, %s)", (nome, email))
        conn.commit()
        cursor.close()

        send_confirmation_email(email)

        return render_template('novidade.html', mensagem2="E-mail cadastrado com sucesso!")


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
