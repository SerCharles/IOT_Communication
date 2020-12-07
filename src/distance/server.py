# -*- coding: utf-8 -*-
import os
from flask import Flask, request

UPLOAD_FOLDER = 'upload'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
else:
    pass

paired_files = [None, None]


def process(filename1, filename2):
    print("processing", filename1, filename2)

    pass


@app.route('/audio/<side>', methods=['POST'])
def upload_file(side):
    global paired_files
    file = request.files['file']
    if side not in ["a", "b"]:
        return "side unknown", 400
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], side + ".wav")
        file.save(filepath)
        print("Received from side", side, ":", filepath)
        if side == "a":
            paired_files[0] = filepath
        else:
            paired_files[1] = filepath
        if paired_files[0] and paired_files[1]:
            paired_files = [None, None]
            process(paired_files[0], paired_files[1])
        return "ok", 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
