import re
from pymongo import MongoClient
client=MongoClient("mongodb://localhost:27017/")
db=client["phonebook"]
contacts_collection=db["Person"]

if "Person" not in db.list_collection_names():
    contacts_collection.insert_one({"first name":"Test User","last_name":"Test User","phone_number":"0000000000"})
    contacts_collection.delete_one({"first name":"Test User"})

phone_pattern = re.compile(r'^\d{10}$')
def validate_phone_number(phone_number):
    """اعتبارسنجی شماره تلفن با استفاده از regex"""
    if phone_pattern.match(phone_number):
        return True
    else:
        return False    
    

def add_contact(first_name, last_name, phone_number):
    if validate_phone_number(phone_number):
        contact = {
        "first name": first_name,
        "last name": last_name,
        "phone number": phone_number
                  }
        contacts_collection.insert_one(contact)
        print("Contact added successfully!")
    else:
        print("Invalid phone number. It should be 10 digits.")


def get_contacts():
    contacts = contacts_collection.find()
    for contact in contacts:
        print(contact)

def update_contact(contact_id, first_name=None, last_name=None, phone_number=None):
    if validate_phone_number(phone_number):
       update_fields = {}
       if first_name:
          update_fields["first_name"] = first_name
       if last_name:
          update_fields["last_name"] = last_name
       if phone_number:
          update_fields["phone_number"] = phone_number
       contacts_collection.update_one({"_id": contact_id}, {"$set": update_fields})
       print("Contact updated successfully!")
    else:
       print("Invalid phone number. It should be 10 digits.") 


def delete_contact(contact_id):
    contacts_collection.delete_one({"_id": contact_id})
    print("Contact deleted successfully!")

def main():
    while True:
        print("\nPhonebook Menu:")
        print("1. Add Contact")
        print("2. View Contacts")
        print("3. Update Contact")
        print("4. Delete Contact")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            first_name = input("Enter first name: ")
            last_name = input("Enter last name: ")
            phone_number = input("Enter phone number: ")
            add_contact(first_name, last_name, phone_number)
        elif choice == '2':
            get_contacts()
        elif choice == '3':
            contact_id = input("Enter contact ID to update: ")
            first_name = input("Enter new  first name (leave blank to keep current): ")
            last_name = input("Enter new last name (leave blank to keep current): ")
            phone_number = input("Enter new phone number (leave blank to keep current): ")
            update_contact(contact_id, first_name, last_name,phone_number )
        elif choice == '4':
            contact_id = input("Enter contact ID to delete: ")
            delete_contact(contact_id)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")
if __name__ == "__main__":
    main()