
from datetime import datetime
import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mykey'

# Connect to MySQL
app.config['MYSQL_HOST'] = 'localhost'  # MySQL server address
app.config['MYSQL_USER'] = 'root'  # MySQL username
app.config['MYSQL_PASSWORD'] = '1234'  # MySQL password
app.config['MYSQL_DB'] = 'loginflask'  # Name of the database to connect
mysql = MySQL(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # ตรวจสอบว่าข้อมูลล็อกอินตรงกับข้อมูลในฐานข้อมูลหรือไม่
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # เชื่อมต่อ ฐานข้อมูล
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,)) 
        user = cursor.fetchone()
        cursor.close()
        
        if username == 'admin' and password == '00000':  # ตรวจสอบรหัสผ่านของผู้ดูแลระบบ
            session['logged_in'] = True
            session['username'] = user['username']
            return redirect(url_for('admin_panel'))
        else:
            return render_template('login.html', error='ข้อมูลเข้าสู่ระบบไม่ถูกต้อง กรุณาลองอีกครั้ง')
    
    # เช็คสถานะการล็อกอิน
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('admin_panel'))
    
    return render_template('login.html')

# เส้นทางออกจากระบบ
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)  # ลบ session variable สำหรับชื่อผู้ใช้
    return redirect(url_for('login'))  # เปลี่ยนเส้นทางไปยังหน้า login หลังจากล็อกเอาท์


@app.route('/admin_panel')
def admin_panel():
    if 'logged_in' in session and session['logged_in']:
        if session['username'] == 'admin':  # ตรวจสอบว่าผู้ใช้เป็นผู้ดูแลระบบหรือไม่
            return render_template('admin_panel.html')
        else:
            return redirect(url_for('login'))  # Redirect ไปยังหน้า login หากผู้ใช้ไม่ใช่ admin
    else:
        return redirect(url_for('login'))  # Redirect ไปยังหน้า login หากไม่มี session ของผู้ใช้


cats = []  # สร้างรายการแมวใหม่ทุกครั้งที่มีการเรียกใช้งานฟังก์ชันนี้

# Define the UPLOAD_FOLDER constant
UPLOAD_FOLDER = 'static/images'

# หน้าแสดงหน้า Datacat
@app.route('/Datacat', methods=['GET', 'POST'])
def data_cat():
    if 'logged_in' in session and session['logged_in']:
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM cats')
            cats = cursor.fetchall()
            cursor.close()
        except Exception as e:
            return str(e)
        return render_template('Datacat.html', cats=cats)
    else:
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM cats')
            cats = cursor.fetchall()
            cursor.close()
        except Exception as e:
            return str(e)
        return render_template('Datacat_guest.html', cats=cats)


@app.route('/add_new_cat', methods=['GET', 'POST'])
def add_new_cat():
    if 'logged_in' in session and session['logged_in']:
        if request.method == 'POST':
            # รับข้อมูลจากแบบฟอร์ม
            name = request.form['name']
            breed = request.form['breed']
            age = request.form['age']
            color = request.form['color']
            status = request.form.get('status', '')  # เปลี่ยนจาก request.form('status', '') เป็น request.form.get('status', '')
            date = request.form['date']
            detail = request.form['detail']

            # ตรวจสอบว่ามีการอัปโหลดไฟล์รูปภาพแมวและภาพหนังสือรับรองการฉีดวัคซีนหรือไม่
            if 'image' in request.files:
                image = request.files['image']
                if image.filename != '':
                    image_path = os.path.join(UPLOAD_FOLDER, image.filename)
                    print(str(request.files['image']))  
                    image.save(image_path)
            else:
                image_path = None

            # สร้าง dictionary เก็บข้อมูลแมว
            new_cat = {
                'name': name,
                'breed': breed,
                'age': age,
                'color': color,
                'status': status,
                'date': date,
                'image': image_path,
                'detail': detail
            }

            # Append the new cat to the 'cats' list
            cats.append(new_cat)
            
            # เพิ่มข้อมูลแมวใหม่ลงในฐานข้อมูล
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("INSERT INTO cats (name, breed, age, color, status, date, image , detail) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (name, breed, age, color, status, date, image_path, detail))
                mysql.connection.commit()
                cursor.close()
            except Exception as e:
                return str(e)

            # หลังจากเพิ่มข้อมูลแมวเสร็จสิ้นให้ redirect ไปยังหน้า Datacat
            return redirect(url_for('data_cat'))

        # ถ้าเป็น GET request ให้แสดงหน้าเพิ่มข้อมูลแมว
        return render_template('add_cat.html', cat=None)
    else:
        return "คุณไม่มีสิทธิเข้าถึงหน้านี้."

# URL Route สำหรับลบการ์ด
@app.route('/delete_cat/<string:cat_name>', methods=['GET', 'POST'])
def delete_card(cat_name):
    if 'logged_in' in session and session['logged_in']:
        try:
            # เชื่อมต่อกับ MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # ลบข้อมูลแมวที่ตรงกับชื่อที่ระบุ
            cursor.execute("DELETE FROM cats WHERE name = %s", (cat_name,))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('data_cat'))
        except Exception as e:
            return str(e)
    else:
        return "คุณไม่มีสิทธิ์เข้าถึงหน้านี้"

@app.route('/edit_cat/<string:cat_name>', methods=['GET', 'POST'])
def edit_cat(cat_name):
    if 'logged_in' in session and session['logged_in']:
        if request.method == 'POST':
            # ดึงข้อมูลแมวจากฐานข้อมูล
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM cats WHERE name = %s', (cat_name,))
                cat = cursor.fetchone()
                cursor.close()
            except Exception as e:
                return str(e)
            
            if cat:
                # อัปเดตข้อมูลแมว
                cat['name'] = request.form['name']
                cat['breed'] = request.form['breed']
                cat['age'] = request.form['age']
                cat['color'] = request.form['color']
                cat['status'] = request.form.get('status', 'Not Ready')
                cat['date'] = request.form['date']
            
                if 'image' in request.files:
                    image = request.files['image']
                    if image.filename != '':
                        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
                        image.save(image_path)
                        cat['image'] = image_path
                            
                cat['detail'] = request.form['detail']
                    
                # อัปเดตข้อมูลแมวในฐานข้อมูล
                try:
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute("UPDATE cats SET name=%s, breed=%s, age=%s, color=%s, status=%s, date=%s, image=%s, detail=%s WHERE name=%s", 
                                   (cat['name'], cat['breed'], cat['age'], cat['color'], cat['status'], cat['date'], cat['image'], cat['detail'], cat_name))
                    mysql.connection.commit()
                    cursor.close()
                except Exception as e:
                    return str(e)
                    
                # หลังจากอัปเดตแมวเสร็จสิ้นให้ redirect ไปยังหน้า Datacat
                return redirect(url_for('data_cat'))
            else:
                return "ไม่พบแมวที่ต้องการแก้ไขในฐานข้อมูล"
        else:
            # ถ้าเป็น GET request ให้ดึงข้อมูลแมวจากฐานข้อมูลและแสดงในแบบฟอร์ม
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM cats WHERE name = %s', (cat_name,))
                cat = cursor.fetchone()
                cursor.close()
            except Exception as e:
                return str(e)
            
            if cat:
                return render_template('edit_cat.html', cat=cat, cat_name=cat_name)
            else:
                return "ไม่พบแมวที่ต้องการแก้ไขในฐานข้อมูล"
    else:
        return "คุณไม่มีสิทธิ์เข้าถึงหน้านี้"

# ข้อมูลตารางแมว
cats_Table = []

# หน้าแสดงข้อมูลที่ถูกเพิ่มล่าสุดในตารางแมว
@app.route('/lookcat_empty_table', methods=['GET'])
def lookcat_empty_table():
    if 'logged_in' in session and session['logged_in']:
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM cats_table")
            cats = cursor.fetchall()
            cursor.close()
            return render_template('lookcat_empty_table.html', cats=cats)
        except Exception as e:
            return str(e)

    # ส่งไปยังเทมเพลต lookcat_empty_table_guest.html เมื่อไม่มีการเข้าสู่ระบบ
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM cats_table")
        cats = cursor.fetchall()
        cursor.close()
        return render_template('lookcat_empty_table_guest.html', cats=cats)
    except Exception as e:
        return str(e)

@app.route('/add_cat_table', methods=['GET', 'POST'])
def add_cat_table():
    if 'logged_in' in session and session['logged_in']:
            if request.method == 'POST':
                # รับข้อมูลจากแบบฟอร์ม
                catName = request.form['catName']
                catBreed = request.form['catBreed']
                catAge = request.form['catAge']
                catColor = request.form['catColor']
                catStatus = request.form.get('catStatus')  # ใช้ get เพื่อรับค่าของ select
                catDate = request.form['catDate']
                
                # ตรวจสอบว่าวันที่ที่รับมาไม่เป็นค่าว่าง
                if not catDate:
                    return "กรุณากรอกวันที่แมว"

                # ตรวจสอบว่าอายุที่รับมาเป็นตัวเลขหรือไม่
                try:
                    catAge = int(catAge)
                except ValueError:
                    return "อายุของแมวต้องเป็นตัวเลข"

                # เพิ่มข้อมูลลงในตาราง cats_table ในฐานข้อมูล MySQL
                try:
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute("INSERT INTO cats_table (cat_name, cat_breed, cat_age, cat_color, cat_status, cat_date) VALUES (%s, %s, %s, %s, %s, %s)", (catName, catBreed, catAge, catColor, catStatus, catDate))
                    mysql.connection.commit()
                    cursor.close()

                    # เพิ่มข้อมูลใน cats_Table สำหรับการแสดงผลในเว็บไซต์
                    num_existing_cats_Table = len(cats_Table)
                    new_cats_Table = {
                        'cat_index': num_existing_cats_Table + 1,   
                        'cat_name': catName,
                        'cat_breed': catBreed,
                        'cat_age': catAge,
                        'cat_color': catColor,
                        'cat_status': catStatus,
                        'cat_date': catDate
                    }
                    cats_Table.append(new_cats_Table)
                    
                    # หลังจากเพิ่มข้อมูลเสร็จสิ้น ให้ redirect ไปยังหน้าที่ต้องการ
                    return redirect(url_for('lookcat_empty_table'))
                except Exception as e:
                    return str(e)
            # ถ้าเป็น GET request ให้แสดงหน้าเพิ่มข้อมูลตารางแมว
            return render_template('add_cat_table.html')
    else:
        return "คุณไม่มีสิทธิ์เข้าถึงหน้านี้"

    
@app.route('/delete_catcell/<int:cat_index>', methods=['POST'])
def delete_catcell(cat_index):
    if 'logged_in' in session and session['logged_in']:
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("DELETE FROM cats_table WHERE cat_index = %s", (cat_index,))
                mysql.connection.commit()

                # รีเซ็ตค่า cat_index ให้เริ่มต้นที่ 1 ใหม่
                cursor.execute("SET @count = 0")
                cursor.execute("UPDATE cats_table SET cat_index = @count:= @count + 1")
                cursor.execute("ALTER TABLE cats_table AUTO_INCREMENT = 1")
                mysql.connection.commit()
                cursor.close()
        
                return redirect(url_for('lookcat_empty_table'))
            except Exception as e:
                return str(e)
    else: 
        return "คุณไม่มีสิทธิใช้งานหน้านี้"

from flask import session, redirect, url_for

@app.route('/edit_cat_tables/<int:cat_index>', methods=['GET', 'POST'])
def edit_cat_tables(cat_index):
    if 'logged_in' in session and session['logged_in']:
        if request.method == 'POST':
            # รับข้อมูลจากฟอร์มแมวที่แก้ไข
            editcat_name = request.form['cat_name']
            editbreed = request.form['breed']
            editage = request.form['age']
            editcolor = request.form['color']
            editstatus = request.form.get('status')
            editdate = request.form['date']
            
            # ตรวจสอบว่าอายุที่รับมาไม่เป็นค่าว่าง
            if not editage:
                return "กรุณากรอกอายุ"

            # แปลงข้อมูลวันที่เป็นรูปแบบที่ถูกต้องก่อนบันทึกลงในฐานข้อมูล
            try:
                editdate = datetime.strptime(editdate, '%Y-%m-%d').date()
            except ValueError:
                return "รูปแบบวันที่ไม่ถูกต้อง"

            # ตรวจสอบข้อมูลที่ได้รับแล้วทำการแก้ไขในฐานข้อมูล
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("UPDATE cats_table SET cat_name=%s, cat_breed=%s, cat_age=%s, cat_color=%s, cat_status=%s, cat_date=%s WHERE cat_index=%s", (editcat_name, editbreed, editage, editcolor, editstatus, editdate, cat_index,))
                mysql.connection.commit()
                cursor.close()

                # หลังจากแก้ไขข้อมูลสำเร็จ ให้ redirect กลับไปยังหน้าที่แสดงข้อมูลทั้งหมด
                return redirect(url_for('lookcat_empty_table'))
            except Exception as e:
                return str(e)

        # ถ้าเป็น GET request ให้ดึงข้อมูลแมวจากฐานข้อมูลและแสดงในฟอร์มแก้ไขแมว
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM cats_table WHERE cat_index = %s", (cat_index,))
            cat = cursor.fetchone()
            cursor.close()
            return render_template('edit_cat_tables.html', cat=cat)
        except Exception as e:
            return str(e)
    else:
        return "คุณไม่มีสิทธิใช้งานหน้านี้"

PeopleTable_entries = []

@app.route('/contact_information', methods=['GET', 'POST'])
def contact_information():
        return render_template('contact_information.html')
    
@app.route('/save_to_system_admin', methods=['GET', 'POST'])
def save_to_system_admin():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        sex = request.form['sex']
        email = request.form['email']
        phonenumber = request.form['phonenumber']
        facebook = request.form['facebook']
        
        if not age:
            return "กรุณากรอกอายุ"
            
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO save_to_system_admin (name, age, sex, email, phonenumber, facebook) VALUES (%s, %s, %s, %s, %s, %s)", (name, age, sex, email, phonenumber, facebook))
        mysql.connection.commit()
        cursor.close()
        
    # อ่านข้อมูลจากฐานข้อมูลเพื่อแสดงผลทุกครั้งที่โหลดหน้าเว็บใหม่
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM save_to_system_admin")
    PeopleTable_entries = cursor.fetchall()
    cursor.close()
        
    return render_template('save_to_system_admin.html', PeopleTable_entries=PeopleTable_entries)

@app.route('/delete_contact_entry/<int:index>', methods=['POST'])
def delete_contact_entry(index):
    if request.method == 'POST':
        if 'logged_in' in session and session['logged_in']:
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT * FROM save_to_system_admin")
                PeopleTable_entries = cursor.fetchall()

                # Check if the index is within the range of existing entries
                if 0 <= index < len(PeopleTable_entries):
                    # Retrieve the contact ID of the entry to be deleted
                    contact_id = PeopleTable_entries[index]['id']

                    # Delete the entry from the database based on the specified index
                    cursor.execute("DELETE FROM save_to_system_admin WHERE id = %s", (contact_id,))
                    mysql.connection.commit()

                    # Close the cursor when done
                    cursor.close()

                    return redirect(url_for('save_to_system_admin'))
                else:
                    return "ไม่พบรายการที่ต้องการลบ"
            except Exception as e:
                return str(e)
        else:
            return "คุณไม่มีสิทธิเข้าถึงหน้านี้"

@app.route('/edit_contact_entry/<int:index>', methods=['GET', 'POST'])
def edit_contact_entry(index):
    if 'logged_in' in session and session['logged_in']:
        if request.method == 'POST':
            # Retrieve edited contact information from the form
            name = request.form['name']
            age = request.form['age']
            sex = request.form['sex']
            email = request.form['email']
            phonenumber = request.form['phonenumber']
            facebook = request.form['facebook']

            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT * FROM save_to_system_admin")
                PeopleTable_entries = cursor.fetchall()

                # Check if the index is within the range of existing entries
                if 0 <= index < len(PeopleTable_entries):
                    # Update contact information in the database based on the provided index
                    cursor.execute("""
                        UPDATE save_to_system_admin
                        SET name = %s, age = %s, sex = %s, email = %s, phonenumber = %s, facebook = %s
                        WHERE id = %s
                        """, (name, age, sex, email, phonenumber, facebook, PeopleTable_entries[index]['id']))
                    mysql.connection.commit()
                    cursor.close()

                    # Redirect to the page displaying all contact entries
                    return redirect(url_for('save_to_system_admin'))
                else:
                    # If the index is out of range, return an error message
                    return "Index out of range"
            except Exception as e:
                return str(e)
        else:
            # If the request method is GET, render the edit contact entry form
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT * FROM save_to_system_admin")
                PeopleTable_entries = cursor.fetchall()
                cursor.close()
            except Exception as e:
                return str(e)
            return render_template('edit_contact_entry.html', index=index, entry=PeopleTable_entries[index])
    else:
        return "คุณไม่มีสิทธิเข้าถึงหน้านี้"

# Configuration of mail 
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'tiger20002543@gmail.com'
app.config['MAIL_PASSWORD'] = 'jvdc dqny rezy abqi'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

# Create Email instance
mail = Mail(app) 

# Route to contact form
@app.route('/Contact', methods=['GET', 'POST'])
def contact_page():
    return render_template('contact.html')

# Send email function mapped to a particular URL ‘/send_email’ 
@app.route("/send_email", methods=['POST']) 
def send_email(): 
    # Get data from the form
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Create message object
    msg = Message(
        'Hello',  # Subject
        sender='yourId@gmail.com',  # Sender email
        recipients=["tiger20002543@gmail.com"] #recipients
    ) 
    msg.body = f'Hello, you have a message from {name} ({email}):\n\n{message}'  # Body of the email

    # Send email
    mail.send(msg) 

    # Save contact information to MySQL database
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO contact_info (name, email, message) VALUES (%s, %s, %s)", (name, email, message))
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        return str(e)

    # Redirect to the home page after sending email and saving to database
    return redirect(url_for('home'))

# หน้าแรก
@app.route('/')
def home():
    return render_template('home.html')

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0' , port=5000)