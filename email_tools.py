import os
from os.path import basename
import json

import configparser

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

from sqlalchemy import create_engine, text



def get_db():
    #eng = create_engine('sqlite:///{}'.format(os.path.join(current_app.root_path, '../db/emails.sqlite3')))
    eng = create_engine('sqlite:///{}'.format(os.path.join('db', 'emails.sqlite3')))
    return eng

def save_email(email_address):
    try:
        #email_address = request.json['email']
        eng = get_db()
        create_table_sql = text('CREATE TABLE IF NOT EXISTS emails (email TEXT PRIMARY KEY, verified_date DATETIME DEFAULT CURRENT_TIMESTAMP)')
        insert_email_sql = text('INSERT INTO emails (email) VALUES (:email)')
        eng.execute(create_table_sql)
        eng.execute(insert_email_sql, {'email': email_address})
        return json.dumps({'status': 'success'}), 200, {'ContentType': 'application/json'}
    except Exception as e:
        print(e)
        return json.dumps({'status': 'error'}), 500, {'ContentType': 'application/json'}

def send_email(email_address, output_file, error=False):
    em = configparser.RawConfigParser()
    em.read('configs/.email.cnf')
    from_ = em.get('email', 'sender')
    email_password = em.get('email', 'password')
    port = em.get('email', 'port')
    
    msg = MIMEMultipart()

    #from_ = 'no-reply@textanalyzer.org'
    to = email_address
    subject = 'Data from county-interpolation.wwbp.org'
    if error:
        body = """
            Thank you for your interest in county-interpolation.wwbp.org!

            Unfortunately, there was an error with your data. Please contact us at {contact}.

            Note, that the example data on the website does not work with the Twitter language features option, which is a common error. 
        """.format(from_=from_, to=to, subject=subject, contact='county.interpolation@gmail.com')
    else:
        body = """
            Thank you for your interest in county-interpolation.wwbp.org!

            The attached file has your interpolations.  

            If you did not request this email, you may safely ignore it. If you have any questions or concerns, please contact us at {contact}.
        """.format(from_=from_, to=to, subject=subject, contact='county.interpolation@gmail.com')

    msg['From'] = from_
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    if not error:
        with open("output/"+output_file, "rb") as fil: 
            attachedfile = MIMEApplication(fil.read())
            attachedfile.add_header('content-disposition', 'attachment', filename=basename("output/"+output_file))

        msg.attach(attachedfile)

    #try:
    smtp_server = smtplib.SMTP('smtp.gmail.com', port)
    #smtp_server.ehlo()
    smtp_server.starttls()
    smtp_server.login(from_, email_password)
    #smtp_server.login(from_, email_password)
    smtp_server.sendmail(from_, to, msg.as_string())
    smtp_server.close()
    return True
    # except Exception as e:
    #     print(e)
    #     #return json.dumps({'status': 'error'}), 500, {'ContentType': 'application/json'}
    #     return False

    # res = make_response(json.dumps({'status': 'success'}))
    # res.set_cookie('email', email_address)
    # #res.set_cookie('verified', 'true', max_age=60*60*24*7*365*3)

    # return res, 200, {'ContentType': 'application/json'}