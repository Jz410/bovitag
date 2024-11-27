from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)

@app.route('/')
@app.route('/login')
def inicio():
    titulo:str = 'Login'
    
    return render_template('login.html', titulo=titulo)

if __name__ == '__main__':
    app.run(debug=True)