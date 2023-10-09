
import os

from flask import Flask, request, current_app, render_template, redirect, url_for, \
    send_from_directory, make_response
from werkzeug.utils import secure_filename

from datetime import datetime

from interpolate import interpolate_csv
from email_tools import send_email, save_email

from multiprocessing import Process

ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def wrap_process(save_location, add_geo, add_twitter, email_address):
    print("Doing this!")
    output_file = interpolate_csv(save_location, add_geo, add_twitter)
    error = False
    error_number = 0
    if isinstance(output_file, int):
        error = True
        error_number = output_file
        print("ERROR", error, error_number)
    send_email(email_address, output_file, error, error_number)
    return ""

def create_app():
    app = Flask(__name__)

    @app.route('/', methods=["GET","POST"])
    def upload():
        if request.method == 'POST':
            add_geo, add_twitter = False, False
            if request.form.get('geo-features'):
                add_geo = True
                print("ADDING GEO")
            if request.form.get('twitter-features'):
                add_twitter = True
                print("ADDING TWITTER")

            email_address = request.form['email']
            save_email(email_address)

            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                new_filename = f'{filename.split(".")[0]}_{str(datetime.now())}.csv'
                save_location = os.path.join('input', new_filename)
                file.save(save_location)

                heavy_process = Process(  # Create a daemonic process with heavy "my_func"
                    target=wrap_process,
                    args=[save_location, add_geo, add_twitter, email_address],
                    daemon=True
                )
                heavy_process.start()

                # output_file = interpolate_csv(save_location, add_geo, add_twitter)

                # send_email(email_address, output_file)
                # return send_from_directory('output', output_file)
                return render_template('index.html', flash_message="True")

        return render_template('index.html', flash_message="False")

    return app

app = create_app()