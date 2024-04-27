from flask import Flask, request, jsonify, session
from pymongo import MongoClient
from flask_cors import CORS

from qldtAPI import qldtAPI

app = Flask(__name__)
CORS(app)

# Set the secret key to enable session management
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Define database
client = MongoClient('mongodb://localhost:27017/')
db = client['data-user']
MarkTableCol = db['mark-table']
SumMarkCol = db['sum-mark']

markTableURL = "https://qldt.utt.edu.vn/CMCSoft.IU.Web.Info/StudentMark.aspx"

def tblStudentMark(username, password):


    print(f"tblStudentMark- username :{username}")
    print(f"tblStudentMark- password :{password}")

    mark_table = qldtAPI()
    mark_table.login(username, password, markTableURL)
    mark_table.htmlElement("table", "tblStudentMark")
    mark_table.jsonConvert()
    return mark_table.preprocessJson("Mã học phần", username)

@app.route('/api/database/req', methods=['POST'])
def push_to_mongodb():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    table = tblStudentMark(username, password)
    collection = MarkTableCol

    for doc in table:
        existing_doc = collection.find_one({'dbKey': doc['dbKey']})
        if existing_doc:
            collection.replace_one({'dbKey': doc['dbKey']}, doc, upsert=True)
        else:
            collection.insert_one(doc)

    return jsonify([{'success': True, 'message': 'Dữ liệu đã được nhận và lưu thành công'}]), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)