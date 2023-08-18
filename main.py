import pymysql
from app import app
from config import mysql
from flask import jsonify
from flask import flash, request, session, redirect, url_for, g
from functools import wraps
import jwt
import datetime
import bcrypt
# superadmin = User(username='superadmin', email='superadmin@example.com', password='hashed_password', role='superadmin')
# db.session.add(superadmin)
# db.session.commit()

#this is a function to check if the admin that is making a change is authorized to do so
# conn = mysql.connect()
# cursor = conn.cursor(pymysql.cursors.DictCursor)	
# _username='superadmin'
# role='superadmin'
# _password='iloverice'
# hashed = bcrypt.hashpw(_password.encode("utf-8"), bcrypt.gensalt())
# query = "INSERT INTO admin (username, PasswordHash, role) VALUES (%s, %s, %s)"
# parameters = (_username, hashed, role)
# Execute the query with parameters
# cursor.execute(query, parameters)
# conn.commit()
# conn.close()
def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        conn = None
        cursor = None
        try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            # Get the token from the Authorization header
            token = request.headers.get('Authorization')
            if token:
                # Remove the 'Bearer ' prefix from the token
                token = token.replace('Bearer ', '')
                payload = jwt.decode(token, 'mynameisslimshady', algorithms=['HS256'])
                user_id = payload['id']
                cursor.execute("SELECT role FROM admin WHERE id=%s", (user_id,))
                user = cursor.fetchone()
                if user['role'] == 'superadmin':
                    return f(*args, **kwargs)
                else:
                    return {'message': 'You are not authorized to perform this action'}, 401
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired'}, 401
        except jwt.DecodeError:
            return {'message': 'Token is invalid'}, 401
        except Exception as e:
            return {'message': 'Authentication failed'}, 401
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return decorated_function

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return {'message': 'Token is missing.'}, 401
        
        try:
            data = jwt.decode(token, 'mynameisslimshady', algorithms=['HS256'])
            # You can store user data from the token in g object for use in route handlers
            g.user_data = data
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired.'}, 401
        except jwt.DecodeError:
            return {'message': 'Token is invalid.'}, 401

        return f(*args, **kwargs)

    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    user_details = []
    try:
        _json = request.json
        _username = _json['username']
        _password = _json['password'].encode('utf-8')	

        # Change the condition to check for request method
        if request.method == 'POST':
            session.pop('admin', None)
            cursor.execute("SELECT * FROM admin WHERE username=%s", (_username,))
            for row in cursor.fetchall():
                user_details.append({"id": row['id'], "username": row['username'], "hashed_password": row['PasswordHash']})
            if len(user_details) > 0:
                user = user_details[0]
                if _username == user['username']:
                    if bcrypt.checkpw(_password, user['hashed_password'].encode('utf-8')):
                        # Generate JWT token
                        token_payload = {
                            'id': user['id'],
                            ''
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expiration time
                        }
                        token = jwt.encode(token_payload, 'mynameisslimshady', algorithm='HS256')

                        return {"token": token, "username": user['username']}, 200
                    else:
                        return {"message": "Invalid Password."}, 401
                else:
                    return {"message": "Invalid Username."}, 401
            else:
                return {"message": "User not found."}, 401
        else:
            return {"message": "Method not allowed."}, 405  # Return a 405 Method Not Allowed response
    except Exception as e:
        return {"message": "An error occurred."}, 500  # Return a 500 Internal Server Error response

    cursor.close()
    conn.close()

@app.route('/create-admin', methods=['POST'])
@superadmin_required
def create_admin():
    role = 'admin'
    try:
        _json = request.json
        _username = _json['username']
        _password = _json['password']
        _password_confirm = _json['password_confirm']  # Correct field name
        if request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM admin WHERE username=%s", (_username,))
            user = cursor.fetchone()
            if user:
                return {"message": "Username already exists"}, 401
            if _password == _password_confirm:
                hashed = bcrypt.hashpw(_password.encode("utf-8"), bcrypt.gensalt())
                cursor.execute(
                    "INSERT INTO admin (username, PasswordHash, role ) VALUES (%s, %s, %s)",
                    (_username, hashed, role)
                )
                conn.commit()
                return {"message": "Admin created successfully"}, 200
            else:
                return {"message": "Passwords do not match"}, 401
        else:
            return {"message": "There is an error"}, 401
    except Exception as e:
        return {"message": "An error occurred"}, 500
    finally:
        cursor.close()
        conn.close()


@app.route('/change-password', methods=['PUT'])
def change_password():
    if g.admin:
        current_admin = session['admin']
        password_details = []
        try:
            _json = request.json
            _password = _json['password']
            _password_confirm = _json['password']
            if _username and _password and _password_confirm == 'PUT':
                if _password == _password_confirm:
                    conn = mysql.connect()
                    cursor = conn.cursor(pymysql.cursors.DictCursor)	
                    cursor.execute("UPDATE admin SET password = ? WHERE username=?", _password, current_admin)
                else:
                    return {"message": "The passwords dont match"}
                user = user_details[0]
                    
        except Exception as e:
            print(e)
        finally:
            cursor.close() 
            conn.close()


# @app.route('/create', methods=['GET', 'POST'])
# def create_emp():
#     try:        
#         _json = request.json
#         _name = _json['name']
#         _email = _json['email']
#         _phone = _json['phone']
#         _address = _json['address']	
#         if _name and _email and _phone and _address and request.method == 'POST':
#             conn = mysql.connect()
#             cursor = conn.cursor(pymysql.cursors.DictCursor)		
#             sqlQuery = "INSERT INTO emp(name, email, phone, address) VALUES(%s, %s, %s, %s)"
#             bindData = (_name, _email, _phone, _address)            
#             cursor.execute(sqlQuery, bindData)
#             conn.commit()
#             respone = jsonify('Employee added successfully!')
#             respone.status_code = 200
#             return respone
#         else:
#             return showMessage()
#     except Exception as e:
#         print(e)
#     finally:
#         cursor.close() 
#         conn.close()          
     
# @app.route('/emp')
# def emp():
#     try:
#         conn = mysql.connect()
#         cursor = conn.cursor(pymysql.cursors.DictCursor)
#         cursor.execute("SELECT id, name, email, phone, address FROM emp")
#         empRows = cursor.fetchall()
#         respone = jsonify(empRows)
#         respone.status_code = 200
#         return respone
#     except Exception as e:
#         print(e)
#     finally:
#         cursor.close() 
#         conn.close()  

# @app.route('/emp/')
# def emp_details(emp_id):
#     try:
#         conn = mysql.connect()
#         cursor = conn.cursor(pymysql.cursors.DictCursor)
#         cursor.execute("SELECT id, name, email, phone, address FROM emp WHERE id =%s", emp_id)
#         empRow = cursor.fetchone()
#         respone = jsonify(empRow)
#         respone.status_code = 200
#         return respone
#     except Exception as e:
#         print(e)
#     finally:
#         cursor.close() 
#         conn.close() 

# @app.route('/update', methods=['PUT'])
# def update_emp():
#     try:
#         _json = request.json
#         _id = _json['id']
#         _name = _json['name']
#         _email = _json['email']
#         _phone = _json['phone']
#         _address = _json['address']
#         if _name and _email and _phone and _address and _id and request.method == 'PUT':			
#             sqlQuery = "UPDATE emp SET name=%s, email=%s, phone=%s, address=%s WHERE id=%s"
#             bindData = (_name, _email, _phone, _address, _id,)
#             conn = mysql.connect()
#             cursor = conn.cursor()
#             cursor.execute(sqlQuery, bindData)
#             conn.commit()
#             respone = jsonify('Employee updated successfully!')
#             respone.status_code = 200
#             return respone
#         else:
#             return showMessage()
#     except Exception as e:
#         print(e)
#     finally:
#         cursor.close() 
#         conn.close() 

# @app.route('/delete/', methods=['DELETE'])
# def delete_emp(id):
# 	try:
# 		conn = mysql.connect()
# 		cursor = conn.cursor()
# 		cursor.execute("DELETE FROM emp WHERE id =%s", (id,))
# 		conn.commit()
# 		respone = jsonify('Employee deleted successfully!')
# 		respone.status_code = 200
# 		return respone
# 	except Exception as e:
# 		print(e)
# 	finally:
# 		cursor.close() 
# 		conn.close()
        
       
@app.errorhandler(404)
def showMessage(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    respone = jsonify(message)
    respone.status_code = 404
    return respone

@app.before_request
def before_request():
    g.user = None
    if 'admin' in session:
        g.user = session['admin']

@app.route('/logout')
def dropsession():
    session.pop('admin', None)
    return redirect('/')
        
if __name__ == "__main__":
    app.run(debug=True)