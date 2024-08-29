from flask import Blueprint, render_template, request, redirect, url_for, session, g
import hashlib
import re
from datetime import datetime
from functools import wraps
import logging

auth = Blueprint('auth', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Helper function to get the database cursor
def get_db_cursor():
    mydb = getattr(g, 'mydb', None)
    if mydb is None:
        raise Exception("Database connection is not available")
    return mydb.cursor()

# Define login_required decorator
def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if 'loggedin' in session:
            return route_function(*args, **kwargs)
        else:
            return redirect(url_for('auth.login'))
    return wrapper

def get_user_role():
    role_id = session.get('rolesID')
    if role_id:
        mydb = getattr(g, 'mydb', None)
        cursor = mydb.cursor()
        cursor.execute('SELECT rolesName FROM user_roles WHERE rolesID = %s', (role_id,))
        role = cursor.fetchone()
        return role[0] if role else None
    return None

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        return redirect(url_for('views.homeUser'))

    mesage = ''

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('userpassword')
        
        if not username or not password:
            mesage = 'Please fill out the form!'
        else:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            try:
                cursor = get_db_cursor()
                
                # Check user login
                cursor.execute('SELECT * FROM users WHERE userName = %s', (username,))
                user = cursor.fetchone()
                
                if user:
                    if user[3] == hashed_password:
                        session['loggedin'] = True
                        session['userID'] = user[0]
                        session['userName'] = user[1]
                        session['userEmail'] = user[2]
                        session['userStatus'] = user[5]
                        session['rolesID'] = user[6]
                        
                        return redirect(url_for('views.homeUser'))
                    else:
                        mesage = 'Incorrect username or password!'
                else:
                    # Check admin login
                    cursor.execute('SELECT * FROM admin WHERE adminName = %s', (username,))
                    admin = cursor.fetchone()
                    
                    if admin:
                        if admin[3] == hashed_password:
                            session['loggedin'] = True
                            session['adminID'] = admin[0]
                            session['adminName'] = admin[1]
                            session['adminEmail'] = admin[2]
                            session['rolesID'] = admin[4]
                            
                            return redirect(url_for('views.homeAdmin'))
                        else:
                            mesage = 'Incorrect username or password!'
                    else:
                        mesage = 'Account not registered yet!'
            except Exception as e:
                logging.error(f"Login error: {e}")
                mesage = "An error occurred during login."

    return render_template('login.html', mesage=mesage)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if 'loggedin' in session:
        return redirect(url_for('views.homeUser'))

    mesage = ''
    if request.method == 'POST':
        username = request.form.get('userName')
        password = request.form.get('userPassword')
        email = request.form.get('userEmail')
        
        if not username or not password or not email:
            mesage = 'Please fill out the form!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address!'
        else:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            try:
                cursor = get_db_cursor()
                cursor.execute('SELECT * FROM users WHERE userName = %s OR userEmail = %s', (username, email))
                account = cursor.fetchone()
                
                if account:
                    mesage = 'Username or email already exists!'
                else:
                    user_date = datetime.now()
                    user_status = 'Not Verified'
                    rolesID = 2  # Default to 'user' role
                    
                    cursor.execute(
                        'INSERT INTO users (userName, userEmail, userPassword, userDateRegister, userStatus, rolesID) '
                        'VALUES (%s, %s, %s, %s, %s, %s)', 
                        (username, email, hashed_password, user_date, user_status, rolesID)
                    )
                    g.mydb.commit()
                    
                    cursor.execute('SELECT * FROM users WHERE userName = %s', (username,))
                    new_account = cursor.fetchone()
                    
                    session['loggedin'] = True
                    session['userID'] = new_account[0]
                    session['userName'] = new_account[1]
                    session['userEmail'] = new_account[2]
                    session['userStatus'] = new_account[5]
                    session['rolesID'] = new_account[6]

                    mesage = "Registration Account Successfull"

                    session['message'] = mesage

                    return redirect(url_for('views.homeUser'))
            except Exception as e:
                logging.error(f"Registration error: {e}")
                mesage = "An error occurred during registration."

    return render_template('login.html', mesage=mesage)

@auth.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('views.homeUser'))

@auth.route('/profileupdate', methods=['GET', 'POST'])
@login_required
def profileupdate():
    message = ''
    user_id = session['userID']
    try:
        cursor = get_db_cursor()
        cursor.execute('SELECT * FROM users WHERE userID = %s', (user_id,))
        user = cursor.fetchone()

        # Adjust the indices according to your database schema
        user_name_index = 1  # Assuming userName is the second field
        user_email_index = 2  # Assuming userEmail is the third field

        if request.method == 'POST':
            username = request.form.get('userName')
            email = request.form.get('userEmail')

            if not username and not email:
                message = 'Please fill out the form!'
            elif email and not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                message = 'Invalid email address!'
            elif username == session['userName'] and email == session['userEmail']:
                message = 'Cannot update to the same username and email as current session values.'
            elif username == session['userName']:
                message = 'Cannot update to the same username as current session value.'
            elif email == session['userEmail']:
                message = 'Cannot update to the same email as current session value.'
            else:
                # Check if the new username or email already exists
                username_exists = False
                email_exists = False

                if username and username != user[user_name_index]:
                    cursor.execute('SELECT * FROM users WHERE userName = %s AND userID != %s', (username, user_id))
                    if cursor.fetchone():
                        username_exists = True

                if email and email != user[user_email_index]:
                    cursor.execute('SELECT * FROM users WHERE userEmail = %s AND userID != %s', (email, user_id))
                    if cursor.fetchone():
                        email_exists = True

                if username_exists:
                    message = 'Username already exists!'
                elif email_exists:
                    message = 'Email already exists!'
                else:
                    # Update the fields
                    update_fields = []
                    update_values = []
                    if username and username != user[user_name_index]:
                        update_fields.append('userName = %s')
                        update_values.append(username)
                        session['userName'] = username
                        message = 'Username updated successfully!'
                    if email and email != user[user_email_index]:
                        update_fields.append('userEmail = %s')
                        update_values.append(email)
                        session['userEmail'] = email
                        if 'successfully!' in message:
                            message = 'Username and Email updated successfully!'
                        else:
                            message = 'Email updated successfully!'

                    if update_fields:
                        update_values.append(user_id)
                        update_query = 'UPDATE users SET ' + ', '.join(update_fields) + ' WHERE userID = %s'
                        cursor.execute(update_query, update_values)
                        g.mydb.commit()
    except Exception as e:
        logging.error(f"Profile update error: {e}")
        message = "An error occurred during profile update."

    return render_template('profilePage.html', user=user, message=message)

@auth.route('/changepassword', methods=['GET', 'POST'])
@login_required
def changepassword():
    mesage = ''
    user_id = session['userID']
    
    if request.method == 'POST':
        old_password = request.form.get('oldpassword')
        new_password = request.form.get('newpassword')
        confirm_password = request.form.get('confirmpass')
        
        if not old_password or not new_password or not confirm_password:
            mesage = 'Please fill out the form!'
        elif new_password != confirm_password:
            mesage = 'New password and confirmation do not match!'
        else:
            try:
                cursor = get_db_cursor()
                cursor.execute('SELECT userPassword FROM users WHERE userID = %s', (user_id,))
                user = cursor.fetchone()
                
                if user and user[0] == hashlib.sha256(old_password.encode()).hexdigest():
                    new_hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
                    cursor.execute('UPDATE users SET userPassword = %s WHERE userID = %s', (new_hashed_password, user_id))
                    g.mydb.commit()
                    mesage = 'Password changed successfully!'
                else:
                    mesage = 'Old password is incorrect!'
            except Exception as e:
                logging.error(f"Password change error: {e}")
                mesage = "An error occurred during password change."
    return render_template('changePass.html', mesage=mesage)

@auth.route('/preresult', methods=['GET', 'POST'])
@login_required
def preresult():
    user_role = get_user_role()
    user_id = session.get('userID')

    if user_role != 'user':
        return redirect(url_for('views.homeAdmin'))
    else:
        mesage=''
        mydb = getattr(g, 'mydb', None)
        cursor = mydb.cursor()

        cursor.execute('SELECT * FROM character_result WHERE userID = %s ', (user_id,))
        listdata = cursor.fetchall()

        img_history = []
        for row in listdata:
            img_history.append({
                "resultID": row[0], 
                "resultName": row[1],  
                "resultDate": row[2],
                "resultImage": row[3]
            })
    
    section = request.args.get('section', 'profile-update')
    
    return render_template('History.html', section=section, img_history=img_history,mesage=mesage)
