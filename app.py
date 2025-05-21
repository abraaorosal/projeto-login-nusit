from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import json
import os

app = Flask(__name__)

# Caminho do arquivo de usuários
ARQUIVO_USUARIOS = "usuarios.json"
LINK_DASHBOARD = "https://script.google.com/macros/s/AKfycbyhqCf8NUBmSNkiEsyABrGTZeINNRtPEnbc95h_N7owOjaDkHhGuis6ZCxuI3ekfPwxDg/exec"

def carregar_usuarios():
    if not os.path.exists(ARQUIVO_USUARIOS):
        return {}
    with open(ARQUIVO_USUARIOS, "r") as f:
        return json.load(f)

def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, "w") as f:
        json.dump(usuarios, f, indent=4)

def registrar_acesso(usuario, ip):
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"{agora} - Usuário: {usuario} - IP: {ip}\n"
    with open("acessos.log", "a") as log:
        log.write(linha)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['usuario']
    senha = request.form['senha']
    usuarios = carregar_usuarios()

    if usuario in usuarios and usuarios[usuario]['senha'] == senha:
        ip = request.remote_addr or "IP não detectado"
        registrar_acesso(usuario, ip)

        if usuarios[usuario]['tipo'] == "admin":
            return redirect(url_for('painel_admin'))
        else:
            return render_template("transicao.html", link=LINK_DASHBOARD)

    else:
        return render_template('erro.html', mensagem="Usuário ou senha incorretos.")

@app.route('/admin')
@app.route('/admin')
def painel_admin():
    usuarios = carregar_usuarios()
    acessos = []

    filtro_usuario = request.args.get("usuario")

    if os.path.exists("acessos.log"):
        with open("acessos.log", "r") as f:
            for linha in f:
                if not filtro_usuario or f"Usuário: {filtro_usuario}" in linha:
                    acessos.append(linha.strip())

    return render_template('admin.html', usuarios=usuarios, acessos=acessos, filtro_usuario=filtro_usuario)

@app.route('/admin/criar', methods=['GET', 'POST'])
def criar_usuario():
    if request.method == 'POST':
        novo_usuario = request.form['usuario']
        nova_senha = request.form['senha']
        tipo = request.form['tipo']
        usuarios = carregar_usuarios()
        if novo_usuario in usuarios:
            return render_template('erro.html', mensagem="Usuário já existe.")
        usuarios[novo_usuario] = {"senha": nova_senha, "tipo": tipo}
        salvar_usuarios(usuarios)
        return redirect(url_for('painel_admin'))
    return render_template('criar_usuario.html')

@app.route('/admin/resetar', methods=['POST'])
def resetar_senha():
    usuario = request.form['usuario']
    usuarios = carregar_usuarios()
    if usuario in usuarios:
        usuarios[usuario]['senha'] = '123456'  # Senha padrão
        salvar_usuarios(usuarios)
    return redirect(url_for('painel_admin'))

@app.route('/admin/excluir', methods=['POST'])
def excluir_usuario():
    usuario = request.form['usuario']
    usuarios = carregar_usuarios()
    if usuario in usuarios and usuario != 'admin':
        del usuarios[usuario]
        salvar_usuarios(usuarios)
    return redirect(url_for('painel_admin'))

@app.route('/logout')
def logout():
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
