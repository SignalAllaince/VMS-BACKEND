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
        try:
            if not token:
                return {'message': 'Token is missing.'}, 401
            else:
                return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired.'}, 401
        except jwt.DecodeError:
            return {'message': 'Token is invalid.'}, 401

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
            cursor.execute("SELECT * FROM admin WHERE username=%s", (_username,))
            for row in cursor.fetchall():
                user_details.append({"id": row['id'], "username": row['username'], "hashed_password": row['PasswordHash'], "role": row['role'], "status": row['status']})
            if len(user_details) > 0:
                user = user_details[0]
                if _username == user['username']:
                    if user['status'] == 'Active':
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
                       return {"message": "User is currently inactive"}, 401 
                else:
                    return {"message": "Invalid Username."}, 401
            else:
                return {"message": "User not found."}, 401
        else:
            return {"message": "Method not allowed."}, 405  # Return a 405 Method Not Allowed response
    except Exception as e:
        print(e)
        return {"message": "An error occurred."}, 500  # Return a 500 Internal Server Error response

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/create-admin', methods=['POST'])
@superadmin_required
def create_admin():
    try:
        _json = request.json
        _username = _json['username']
        _password = _json['password']
        _password_confirm = _json['password_confirm']  # Correct field name
        _role = _json['role']
        _status = _json['status']
        _email = _json['email']
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
                    "INSERT INTO admin (username, PasswordHash, role, status, email ) VALUES (%s, %s, %s, %s, %s)",
                    (_username, hashed, _role, _status, _email)
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
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/change-password', methods=['PUT'])
@token_required
def change_password():
    try:
        _json = request.json
        _password = _json['password']
        _password_confirm = _json['password confirm']
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)	
        if request.method == 'PUT':
            token = request.headers.get('Authorization')
            if token:
                token = token.replace('Bearer ', '')
                payload = jwt.decode(token, 'mynameisslimshady', algorithms=['HS256'])
                user_id = payload['id']
                cursor.execute("SELECT username FROM admin WHERE id=%s", (user_id,))
                user = cursor.fetchone()
                if _password == _password_confirm:
                    hashed = bcrypt.hashpw(_password.encode("utf-8"), bcrypt.gensalt())
                    cursor.execute("UPDATE admin SET PasswordHash = %s WHERE username=%s", (hashed, user['username']))
                    conn.commit()
                    return {"message": "Password changed successfully"}, 200
                else:
                    return {"message": "The passwords dont match"}, 401
                
    except Exception as e:
        print(e)
        return {"message": "An error occurred"}, 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/change-details', methods=['PUT'])
@superadmin_required
def change_details():
    try:
        _json = request.json
        _id = _json['id']
        _username = _json['username']
        _email = _json['email']
        _status = _json['status']
        _role = _json['role']
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)	
        if request.method == 'PUT':
            cursor.execute("UPDATE admin SET username = %s, role= %s, status= %s, email= %s WHERE id=%s", (_username, _role, _status, _email, _id))
            conn.commit()
            return {"message": "Details changed successfully"}, 200
        else:
            return {"message": "There is an error"}, 401
                
    except Exception as e:
        print(e)
        return {"message": "An error occurred"}, 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/admin-detail/<int:admin_id>', methods=['GET'])
@token_required
def admin_detail(admin_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id, username, email, role, status FROM admin WHERE id=%s", (admin_id))
        admin = cursor.fetchone()
        response = jsonify(admin)
        response.status_code = 200
        return response
                
    except Exception as e:
        print(e)
        return {"message": "An error occurred"}, 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/admin-management', methods=['GET'])
@token_required
def admin_management():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT username, email, role, status FROM admin")
        admin = cursor.fetchall()
        response = jsonify(admin)
        response.status_code = 200
        return response
                
    except Exception as e:
        print(e)
        return {"message": "An error occurred"}, 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/visit-management/<int:visit_id>', methods=['GET'])
@token_required
def visit_management(visit_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM visitor WHERE id=%s", (visit_id))
        visit = cursor.fetchone()
        response = jsonify(visit)
        response.status_code = 200
        return response
                
    except Exception as e:
        print(e)
        return {"message": "An error occurred"}, 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/visitor-management', methods=['GET'])
@token_required
def visitor_management():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM visitor")
        visitors = cursor.fetchall()
        response = jsonify(visitors)
        response.status_code = 200
        return response
                
    except Exception as e:
        print(e)
        return {"message": "An error occurred"}, 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

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
    response = jsonify(message)
    response.status_code = 404
    return response

@app.route('/logout', methods=['POST'])
@token_required
def logout():
    try:
        return {"message": "Logout successful"}, 200
    
    except Exception as e:
        print(e)
        return {"message": "An error occurred"}, 500
        
if __name__ == "__main__":
    app.run(debug=True)