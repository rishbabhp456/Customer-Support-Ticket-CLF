💬 Smart Customer Support Ticket Classification System

This project implements a custom Recurrent Neural Network (LSTM/GRU) for automatically classifying customer support tickets into categories (Access, HR Support, Hardware, etc.) and assigning priority levels. The model is deployed as a full-stack web application using Flask, featuring JWT authentication, a modern glassmorphism Agent dashboard, live category analytics, and automated priority routing. It leverages PyMongo for ticket history management and is structured for production deployment on cloud platforms like Azure.

Table of Contents

Features

Project Flow

Local Setup

Project Structure

Azure Deployment Guide

Features

Ticket Classification AI: Utilizes a custom LSTM/GRU model to process natural language text and classify support tickets into multiple distinct categories.

Automated Priority Assignment: Automatically evaluates the AI-predicted category and routes tickets by assigning a priority level (Critical, High, Medium, Low).

Agent Dashboard & Analytics: A Flask backend serves RESTful APIs connected to a dynamic, modern frontend featuring chronological ticket history and live category breakdown analytics.

Secure Authentication: Provides support agent registration and login endpoints secured via JSON Web Tokens (JWT).

Database Integration: Interacts with MongoDB to persistently store agent credentials and ticket records (Agent Name, Ticket Text, Category, Confidence, Priority, Date).

Project Flow

Model Training: An LSTM/GRU architecture is trained on historical customer support texts using text tokenization and sequence padding. The trained model (.keras), tokenizer configuration, and class index mapping (.json) are saved as artifacts.

Authentication: Agents log in, receiving a JWT access token stored in localStorage.

Inference & Routing: The /predict_ticket endpoint accepts customer message text, verifies the JWT, tokenizes/pads the text, classifies the category, and maps it to an operational priority level.

Analytics & Logging: Results are permanently logged in MongoDB. The /analytics endpoint provides real-time metrics for total tickets processed and a dynamic breakdown of tickets by category.

History Retrieval: The dashboard fetches past tickets, displaying the raw customer text alongside the AI-assigned category, confidence score, and priority badge.

Local Setup

Clone and enter repository:

git clone https://github.com/your-username/Cust_Support_Ticket_CLF.git
cd Cust_Support_Ticket_CLF


Create and activate virtual environment:

python -m venv .venv
# Windows: .venv\Scripts\activate | macOS/Linux: source .venv/bin/activate


Install dependencies:

pip install -r requirements.txt


Prepare artifacts: Place your trained model (ticket_classifier.keras), tokenizer config (tokenizer.json), and mapping file (classes.json) in the artifacts/ directory.

Environment Variables: Configure your .env or config.py directly:

export FLASK_APP=main.py
export MONGODB_URI="mongodb://localhost:27017/ticket_db"
export JWT_SECRET_KEY="your_super_secret_key"


Run Application:

flask run
# OR for production-like local run: gunicorn -w 4 -b 0.0.0.0:8000 main:app


Project Structure

Cust_Support_Ticket_CLF/
├── .venv/                            
├── artifacts/                        
│   ├── classes.json                  # JSON mapping of class indices to topics
│   ├── tokenizer.json                # Saved Keras text tokenizer vocabulary
│   └── ticket_classifier.keras       # Trained custom LSTM/GRU model
├── src/
│   └── utils.py                      # Text preprocessing (tokenization/padding) and inference logic
├── static/
│   └── style.css                     # Modern glassmorphism UI styling
├── templates/
│   ├── login.html                    
│   ├── register.html                 
│   ├── forget_password.html          
│   └── dashboard.html                # Agent interface with text input, analytics, and history
├── config.py                         
├── main.py                           # Flask app, APIs, Analytics, and Priority mapping logic
└── requirements.txt                  # Python dependencies


Azure Deployment Guide

1. Set up Azure Cosmos DB (MongoDB API)

Create Cosmos DB:

az cosmosdb create --name <your-cosmosdb-name> --resource-group <your-rg> --kind MongoDB


Retrieve connection string (Save this for MONGODB_URI):

az cosmosdb keys list --name <your-cosmosdb-name> --resource-group <your-rg> --type connection-strings


2. Set up Azure Blob Storage (For Model Artifacts)

Create Storage & Container:

az storage account create --name <your-storage-name> --resource-group <your-rg> --location "East US" --sku Standard_LRS
az storage container create --name models --account-name <your-storage-name> --public-access off


Upload model and JSON files:

az storage blob upload --container-name models --file artifacts/ticket_classifier.keras --name ticket_classifier.keras --account-name <your-storage-name>


3. Deploy to Azure App Service

Create Web App:

az webapp create --resource-group <your-rg> --plan <your-plan> --name <your-webapp-name> --runtime "PYTHON|3.11"


Configure Settings & Startup:

az webapp config appsettings set --resource-group <your-rg> --name <your-webapp-name> --settings MONGODB_URI="<your-mongodb-uri>" JWT_SECRET_KEY="<secret>"
az webapp config set --resource-group <your-rg> --name <your-webapp-name> --startup-file "gunicorn --bind 0.0.0.0 --timeout 600 main:app"


Deploy Code:

az webapp deployment user set --username <git-user> --password <git-pass>
az webapp deployment source config-local-git --name <your-webapp-name> --resource-group <your-rg> --query scmUri --output tsv
# Add remote and git push azure master
