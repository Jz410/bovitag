from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('inicio'))

@app.route('/login', methods=["POST", "GET"])
def inicio():
    titulo:str = 'Login'
    if request.method == "POST":
        user = request.form.get("user", "N/A")
        password = request.form.get("password", "N/A")

        if (user, password) == (user,password):
            pass
    else:
        user, password = None, None
    
    return render_template('login.html', titulo=titulo)

if __name__ == '__main__':
    app.run(debug=True)