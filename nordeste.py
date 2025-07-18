from pymongo import MongoClient
import bcrypt
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['dashboard_pedidos']
senha = bcrypt.hashpw('@nordeste25'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
db['usuarios'].insert_one({
    'username': 'nordeste',
    'password': senha,
    'role': 'nordeste'
})
print("Usuário nordeste criado!")
