import os
import base64
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppresses unneeded compiled optimization warnings
from flask import send_file
from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from src.utils import Text_clf
import config
import pymongo
import datetime

client = pymongo.MongoClient(config.MONGO_URL)
db = client[config.db_name]
data_collection = db[config.collection_data]
user_collection = db[config.collection_user]

obj_text_clf = Text_clf()

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = 'secret'
app.config["SECRET_KEY"] = "flask-session-secret"
jwt = JWTManager(app)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/register_page')
def register_page():
    return render_template('register.html')

@app.route('/forgot_password_page')
def forgot_password_page():
    return render_template('forget_password.html')

@app.route('/dashboard_page')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.form
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    response = user_collection.find_one({"username": username},{"email": email})
    if not response:
        user_collection.insert_one({"username": username, "password": password, "email": email})
        return jsonify({"message": "Operator registered successfully!"})
    else:
        return jsonify({"message": "Operator already exists!"})

@jwt_required
@app.route('/login', methods=['POST'])
def login():
    data = request.form
    username = data.get('username') 
    password = data.get('password')
    response = user_collection.find_one({"username": username, "password": password})

    if response:
        access_token = create_access_token(identity=username,
                                           expires_delta= datetime.timedelta(minutes=60))
        return jsonify({"status": "success","message": "Login Successful", 
                        "access_token":access_token})
    else:
        return jsonify({"status": "failure", "message": "Invalid Credentials"})

@app.route("/forget_password", methods=["POST"])
def forget_password():
    data = request.form
    username = data.get('username')
    email = data.get('email')
    new_password = data.get('new_password')

    response = user_collection.find_one({"username": username, "email": email})
    if response:
        user_collection.update_one({"username": username, "email": email}, {"$set": {"password": new_password}})
        return jsonify({"status": "success", "message": "Password updated successfully"})
    else:
        return jsonify({"status": "failure", "message": "Invalid username or email"})

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    if request.method == 'POST':
        return jsonify({"status": "success", "message": "Logged out successfully"})
    return redirect(url_for('login_page'))

"""Make Prediction On User Input"""
@app.route("/predict_ticket", methods=["POST"])
def predict_ticket():
    username = request.form.get('username', 'anonymous')
    text = request.form.get('text')
    
    # Priority mapping for your specific classes
    PRIORITY_MAP = {
        "Access": "Critical",
        "Administrative rights": "Critical",
        "Hardware": "High",
        "Storage": "High",
        "HR Support": "Medium",
        "Purchase": "Medium",
        "Internal Project": "Medium",
        "Miscellaneous": "Low"
    }
    
    if text:
        input_text = text.strip()
        try:
            # Get prediction from your utils.py CNN/RNN model
            predicted_topic, raw_prediction_array = obj_text_clf.make_prediction(input_text)
            
            # Optional: Calculate confidence percentage from the raw prediction array
            import numpy as np
            confidence = round(float(np.max(raw_prediction_array)) * 100, 2)

            # Assign priority, defaulting to 'Medium' if not found
            ticket_priority = PRIORITY_MAP.get(predicted_topic, "Medium")

            # Save the Ticket Record
            ticket_record = {
                "username": username,
                "ticket_text": input_text,
                "predicted_category": predicted_topic,
                "confidence": confidence,
                "priority": ticket_priority,  # Priority added here
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            data_collection.insert_one(ticket_record)

            return jsonify({
                "status": "success", 
                "predicted_category": predicted_topic, 
                "confidence": confidence,
                "priority": ticket_priority   # Sent to frontend
            })

        except Exception as e:
            return jsonify({"status": "failure", "message": str(e)}), 500
    else:
        return jsonify({"status": "failure", "message": "No text provided"}), 400 


@app.route("/saved_data", methods=["GET"])
def saved_data():
    username = request.args.get('username')
    response = user_collection.find_one({"username": username})
    
    if response:
        # Retrieve all tickets submitted by this user
        user_history = list(data_collection.find({"username": username}, {"_id": 0}))
        return jsonify({"status": "success", "history": user_history})
    
    return jsonify({"status": "success", "message": "No previous tickets found", "history": []})


@app.route("/analytics", methods=["GET"])
def analytics():
    username = request.args.get('username')
    
    # 1. Fetch all ticket records for this user from MongoDB
    user_tickets = list(data_collection.find({"username": username}))
    
    # 2. Total count is just the length of the list
    total_tickets = len(user_tickets)
    
    # 3. Count categories using a simple Python loop
    category_counts = {}
    for ticket in user_tickets:
        category = ticket.get("predicted_category", "Unknown")
        category_counts[category] = category_counts.get(category, 0) + 1
        
    return jsonify({
        "status": "success",
        "total_tickets": total_tickets,
        "category_breakdown": category_counts
    })


if __name__ == "__main__":
    app.run(host= config.FLASK_HOST, port= config.FLASK_PORT, debug= True)