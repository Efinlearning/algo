from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, BrokerCredentials

app = Flask(__name__)
app.secret_key = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/data.db'

# Initialize the database
db.init_app(app)

# Routes
@app.route('/')
def index():
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect('/broker')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

@app.route('/broker', methods=['GET', 'POST'])
def broker():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        broker_username = request.form['broker_username']
        broker_password = request.form['broker_password']
        credentials = BrokerCredentials(
            user_id=session['user_id'],
            broker_username=broker_username,
            broker_password=broker_password
        )
        db.session.add(credentials)
        db.session.commit()
        return redirect('/auth-code')
    return render_template('broker.html')

@app.route('/auth-code')
def auth_code():
    auth_code = "AUTH123456"  # Replace with actual broker API code logic
    return render_template('auth_code.html', auth_code=auth_code)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    # Dummy option chain data
    option_chain = [
        {"strike_price": 17000, "call_oi": 5000, "put_oi": 4000},
        {"strike_price": 17100, "call_oi": 6000, "put_oi": 3000},
    ]

    user = User.query.filter_by(id=session['user_id']).first()
    return render_template('dashboard.html', option_chain=option_chain, user=user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
