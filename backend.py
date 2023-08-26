from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import psycopg2
import base64
from flask_cors import CORS
# import elasticapm
# from elasticapm.contrib.flask import ElasticAPM

conn = psycopg2.connect(database="twm", 
                        user="elaine", 
                        password="1234", 
                        host="127.0.0.1", 
                        port="5432")

# conn = psycopg2.connect(
#     host="34.125.111.91",
#     database="twm",
#     user="postgres",
#     password="1234"
# )

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# app.config["ELASTIC_APM"] = {
#     # allowed app_name chars: a-z, A-Z, 0-9, -, _, and space from elasticapm.contrib.flask
#     "APP_NAME": "flask-apm-client",
#     "DEBUG": True,
#     "SERVER_URL": "http://35.229.136.89:8200",
#     "TRACES_SEND_FREQ": 5,
#     "SERVICE_NAME": "backend",
#     "FLUSH_INTERVAL": 1,  # 2.x
#     "MAX_QUEUE_SIZE": 1,  # 2.x
#     "TRANSACTIONS_IGNORE_PATTERNS": [".*healthcheck"],
# }
# apm = ElasticAPM(app, logging=True)

# Define a route for assigning a number
# @elasticapm.capture_span()
@app.route('/api/assign_number', methods=['POST'])
def assign_number():
    try:
        # Get JSON data from the request
        data = request.get_json()
        client_phone = data['client_phone']
        client_name = data['client_name']
        base64_data = data['base64']
        #print (client_name)
        #print("Received JSON data:")

        cur = conn.cursor() # Create a cursor to interact with the database

        # Check if the client's phone number exists in the Client_info table
        check_client_query = "SELECT client_phone FROM Client_info WHERE client_phone = %s"
        cur.execute(check_client_query, (client_phone,))
        existing_client = cur.fetchone() # Fetch the result of the query
        #print(existing_client)

        if existing_client:
            # Check if the client is already in the waiting list
            #check_waiting_query = "SELECT client_phone FROM waiting_list WHERE client_phone = %s"
            check_waiting_query = "SELECT id, client_phone, client_name, base64_data FROM waiting_list WHERE client_phone = %s"
            cur.execute(check_waiting_query, (client_phone,))
            existing_waiting_client = cur.fetchone()

            if existing_waiting_client:
                # If client is already in waiting list, return the waiting list details
                response_data = {
                    'number_plate_id': existing_waiting_client[0],
                    'client_phone': existing_waiting_client[1],
                    'client_name': existing_waiting_client[2],
                    'base64_data': existing_waiting_client[3].tobytes().decode('utf-8') 
                }
                socketio.emit('number_assigned', response_data)
                return jsonify(response_data)
            
            # Get the maximum ID from the waiting_list table
            get_max_id_query = "SELECT MAX(id) FROM waiting_list"
            cur.execute(get_max_id_query)
            max_id = cur.fetchone()[0] # Extract the value from the result (since the query returns a single value)

            if max_id is None:
                max_id = 0

            # Calculate a new number plate ID
            new_number_plate_id = max_id + 1
            # Insert the client into the waiting_list table
            insert_waiting_query = "INSERT INTO waiting_list (id, client_phone, client_name, base64_data) VALUES (%s, %s, %s, %s)"
            cur.execute(insert_waiting_query, (new_number_plate_id, client_phone, client_name, base64_data))
            conn.commit() # Save the changes to the database

            # Return a JSON response with the assigned number plate details
            response_data={
                'number_plate_id': new_number_plate_id,
                'client_phone': client_phone,
                'client_name': client_name,
                'base64_data': base64_data
            }
            
            socketio.emit('number_assigned', response_data)
            return jsonify(response_data)

        else:
            return jsonify({'message': 'Phone number not found'})

    # Handle errors using Exception
    except Exception as e:
        print("An error occurred:", str(e))
        conn.rollback() # Rollback changes in case of an error
        # Handle errors and emit a socket event
        socketio.emit('number_assignment_failed', {'message': 'An error occurred'}) # Emit a socket event to notify about the error
        return jsonify({'message': 'An error occurred'})  # Make sure to return an error response 
    
    finally:
        # Close the cursor and the database connection
        cur.close()

# @elasticapm.capture_span()
@app.route('/api/waiting_list', methods=['GET'])
def get_waiting_list():
    try:
        cur = conn.cursor() # Create a cursor to interact with the database
        get_waiting_list_query = "SELECT id, client_name, client_phone FROM waiting_list"
        print(get_waiting_list_query )
        cur.execute(get_waiting_list_query)
        waiting_list_data = cur.fetchall()

        waiting_list = [
            {
                'id': row[0],
                'client_name': row[1],
                'client_phone': row[2]
            }
            for row in waiting_list_data
        ]

        return jsonify(waiting_list)

    except Exception as e:
        print("An error occurred:", str(e))
        conn.rollback()
        return jsonify({'message': 'An error occurred'})

    finally:
        cur.close()

# @elasticapm.capture_span()
@app.route('/api/next_number', methods=['POST'])
def next_number():
    try:
        cursor = conn.cursor()
        query = "DELETE FROM waiting_list WHERE id = (SELECT id FROM waiting_list ORDER BY id LIMIT 1);"
        cursor.execute(query)
        conn.commit()
        return jsonify({'message': 'Next number removed from waiting list.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Run the Flask app with Socket.IO
if __name__ == '__main__':
    socketio.init_app(app)
    socketio.run(app, host='0.0.0.0', debug=True, port=443)

