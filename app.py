from flask import Flask, render_template, url_for, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Chatterbox2005*@localhost/library_db'
app.config['SECRET_KEY'] = 'thisisasecretkey'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # Define the relationship with the transactions table
    transactions = db.relationship('Transaction', back_populates='user')

class Book(db.Model):
    ISBN = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    available = db.Column(db.Boolean, default=True)

    # Define the relationship with the transactions table
    transactions = db.relationship('Transaction', back_populates='book')

    
class Transaction(db.Model):
    __tablename__ = 'transactions'  # Explicitly set the table name as 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_isbn = db.Column(db.BigInteger, db.ForeignKey('book.ISBN'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)

    # Define the relationship with the User model and Book model
    user = db.relationship('User', back_populates='transactions')
    book = db.relationship('Book', back_populates='transactions')


#Admin Model
class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    
    # New field to select role
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')], validators=[InputRequired()])
    
    submit = SubmitField('Register')

    def validate_username(self, username):
        # Check both tables for existing username
        existing_user_username = User.query.filter_by(username=username.data).first()
        existing_admin_username = Admin.query.filter_by(username=username.data).first()
        if existing_user_username or existing_admin_username:
            raise ValidationError('That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(),Length(min=4,max=20)], render_kw={"placeholder":"Username"})
    password = PasswordField(validators=[InputRequired(),Length(min=4,max=20)], render_kw={"placeholder":"Password"})
    submit = SubmitField("Login")

@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/Userlogin', methods=['GET', 'POST'])
def Userlogin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('Userdashboard'))
        else:
            flash('Invalid username or password!', 'danger')  # Flash message if login fails
    return render_template('user_login.html', form=form)


@app.route('/Adminlogin', methods=['GET', 'POST'])
def Adminlogin():
    form = LoginForm()
    if form.validate_on_submit():
        # Change from User to Admin
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and bcrypt.check_password_hash(admin.password, form.password.data):
            login_user(admin)
            return redirect(url_for('Admindashboard'))

        else:
            flash('Invalid admin username or password!', 'danger')  # Admin-specific flash message
    return render_template('admin_login.html', form=form)


@app.route('/Register', methods=['GET', 'POST'])
def Register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        if form.role.data == 'user':
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
        elif form.role.data == 'admin':
            new_admin = Admin(username=form.username.data, password=hashed_password)
            db.session.add(new_admin)

        db.session.commit()
        flash(f'Account created successfully as {form.role.data}!', 'success')
        
        # Redirect to the appropriate login page based on role
        if form.role.data == 'user':
            return redirect(url_for('Userlogin'))
        else:
            return redirect(url_for('Adminlogin'))
    
    return render_template('register.html', form=form)


@app.route('/Userdashboard', methods=['GET', 'POST'])
@login_required
def Userdashboard():
    return render_template('user_dashboard.html')

@app.route('/Admindashboard', methods=['GET', 'POST'])
@login_required
def Admindashboard():
    return render_template('admin_dashboard.html')

##########
##### For the User dahsboard, the routes are as follows ####
##########

@app.route('/catalog')
def catalog():
    books = Book.query.all()  # Fetch all books from the database
    return render_template('catalog.html', books=books)


# Route for Fines
@app.route('/fines')
def fines():
    return render_template('fines.html')  # Replace this with the template for fines.

# Route for Logout
@app.route('/logout')
def logout():
    return render_template('user_login.html')  # Replace with the login page template.


@app.route('/borrow_return', methods=['GET', 'POST'])
@login_required
def borrow_return():
    if request.method == 'POST':
        book_id = request.form.get('book_id')
        action = request.form.get('action')
        
        # Fetch the book from the database
        book = Book.query.filter_by(ISBN=book_id).first()
        
        if not book:
            flash('Book not found!', 'danger')
            return redirect(url_for('borrow_return'))
        
        # Handle the borrow action
        if action == 'borrow' and book.available:
            # Create a transaction for borrowing
            transaction = Transaction(
                user_id=current_user.id,
                book_isbn=book.ISBN,
                borrow_date=datetime.utcnow()
            )
            db.session.add(transaction)
            book.available = False  # Update book availability to 'No'
            db.session.commit()
            flash('You have successfully borrowed the book!', 'success')

        # Handle the return action
        elif action == 'return' and not book.available:
            # Update the transaction with a return date
            transaction = Transaction(
                user_id=current_user.id,
                book_isbn=book.ISBN,
                return_date=datetime.utcnow()
            )
            db.session.add(transaction)
            book.available = True  # Update book availability to 'Yes'
            db.session.commit()
            flash('You have successfully returned the book!', 'success')
        
        else:
            flash('Invalid action or book status!', 'danger')
        
        return redirect(url_for('borrow_return'))

    return render_template('borrow_return.html')

#######
# Admin Dashboard
#######

#For managing books route
@app.route('/admin_book_catalog')
def admin_catalog():
    books = Book.query.all()  # Fetch all books from the database
    return render_template('catalog.html', books=books)


# Route for Suppliers and Publishers
@app.route('/suppliers_publishers')
def suppliers():
    return render_template('suppliers_publishers.html')  

# Route for Suppliers and Publishers Adding
@app.route('/suppliers_publishers_add')
def add_suppliers():
    return render_template('add_supplier_publisher.html')  

# Route for Suppliers and Publishers Editing
@app.route('/suppliers_publishers_edit')
def edit_suppliers():
    return render_template('edit_supplier_publisher.html') 

# Route for Suppliers and Publishers Deleting
@app.route('/suppliers_publishers_delete')
def delete_suppliers():
    return render_template('delete_supplier_publisher.html') 

# Route for Users
@app.route('/user_management')
def users():
    return render_template('user_management.html')  

# Route for Transactions
@app.route('/transactions')
def transactions():
    return render_template('transactions.html') 

# # Route for Borrow Records
# @app.route('/borrowing_records')
# def borrow():
#     return render_template('user_login.html')  

# Route for Logout
@app.route('/admin_logout')
def Adminlogout():
    return render_template('admin_login.html')  


if __name__=='__main__':
    app.run(debug=True)