from flask import Flask, flash, redirect, render_template, request, url_for, session, abort
from server_backend_functions import *
import datetime
from sqlalchemy import create_engine
import os, json
from sqlalchemy.orm import sessionmaker
from tabledef import *
from sqlalchemy import desc

engine = create_engine('sqlite:///tutorial.db', echo=True)

app = Flask(__name__)

class Result(object):
    live_inst_list = ""
    live_floating_ip_list = ""
    live_floating_ip_id_list = ""

    # The class "constructor" - It's actually an initializer 
    def __init__(self, live_inst_list, live_floating_ip_list, live_floating_ip_id_list):
        self.live_inst_list = live_inst_list
        self.live_floating_ip_list = live_floating_ip_list
        self.live_floating_ip_id_list = live_floating_ip_id_list

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html')

@app.route('/status', methods=['GET','POST'])
def status():
    if request.method == 'POST':
        value=request.form['delete']

        # delete the cluster
        Session = sessionmaker(bind=engine)
        s = Session()
        query = s.query(Cluster).order_by(Cluster.id).all()

        live_inst_list={}
        live_ip_list={}
        live_ip_id_list={}
        for u in query:
            row=u.__dict__
            print row
            idx=row.values()[4]
            key='VM'+str(idx)
            print key
            live_ip_id_list[key]=row.values()[0]
            live_inst_list[key]=row.values()[1]
            live_ip_list[key]=row.values()[3]

        print live_inst_list
        print live_ip_list
        print live_ip_id_list

        s.query(Cluster).delete()
        s.commit()

        # perform_cluster_cleanup(True)
        return render_template('index.html')
    
    # inst_list = request.args.get('inst_list')
    # ip_list = request.args.get('ip_list')
    # ip_id_list = request.args.get('ip_id_list')
    statuslist = request.args.get('statuslist')
    # statuslist = statuslist.encode('utf-8')
    return render_template('status.html', statuslist=statuslist)

@app.route('/index', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        nodes=request.form['nodes']
        strvm=str(nodes)
        intvm=int(nodes)
        spec=request.form['spec']

        if int(spec) == 1:
            C='m1.medium'
        elif int(spec) == 2:
            C='m1.large'

        print('Number of nodes: '+strvm+' Cluster Specification: '+C)

        create_status,instances = create_cluster(2 + 1, "m1.large")

        if (create_status == False):
            print 'Sorry ! We could not create your cluster at this time\n'
            cleanup_status = perform_cluster_cleanup(True, live_inst_list, live_floating_ip_id_list, live_floating_ip_list)

        else:
            private_ip_dict = get_private_ips(live_inst_list)
            instances = map(lambda x:x+(private_ip_dict.get(x[0]),),instances)

            print "Following instances created :: "
            print instances


            print "Sleeping !! \n"
            time.sleep(60)
            print "Awake !! \n"

            create_ambari_cluster(instances)


        # result=create_cluster(intvm, C)

        live_inst_list = {'VM2': u'8119711c-a48a-425d-b13e-3357615eede0', 'VM1': u'9ab2fbd0-b12a-4269-8449-e8386ffab66d'}
        live_floating_ip_list =  {'VM2': u'10.23.2.187', 'VM1': u'10.23.2.186'} 
        live_floating_ip_id_list = {'VM2': u'8956a3fb-982e-4a67-a3e7-010aa6431860', 'VM1': u'f9993340-8f4d-4c42-92f5-d8fa09b30dc2'} 
        result = Result(live_inst_list, live_floating_ip_list, live_floating_ip_id_list)

        print result.live_inst_list
        print result.live_floating_ip_list
        print result.live_floating_ip_id_list

        Session = sessionmaker(bind=engine)
        s = Session()
        statuslist={}
        for index in range(len(result.live_inst_list)):
            x=result.live_inst_list.values()[index]
            y=result.live_floating_ip_list.values()[index]
            z=result.live_floating_ip_id_list.values()[index]
        # Add the cluster details to DB
            cluster = Cluster(x,y,z)
            statuslist[index]=[x,y,z]
            s.add(cluster)

        s.commit()    
        print statuslist
        # for key, value in result.live_inst_list.iteritems():
        #     print key, ' = ', result.live_inst_list[key]

        return redirect(url_for('.status', statuslist=statuslist))

    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        POST_USERNAME = str(request.form['username'])
        POST_PASSWORD = str(request.form['password'])
 
        Session = sessionmaker(bind=engine)
        s = Session()
        query = s.query(User).filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD]) )
        result = query.first()

        if result:
            session['logged_in'] = True
            user=POST_USERNAME
            return redirect(url_for('index'))
        else:
            error = 'Invalid Credentials. Please try again.'

    return render_template('login.html', error=error)

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return render_template('login.html')

# @app.route('/showSignUp')
# def showSignUp():
#     return render_template('signup.html')

# @app.route('/signUp',methods=['POST'])
# def signUp():
 
#     # read the posted values from the UI
#     _name = request.form['inputName']
#     _email = request.form['inputEmail']
#     _password = request.form['inputPassword']
 
#     # validate the received values
#     if _name and _email and _password:
#         return json.dumps({'html':'<span>All fields good !!</span>'})
#     else:
#         return json.dumps({'html':'<span>Enter the required fields</span>'})

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,port=5002)
