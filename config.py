import os

FLASK_HOST = '0.0.0.0'
FLASK_PORT = 8000
MONGO_PASSWORD = 'test123$'
MONGO_URL = f'mongodb+srv://rishabhp:{MONGO_PASSWORD}@docdb-cluster-20260630-0923.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000'
# MONGO_URL = 'mongodb://localhost:27017'
db_name = 'text_clf_db'
collection_user = 'clf_users'
collection_data = 'Support_ticket_data'

MODEL_PATH = os.path.join(os.getcwd(),"artifacts","Ticket_clf_model.keras")
MODEL_CONFIG = os.path.join(os.getcwd(),"artifacts","topic_classes.json")
PREPROCESSOR = os.path.join(os.getcwd(),"artifacts","tokenizer.json")