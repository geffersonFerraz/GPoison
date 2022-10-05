from flask import Flask, request
from crudDb import select
import sqlite3
import datetime


con = sqlite3.connect("gpoison.db", check_same_thread=False)
cur = con.cursor()


app = Flask(__name__)


@app.route("/get")
def hello_world():
    uuid = request.args.get('uuid')
    numis = request.args.get('numis')
    print("{} - {}".format(uuid, numis))
    result = select(cur, uuid)
    if result == None:
        # CHANGE THIS WHEN CREATE A VALIDATION
        return {'active': True, 'uuid': uuid}
    else:
        return {'active': True, 'uuid': uuid}


@ app.route("/")
def handshake():
    now = datetime.datetime.now()
    return {'numis': "{year}-{month}-{day}".format(year=now.year, month=now.month, day=now.day)}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)
