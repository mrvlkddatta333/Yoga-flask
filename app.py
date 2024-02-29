from flask import Flask,render_template,redirect,url_for,request,flash,session
from flask_session import Session
app=Flask(__name__)  #it shows the current module path
import mysql.connector
import mysql.connector.pooling
import os

conn=mysql.connector.pooling.MySQLConnectionPool(host=host,user=user,password=password,db=db,pool_name='DED',pool_size=25, pool_reset_session=True)


app.secret_key='guruji'
app.config['SESSION_TYPE']='filesystem'
Session(app)
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/register',methods=['Get','POST'])
def register():
    if request.method=='POST':
        fname=request.form['fname']
        lname=request.form['lname']
        email=request.form['email']
        password=request.form['password']
        cpassword=request.form['cpassword']
        phone=request.form['phone']
        img=request.files['image']
        print(img)
        filename=img.filename
        print(filename)
        path=os.path.dirname(os.path.abspath(__file__))
        static_path=os.path.join(path,'static')
        img.save(os.path.join(static_path,filename))

        try:
            mydb=conn.get_connection()
            cursor = mydb.cursor(buffered=True)
            cursor.execute('select count(*) from register where first_name=%s',[fname])
            count=cursor.fetchone()[0]
            print(count)
            if count==1:
                raise Exception
        except Exception as e:
            flash('user already existed')
            return redirect(url_for('home'))
        finally:
            if mydb.is_connected():
                mydb.close()
        else:
            try:
                mydb=conn.get_connection()
                cursor = mydb.cursor(buffered=True)
                cursor.execute('insert into register(first_name,last_name,phone,email,password,img) values(%s,%s,%s,%s,%s,%s)',[fname,lname,phone,email,password,filename])
                mydb.commit()
                cursor.close()
            except Exception as e:
                print(e)
            finally:
                if mydb.is_connected():
                    mydb.close()
            flash('Your Details has registered successfully')
            return redirect(url_for('home'))
    return redirect(url_for('home'))
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        print(username)
        try:
            mydb=conn.get_connection()
            cursor = mydb.cursor(buffered=True)
            cursor.execute('select count(*) from register where email=%s and password=%s',[username,password])
            count=cursor.fetchone()[0]
            cursor.close()
            print(count)
            if count==0:
                raise Exception
        except Exception as e:
            flash('username or password was incorrect')
            return redirect(url_for('login'))
        finally:
            if mydb.is_connected():
                mydb.close()
        else:
            session['user']=username
            if not session.get(username):
                session[username]={}
            return redirect(url_for('home'))
    return redirect(url_for('home'))
@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('home'))
    return redirect(url_for('home'))
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/gurus')
def gurus():
    try:
        mydb=conn.get_connection()
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select * from register')
        users=cursor.fetchall()
        cursor.close()
    except Exception as e:
        print(e)
    finally:
            if mydb.is_connected():
                mydb.close()
    return render_template('gurus.html',users=users)
@app.route('/guru/<user>')
def guru(user):
    try:
        mydb=conn.get_connection()
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select first_name,last_name,phone,img,description from register where email=%s',[user])
        data=cursor.fetchone()
        cursor.close()
    except Exception as e:
        print(e)
    finally:
            if mydb.is_connected():
                mydb.close()
    return render_template('guru.html',data=data)
@app.route('/contactus',methods=['GET','POST'])
def contactus():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        msg=request.form['msg']
        try:
            mydb=conn.get_connection()
            cursor = mydb.cursor(buffered=True)
            cursor.execute('insert into contact(name,email,message) values(%s,%s,%s)',[name,email,msg])
            mydb.commit()
            cursor.close()
        except Exception as e:
            print(e)
        finally:
            if mydb.is_connected():
                mydb.close()
        return redirect(url_for('home'))
    return render_template('contact.html')
@app.route('/profile',methods=['GET','POST'])
def profile():
    try:
        mydb=conn.get_connection()
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select first_name,last_name,phone,img,description from register where email=%s',[session.get('user')])
        count=cursor.fetchone()
        cursor.close()
    except Exception as e:
        print(e)
    finally:
            if mydb.is_connected():
                mydb.close()
    if request.method=='POST':
        fname=request.form['fname']
        lname=request.form['lname']
        phone=request.form['phone']
        des=request.form['editordata']
        print(fname,lname,phone)
        try:
            mydb=conn.get_connection()
            cursor = mydb.cursor(buffered=True)
            cursor.execute('update register set first_name=%s,last_name=%s,phone=%s,description=%s where email=%s',[fname,lname,phone,des,session.get('user')])
            mydb.commit()
            cursor.close()
        except Exception as e:
            print(e)
        finally:
            if mydb.is_connected():
                mydb.close()
        return redirect(url_for('profile'))
    return render_template('profile.html',count=count)
@app.route('/admin')
def admin():
    try:
        mydb=conn.get_connection()
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select * from register')
        users=cursor.fetchall()
        cursor.close()
    except Exception as e:
        print(e)
    finally:
        if mydb.is_connected():
            mydb.close()
    return render_template('admindashboard.html',users=users)
@app.route('/upadte/<name>',methods=['GET','POST'])
def update(name):
    try:
        mydb=conn.get_connection()
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select first_name,last_name,phone,img,description from register where first_name=%s',[name])
        count=cursor.fetchone()
    except Exception as e:
        print(e)
    finally:
            if mydb.is_connected():
                mydb.close()
    print(count)
    if request.method=='POST':
        fname=request.form['fname']
        lname=request.form['lname']
        phone=request.form['phone']
        des=request.form['editordata']
        print(fname,lname,phone)
        try:
            mydb=conn.get_connection()
            cursor = mydb.cursor(buffered=True)
            cursor.execute('update register set first_name=%s,last_name=%s,phone=%s,description=%s where first_name=%s',[fname,lname,phone,des,name])
            mydb.commit()
            cursor.close()
        except Exception as e:
            print(e)
        finally:
            if mydb.is_connected():
                mydb.close()
        return redirect(url_for('update',name=name))
    return render_template('profile.html',count=count)
@app.route('/delete/<name>')
def delete(name):
    try:
        mydb=conn.get_connection()
        cursor = mydb.cursor(buffered=True)
        cursor.execute('delete from register where first_name=%s',[name])
        mydb.commit()
        cursor.close()
    except Exception as e:
        print(e)
    finally:
            if mydb.is_connected():
                mydb.close()
    return redirect(url_for('admin'))
@app.route('/adminregister',methods=['Get','POST'])
def adminregister():
    if request.method=='POST':
        fname=request.form['fname']
        lname=request.form['lname']
        email=request.form['email']
        password=request.form['password']
        cpassword=request.form['cpassword']
        phone=request.form['phone']
        img=request.files['image']
        filename='photo'+'.jpg'
        print(filename)
        path=os.path.dirname(os.path.abspath(__file__))
        static_path=os.path.join(path,'static')
        img.save(os.path.join(static_path,filename))

        try:
            mydb=conn.get_connection()
            cursor = mydb.cursor(buffered=True)
            cursor.execute('select count(*) from register where first_name=%s',[fname])
            count=cursor.fetchone()[0]
            cursor.close()
            print(count)
            if count==1:
                raise Exception
        except Exception as e:
            flash('user already existed')
            return redirect(url_for('admin'))
        else:
            mydb=conn.get_connection()
            cursor = mydb.cursor(buffered=True)
            cursor.execute('insert into register(first_name,last_name,phone,email,password,img) values(%s,%s,%s,%s,%s,%s)',[fname,lname,phone,email,password,filename])
            mydb.commit()
            cursor.close()
            flash('Your Details has registered successfully')
            return redirect(url_for('admin'))
        finally:
            if mydb.is_connected():
                mydb.close()
    return redirect(url_for('admin'))
app.run(debug=True)
