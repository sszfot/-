import pymysql
from jinja2 import Environment, FileSystemLoader
from flask import Flask, render_template, request, redirect, url_for
import os

# 连接数据库
connection = pymysql.connect(host='localhost', port=3306, user='root', password='123456', db='test', charset='utf8')

# 创建游标对象
cursor = connection.cursor()


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


# @app.route('/hightrain_ticket_trip_view/<string:userid>', methods=['GET','POST'])
# def sel(userid):

#     with connection.cursor() as cursor:
#         cursor.execute("SELECT * FROM hightrain_ticket_trip_view WHERE userid=%s", (userid,))
#         data = cursor.fetchall()
#         cursor.execute("SELECT * FROM hightrain WHERE userid=%s", (userid,))
#         user = cursor.fetchone()
#     return render_template('sel.html', data=data,user=user)

@app.route('/user', methods=['GET'])
def user():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()
    return render_template('user.html', users=users)
# @app.route('/user/add', methods=['GET', 'POST'])
# def add_user():
#     if request.method == 'POST':
#         phonenumber = request.form.get('phonenumber')
#         username = request.form.get('username')
#         userid = request.form.get('userid')
#         with connection.cursor() as cursor:
#             sql = "INSERT INTO user (phonenumber,username,userid) VALUES (%s,'%s','%s')" %(phonenumber,username,userid)

#             print(sql)

#             cursor.execute(sql)
#             connection.commit()
#         return redirect(url_for('user'))
#     else:
#         return render_template('add_user.html')
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        userid = request.form['userid']
        phonenumber = request.form['phonenumber']
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO user (username, userid, phonenumber) VALUES (%s, %s, %s)"
                cursor.execute(sql, (username, userid, phonenumber))
                connection.commit()
            return redirect(url_for('user'))
        except pymysql.Error as e:
            return str(e)
    else:
        return render_template('add_user.html')



@app.route('/user/edit/<int:userid>', methods=['GET', 'POST'])
def edit_user(userid):
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_phonenumber = request.form.get('phonenumber')
        
        # 检查数据完整性
        if not new_username or not new_phonenumber:
            return "错误：所有字段都是必填的！", 400

        try:
            with connection.cursor() as cursor:
                # 调用存储过程更新用户信息
                cursor.callproc('UpdateUser1', (userid, new_username, new_phonenumber))
                connection.commit()
        except pymysql.Error as e:
            connection.rollback()
            return f"更新失败，错误信息：{str(e)}"
        
        # 数据更新成功后重定向到用户列表页面
        return redirect(url_for('user'))
    else:
        # 如果是 GET 请求，从数据库获取当前用户的信息
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM user WHERE userid = %s", (userid,))
                user = cursor.fetchone()
        except pymysql.Error as e:
            return f"数据库查询失败，错误信息：{str(e)}"

        # 将用户数据传递给模板以显示
        if user:
            return render_template('edit_user.html', user=user)
        else:
            return "未找到指定用户！", 404

@app.route('/user/delete/<int:userid>')
def delete_user(userid):
    try:
        with connection.cursor() as cursor:
            cursor.execute("START TRANSACTION")
            cursor.execute("DELETE FROM user WHERE userid = %s", (userid,))
            cursor.execute("COMMIT")
    except Exception as e:
        connection.rollback()
    return redirect(url_for('user'))
@app.route('/user/update_phone/<int:userid>', methods=['POST'])
def update_user_phone(userid):
    new_phone_number = request.form['phonenumber']
    try:
        with connection.cursor() as cursor:
            cursor.callproc('UpdateUserPhoneNumber', (userid, new_phone_number))
            connection.commit()
    except pymysql.Error as e:
        return str(e)
    return redirect(url_for('user'))

#############################################################################################################3
@app.route('/station', methods=['GET'])
def station():

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM station")
        stations = cursor.fetchall()
    return render_template('station.html', stations=stations)
@app.route('/station/add', methods=['GET', 'POST'])
def add_station():
    if request.method == 'POST':
        stationid = request.form.get('stationid')
        stationname = request.form.get('stationname')
        address = request.form.get('address')

        try:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO station (stationid, stationname, address) VALUES (%s, %s, %s)",
                               (stationid, stationname, address))
                connection.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            connection.rollback()
            return render_template('add_station.html', error="Failed to add station.")
        return redirect(url_for('station'))
    else:
        return render_template('add_station.html')


@app.route('/station/edit/<int:stationid>', methods=['GET', 'POST'])
def edit_station(stationid):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM station WHERE stationid=%s", (stationid,))
        station = cursor.fetchone()

    if request.method == 'POST':
        stationid = request.form.get('stationid')
        stationname=request.form.get('stationname')
        address=request.form.get('address')
        with connection.cursor() as cursor:
            cursor.execute("UPDATE station WHERE stationid=%s",
                           (stationid,stationname,address))
            connection.commit()
        return redirect(url_for('station'))

    return render_template('edit_station.html', station=station)
@app.route('/station/delete/<int:stationid>')
def delete_station(stationid):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM station WHERE stationid=%s", (stationid,))
        connection.commit()
    return redirect(url_for('station'))


@app.route('/trip', methods=['GET'])
def trip():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM trip")
        trips = cursor.fetchall()
    return render_template('trip.html', trips=trips)

@app.route('/trip/add', methods=['GET', 'POST'])
def add_trip():
    if request.method == 'POST':
        tripid=request.form.get('tripid')
        startstation=request.form.get('startstation')
        endstation=request.form.get('endstation')
        starttime=request.form.get('starttime')
        endtime=request.form.get('endtime')
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO trip (tripid,startstation,endstation,starttime,endtime) VALUES (%s,%s,%s,%s,%s,%s)",
                           (tripid,startstation,endstation,starttime,endtime))
            connection.commit()
        return redirect(url_for('trip'))
    else:
        return render_template('add_trip.html')

@app.route('/trip/edit/<string:tripname>', methods=['GET', 'POST'])
def edit_trip(tripid):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM trip WHERE tripname=%s", (tripid,))
        trip = cursor.fetchone()
    if request.method == 'POST':
        x=tripid
        tripid = request.form.get('tripid')
        startstation=request.form.get('startstation')
        endstation=request.form.get('endstation')
        starttime=request.form.get('starttime')
        endtime=request.form.get('endtime')

        with connection.cursor() as cursor:
            cursor.execute("UPDATE trip SET tripid=%s, startstation=%s, endstation=%s, starttime=%s, endtime=%s,  WHERE tripid=%s",
                           (tripid,startstation,endstation,starttime,endtime,x))
            connection.commit()
        return redirect(url_for('trip'))

    return render_template('edit_trip.html', trip=trip)

@app.route('/trip/delete/<string:tripid>')
def delete_trip(tripid):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM trip WHERE tripid=%s", (tripid,))
    return redirect(url_for('trip'))

#############################################################################################
@app.route('/train', methods=['GET'])
def train():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM train")
        trains = cursor.fetchall()
    return render_template('train.html', trains=trains)
@app.route('/add_train', methods=['GET', 'POST'])
def add_train():
    if request.method == 'POST':
        trainid = request.form['trainid']
        type = request.form['type']
        maxspeed = request.form['maxspeed']

        # 插入数据库
        sql = "INSERT INTO train (trainid, type, maxspeed) VALUES (%s, %s, %s)"
        cursor.execute(sql, (trainid, type, maxspeed))
        connection.commit()
        
        return redirect(url_for('train'))  # 重定向到火车管理页面
    else:
        return render_template('add_train.html')
    
#@app.route('/delete_train/<int:trainid>', methods=['POST'])
#def delete_train(trainid):
#    try:
#        with connection.cursor() as cursor:
#            cursor.execute("DELETE FROM train WHERE trainid = %s", (trainid,))
#           connection.commit()
#    except Exception as e:
#       connection.rollback()
#        print(f"An error occurred: {e}")
#    return redirect(url_for('train'))
@app.route('/train/delete/<int:trainid>', methods=['POST'])
def delete_train(trainid):
    try:
        with connection.cursor() as cursor:
            cursor.execute("START TRANSACTION")
            # 删除该列车的所有票务信息
            cursor.execute("DELETE FROM ticket WHERE tripid IN (SELECT tripid FROM trip WHERE trainid = %s)", (trainid,))
            # 删除该列车的所有行程信息
            cursor.execute("DELETE FROM trip WHERE trainid = %s", (trainid,))
            # 删除列车信息
            cursor.execute("DELETE FROM train WHERE trainid = %s", (trainid,))
            cursor.execute("COMMIT")
    except Exception as e:
        print(f"发生错误: {e}")
        connection.rollback()
    return redirect(url_for('train'))

@app.route('/edit_train/<int:trainid>', methods=['GET', 'POST'])
def edit_train(trainid):
    if request.method == 'POST':
        type = request.form.get('type')
        maxspeed = request.form.get('maxspeed')

        if type and maxspeed:
            try:
                sql = "UPDATE train SET type=%s, maxspeed=%s WHERE trainid=%s"
                cursor.execute(sql, (type, maxspeed, trainid))
                connection.commit()
                return redirect(url_for('train'))
            except Exception as e:
                print(f"An error occurred: {e}")
                connection.rollback()
                return render_template('edit_train.html', error="Failed to update train.", trainid=trainid, type=type, maxspeed=maxspeed)
        else:
            return render_template('edit_train.html', error="All fields are required.", trainid=trainid, type=type, maxspeed=maxspeed)
    else:
        # Attempt to fetch the current train details
        cursor.execute("SELECT * FROM train WHERE trainid=%s", (trainid,))
        train = cursor.fetchone()
        if train:
            return render_template('edit_train.html', trainid=train.trainid, type=train.type, maxspeed=train.maxspeed)
        else:
            return redirect(url_for('train'))  # Redirect if no train found

# hightrain
@app.route('/train/hightrain', methods=['GET'])
def hightrain():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM `hightrain`")
        hightrains = cursor.fetchall()
    return render_template('hightrain.html', hightrains=hightrains)


@app.route('/hightrain/add', methods=['GET', 'POST'])
def add_hightrain():
    if request.method == 'POST':
       trainid=request.form.get('trainid')
       maxspeed=request.form.get('maxspeed')
       with connection.cursor() as cursor:
            cursor.execute("INSERT INTO `hightrain` (trainid,maxspeed) VALUES (%s,%s)",(trainid,))
            connection.commit()
       return redirect(url_for('hightrain'))
    else:
        return render_template('add_hightrain.html')

@app.route('/hightrain/edit/<string:trainid>', methods=['GET', 'POST'])
@app.route('/edit_hightrain/<int:trainid>', methods=['GET', 'POST'])
def edit_hightrain(trainid):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM `hightrain` WHERE trainid=%s", (trainid,))
        hightrain = cursor.fetchone()

    if request.method == 'POST':
        # 假设有其他字段需要更新，例如 train_type 和 max_speed
        type = request.form.get('type')
        maxspeed = request.form.get('maxspeed')

        with connection.cursor() as cursor:
            # 更新操作不应改变 userid，只更新其他字段
            cursor.execute("UPDATE `hightrain` SET type=%s, maxspeed=%s WHERE trainid=%s",
                           (type, maxspeed, trainid))
            connection.commit()
        return redirect(url_for('hightrain'))

    return render_template('edit_hightrain.html', hightrain=hightrain)


@app.route('/hightrain/delete/<string:userid>')
def delete_hightrain(userid):

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM `hightrain` WHERE userid=%s", userid)
        cursor.execute("DELETE FROM `user` WHERE userid=%s", userid)
        cursor.execute("DELETE FROM `trip` WHERE userid=%s", userid)
        cursor.execute("DELETE FROM `station` WHERE userid=%s", userid)
        connection.commit()
    return redirect(url_for('hightrain'))

# usualtrain

@app.route('/train/usualtrain', methods=['GET'])
def usualtrain():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM usualtrain")
        usualtrains = cursor.fetchall()
    return render_template('usualtrain.html', usualtrains=usualtrains)


@app.route('/usualtrain/add', methods=['GET', 'POST'])
def add_usualtrain():
    if request.method == 'POST':
        usualtrainnumber=request.form.get('usualtrainnumber')
       
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO usualtrain (usualtrainnumber) VALUES (%s)",
                           (usualtrainnumber))
            #cursor.callproc("AddToCart", (cart_id, user_id,product_id, quantity))
            connection.commit()
        return redirect(url_for('usualtrainnumber'))
    else:
        return render_template('add_usualtrain.html')

@app.route('/usualtrain/edit/<int:usualtrainnumber>', methods=['GET', 'POST'])
def edit_usualtrain(usualtrainnumber):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM usualtrain WHERE usualtrainnumber=%s", usualtrainnumber)
        usualtrain = cursor.fetchone()
    if request.method == 'POST':
        x=usualtrainnumber
        #p=cart[2]
        usualtrainnumber = request.form.get('usualtrainnumber')
       
        with connection.cursor() as cursor:
            cursor.execute("UPDATE `usualtrain` SET usualtrainnumber=%s,time=%s, location=%s, usualtrainscore=%s, ticketname=%s WHERE userid=%s",
                           (usualtrainnumber, x))
            connection.commit()
        return redirect(url_for('usualtrain'))
    return render_template('edit_usualtrain.html', usualtrain=usualtrain)

@app.route('/usualtrain/delete/<int:usualtrainnumber>', methods=['POST'])
def delete_usualtrain(usualtrainnumber):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM usualtrain WHERE usualtrainnumber=%s", usualtrainnumber)
        connection.commit()
    return redirect(url_for('usualtrain'))

@app.route('/ticket', methods=['GET'])
def ticket():

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM ticket")
        tickets = cursor.fetchall()
    return render_template('ticket.html', tickets=tickets)

@app.route('/ticket/add', methods=['GET', 'POST'])
def add_ticket():
    if request.method == 'POST':
        ticketid = request.form.get('ticketid')
        userid = request.form.get('userid')
        tripid = request.form.get('tripid')
        price = request.form.get('price')
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO ticket (ticketid,userid, tripid, price) VALUES (%s,%s,%s,%s)", (ticketid))
            connection.commit()
        return redirect(url_for('ticket'))
    else:
        return render_template('add_ticket.html')

@app.route('/ticket/edit/<string:ticketid>', methods=['GET', 'POST'])
def edit_ticket(ticketid):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM ticket WHERE ticketid=%s", ticketid)
        ticket = cursor.fetchone()
    if request.method == 'POST':
        x=ticket.id
        ticketid = request.form.get('ticketid')
        
        with connection.cursor() as cursor:
            cursor.execute("UPDATE payment SET ticketid=%s  WHERE ticketid=%s", (ticketid,x))
            connection.commit()
        return redirect(url_for('ticket'))
    return render_template('edit_ticket.html', ticket=ticket)

@app.route('/ticket/delete/&lt;string:ticketid&gt;', methods=['POST'])
def delete_ticket(ticketid):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM ticket WHERE ticketid=%s", ticketid)
        #cursor.execute("DELETE FROM usualtrain WHERE ticketname=%s", ticketname)
        #cursor.execute("DELETE FROM hightrain WHERE ticketname=%s", ticketname)
        connection.commit()
    return redirect(url_for('ticket'))

@app.route('/user/tickets')
def user_tickets():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM user_tickets_view")
            user_tickets_data = cursor.fetchall()
    except pymysql.Error as e:
        return f"数据库查询失败，错误信息：{str(e)}", 500

    return render_template('user_tickets.html', user_tickets=user_tickets_data)


if __name__ == '__main__':
    app.run(debug=True)


# 关闭游标和数据库连接
cursor.close()
connection.close()
