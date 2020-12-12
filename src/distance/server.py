# -*- coding: utf-8 -*-
import threading
import time

from flask import Flask, request, jsonify

import utils
from distance.beepbeep import calculate_distance

app = Flask(__name__, static_folder='static', static_url_path='')
program_args = utils.init_args()
program_args.beep_beep = True
program_args.threshold = 5e10

paired_files = [{}, {}]
server_state = {
    "process": []
}


def dump_file_info(file):
    return {
        "filename": file["filename"],
        "size": len(file["data"]),
        "time": file["time"],
    }


def process(file1, file2):
    print("processing", file1['filename'], file2['filename'])
    state_dict = {
        "processing": True,
        "a": dump_file_info(file1),
        "b": dump_file_info(file2),
    }

    def process_file():
        d = calculate_distance(program_args, file1['data'], file2['data'])
        state_dict['processing'] = False
        state_dict['success'] = (d['distance'] != -1)
        state_dict['result'] = d

    server_state['process'].append(state_dict)
    thr = threading.Thread(target=process_file)
    thr.start()
    pass


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/distance/reset', methods=['GET'])
def reset():
    paired_files[0] = {}
    paired_files[1] = {}
    return jsonify({
        "success": True,
    })


@app.route('/distance/status', methods=['GET'])
def get_status():
    ret = {}
    if paired_files[0]:
        ret['a'] = dump_file_info(paired_files[0])
    if paired_files[1]:
        ret['b'] = dump_file_info(paired_files[1])
    return jsonify({
        "data": {
            "files": ret,
            "server_state": server_state,
        },
        "success": True,
    })


@app.route('/distance/<side>', methods=['POST'])
def upload_file(side):
    global paired_files
    file = request.files['file']
    if side not in ["a", "b"]:
        return jsonify({
            "success": False,
            "message": "unknown side",
        }), 400
    if file:
        print("Received from side", side, ":", file.filename)
        file_info = {
            "filename": str(file.filename),
            "data": file.read(),
            "time": int(time.time())
        }
        if side == "a":
            paired_files[0] = file_info
        else:
            paired_files[1] = file_info
        if paired_files[0] and paired_files[1]:
            process(paired_files[0], paired_files[1])
            paired_files = [None, None]
        return jsonify({
            "success": True,
        })
    return jsonify({
        "success": False,
        "message": "file not attached",
    }), 400


@app.route('/bluetooth', methods=['POST'])
def get_bluetooth_file():
    file = request.files['file']
    if file:
        print("Received file {}.".format(file.filename))
        file.save('../receive/output.wav')
        return jsonify({
            "success": True,
        })
    return jsonify({
        "success": False,
        "message": "file not attached",
    }), 400


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
