from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
import random
import string
from flask_mail import Mail, Message
import re


app = Flask(__name__)
app.secret_key = 'abc123secreta'

# Configurare email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mathealexandra1@gmail.com'
app.config['MAIL_PASSWORD'] = 'crvj tniq acfm ptfw'  # NU parola Gmail, ci parola de aplicație!

mail = Mail(app)

# Funcție conexiune MySQL
def get_connection():
    return mysql.connector.connect(
        host='192.168.98.51',
        user='root',
        password='root',
        database='parcare'
    )

# Pagina principală
@app.route('/')
def index():
    return render_template('login.html')

# Trimitere cod pe email
@app.route('/send_code', methods=['POST'])
def send_code():
    email = request.form['email']
    password = request.form['password']

    code = ''.join(random.choices(string.digits, k=6))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    if user:
        cursor.execute("UPDATE users SET password=%s, code=%s WHERE email=%s", (password, code, email))
    else:
        cursor.execute("INSERT INTO users (email, password, code) VALUES (%s, %s, %s)", (email, password, code))
    conn.commit()
    conn.close()

    # Trimitere email
    msg = Message('Cod de verificare', sender='mathealexandra1@gmail.com', recipients=[email])
    msg.body = f'Codul tau de autentificare este: {code}'
    mail.send(msg)

    session['email'] = email
    return render_template('verify.html')

# Verificare cod
@app.route('/verify_code', methods=['POST'])
def verify_code():
    entered_code = request.form['code']
    email = session.get('email')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT code FROM users WHERE email=%s", (email,))
    db_code = cursor.fetchone()
    conn.close()

    if db_code and entered_code == db_code[0]:
        session['logged_in'] = True
        return redirect('/dashboard')
    else:
        return 'Cod incorect. Încearcă din nou.'

# Dashboard utilizator
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/')

    email = session.get('email')
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Obține ID-ul utilizatorului
    cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return redirect('/')

    user_id = user['id']

    # Obține mașinile utilizatorului
    cursor.execute("SELECT nrinmatriculare, nume, functie, id FROM masini WHERE users_id=%s", (user_id,))
    cars = cursor.fetchall()

    conn.close()
    return render_template('dashboard.html', cars=cars)


# Ștergere mașină
@app.route('/delete_car/<int:car_id>', methods=['POST'])
def delete_car(car_id):
    if not session.get('logged_in'):
        return redirect('/')

    email = session.get('email')
    conn = get_connection()
    cursor = conn.cursor()

    # Verifică dacă mașina aparține utilizatorului
    cursor.execute("SELECT users_id FROM masini WHERE id=%s", (car_id,))
    car = cursor.fetchone()

    if car:
        user_id = car[0]  # Folosim indexul pentru a accesa valoarea corectă

        # Verifică dacă utilizatorul are permisiunea să șteargă mașina
        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        current_user_id = cursor.fetchone()[0]
        
        if current_user_id == user_id:
            # Șterge mașina din baza de date
            cursor.execute("DELETE FROM masini WHERE id=%s", (car_id,))
            conn.commit()
            flash("Mașina a fost ștearsă cu succes!", "success")
        else:
            flash("Nu ai permisiunea să ștergi această mașină.", "error")
    else:
        flash("Mașina nu a fost găsită.", "error")

    conn.close()
    return redirect('/dashboard')


@app.route('/edit_car/<int:car_id>', methods=['GET', 'POST'])
def edit_car(car_id):
    if not session.get('logged_in'):
        return redirect('/')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)  # ca să accesezi car['nrinmatricuolare']

    cursor.execute("SELECT * FROM masini WHERE id=%s", (car_id,))
    car = cursor.fetchone()

    if not car:
        conn.close()
        flash("Mașina nu a fost găsită.", "error")
        return redirect('/dashboard')

    if request.method == 'POST':
        new_plate = request.form['plate'].upper().strip()

        # Validare placă
        pattern = r'^([A-Z]{1,2})(\d{2,3})([A-Z]{3})$'
        match = re.match(pattern, new_plate)

        judete_valide = {
            "AB", "AR", "AG", "BC", "BH", "BN", "BR", "BT", "BV", "BZ",
            "CS", "CL", "CJ", "CT", "CV", "DB", "DJ", "GL", "GR", "GJ",
            "HR", "HD", "IL", "IS", "IF", "MM", "MH", "MS", "NT", "OT",
            "PH", "SM", "SJ", "SB", "SV", "TR", "TM", "TL", "VS", "VL", "VN", "B"
        }

        if not match or match.group(1) not in judete_valide:
            flash("Numărul de înmatriculare este invalid. Verifică formatul și județul!", "error")
            conn.close()
            return redirect(f'/edit_car/{car_id}')

        cursor.execute("""
            UPDATE masini
            SET nrinmatriculare = %s
            WHERE id = %s
        """, (new_plate, car_id))
        conn.commit()

        flash("Numărul de înmatriculare a fost actualizat cu succes!", "success")
        conn.close()
        return redirect('/dashboard')

    conn.close()
    return render_template('edit_car.html', car=car)





# Adăugare mașină
@app.route('/add_car', methods=['POST'])
def add_car():
    if not session.get('logged_in'):
        return redirect('/')

    plate = request.form.get('plate', '').upper()  # transformă automat în litere mari
    name = request.form.get('name', '')
    function = request.form.get('function', '')
    email = session.get('email')

    # Validare format placă
    pattern = r'^([A-Z]{1,2})(\d{2,3})([A-Z]{3})$'
    match = re.match(pattern, plate)

    judete_valide = {
        "AB", "AR", "AG", "BC", "BH", "BN", "BR", "BT", "BV", "BZ",
        "CS", "CL", "CJ", "CT", "CV", "DB", "DJ", "GL", "GR", "GJ",
        "HR", "HD", "IL", "IS", "IF", "MM", "MH", "MS", "NT", "OT",
        "PH", "SM", "SJ", "SB", "SV", "TR", "TM", "TL", "VS", "VL", "VN", "B"
    }

    if not match or match.group(1) not in judete_valide:
        flash("Numărul de înmatriculare este invalid. Verifică formatul și județul!", "error")
        return redirect('/dashboard')

    # Obține ID-ul utilizatorului
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
    user_id = cursor.fetchone()[0]

    # Adaugă mașina în baza de date
    cursor.execute("INSERT INTO masini (nrinmatriculare, nume, functie, users_id) VALUES (%s, %s, %s, %s)", (plate, name, function, user_id))
    conn.commit()
    conn.close()


    flash("Mașina a fost adăugată cu succes!", "success")
    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.clear()
    #flash("Te-ai deconectat cu succes.", "info")
    return redirect('/')





if __name__ == '__main__':
    app.run(debug=True)
