from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from bson.objectid import ObjectId
import re

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')
client = MongoClient("mongodb://localhost:27017/")
db = client["phonebook"]
contacts_collection = db["Person"]

phone_pattern = re.compile(r'^\d{11}$')

def validate_phone_number(phone_number):
    if phone_pattern.match(phone_number):
        return True
    else:
        return False

@app.route('/contacts', methods=['POST'])
def add_contact():
    data = request.json
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    phone_number = data.get("phone_number")
    
    if validate_phone_number(phone_number):
        contact = {
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number
        }
        contacts_collection.insert_one(contact)
        return jsonify({"message": "Contact added successfully!"}), 201
    else:
        return jsonify({"message": "Invalid phone number. It should be 11 digits."}), 400

@app.route('/contacts', methods=['GET'])
def get_contacts():
    contacts = list(contacts_collection.find())
    for contact in contacts:
        contact["_id"] = str(contact["_id"])
    return jsonify(contacts), 200

@app.route('/contacts/<contact_id>', methods=['PUT'])
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
def delete_contact(contact_id):
    contacts_collection.delete_one({"_id": ObjectId(contact_id)})
    return jsonify({"message": "Contact deleted successfully!"}), 200

if __name__ == "__main__":
    app.run(debug=True)
