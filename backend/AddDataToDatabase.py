import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Load the service account credentials from a JSON file
cred = credentials.Certificate("basicaiortc__serviceAccountKey.json")
# Initialize the Firebase app with the credentials and the database URL
firebase_admin.initialize_app(cred,{
    "databaseURL":"https://basicaiortc-default-rtdb.firebaseio.com/"
})

# Create a reference to the "Client" node in the Firebase Realtime Databa2se
ref = db.reference("Client_Info")

# Define the data to be stored in the database
data = {

    "0900891213":
    {
        "customer_name":"Taylor Swift",
        "customer_phone":"0900891213"
    },

    "0900920722":
    {
        "customer_name":"Selena Gomez",
        "customer_phone":"0900920722"
    },

    "0900921123":
    {
        "customer_name":"Miley Cyrus",
        "customer_phone":"0900921123"
    },

    "0900980103":
    {
        "customer_name":"Elaine",
        "customer_phone":"0900980103"
    }

}

# Store the data in the Firebase Realtime Database
for key,value in data.items():
    ref.child(key).set(value)