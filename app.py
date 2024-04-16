from datetime import datetime  # เรียกใช้งานโมดูล datetime แล้ว import class datatime เพื่อใช้ในการจัดการเวลาและวันที่
import os # เรียกใช้งานโมดูล os  เพื่อทำงานกับระบบไฟล์และสิ่งที่เกี่ยวข้องกับการจัดการไฟล์และโฟลเดอร์ในระบบปฏิบัติการ 
from flask import Flask, render_template, request, redirect, url_for, session # เรียกใช้งาน โมดูล Flask แล้ว import class เพื่อสร้างเทมเพลต HTML, เพื่อจัดการข้อมูลที่ส่งมาจาก HTTP request, 
# เพื่อเปลี่ยนเส้นทางการเรียกใช้, เพื่อสร้าง URL สำหรับฟังก์ชันที่กำหนด เพื่อจัดการข้อมูล session ใน Flask 
from flask_mail import Mail, Message # เรียกใช้โมดูล Flask-Mail แล้ว import class เข้ามาใช้งาน การส่งอีเมล์ผ่าน Flask ด้วย Flask-Mail extension
from flask_mysqldb import MySQL # เรียกใช้โมดูล MySQLdb แล้ว import class MySQL เพื่อใช้ในการเชื่อมต่อกับฐานข้อมูล MySQL ใน Flask โดยใช้ Flask-MySQLdb extension
import MySQLdb.cursors # เรียกใช้งานโมดูล cursors จากไลบรารี MySQLdb เพื่อใช้ในการทำงานกับคำสั่ง MySQL ในลักษณะของ cursor objects

app = Flask(__name__) # ระบุ โมดูล ประกาศฟังก์ชันเริ่มต้น Flask Framework 

app.config['SECRET_KEY'] = 'mykey' 

# เชื่อมฐานข้อมูล Mysql
app.config['MYSQL_HOST'] = 'localhost'  # MySQL server ที่อยู่เซิฟเวอร์
app.config['MYSQL_USER'] = 'root'  # MySQL username Id ฐานข้อมูล
app.config['MYSQL_PASSWORD'] = '1234'  # MySQL password รหัสผ่านฐานข้อมูล
app.config['MYSQL_DB'] = 'loginflask'  # ชื่อ Database ที่เชื่อมต่อฐานข้อมูล
mysql = MySQL(app)  # ประกาศฟังก์ชันเชื่อมต่อฐานข้อมูล ในตัวแปร mysql ที่มีค่าเป็น app 

# กำหนดเส้นทาง URL ล็อคอินที่เชื่อมโยงฟังก์ชัน home
@app.route('/')
def home(): # ประกาศฟังก์ชันชื่อ home
    return render_template('home.html')  # คืนค่าจากฟังก์ชัน home() โดยใช้ render_template

# กำหนดเส้นทาง URL ล็อคอินที่เชื่อมโยงฟังก์ชัน login เพื่อรองรับการร้องขอ GET และ POST 
@app.route('/login', methods=['GET', 'POST'])
def login(): # กำหนดฟังก์ชัน login() ซึ่งจะถูกเรียกเมื่อเข้าสู่ URL เข้าสู่ระบบ
    #ตรวจสอบว่าเมธอดการร้องขอเป็น POST หรือไม่ ถ้าเป็น POST แสดงว่าผู้ใช้ได้ส่งฟอร์มการเข้าสู่ระบบ
    if request.method == 'POST':
        
        #ดึงชื่อผู้ใช้และรหัสผ่านจากการส่งฟอร์มโดยใช้ request.form
        username = request.form['username']
        password = request.form['password']
        
        # เชื่อมต่อกับฐานข้อมูลและดำเนินการคิวรี่เพื่อตรวจสอบว่ามีผู้ใช้งานที่มีชื่อผู้ใช้และรหัสผ่านที่ให้มาหรือไม่
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,)) 
        # เรียกข้อมูลแถวแรกที่ถูกคิวรีออกมาจากฐานข้อมูล และเก็บข้อมูลนั้นไว้ในตัวแปร user 
        user = cursor.fetchone()
        #ปิด cursor ช่วยป้องกันการชคิวรีข้อมูลที่ไม่จำเป็นในแถวของผู้ใช้งาน
        cursor.close()
        
        #ถ้าตรวจสอบว่าชื่อผู้ใช้และรหัสผ่านที่ให้ตรงกับข้อมูลของผู้ดูแลระบบหรือไม่
        if username == 'admin' and password == '00000': 
            session['logged_in'] = True # กำหนดค่าให้กับตัวแปร logged_in ใน session เป็น True ว่าผู้ใช้ได้เข้าสู่ระบบแล้ว
            session['username'] = user['username'] # เก็บค่าชื่อผู้ใช้ใน session เพื่อใช้ในการตรวจสอบตัวตนหรือแสดงชื่อผู้ใช้ในหน้าเว็บ
            return redirect(url_for('admin_panel')) # นำผู้ใช้ไปยังหน้า 'admin_panel' โดยใช้ฟังก์ชัน redirect()
        else: # ถ้าไม่เป็นจริงระบบจะทำการ เรนเดอร์ หน้า login แล้วแสดงข้อความ error
            return render_template('login.html', error='ข้อมูลเข้าสู่ระบบไม่ถูกต้อง กรุณาลองอีกครั้ง')
    
    # ถ้าตรวจสอบว่าผู้ใช้ได้ล็อกอินอยู่และถ้าใช้ เปลี่ยนเส้นทางไปยัง admin_panel
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('admin_panel')) # นำผู้ใช้ไปยังหน้า 'admin_panel' โดยใช้ฟังก์ชัน redirect()
    
    #ถ้าไม่มีเงื่อนไขใดเป็นจริง หรือถ้าผู้ใช้ยังไม่ได้ล็อกอิน แสดงเทมเพลต login.html
    return render_template('login.html')

# กำหนดเส้นทาง URL ออกจากระบบที่เชื่อมโยงฟังก์ชัน  logout
@app.route('/logout')
def logout(): #ประกาศฟังก์ชันชื่อ logout
    session.pop('logged_in', None) # ลบ session variable สำหรับตัวแปร logged_in
    session.pop('username', None)  # ลบ session variable สำหรับชื่อผู้ใช้
    return redirect(url_for('login'))  # เปลี่ยนเส้นทางไปยังหน้า login หลังจากล็อกเอาท์

# กำหนดเส้นทาง URL ควบคุมระบบที่เชื่อมโยงฟังก์ชัน  admin_panel
@app.route('/admin_panel')
def admin_panel():#ประกาศฟังก์ชันชื่อ admin_panel
    if 'logged_in' in session and session['logged_in']: #ตรวจสอบว่าผู้ใช้ได้ล็อกอินเข้าสู่ระบบหรือไม่ โดยดูจากค่า 'logged_in' ใน session object
        if session['username'] == 'admin':  # ตรวจสอบว่าผู้ใช้เป็นผู้ดูแลระบบหรือไม่
            return render_template('admin_panel.html') #ถ้าผู้ใช้เป็นผู้ดูแลระบบ (admin) จะแสดงหน้า admin_panel.html
        else:
            return redirect(url_for('login'))  # ถ้าผู้ใช้ไม่ใช่ผู้ดูแลระบบ (admin) จะเปลี่ยนเส้นทางไปยังหน้า login
    else:
        return redirect(url_for('login'))  # ถ้าผู้ใช้ไม่ได้ล็อกอินเข้าสู่ระบบ จะเปลี่ยนเส้นทางไปยังหน้า login เช่นกัน

cats = []  #  กำหนดให้ cats เป็นลิสต์ว่างเพื่อใช้ในการเก็บข้อมูลแมวจากฐานข้อมูล

#  กำหนดเพื่อระบุโฟลเดอร์ที่จะใช้เก็บไฟล์ภาพที่อัปโหลด
UPLOAD_FOLDER = 'static/images'

# กำหนดเส้นทาง URL ข้อมูลการ์ดแมวที่เชื่อมโยงฟังก์ชัน  Datacat  โดยใช้เมทอด GET และ POST
@app.route('/Datacat', methods=['GET', 'POST'])
def data_cat():# ประกาศฟังก์ชันชื่อ data_cat 
    if 'logged_in' in session and session['logged_in']: # ถ้าเงื่อนไขเป็นจริงตรวจสอบว่าผู้ใช้ได้ล็อกอินเข้าสู่ระบบหรือไม่ โดยดูจากค่า 'logged_in' ใน session object
        try: # บล็อกตรวจสอบการเกิดข้อผิดพลาด (exceptions)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # เชื่อมต่อกับ MySQL database ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลการ์ดแมว โดยใช้คลาส DictCursor ซึ่งจะทำให้ได้ผลลัพธ์ในรูปแบบ dictionary เพื่อดึงข้อมูลการ์ดแมวทั้งหมดออกมาในฐานข้อมูล
            cursor.execute('SELECT * FROM cats') # สั่ง SQL เพื่อดึงข้อมูลทั้งหมดจากตาราง 'cats' ในฐานข้อมูล
            cats = cursor.fetchall() # เก็บผลลัพธ์ที่ได้จากการดึงข้อมูลจากฐานข้อมูลลงในตัวแปร cats
            cursor.close() # ปิด cursor เพื่อทำการจบการทำงานในบล็อก try
        except Exception as e: # ถ้าเกิดข้อผิดพลาดในการทำงานในบล็อก try
            return str(e) # แสดงข้อความผิดพลาด ในกรณีที่เกิดข้อผิดพลาดในการทำงานในบล็อก try
        return render_template('Datacat.html', cats=cats) # ส่งข้อมูลมายังเทมเพจ Datacat.html โดยใช้ cats และ cats ในการแสดงผล
    else: # เงื่อนไข if เป็นเท็จไม่เป็นจริง ผู้ใช้ไม่ได้ล็อกอินเข้าสู่ระบบ จะเข้าหน้าส่วนของแขก
        try: # บล็อกตรวจสอบการเกิดข้อผิดพลาด (exceptions)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # เชื่อมต่อกับ MySQL database ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลการ์ดแมว โดยใช้คลาส DictCursor ซึ่งจะทำให้ได้ผลลัพธ์ในรูปแบบ dictionary เพื่อดึงข้อมูลการ์ดแมวทั้งหมดออกมาในฐานข้อมูล
            cursor.execute('SELECT * FROM cats') # สั่ง SQL เพื่อดึงข้อมูลทั้งหมดจากตาราง 'cats' ในฐานข้อมูล
            cats = cursor.fetchall() # เก็บผลลัพธ์ที่ได้จากการดึงข้อมูลจากฐานข้อมูลลงในตัวแปร cats
            cursor.close() # ปิด cursor เพื่อทำการจบการทำงานในบล็อก try
        except Exception as e: # หากมีข้อผิดพลาดในการดำเนินการหรือการเชื่อมต่อกับฐานข้อมูล จะคืนค่าเป็นข้อผิดพลาดที่เกิดขึ้น โดยใช้ str(e)
            return str(e) 
        return render_template('Datacat_guest.html', cats=cats) # ส่งข้อมูลมายังเทมเพจ Datacat_guest.html โดยใช้ cats และ cats ในการแสดงผล

# กำหนดเส้นทาง URL เพิ่มการ์ดแมวที่เชื่อมโยงฟังก์ชัน  add_new_cat  โดยใช้เมทอด GET และ POST
@app.route('/add_new_cat', methods=['GET', 'POST'])
def add_new_cat(): # กำหนดฟังชัน add_new_cat
    if 'logged_in' in session and session['logged_in']: # ถ้าเงื่อนไขเป็นจริงตรวจสอบว่าผู้ใช้ได้ล็อกอินเข้าสู่ระบบหรือไม่ โดยดูจากค่า 'logged_in' ใน session object
        if request.method == 'POST': #ตรวจสอบว่าเมธอดการร้องขอเป็น POST หรือไม่ ถ้าเป็น POST แสดงว่าผู้ใช้ได้ส่่งฟอร์ม เพิ่มการ์ดแมวแล้ว
            # รับข้อมูลเพิ่มการ์ดแมวจาก request form แบบฟอร์ม
            name = request.form['name']
            breed = request.form['breed']
            age = request.form['age']
            color = request.form['color']
            status = request.form.get('status', '')  # รับค่า Status  จาก Form 
            date = request.form['date']
            detail = request.form['detail']

            # ตรวจสอบว่าข้อมูลที่รับมาไม่เป็นค่าว่าง ถ้าเงื่อนไขเป็นจริง ถ้าเป็นค่าว่างจะ Retuen ข้อความไปยังผู้ใช้
            if not name or not breed or not age or not color or not status or not date or not detail: # not ถ้าเป็น สตริง ว่าง จะประเมินเป็น True , or not ตรวจสอบว่าเงื่อนไขใดเป็นจริง หรือไม่ 
                return "กรอกข้อมูลการ์ดแมวให้ครบถ้วน"
            
            # กำหนดให้ image_path เป็นค่าว่าง ในกรณีที่ไม่มีการอัปโหลดไฟล์รูปภาพ 
            image_path = None
            # ตรวจสอบว่ามีการอัปโหลดไฟล์รูปภาพแมวหรือไม่
            if 'image' in request.files: 
                image = request.files['image'] # หากมีการอัปโหลดไฟล์รูปภาพ จะเก็บข้อมูลของไฟล์นั้นไว้ในตัวแปร image
                if image.filename != '': # ตรวจสอบว่าไฟล์ที่อัปโหลดมีชื่อหรือไม่
                    image_path = os.path.join(UPLOAD_FOLDER, image.filename) # กำหนดที่อยู่ของไฟล์รูปภาพที่อัปโหลดไปที่โฟลเดอร์ UPLOAD_FOLDER
                    print(str(request.files['image'])) # แสดงที่อยู่ของไฟล์รูปภาพที่อัปโหลดไป
                    image.save(image_path) # บันทึกไฟล์รูปภาพที่อัปโหลดไปที่โฟลเดอร์ UPLOAD_FOLDER

            # สร้าง dictionary เก็บข้อมูลแมวจากแบบฟอร์ม และเพิ่มข้อมูลแมวใหม่ลงใน list cats
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
            # เพิ่มข้อมูลการ์ดแมวใหม่ลงใน list cats ในฐานข้อมูล และบันทึกการเปลี่ยนแปลง ในฐานข้อมูล เพื่อให้ผู้ใช้สามารถดูข้อมูลแมวได้ 
            cats.append(new_cat) 
            
            try: # บล็อกตรวจสอบการเกิดข้อผิดพลาด (exceptions)
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # เชื่อมต่อกับ MySQL database ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลการ์ดแมว โดยใช้คลาส DictCursor เพื่อดึงข้อมูลแมวทั้งหมดออกมา เพื่อเพิ่มการ์ดแมว ในฐานข้อมูล 
                cursor.execute("INSERT INTO cats (name, breed, age, color, status, date, image , detail) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (name, breed, age, color, status, date, image_path, detail)) # เพิ่มข้อมูลแมวใหม่ลงในฐานข้อมูล
                mysql.connection.commit() # ทำการ commit การเพิ่มฐานข้อมูล เพื่อบันทึกข้อมูลใหม่ลงในฐานข้อมูล
                cursor.close() # ปิด cursor เพื่อทำการจบการทำงานในบล็อก try
            except Exception as e: # หากมีข้อผิดพลาดในการดำเนินการเพิ่มข้อมูลการ์ดแมวหรือการเชื่อมต่อกับฐานข้อมูล จะคืนค่าเป็นข้อผิดพลาดที่เกิดขึ้น โดยใช้ str(e)
                return str(e) 

            # หลังจากเพิ่มข้อมูลแมวเสร็จสิ้นให้ redirect ไปยังหน้า Datacat
            return redirect(url_for('data_cat'))

        # ถ้าเป็น GET request ให้แสดงหน้าเพิ่มข้อมูลแมว
        return render_template('add_cat.html', cat=None) # กำหนดค่า None หรือไม่มีค่า ส่งข้อมูลเป็นค่าว่างไปยังเทมเพลต
    else: 
        return "คุณไม่มีสิทธิเข้าถึงหน้านี้" # กรณีผู้ใช้ไม่ได้ล็อกอินเข้าสู่ระบบ ฟังก์ชันจะคืนค่าเป็นข้อความที่บอกว่าผู้ใช้ไม่มีสิทธิ์ในการเข้าถึงหน้านี้:

# กำหนดเส้นทาง URL ลบการ์ดแมวที่เชื่อมโยงฟังก์ชัน  delete_cat โดยใช้เมทอด GET และ POST
@app.route('/delete_cat/<string:cat_name>', methods=['GET', 'POST'])
def delete_card(cat_name): # สร้างฟังชั่น delete_card โดยรับค่า cat_name ที่รับ มาจากพารามิเตอร์ เป็นสตริง  
    if 'logged_in' in session and session['logged_in']: # ถ้าเงื่อนไขเป็นจริงตรวจสอบว่าผู้ใช้ได้ล็อกอินเข้าสู่ระบบหรือไม่ โดยดูจากค่า 'logged_in' ใน session object
        try: # บล็อกตรวจสอบการเกิดข้อผิดพลาด (exceptions)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # เชื่อมต่อกับ MySQL database ซึ่งเป็นฐานข้อมูลที่ใช้ลบข้อมูลการ์ดแมว โดยใช้คลาส DictCursor เพื่อดึงข้อมูลแมวทั้งหมดออกมา เพื่อนําไปลบ ในฐานข้อมูล 
            cursor.execute("DELETE FROM cats WHERE name = %s", (cat_name,)) # ลบข้อมูลการ์ดแมวที่ตรงกับชื่อที่ระบุจากฐานข้อมูล
            mysql.connection.commit() # ทำการ commit ลบฐานข้อมูลสำเร็จ 
            cursor.close() # ปิด cursor เพื่อทำการจบการทำงานในบล็อก try
            return redirect(url_for('data_cat')) #หลังจากลบการ์ดแมวแล้วจะ redirect ไปยังหน้า Datacat
        except Exception as e: # หากมีข้อผิดพลาดในการดำเนินการแก้ไขข้อลบการ์ดแมวหรือการเชื่อมต่อกับฐานข้อมูล จะคืนค่าเป็นข้อผิดพลาดที่เกิดขึ้น โดยใช้ str(e)
            return str(e) 
    else: # กรณีผู้ใช้ไม่ได้ล็อกอินเข้าสู่ระบบ ฟังก์ชันจะคืนค่าเป็นข้อความที่บอกว่าผู้ใช้ไม่มีสิทธิ์ในการเข้าถึงหน้านี้
        return "คุณไม่มีสิทธิ์เข้าถึงปุ่มลบนี้"

# กำหนดเส้นทาง URL แก้ไขการ์ดแมวที่เชื่อมโยงฟังก์ชัน edit_cat โดยใช้เมทอด GET และ POST
@app.route('/edit_cat/<string:cat_name>', methods=['GET', 'POST']) 
def edit_cat(cat_name): # สร้างฟังชั่น edit_cat โดยรับค่า cat_name ที่รับ มาจากพารามิเตอร์ เป็นสตริง
    if 'logged_in' in session and session['logged_in']: # ถ้าเงื่อนไขเป็นจริงตรวจสอบว่าผู้ใช้ได้ล็อกอินเข้าสู่ระบบหรือไม่ โดยดูจากค่า 'logged_in' ใน session object
        if request.method == 'POST': #ตรวจสอบว่าเมธอดการร้องขอเป็น POST หรือไม่ ถ้าเป็น POST แสดงว่าผู้ใช้ได้ส่่งฟอร์ม แก้ไขการ์ดแมวแล้ว
            # ดึงข้อมูลแมวจากฐานข้อมูล
            try: # บล็อกตรวจสอบการเกิดข้อผิดพลาด (exceptions)
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # เชื่อมต่อกับ MySQL database ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลการ์ดแมว โดยใช้คลาส DictCursor เพื่อดึงข้อมูลแมวทั้งหมดออกมา เพื่อนําไปแก้ไข ในฐานข้อมูล 
                cursor.execute('SELECT * FROM cats WHERE name = %s', (cat_name,)) # execute เพื่อดึงข้อมูลทั้งหมดจากตาราง 'cats' ในฐานข้อมูล โดยรับจาก พารามิเตอร์ cat_name
                cat = cursor.fetchone() # ดึงข้อมูลแมวที่เก็บไว้ในตาราง 'cats' ออกมา และเก็บไว้ในตัวแปร cats
                cursor.close() # ปิด cursor เพื่อทำการจบการทำงานในบล็อก try
            except Exception as e: # ถ้าเกิดข้อผิดพลาดในการทำงานในบล็อก try
                return str(e) # แสดงข้อความผิดพลาด ในกรณีที่เกิดข้อผิดพลาดในการทำงานในบล็อก try
            
            if cat: # ถ้าตรวจสอบว่า มีข้อมูลแมวที่เก็บไว้ในตาราง 'cats' หรือไม่ ถ้าเป็นจริง   
                # อัปเดตข้อมูลแมว รับข้อมูลจาก request form
                cat['name'] = request.form['name']
                cat['breed'] = request.form['breed']
                cat['age'] = request.form['age']
                cat['color'] = request.form['color']
                cat['status'] = request.form.get('status', 'Not Ready')
                cat['date'] = request.form['date']
                cat['detail'] = request.form['detail']
                
                # ตรวจสอบว่าข้อมูลที่รับมาไม่เป็นค่าว่าง ถ้าเงื่อนไขเป็นจริง ถ้าเป็นค่าว่างจะ Retuen ข้อความไปยังผู้ใช้
                if not cat['name'] or not cat['breed'] or not cat['age'] or not cat['color'] or not cat['status'] or not cat['date'] or not cat['detail']: # not ถ้าเป็น สตริง ว่าง จะประเมินเป็น True , or not ตรวจสอบว่าเงื่อนไขใดป็นจริง หรือไม่ ถ้าไม่ จะ Return ข้อความยังผู้ใช้ 
                    return "กรอกข้อมูลแก้ไขแมวให้ครบถ้วน" 
               
                if 'image' in request.files: # ตรวจสอบว่ามีการอัปโหลดไฟล์รูปภาพแมวหรือไม่ 
                    image = request.files['image']  # ถ้าหากมีการอัปโหลดไฟล์รูปภาพ จะเก็บข้อมูลของไฟล์นั้นไว้ในตัวแปร image
                    if image.filename != '': # กำหนดที่อยู่ของไฟล์รูปภาพที่อัปโหลดไปที่โฟลเดอร์ UPLOAD_FOLDER
                        image_path = os.path.join(UPLOAD_FOLDER, image.filename) # กำหนดที่อยู่ของไฟล์รูปภาพที่อัปโหลดไปที่โฟลเดอร์ UPLOAD_FOLDER
                        image.save(image_path) # แสดงที่อยู่ของไฟล์รูปภาพที่อัปโหลดไป 
                        cat['image'] = image_path  # บันทึกไฟล์รูปภาพที่อัปโหลดไปที่โฟลเดอร์ UPLOAD_FOLDER
                            
                # อัปเดตข้อมูลแมวในฐานข้อมูล
                try: # บล็อกตรวจสอบการเกิดข้อผิดพลาด (exceptions) 
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # เชื่อมต่อกับ MySQL database ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลการ์ดแมว ในการอัปเดต ข้อมูลจากฐานข้อมูลซึ่งจะเป็นตัวแปร cursorในการอัปเดตแมว
                    cursor.execute("UPDATE cats SET name=%s, breed=%s, age=%s, color=%s, status=%s, date=%s, image=%s, detail=%s WHERE name=%s", #ดึงข้อมูลแมวจากฐานข้อมูล ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลการ์ดแมว
                                   (cat['name'], cat['breed'], cat['age'], cat['color'], cat['status'], cat['date'], cat['image'], cat['detail'], cat_name)) 
                    mysql.connection.commit() # ทำการ commit อัพเดตฐานข้อมูลสำเร็จ 
                    cursor.close() # ปิด cursor เพื่อทำการจบการทำงานในบล็อก try
                except Exception as e: # หากมีข้อผิดพลาดในการดำเนินการแก้ไขข้อมูลการ์ดแมวหรือการเชื่อมต่อกับฐานข้อมูล จะคืนค่าเป็นข้อผิดพลาดที่เกิดขึ้น โดยใช้ str(e)
                    return str(e) 
                    
                # หลังจากอัปเดตแมวเสร็จสิ้นให้ redirect ไปยังหน้า Datacat 
                return redirect(url_for('data_cat'))
            
        else: # ตรวจสอบว่าผู้ใช้ไม่ได้ล็อกอินเข้าสู่ระบบ:
            # ถ้าเป็น GET request ให้ดึงข้อมูลแมวจากฐานข้อมูลและแสดงในแบบฟอร์ม
            try: # บล็อกตรวจสอบการเกิดข้อผิดพลาด (exceptions) 
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # เชื่อมต่อกับ MySQL database ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลการ์ดแมว ในการอัปเดต ข้อมูลจากฐานข้อมูลซึ่งจะเป็นตัวแปร cursorในการอัปเดตแมว
                cursor.execute('SELECT * FROM cats WHERE name = %s', (cat_name,)) # ดึงข้อมูลแมวจากฐานข้อมูล ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลการ์ดแมว
                cat = cursor.fetchone() # ดึงข้อมูลแมวที่เก็บไว้ในตาราง 'cats' ออกมา และเก็บไว้ในตัวแปร cat
                cursor.close() # ปิด cursor เพื่อทำการจบการทำงานในบล็อก try
            except Exception as e: # หากมีข้อผิดพลาดในการดำเนินการแก้ไขข้อมูลการ์ดแมวหรือการเชื่อมต่อกับฐานข้อมูล จะคืนค่าเป็นข้อผิดพลาดที่เกิดขึ้น โดยใช้ str(e)
                return str(e) 
            
            if cat: # ถ้าตรวจสอบว่า มีข้อมูลแมวที่หน้าแก้ไข 'cats' หรือไม่ ถ้าเป็นจริง   
                return render_template('edit_cat.html', cat=cat, cat_name=cat_name) # จะแสดงหน้าแก้ไขแมว โดยส่งเทมเพลตแล้วส่งข้อมูลแมวเพื่อไปแก้ไข
    else: # กรณีผู้ใช้ไม่ได้ล็อกอินเข้าสู่ระบบ ฟังก์ชันจะคืนค่าเป็นข้อความที่บอกว่าผู้ใช้ไม่มีสิทธิ์ในการเข้าถึงหน้านี้
        return "คุณไม่มีสิทธิ์เข้าถึงปุ่มแก้ไขนี้"

# กำหนดให้ cats_Table เป็นลิสต์ว่างเพื่อใช้ในการเก็บข้อมูลตารางแมวจากฐานข้อมูล
cats_Table = []

# กำหนดเส้นทาง URL แก้ไขการ์ดแมวที่เชื่อมโยงฟังก์ชัน lookcat_empty_table โดยใช้เมทอด GET
@app.route('/lookcat_empty_table', methods=['GET'])
def lookcat_empty_table(): # ประกาศฟังชั่น lookcat_empty_table 
    if 'logged_in' in session and session['logged_in']:  # ถ้าเงื่อนไขเป็นจริงตรวจสอบว่าผู้ใช้ได้ล็อกอินเข้าสู่ระบบหรือไม่ โดยดูจากค่า 'logged_in' ใน session object
        try: # บล็อกตรวจสอบการเกิดข้อผิดพลาด (exceptions) 
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # เชื่อมต่อกับ MySQL database ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลตารางแมว 
            cursor.execute("SELECT * FROM cats_table") # ดึงข้อมูลตารางแมวจากฐานข้อมูล ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลตารางแมว
            cats = cursor.fetchall()  # ดึงข้อมูลแมวที่เก็บไว้ในตาราง 'cats_Table' ออกมา และเก็บไว้ในตัวแปร cats
            cursor.close() # ปิด cursor เพื่อทำการจบการทำงานในบล็อก try 
            return render_template('lookcat_empty_table.html', cats=cats) # ส่งไปยังเทมเพลต lookcat_empty_table.html และแสดงข้อมูลแมวที่เก็บไว้ในตาราง เมื่อมีการเข้าสู่ระบบ
        except Exception as e:  # หากมีข้อผิดพลาดในการดำเนินการหรือการเชื่อมต่อกับฐานข้อมูล จะคืนค่าเป็นข้อผิดพลาดที่เกิดขึ้น โดยใช้ str(e)
            return str(e) 
        
    #ถ้าเป็น GET request ให้ดึงข้อมูลตารางแมวจากฐานข้อมูลและแสดงหน้า ตารางแมว
    try: # บล็อกตรวจสอบการเกิดข้อผิดพลาด (exceptions) 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # เชื่อมต่อกับ MySQL database ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลตารางแมว 
        cursor.execute("SELECT * FROM cats_table") # ดึงข้อมูลตารางแมวจากฐานข้อมูล ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลตารางแมว
        cats = cursor.fetchall() # ดึงข้อมูลแมวที่เก็บไว้ในตาราง 'cats_Table' ออกมา และเก็บไว้ในตัวแปร cats
        cursor.close() # ปิด cursor เพื่อทำการจบการทำงานในบล็อก try 
        return render_template('lookcat_empty_table_guest.html', cats=cats) # ส่งไปยังเทมเพลต lookcat_empty_table_guest.html เมื่อไม่มีการเข้าสู่ระบบ
    except Exception as e: # หากมีข้อผิดพลาดในการดำเนินหรือการเชื่อมต่อกับฐานข้อมูล จะคืนค่าเป็นข้อผิดพลาดที่เกิดขึ้น โดยใช้ str(e)
        return str(e) 

# กำหนดเส้นทาง URL แก้ไขการ์ดแมวที่เชื่อมโยงฟังก์ชัน and_cat_table โดยใช้เมทอด GET และ POST
@app.route('/add_cat_table', methods=['GET', 'POST'])
def add_cat_table(): #ประกาศฟังชัน add_cat_table 
    if 'logged_in' in session and session['logged_in']: # ถ้าเงื่อนไขเป็นจริงตรวจสอบว่าผู้ใช้ได้ล็อกอินเข้าสู่ระบบหรือไม่ โดยดูจากค่า 'logged_in' ใน session object
            if request.method == 'POST': #ตรวจสอบว่าเมธอดการร้องขอเป็น POST หรือไม่ ถ้าเป็น POST แสดงว่าผู้ใช้ได้ส่่งฟอร์ม เพิ่มตารางแมวแล้ว
                # รับข้อมูลจากเพิ่มตารางแมว request form แบบฟอร์ม
                catName = request.form['catName']
                catBreed = request.form['catBreed']
                catAge = request.form['catAge']
                catColor = request.form['catColor']
                catStatus = request.form.get('catStatus')  
                catDate = request.form['catDate']
                
                # ตรวจสอบว่าวันเกิดแมวที่รับมาไม่เป็นค่าว่าง ถ้าเงื่อนไขเป็นจริง ถ้าเป็นค่าว่างจะ Retuen ข้อมความไปยังผู้ใช้
                if not catDate:  
                    return "กรุณากรอกวันเกิดแมว"

                # ตรวจสอบว่าอายุที่รับมาเป็นตัวเลขหรือไม่
                try: # บล็อกตรวจสอบการเกิดข้อผิดพลาด (exceptions) 
                    catAge = int(catAge)
                except ValueError: # ยกเว้นค่าผิดพลาด จะ Retuen ข้อมความไปยังผู้ใช้
                    return "กรุณากรอกอายุแมว"

                # เพิ่มข้อมูลลงในตาราง cats_table ในฐานข้อมูล MySQL
                try:
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # เชื่อมต่อกับ MySQL database ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลตารางแมว โดยใช้คลาส DictCursor เพื่อดึงข้อมูลแมวทั้งหมดออกมา เพื่อเพิ่มตารางแมว ในฐานข้อมูล 
                    cursor.execute("INSERT INTO cats_table (cat_name, cat_breed, cat_age, cat_color, cat_status, cat_date) VALUES (%s, %s, %s, %s, %s, %s)", (catName, catBreed, catAge, catColor, catStatus, catDate)) #ดึงข้อมูลตารางแมวจากฐานข้อมูล ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลตารางแมว %s ยึดตำแหน่งเป็นพารามิเตอร์  สั่ง execute query เพื่อเพิ่มข้อมูลที่รับมาจากฟอร์มลงในตาราง
                    mysql.connection.commit() # ทำการ commit อัพเดตฐานข้อมูลสำเร็จ 
                    cursor.close() # ปิด cursor เพื่อทำการจบการทำงานในบล็อก try 

                    # เพิ่มข้อมูลในตาราง cats_Table 
                    num_existing_cats_Table = len(cats_Table) # นับจำนวนแมวในตาราง cats_Table ฟังก์ชัน len() เพื่อนับจำนวนสมาชิกทั้งหมดใน cats_Table แล้วเก็บค่านั้นไว้ในตัวแปร num_existing_cats_Table
                    new_cats_Table = { #  สร้าง dictionary ใหม่เพื่อเก็บข้อมูลแมวใหม่ที่จะถูกเพิ่มลงใน cats_tables โดยระบุ Index ของแมวใหม่
                        'cat_index': num_existing_cats_Table + 1,   # เพื่ม dictionary ที่เก็บข้อมูลแมวใหม่ลงในตาราง cats_table 
                        'cat_name': catName, # ชื่อตัวแปร = {key : value}
                        'cat_breed': catBreed,
                        'cat_age': catAge,
                        'cat_color': catColor,
                        'cat_status': catStatus,
                        'cat_date': catDate
                    }
                    cats_Table.append(new_cats_Table) # append เพิ่มข้อมูลตารางแมวใหม่ลงใน list cats_Table ในฐานข้อมูล และบันทึกการเปลี่ยนแปลง ในฐานข้อมูล เพื่อให้ผู้ใช้สามารถดูข้อมูลตารางแมวได้ 
                    
                    # หลังจากเพิ่มข้อมูลเสร็จสิ้น ให้ redirect ไปยังหน้าที่ต้องการ
                    return redirect(url_for('lookcat_empty_table'))
                except Exception as e: # หากมีข้อผิดพลาดในการดำเนินการเพิ่มตารางข้อมูลหรือการเชื่อมต่อกับฐานข้อมูล จะคืนค่าเป็นข้อผิดพลาดที่เกิดขึ้น โดยใช้ str(e)
                    return str(e) 
            # ถ้าเป็น GET request ให้แสดงหน้าเพิ่มข้อมูลตารางแมว 
            return render_template('add_cat_table.html')
    else:  # ถ้าไม่ได้เข้าสู่ระบบไม่มีสิทธิเข้าถึงหน้านี้ ให้ return ข้อความ "คุณไม่มีสิทธิเข้าถึงหน้านี้"
        return "คุณไม่มีสิทธิ์เข้าถึงปุ่มเพิ่มตารางแมว"

# กำหนดเส้นทาง URL ลบตารางแมวที่เชื่อมโยงฟังก์ชัน  delete_catcell โดยใช้เมทอด POST    
@app.route('/delete_catcell/<int:cat_index>', methods=['POST'])
def delete_catcell(cat_index): # กำหนดฟังชั่น delete_catcell ที่รับ มาจากพารามิเตอร์ cat_index เป็นตัวเลข 
    if 'logged_in' in session and session['logged_in']: # ถ้าเงื่อนไขเป็นจริงตรวจสอบว่าผู้ใช้ได้ล็อกอินเข้าสู่ระบบหรือไม่ โดยดูจากค่า 'logged_in' ใน session object
            try: # บล็อกตรวจสอบการเกิดข้อผิดพลาด (exceptions)
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # เชื่อมต่อกับ MySQL database ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลตารางแมว โดยใช้คลาส DictCursor เพื่อดึงข้อมูลตารางแมวทั้งหมดออกมา เพื่อลบ ในฐานข้อมูล 
                cursor.execute("DELETE FROM cats_table WHERE cat_index = %s", (cat_index,))
                mysql.connection.commit() # ทำการ commit อัพเดตฐานข้อมูลสำเร็จ 

                cursor.execute("SET @count = 0") # รีเซ็ตค่า cat_index ให้เริ่มต้นที่ 1 ใหม่ เตรียมการนับลำดับใหม่ของแถวที่จะถูกอัปเดต
                cursor.execute("UPDATE cats_table SET cat_index = @count:= @count + 1") # ระบุ index ของแมวที่ต้องการลบ
                cursor.execute("ALTER TABLE cats_table AUTO_INCREMENT = 1") # หลังจากลบข้อมูลแมว จะมีรีเซ็ตค่า index ให้เริ่มต้นที่ 1 ใหม่
                mysql.connection.commit() # ทำการ commit อัพเดตฐานข้อมูลสำเร็จ 
                cursor.close()  # ปิด cursor เพื่อทำการจบการทำงานในบล็อก try
        
                return redirect(url_for('lookcat_empty_table')) # เมื่อลบข้อมูลแมวเสร็จสิ้นให้ redirect ไปยังหน้าที่แสดงตารางแมวทั้งหมด
            except Exception as e: # หากมีข้อผิดพลาดในการดำเนินการลบข้อมูลหรือการเชื่อมต่อกับฐานข้อมูล จะคืนค่าเป็นข้อผิดพลาดที่เกิดขึ้น โดยใช้ str(e)
                return str(e) 
    else: # ถ้าไม่ได้เข้าสู่ระบบไม่มีสิทธิเข้าถึงหน้านี้ ให้ return ข้อความ "คุณไม่มีสิทธิเข้าถึงหน้านี้"
        return "คุณไม่มีสิทธิใช้งานหน้านี้" 
    
# กำหนดเส้นทาง URL ลบตารางแมวที่เชื่อมโยงฟังก์ชัน  edit_cat_tables โดยใช้เมทอด GET และ POST  
@app.route('/edit_cat_tables/<int:cat_index>', methods=['GET', 'POST'])
def edit_cat_tables(cat_index): # กำหนดฟังชัน edit_cat_tables โดยรับค่า cat_index ที่ส่งมา 
    if 'logged_in' in session and session['logged_in']: # ถ้าเงื่อนไขเป็นจริงตรวจสอบว่าผู้ใช้ได้ล็อกอินเข้าสู่ระบบหรือไม่ โดยดูจากค่า 'logged_in' ใน session object
        if request.method == 'POST': #ตรวจสอบว่าเมธอดการร้องขอเป็น POST หรือไม่ ถ้าเป็น POST แสดงว่าผู้ใช้ได้ส่่งฟอร์ม แก้ไขตารางแมวแล้ว
            # รับข้อมูลจากแก้ไขตารางแมว request form แบบฟอร์ม ส่วนค่า get.status รับ select ที่เลือกจากฟอร์ม
            editcat_name = request.form['cat_name']
            editbreed = request.form['breed']
            editage = request.form['age']
            editcolor = request.form['color']
            editstatus = request.form.get('status') 
            editdate = request.form['date']
            
            # ตรวจสอบว่าข้อมูลที่รับมาไม่เป็นค่าว่าง ถ้าเงื่อนไขเป็นจริง ถ้าเป็นค่าว่างจะ Retuen ข้อมความไปยังผู้ใช้
            if not editcat_name or not editbreed or not editcolor or not editstatus:  # not ถ้าเป็น สตริง ว่าง จะประเมินเป็น True , or not ตรวจสอบว่าเงื่อนไขใดป็นจริง หรือไม่  
                return "กรุณากรอกข้อมูลให้ครบถ้วน"

            # แปลงข้อมูลวันที่ที่รับมาจากฟอร์มให้เป็นรูปแบบของวันที่โดยใช้ฟังก์ชัน strptime และรูปแบบ '%Y-%m-%d' 
            try: # บล็อกตรวจสอบการเกิดข้อผิดพลาด (exceptions) 
                editdate = datetime.strptime(editdate, '%Y-%m-%d').date()
            except ValueError: #ยกเว้นค่าที่ผิดพลาด จะ Return ข้อความไปยังผู้ใช้
                return "กรุณากรอกวันเกิดแมว"

            # ตรวจสอบข้อมูลที่ได้รับแล้วทำการแก้ไขในฐานข้อมูล
            try: # บล็อกตรวจสอบการเกิดข้อผิดพลาด (exceptions) 
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # เชื่อมต่อกับ MySQL database ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลตารางแมว โดยใช้คลาส DictCursor เพื่อดึงข้อมูลตารางแมวทั้งหมดออกมา เพื่ออัพเดตและแก้ไข ในฐานข้อมูล 
                cursor.execute("UPDATE cats_table SET cat_name=%s, cat_breed=%s, cat_age=%s, cat_color=%s, cat_status=%s, cat_date=%s WHERE cat_index=%s", (editcat_name, editbreed, editage, editcolor, editstatus, editdate, cat_index,))  # ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลแก้ไขตารางแมว %s ยึดตำแหน่งเป็นพารามิเตอร์
                mysql.connection.commit() # ทำการ commit อัพเดตฐานข้อมูลสำเร็จ
                cursor.close() # ปิด cursor เพื่อจบการทำงานในบล็อค try

                # หลังจากแก้ไขข้อมูลสำเร็จ ให้ redirect กลับไปยังหน้าที่แสดงข้อมูลทั้งหมด
                return redirect(url_for('lookcat_empty_table'))
            except Exception as e: # ถ้าเกิดข้อผิดพลาดในการทำงานในบล็อก try
                return str(e) # แสดงข้อความผิดพลาด ในกรณีที่เกิดข้อผิดพลาดในการทำงานในบล็อก try

        try: # บล็อกตรวจสอบการเกิดข้อผิดพลาด (exceptions)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM cats_table WHERE cat_index = %s", (cat_index,))  # สั่ง SQL execute เพื่อดึงข้อมูลทั้งหมดจากตาราง 'cats_Table' ในฐานข้อมูล โดยรับจาก พารามิเตอร์ cat_index
            cat = cursor.fetchone() # ดึงข้อมูลแมวที่เก็บไว้ในตาราง 'cats_Table' ออกมา และเก็บไว้ในตัวแปร cats
            cursor.close() # ปิด cursor เพื่อทำการจบการทำงานในบล็อก try 
            return render_template('edit_cat_tables.html', cat=cat) # ถ้าเป็น GET request ให้ดึงข้อมูลแมวจากฐานข้อมูลและแสดงในฟอร์มแก้ไขแมว
        except Exception as e: # หากมีข้อผิดพลาดในการดำเนินการลบข้อมูลหรือการเชื่อมต่อกับฐานข้อมูล จะคืนค่าเป็นข้อผิดพลาดที่เกิดขึ้น โดยใช้ str(e)
            return str(e) 
    else: # ถ้าไม่ได้เข้าสู่ระบบไม่มีสิทธิเข้าถึงหน้านี้ ให้ return ข้อความ "คุณไม่มีสิทธิเข้าถึงหน้านี้"
        return "คุณไม่มีสิทธิใช้งานปุ่มนี้"

PeopleTable_entries = [] #  กำหนดให้ PeopleTable_entries เป็นลิสต์ว่างเพื่อใช้ในการเก็บข้อมูลบุคคลจากฐานข้อมูล

# กำหนดเส้นทาง URL หน้าฟอร์มตารางข้อมูลที่เชื่อมโยงฟังก์ชัน  contact_information โดยใช้เมทอด GET และ POST  
@app.route('/contact_information', methods=['GET', 'POST'])
def contact_information(): # ประกาศฟังก์ชันชื่อ contact_information เพื่อใช้ในการแสดงหน้า contact_information
        return render_template('contact_information.html') # ทำการส่งคืนค่าหน้าแบบฟอร์มเทมเพลต contact_information

# กำหนดเส้นทาง URL หน้าตารางข้อมูลติดต่อแขกที่เชื่อมโยงฟังก์ชัน  contact_table โดยใช้เมทอด POST      
@app.route('/contact_table', methods=['GET', 'POST'])
def contact_table(): # ประกาศฟังก์ชันชื่อ contact_table เพื่อใช้ในการแสดงหน้า contact_table
    if request.method == 'POST': #ตรวจสอบว่าเมธอดการร้องขอเป็น POST หรือไม่ ถ้าเป็น POST จะแสดงตาราง ผู้ใช้ทั่วไป
        # รับข้อมูลจาก request form 
        name = request.form['name']
        age = request.form['age']
        sex = request.form['sex']
        email = request.form['email']
        phonenumber = request.form['phonenumber']
        facebook = request.form['facebook']
        
        # ตรวจสอบว่าอายุที่รับมาไม่เป็นค่าว่าง ถ้าเงื่อนไขเป็นจริง ถ้าเป็นค่าว่างจะ Retuen ข้อความไปยังผู้ใช้
        if not name or not age or not sex or not email or not phonenumber or not facebook: # not ถ้าเป็น สตริง ว่าง จะประเมินเป็น True , or not ตรวจสอบว่าเงื่อนไขใดป็นจริง หรือไม่  ถ้า ไม่จะ Return ข้อความยังผู้ใช้
            return "กรุณากรอกข้อมูลให้ครบถ้วน"
            
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # เชื่อมต่อกับ MySQL database ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลตารางติดต่อแอดมิน 
        cursor.execute("INSERT INTO save_to_system_admin (name, age, sex, email, phonenumber, facebook) VALUES (%s, %s, %s, %s, %s, %s)", (name, age, sex, email, phonenumber, facebook))  # สร้างคำสั่ง SQL เพื่อเพิ่มข้อมูลลงในตาราง สั่ง execute query เพื่อเพิ่มข้อมูลที่รับมาจากฟอร์มลงในตาราง
        mysql.connection.commit() # ทำการ commit การเปลี่ยนแปลงข้อมูล
        cursor.close() # ปิด cursor
        
        return redirect(url_for('contact_table')) # หลังจากเพิ่มข้อมูลเสร็จสามารถ redirect กลับไปที่หน้า contact_table ได้
    else:  # ถ้าเงื่อนไขไม่เป็นจริง จะแสดงแบบฟอร์มข้อมูล ของ ผู้ใช้ทั่วไป
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # เชื่อมต่อกับ MySQL database ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลตารางแขก 
        cursor.execute("SELECT * FROM save_to_system_admin") # สั่ง SQL เพื่อดึงข้อมูลทั้งหมดจากตาราง 'save_to_system_admin'
        PeopleTable_entries = cursor.fetchall() # ดึงข้อมูลบุคคลทั้งหมดออกมา
        cursor.close() # ปิด cursor

        return render_template('contact_table.html', PeopleTable_entries=PeopleTable_entries) # ส่งคืนค่าหน้า contact_table

# กำหนดเส้นทาง URL ตารางข้อมูลติดต่อที่เชื่อมโยงฟังก์ชัน  save_to_system_admin โดยใช้เมทอด GET และ POST      
@app.route('/save_to_system_admin', methods=['GET', 'POST'])
def save_to_system_admin(): #ประกาศฟังชัน save_to_system_admin เพื่อใช้ในการแสดงหน้า save_to_system_admin
    if 'logged_in' in session and session['logged_in']: # ถ้าเงื่อนไขเป็นจริงตรวจสอบว่าผู้ใช้ได้ล็อกอินเข้าสู่ระบบหรือไม่ โดยดูจากค่า 'logged_in' ใน session object
        if request.method == 'POST': #ตรวจสอบว่าเมธอดการร้องขอเป็น POST หรือไม่ ถ้าเป็น POST จะแสดงตาราง แอดมิน
            # รับข้อมูลจาก request form 
            name = request.form['name']
            age = request.form['age']
            sex = request.form['sex']
            email = request.form['email']
            phonenumber = request.form['phonenumber']
            facebook = request.form['facebook']
            
            # ตรวจสอบว่าข้อมูลที่ส่งมาครบถ้วนหรือไม่ ถ้าเงื่อนไขเป็นจริง ถ้าเป็นค่าว่างจะ Retuen ข้อความไปยังผู้ใช้
            if not name or not age or not sex or not email or not phonenumber or not facebook:  # not ถ้าเป็น สตริง ว่าง จะประเมินเป็น True , or not ตรวจสอบว่าเงื่อนไขใดป็นจริง หรือไม่  
                return "กรุณากรอกข้อมูลให้ครบถ้วน"
                
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # เชื่อมต่อกับ MySQL database ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลตารางติดต่อแอดมิน 
            cursor.execute("INSERT INTO save_to_system_admin (name, age, sex, email, phonenumber, facebook) VALUES (%s, %s, %s, %s, %s, %s)", (name, age, sex, email, phonenumber, facebook))  #ดึงข้อมูลตารางบันทึกติดต่อแอดมินจากฐานข้อมูล ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลตารางติดต่อ  สั่ง execute query เพื่อเพิ่มข้อมูลที่รับมาจากฟอร์มลงในตาราง
            mysql.connection.commit() # ทำการ commit อัพเดตฐานข้อมูลสำเร็จ
            cursor.close() # ปิด cursor เพื่อทำการจบการทำงานในบล็อก try 
            
        # Read data from the database to display whenever the page is loaded
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # เชื่อมต่อกับ MySQL database ซึ่งเป็นฐานข้อมูลที่ใช้เก็บข้อมูลตารางติดต่อแอดมิน 
        cursor.execute("SELECT * FROM save_to_system_admin") # สั่ง SQL เพื่อดึงข้อมูลทั้งหมดจากตาราง 'PeopleTable_entries' ในฐานข้อมูล 
        PeopleTable_entries = cursor.fetchall() # ดึงข้อมูลบุคคลงที่เก็บไว้ในตาราง 'PeopleTable_entries' ออกมา และเก็บไว้ในตัวแปร PeopleTable_entries
        cursor.close() # ปิด cursor เพื่อทำการจบการทำงานในบล็อก try
            
        return render_template('save_to_system_admin.html', PeopleTable_entries=PeopleTable_entries) # ส่งไปยังเทมเพลต save_to_system_admin.html และแสดงตารางข้อมูลบุคคลที่เก็บไว้ในตาราง
    else: # กรณีผู้ใช้ไม่ได้ล็อกอินเข้าสู่ระบบ ฟังก์ชันจะคืนค่าเป็นข้อความที่บอกว่าผู้ใช้ไม่มีสิทธิ์ในการเข้าถึงหน้านี้:
        return "คุณไม่มีสิทธิใช้งานหน้านี้"

#กำหนดเส้นทาง URL delete_contact_entry ที่สามารถรับคำขอ HTTP แบบ POST ได้ โดย index จะเป็นพารามิเตอร์ที่ระบุลำดับของรายการที่ต้องการลบ
@app.route('/delete_contact_entry/<int:index>', methods=['POST'])
def delete_contact_entry(index):# กำหนดฟังชัน delete_contact_entry โดยรับค่า index ที่ส่งมา ลบ
    if request.method == 'POST': #ตรวจสอบว่าเมธอดการร้องขอเป็น POST หรือไม่ ถ้าเป็น POST แสดงว่าผู้ใช้ได้ลบหน้าตาราง
        if 'logged_in' in session and session['logged_in']:  # ถ้าเงื่อนไขเป็นจริงตรวจสอบว่าผู้ใช้ได้ล็อกอินเข้าสู่ระบบหรือไม่ โดยดูจากค่า 'logged_in' ใน session object
            try: # บล็อกตรวจสอบการเกิดข้อผิดพลาด (exceptions)
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # เชื่อมต่อกับ MySQL database ซึ่งเป็นฐานข้อมูลที่ลบเก็บข้อมูลตาราง โดยใช้คลาส DictCursor เพื่อดึงข้อมูลตารางทั้งหมดออกมา เพื่อลบในฐานข้อมูล 
                cursor.execute("SELECT * FROM save_to_system_admin") # สั่ง SQL เพื่อดึงข้อมูลทั้งหมดจากตาราง 'PeopleTable_entries' ในฐานข้อมูล  
                PeopleTable_entries = cursor.fetchall() # ดึงข้อมูลทั้งหมดออกมา และเก็บไว้ในตัวแปร PeopleTable_entries

                # ถ้าตรวจสอบว่า index อยู่ในช่วงของรายการที่มีอยู่หรือไม่
                if 0 <= index < len(PeopleTable_entries):
                    # ดึง ID ผู้ติดต่อของรายการที่จะลบ
                    contact_id = PeopleTable_entries[index]['id']

                    # ลบรายการออกจากฐานข้อมูลตาม index ที่ระบุ
                    cursor.execute("DELETE FROM save_to_system_admin WHERE id = %s", (contact_id,))
                    mysql.connection.commit() # ทำการ commit อัพเดตฐานลบข้อมูลสำเร็จ

                    # ปิด cursor เพื่อทำการจบการทำงานในบล็อก try 
                    cursor.close()

                    return redirect(url_for('save_to_system_admin'))  # เมื่อลบข้อมูลบุคคลเสร็จสิ้นให้ redirect ไปยังหน้าที่แสดงตารางติดต่อข้อมูล
            except Exception as e: # หากมีข้อผิดพลาดในการดำเนินการลบข้อมูลหรือการเชื่อมต่อกับฐานข้อมูล จะคืนค่าเป็นข้อผิดพลาดที่เกิดขึ้น โดยใช้ str(e)
                return str(e)
        else: # กรณีผู้ใช้ไม่ได้ล็อกอินเข้าสู่ระบบ ฟังก์ชันจะคืนค่าเป็นข้อความที่บอกว่าผู้ใช้ไม่มีสิทธิ์ในการเข้าถึงหน้านี้:
            return "คุณไม่มีสิทธิเข้าถึงปุ่มลบนี้"

#กำหนดเส้นทาง URL edit_contact_entry ที่สามารถรับคำขอ HTTP แบบ GET และ POSTได้ โดย index จะเป็นพารามิเตอร์ที่ระบุลำดับของรายการที่ต้องกาแก้ไข
@app.route('/edit_contact_entry/<int:index>', methods=['GET', 'POST'])
def edit_contact_entry(index): # กำหนดฟังชัน delete_contact_entry โดยรับค่า index ที่ส่งมา แก้ไข
    if 'logged_in' in session and session['logged_in']:
        if request.method == 'POST': #ตรวจสอบว่าเมธอดการร้องขอเป็น POST หรือไม่ ถ้าเป็น POST แสดงว่าผู้ใช้ได้แก้ไขแถวหน้าตาราง
            # ดึงข้อมูลการติดต่อที่แก้ไขแล้วจากแบบฟอร์ม
            name = request.form['name']
            age = request.form['age']
            sex = request.form['sex']
            email = request.form['email']
            phonenumber = request.form['phonenumber']
            facebook = request.form['facebook']
            
            # ตรวจสอบว่าอายุเป็นค่าว่างหรือไม่ ถ้าเงื่อนไขเป็นจริง ถ้าเป็นค่าว่างจะ Retuen ข้อความไปยังผู้ใช้
            if not age:  
                return "กรุณากรอกอายุตัวเอง"

            try: # บล็อกตรวจสอบการเกิดข้อผิดพลาด (exceptions)
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # เชื่อมต่อกับ MySQL database ซึ่งเป็นฐานข้อมูลที่แก้ไขเก็บข้อมูลตาราง โดยใช้คลาส DictCursor เพื่อดึงข้อมูลตารางทั้งหมดออกมา เพื่อแก้ไขในฐานข้อมูล 
                cursor.execute("SELECT * FROM save_to_system_admin") # สั่ง SQL เพื่อดึงข้อมูลทั้งหมดจากตาราง 'PeopleTable_entries' ในฐานข้อมูล 
                PeopleTable_entries = cursor.fetchall() # ดึงข้อมูลบุคคลงที่เก็บไว้ในตาราง 'PeopleTable_entries' ออกมา และเก็บไว้ในตัวแปร PeopleTable_entries

                # ถ้าตรวจสอบว่า index อยู่ในช่วงของรายการที่มีอยู่หรือไม่
                if 0 <= index < len(PeopleTable_entries):
                    # อัปเดตข้อมูลการติดต่อในฐานข้อมูลตาม index 
                    cursor.execute("""
                        UPDATE save_to_system_admin
                        SET name = %s, age = %s, sex = %s, email = %s, phonenumber = %s, facebook = %s
                        WHERE id = %s
                        """, (name, age, sex, email, phonenumber, facebook, PeopleTable_entries[index]['id']))
                    mysql.connection.commit() # ทำการ commit อัพเดตฐานข้อมูลสำเร็จ
                    cursor.close() # ปิด cursor เพื่อทำการจบการทำงานในบล็อก try

                    # เมื่อแก้ไขข้อมูลบุคคลเสร็จสิ้นให้ redirect ไปยังหน้าที่แสดงตารางติดต่อข้อมูล
                    return redirect(url_for('save_to_system_admin'))
                else:
                    # หากค่า index ที่ระบุไม่ถูกต้องหรือไม่มีอยู่ในรายการของข้อมูลที่ใช้อ้างอิงแก้ไข
                    return "ไม่พบรายการที่ต้องการแก้ไข"
            except Exception as e: # หากมีข้อผิดพลาดในการดำเนินการแก้ข้อมูลตารางหรือการเชื่อมต่อกับฐานข้อมูล จะคืนค่าเป็นข้อผิดพลาดที่เกิดขึ้น โดยใช้ str(e)
                return str(e)
        else: # เริ่มต้นโดยตรวจสอบว่าการร้องขอเป็น GET method หรือไม่
            # หากเป็น GET method จะเริ่มดำเนินการโดยการเชื่อมต่อกับฐานข้อมูลและดึงข้อมูลทั้งหมดจากตาราง "save_to_system_admin"
            try: # บล็อกตรวจสอบการเกิดข้อผิดพลาด (exceptions)
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT * FROM save_to_system_admin") # สั่ง SQL เพื่อดึงข้อมูลทั้งหมดจากตาราง 'PeopleTable_entries' ในฐานข้อมูล 
                PeopleTable_entries = cursor.fetchall() # ดึงข้อมูลบุคคลงที่เก็บไว้ในตาราง 'PeopleTable_entries' ออกมา และเก็บไว้ในตัวแปร PeopleTable_entries
                cursor.close() # ปิด cursor เพื่อทำการจบการทำงานในบล็อก try
            except Exception as e: # หากมีข้อผิดพลาดในการดำเนินการแก้ข้อมูลตารางหรือการเชื่อมต่อกับฐานข้อมูล จะคืนค่าเป็นข้อผิดพลาดที่เกิดขึ้น โดยใช้ str(e)
                return str(e)
            return render_template('edit_contact_entry.html', index=index, entry=PeopleTable_entries[index]) # จะแสดงผลข้อมูลของบุคคลที่ต้องการแก้ไขโดยใช้ข้อมูลจาก PeopleTable_entries[index] ซึ่งจะถูกส่งไปในรูปแบบของตัวแปร entry พร้อมด้วย index ที่ระบุถึงลำดับของข้อมูลที่ต้องการแก้ไขในตาราง
    else: # กรณีผู้ใช้ไม่ได้ล็อกอินเข้าสู่ระบบ ฟังก์ชันจะคืนค่าเป็นข้อความที่บอกว่าผู้ใช้ไม่มีสิทธิ์ในการเข้าถึงหน้านี้:
        return "คุณไม่มีสิทธิเข้าถึงปุ่มแก้ไขนี้"

# เชื่อมต่ออีเมล์
app.config['MAIL_SERVER'] = 'smtp.gmail.com' # กำหนดเซิร์ฟเวอร์ SMTP ของ Gmail เป็น 'smtp.gmail.com' เนื่องจากเราใช้ Gmail SMTP server.
app.config['MAIL_PORT'] = 465 # กำหนดพอร์ตสำหรับการเชื่อมต่อ SMTP เป็น 465 ที่ใช้สำหรับการเชื่อมต่อแบบ SSL
app.config['MAIL_USERNAME'] = 'tiger20002543@gmail.com' # กำหนดชื่อผู้ใช้และรหัสผ่านของบัญชี Gmail ที่จะใช้สำหรับการเชื่อมต่อ SMTP.
app.config['MAIL_PASSWORD'] = 'jvdc dqny rezy abqi' # กำหนดให้ใช้ SSL ในการเชื่อมต่อเพื่อความปลอดภัย.
app.config['MAIL_USE_TLS'] = False # Transport Layer Security (TLS) เพื่อการเชื่อมต่อ SMTP server ของ Gmail ในการส่งอีเมล์
app.config['MAIL_USE_SSL'] = True # Secure Sockets Layer (SSL) เพื่อการเชื่อมต่อ SMTP server ของ Gmail เป็นโปรโตคอลที่ช่วยในการเข้ารหัสข้อมูลที่ถูกส่งผ่านเครือข่ายอินเทอร์เน็ต

mail = Mail(app) # ประกาศฟังก์ชันเชื่อมต่อฐานอีเมล ในตัวแปร mail ที่มีค่าเป็น app 

#กำหนดเส้นทาง URL Contact ที่สามารถรับคำขอ HTTP แบบ GET และ POSTได้ 
@app.route('/Contact', methods=['GET', 'POST'])
def contact_page(): # กำหนดฟังชัน contact_page โดยรับค่า index ที่ส่งมา แก้ไข
    return render_template('contact.html') # คืนค่าจากฟังก์ชัน contact_page() โดยใช้ render_template

# กำหนดเส้นทาง URL ส่งอีเมล์ติดต่อที่เชื่อมโยงฟังก์ชัน  send_email โดยใช้เมทอด POST   
@app.route("/send_email", methods=['POST']) 
def send_email(): #กำหนดฟังก์ชัน send_email
    # รับข้อมูลจากแบบฟอร์มส่งอีเมล์
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # ตรวจสอบว่าข้อมูลว่าไม่ว่างเปล่า ถ้าเงื่อนไขเป็นจริง ถ้าเป็นค่าว่างจะ Retuen ข้อความไปยังผู้ใช้
    if not name or not email or not message: # not ถ้าเป็น สตริง ว่าง จะประเมินเป็น True , or not ตรวจสอบว่าเงื่อนไขใดป็นจริง หรือไม่  
        return "กรุณากรอกข้อมูลให้ครบถ้วน"

    # สร้างวัตถุข้อความ
    msg = Message(
        'Hello',  # กำหนดหัวข้ออีเมล์
        sender='yourId@gmail.com',  # กำหนดอีเมล์ผู้ส่ง
        recipients=["tiger20002543@gmail.com"] # กำหนดอีเมล์ผู้รับ
    ) 
    msg.body = f'Hello, you have a message from {name} ({email}):\n\n{message}'  # กำหนดเนื้อหาของอีเมลโดยใช้ข้อมูลที่รับมาจากฟอร์ม 

    # ส่งอีเมลโดยใช้วัตถุ msg ที่สร้างไว้ก่อนหน้านี้
    mail.send(msg) 

    # บันทึกข้อมูลการติดต่อไปยังฐานข้อมูล MySQL
    try: # บล็อกสำหรับจัดการข้อผิดพลาดที่อาจเกิดขึ้นในกระบวนการบันทึกข้อมูล
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # เชื่อมต่อกับฐานข้อมูล MySQL โดยใช้คลาส DictCursor ซึ่งจะทำให้ได้ผลลัพธ์ในรูปแบบ dictionary เพื่อดึงข้อมูลจากตารางที่เก็บข้อมูลการติดต่อออกมา
        cursor.execute("INSERT INTO contact_info (name, email, message) VALUES (%s, %s, %s)", (name, email, message)) #  สั่ง execute query เพื่อเพิ่มข้อมูลที่รับมาจากฟอร์มลงในตาราง
        mysql.connection.commit() # ทำการ commit ข้อมูลลงในฐานข้อมูล
        cursor.close() # ปิด cursor เมื่อเสร็จสิ้นการทำงานกับฐานข้อมูล
    except Exception as e:  # หากมีข้อผิดพลาดในการดำเนินการแก้ข้อมูลตารางหรือการเชื่อมต่อกับฐานข้อมูล จะคืนค่าเป็นข้อผิดพลาดที่เกิดขึ้น โดยใช้ str(e)
        return str(e)

    # redirect ไปยังหน้า home เมื่อเรียกใช้ ฟังก์ชัน send email ทำงานเสร็จสิ้น
    return redirect(url_for('home'))

# เรียกใช้แอปพลิเคชัน Flask
if __name__ == '__main__': # เงื่อนไขนี้จะตรวจสอบว่าสคริปต์กำลังดำเนินการโดยตรงหรือไม่ 
app.run(debug=True, host='0.0.0.0' , port=5000) # เริ่มต้นเซิร์ฟเวอร์การพัฒนา Flask เมื่อสคริปต์ทำงานโดยตรง เซิร์ฟเวอร์การพัฒนาในตัวของ Flask รับฟังคำขอเข้าบนโฮสต์ที่ระบุและพอร์ต  อาร์กิวเมนต์debug=True เปิดใช้งานโหมดดีบักซึ่งมีข้อความแสดงข้อผิดพลาด

