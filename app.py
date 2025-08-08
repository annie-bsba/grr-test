from flask import Flask, render_template, request, redirect, url_for, session, flash
import datetime

app = Flask(__name__)
app.secret_key = 'topsecretkey'  # Use env vars in production

USERNAME = 'admin'
PASSWORD = 'surveillance123'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        if user == USERNAME and pwd == PASSWORD:
            session['user'] = user
            return redirect(url_for('dashboard'))
        else:
            flash('Access Denied: Invalid Credentials', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('You must be logged in to view the dashboard.', 'warning')
        return redirect(url_for('login'))

    surveillance_logs = [
        {'ip': '192.168.0.12', 'activity': 'Port scan detected', 'timestamp': datetime.datetime.now()},
        {'ip': '10.0.0.8', 'activity': 'Login attempt failed', 'timestamp': datetime.datetime.now()},
        {'ip': '172.16.5.21', 'activity': 'Unusual traffic spike', 'timestamp': datetime.datetime.now()},
    ]
    return render_template('dashboard.html', logs=surveillance_logs)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
