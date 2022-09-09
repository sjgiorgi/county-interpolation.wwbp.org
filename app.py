import os

from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
from interpolate import interpolate_csv

ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                new_filename = f'{filename.split(".")[0]}_{str(datetime.now())}.csv'
                save_location = os.path.join('input', new_filename)
                file.save(save_location)

                output_file = interpolate_csv(save_location, add_geo, add_twitter)
                return send_from_directory('output', output_file)

        return render_template('index.html')
        
    return app

app = create_app()