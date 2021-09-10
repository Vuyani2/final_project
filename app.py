import hmac
import sqlite3
import datetime
from flask_cors import CORS
from flask_mail import Message, Mail


from flask import Flask, request, jsonify, redirect
from flask_jwt import JWT, jwt_required, current_identity


# This function create dictionaries out of SQL rows, so that the data follows JSON format
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def fetch_users():
    with sqlite3.connect('plane_tkt.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[3], data[4]))
    return new_data





# ---Creating User Table---
def init_user_table():
    conn = sqlite3.connect('plane_tkt.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL,"
                 "email TEXT NOT NULL,"
                 "mobile_number)")
    print("user table created successfully")
    conn.close()


# ---CREATING TICKETS TABLE---
def init_tickets_table():
    with sqlite3.connect('plane_tkt.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS tickets (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "from_ TEXT NOT NULL,"
                     "to_ TEXT NOT NULL,"
                     "airline TEXT NOT NULL,"
                     "departure TEXT NOT NULL,"
                     "arrival TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "type TEXT NOT NULL,"
                     "user_id INTEGER NOT NULL,"
                     "date_bought TEXT NOT NULL,"
                     "FOREIGN KEY (user_id) REFERENCES user(user_id))")
    print("tickets table created successfully.")


#---Creating Car Hire Table---
def init_car_hire_table():
    with sqlite3.connect('plane_tkt.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS car_hire (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "car_name TEXT NOT NULL,"
                     "pick_up TEXT NOT NULL,"
                     "supplier TEXT NOT NULL,"
                     "time TEXT NOT NULL,"
                     "fuel_policy TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "date_ordered TEXT NOT NULL)")
        print("car_hire table created successfully.")

init_user_table()
init_tickets_table()
init_car_hire_table()

users = fetch_users()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
CORS(app)

jwt = JWT(app, authenticate, identity)


@app.route('/protected')
def protected():
    return '%s' % current_identity


# ---User Registration---
@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":

        first_name = request.json['first_name']
        last_name = request.json['last_name']
        username = request.json['username']
        password = request.json['password']
        email = request.json['email']
        mobile_number = request.json['mobile_number']

        with sqlite3.connect("plane_tkt.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user("
                           "first_name,"
                           "last_name,"
                           "username,"
                           "password,"
                           "email,"
                           "mobile_number) VALUES(?, ?, ?, ?, ?, ?)", (first_name, last_name, username, password, email, mobile_number))

            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


# ---Image Hosting---
@app.route('/image-hosting/')
def image_hosting():
    with sqlite3.connect("plane_tkt.db.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT image FROM car_hire WHERE id='2'")
        image = cursor.fetchone()
        for i in image:
            image1 = i
    return redirect(image1)


@app.route('/get-user/', methods=["GET"])
def get_user():
    response = {}
    with sqlite3.connect("plane_tkt.db") as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")

        tickets = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = tickets
    return response


# ---Creating Products---
@app.route('/add-car/', methods=["POST"])
def add_car():
    response = {}

    if request.method == "POST":
        car_name = request.json['car_name']
        pick_up = request.json['pick_up']
        supplier = request.json['supplier']
        time = request.json['time']
        fuel_policy = request.json['fuel_policy']
        price = request.json['price']
        date_ordered = datetime.datetime.now()

        with sqlite3.connect('plane_tkt.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO car_hire ("
                           "car_name,"
                           "pick_up,"
                           "supplier,"
                           "time,"
                           "fuel_policy,"
                           "price,"
                           "date_ordered) VALUES(?, ?, ?, ?, ?, ?, ?)", (car_name, pick_up, supplier, time, fuel_policy, price, date_ordered))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "Car added successfully"
        return response


@app.route('/add-ticket/', methods=["POST"])
def add_ticket():
    response = {}

    if request.method == "POST":
        from_ = request.json['from_']
        to_ = request.json['to_']
        airline = request.json['airline']
        departure = request.json['departure']
        arrival = request.json['arrival']
        price = request.json['price']
        type_ = request.json['type_']
        user_id = request.json['user_id']

        date_bought = datetime.datetime.now()

        with sqlite3.connect('plane_tkt.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tickets ("
                           "from_,"
                           "to_,"
                           "airline,"
                           "departure,"
                           "arrival,"
                           "price,"
                           "type,"
                           "user_id,"
                           "date_bought) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (from_, to_, airline, departure, arrival, price, type_, user_id, date_bought))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "Ticket added successfully"
        return response

# ---Get Car---
@app.route('/get-car/', methods=["GET"])
def get_car():
    response = {}
    with sqlite3.connect("plane_tkt.db") as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM car_hire")

        cars = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = cars
    return response


# ---Get TICKETS---
@app.route('/get-tickets/', methods=["GET"])
def get_tickets():
    response = {}
    with sqlite3.connect("plane_tkt.db") as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets")

        tickets = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = tickets
    return response



# ---Sorting tickets by price---
@app.route('/sort-tickets/', methods=["GET"])
def sort_tickets():
    response = {}
    with sqlite3.connect("plane_tkt.db") as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets ORDER BY price")

        tickets = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = tickets
    return response

# ---Delete Car---
@app.route("/delete-car/<int:ticket_id>")
def delete_car(ticket_id):
    response = {}
    with sqlite3.connect("plane_tkt.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM car_hire WHERE id=" + str(ticket_id))
        conn.commit()

    response['status_code'] = 200
    response['message'] = "ticket deleted successfully."
    return response


# ---Delete Tickets---
@app.route("/delete-ticket/<int:ticket_id>")
def delete_ticket(ticket_id):
    response = {}
    with sqlite3.connect("plane_tkt.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tickets WHERE id=" + str(ticket_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "ticket deleted successfully."
    return response


# ---Edit Tickets---
@app.route('/edit-ticket/<int:ticket_id>/', methods=["PUT"])
def edit_ticket(ticket_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('plane_tkt.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("from") is not None:
                put_data["from"] = incoming_data.get("from")
                with sqlite3.connect('price_tkt.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tickets SET name =? WHERE id=?", (put_data["from"], ticket_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200

            if incoming_data.get("to") is not None:
                put_data['to'] = incoming_data.get('to')

                with sqlite3.connect('plane_txt.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tickets SET to =? WHERE id=?", (put_data["to"], ticket_id))
                    conn.commit()

                    response["to"] = "to updated successful"
                    response["status_code"] = 200

            if incoming_data.get("airline") is not None:
                put_data["airline"] = incoming_data.get("airline")
                with sqlite3.connect('plane_tkt.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tickets SET airline =? WHERE id=?", (put_data["airline"], ticket_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200

            if incoming_data.get("departure") is not None:
                put_data["departure"] = incoming_data.get("departure")
                with sqlite3.connect('plane_tkt.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tickets SET departure =? WHERE id=?",
                                   (put_data["departure"], ticket_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200

            if incoming_data.get("arrival") is not None:
                put_data["arrival"] = incoming_data.get("arrival")
                with sqlite3.connect('plane_tkt.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tickets SET arrival =? WHERE id=?",
                                   (put_data["arrival"], ticket_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200

            if incoming_data.get("price") is not None:
                put_data["price"] = incoming_data.get("price")
                with sqlite3.connect('plane_tkt.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tickets SET price =? WHERE id=?",
                                   (put_data["price"], ticket_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200

            if incoming_data.get("type") is not None:
                put_data["type"] = incoming_data.get("type")
                with sqlite3.connect('plane_tkt.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tickets SET type =? WHERE id=?",
                                   (put_data["type"], ticket_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200
    return response


# ---Get Product by ID---
@app.route('/get-ticket/<int:ticket_id>/', methods=["GET"])
def get_ticket(ticket_id):
    response = {}

    with sqlite3.connect("plane_tkt.db") as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets WHERE id=" + str(ticket_id))

        response["status_code"] = 200
        response["description"] = "ticket retrieved successfully"
        response["data"] = cursor.fetchone()

    return jsonify(response)


@app.route('/get-tkt/<from_>/<to_>', methods=["GET"])
def get_tkt(from_, to_):
    response = {}

    with sqlite3.connect("plane_tkt.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets WHERE to_ =? AND from_=?", (to_, from_))
        response["status_code"] = 200
        response["description"] = "ticket retrieved successfully"
        response["data"] = cursor.fetchall()
    return jsonify(response)


app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
# app.config['SECRET_KEY'] = "super-secret"
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PASSWORD'] = "Vuya@2019"
app.config['MAIL_USERNAME'] = "vuyanilottoapp@gmail.com"

mail = Mail(app)


def send_email(subject, message, email_address):
    email_to_send = Message(subject, sender='vuyanilottoapp@gmail.com',
                            recipients=[email_address])

    email_to_send.body = message
    mail.send(email_to_send)


@app.route('/send-email/<int:user_id>/', methods=["POST"])
def reminder_email(user_id):
    print(user_id)
    from_ = request.json['from_']
    to_ = request.json['to_']
    airline = request.json['airline']
    departure = request.json['departure']
    arrival = request.json['arrival']
    price = request.json['price']
    type_ = request.json['type']
    # user_id = request.json['user_id']

    response = {}
    with sqlite3.connect("plane_tkt.db") as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM user WHERE user_id='{user_id}'")
        user = cursor.fetchone()

        print(user)

        first_name = user[2] + user[3]
        email = user[5]
        print(email)
        with sqlite3.connect("plane_tkt.db") as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM tickets WHERE user_id='{user_id}'")
            tkts = cursor.fetchone()

        # print(tkts)
        # print(tkts[2])
        # print(tkts[3])
        # print(tkts[4])
        # print(tkts[5])
        # print(tkts[6])
        # print(tkts[7])
        # print(tkts[8])
        #
        #
        # from_ = tkts[1]
        # to_ = tkts[2]
        # plane = tkts[3]
        # departure = tkts[4]
        # arrival = tkts[5]
        # price = tkts[6]
        # type_ = tkts[7]
        date_bought = tkts[9]

        send_email("you successfully bought a ticket thank oy for using Cheap Tickets", "hey "
                   + first_name + " this is to confirm that you have succefully bought a plane ticket to travel from " +
                    from_ + " to " + to_ + " flying with " + airline + "the plane will be taking of at " + departure +
                   " the arrival time will be at " + arrival + " the ticket is a " + type_ + " at a price of " + price +
                   " on the " + date_bought, email)
        response["status_code"] = 200
        response["description"] = "Flight Details sent successfully"
    return jsonify(response)


if __name__ == "__main__":
    app.debug = True
    app.run()

# with sqlite3.connect("plane_tkt.db") as conn:
#     cursor = conn.cursor()
#     cursor.execute(f"ALTER TABLE car_hire ADD COLUMN Image TEXT")
#     conn.commit()
# with sqlite3.connect("plane_tkt.db") as conn:
#     cursor = conn.cursor()
#     cursor.execute(f"SELECT * FROM car_hire")
#     print(cursor.fetchall())