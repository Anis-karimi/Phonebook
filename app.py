from flask import Flask, request, jsonify, render_template, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import re
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

client = MongoClient("mongodb://localhost:27017/")
db = client["phonebook"]
contacts_collection = db["Person"]
users_collection = db["Users"]

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_login'

phone_pattern = re.compile(r'^\d{11}$')

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(str(user["_id"]))
    return None

def validate_phone_number(phone_number):
    if phone_pattern.match(phone_number):
        return True
    else:
        return False

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = users_collection.find_one({"_id": ObjectId(current_user.id)})
            if user and user.get("role") == role:
                return f(*args, **kwargs)
            return "Access denied", 403
        return decorated_function
    return decorator

@app.route('/')
@login_required
def index():
    user_role = users_collection.find_one({"_id": ObjectId(current_user.id)})["role"]
    return render_template('index.html', role=user_role)


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            user_obj = User(str(user["_id"]))
            login_user(user_obj)
            return redirect(url_for('index'))
        return "Invalid email or password", 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # Check if an admin already exists
        if role == 'admin' and users_collection.find_one({"role": "admin"}):
            return "An admin already exists", 400

        if users_collection.find_one({"email": email}):
            return "Email already exists", 400
        
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({"email": email, "password": hashed_password, "role": role})
        return redirect(url_for('user_login'))
    # Check if an admin already exists to display the appropriate message
    admin_exists = users_collection.find_one({"role": "admin"}) is not None
    return render_template('register.html', admin_exists=admin_exists)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('user_login'))

@app.route('/contacts', methods=['POST'])
@login_required
@role_required('admin')
def add_contact():
    data = request.json
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    phone_number = data.get("phone_number")
        
    if validate_phone_number(phone_number):
        contact = {
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number,
            "user_id": current_user.id
        }
        contacts_collection.insert_one(contact)
        return jsonify({"message": "Contact added successfully!"}), 201
    else:
        return jsonify({"message": "Invalid phone number. It should be 11 digits."}), 400

@app.route('/contacts', methods=['GET'])
@login_required
def get_contacts():
    user = users_collection.find_one({"_id": ObjectId(current_user.id)})
    if not user:
        return jsonify({"message": "User not found"}), 404

    role = user.get("role") 
    
    if role == 'admin':
        # ادمین می‌تواند تمام مخاطبین را ببیند
        contacts = list(contacts_collection.find())
    else:
        # کاربران عادی فقط مخاطبین خودشان را می‌بینند
        contacts = list(contacts_collection.find())

    for contact in contacts:
        contact["_id"] = str(contact["_id"])  # تبدیل ObjectId به str برای JSON
    return jsonify(contacts), 200



@app.route('/contacts/<contact_id>', methods=['PUT'])
@login_required
@role_required('admin')
def update_contact(contact_id):
    data = request.json
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    phone_number = data.get("phone_number")
    
    update_fields = {}
    if first_name:
        update_fields["first_name"] = first_name
    if last_name:
        update_fields["last_name"] = last_name
    if phone_number and validate_phone_number(phone_number):
        update_fields["phone_number"] = phone_number
    elif phone_number:
        return jsonify({"message": "Invalid phone number. It should be 11 digits."}), 400
    
    contacts_collection.update_one({"_id": ObjectId(contact_id)}, {"$set": update_fields})
    return jsonify({"message": "Contact updated successfully!"}), 200

@app.route('/contacts/<contact_id>', methods=['DELETE'])
@login_required
@role_required('admin')
def delete_contact(contact_id):
    contacts_collection.delete_one({"_id": ObjectId(contact_id)})
    return jsonify({"message": "Contact deleted successfully!"}), 200


if __name__ == "__main__":
    app.run(debug=True)

