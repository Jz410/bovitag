from flask import redirect, session, flash

def Verificador(Ruta:str):
    if 'user_id' not in session:
        flash(f"Debes iniciar sesión para acceder al {Ruta}", "warning")
        return redirect('/login')