from flask import Flask , render_template , request ,session , redirect
from flask_login import LoginManager , UserMixin , login_user , login_required , logout_user , current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash , check_password_hash
app = Flask(__name__)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = None
class User(UserMixin ,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80), nullable=True)
    lastname = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    disease = db.Column(db.String(255), nullable=True)
    confirmed_at = db.Column(db.DateTime, nullable=False,default= datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False,default= datetime.utcnow)
    def __init__(self,**kwargs):
        for property, value in kwargs.items():
            if property == 'password':
                value = generate_password_hash(value, method='sha256')
            setattr(self,property,value)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def HelloWorld():
    return render_template('home.html' , title='Home');

@app.route('/signin' , methods=['GET','POST'])
def SignIn():
    if request.method == 'GET':
        if(current_user.is_authenticated):
            return redirect('/')
        return render_template('signin.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect('/')

@app.route('/signup' ,  methods=['GET','POST'])
def SignUp():
    if request.method == 'GET':
        if(current_user.is_authenticated):
            return redirect('/')
        return render_template('signup.html')
    if request.method == 'POST':
        data = request.form
        if data['password'] != data['confirm_password']:
            return redirect('/signup')
        user = User.query.filter_by(email=data['email']).first()
        if user:
            return redirect('/signin')
        datatuple = User(**data)
        db.session.add(datatuple)
        db.session.commit()
        return redirect('/signin')

    

@app.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect('/signin')

@app.route('/predict' , methods=['GET'])
@login_required
def predict():
    available_diseases = ["val1", "val2","val3"]
    return render_template('predict.html' ,available_diseases=available_diseases)

@app.route('/predict-disease' , methods=['GET','POST'])
@login_required
def predictDisease():
    diseases = request.form.getlist('diseases')
    print(request.form.getlist('diseases'))
    result = "someDisease"
    return render_template('predict.html' , disease=result)


if __name__ == '__main__':
    db.create_all()
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
    app.debug = True
    app.run(port = 5000)
