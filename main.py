#!/usr/bin/env python3

import os
import json
from flask import Flask
from flask import request
from flask import jsonify
from flask import Markup
from flask import render_template
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, support_credentials=True)

@app.route("/")
def root(): return "root is ok"

# User roots
@app.route("/book")
@cross_origin(supports_credentials=True)
def book():
    with open('booked.json', "r", encoding="utf-8") as f:
        booked = json.load(f)

        if booked[str(request.args["seatNumber"])] == "":
            if "phoneNumber" in request.args:
                booked[str(request.args["seatNumber"])] = {
                    "name": request.args["name"],
                    "phoneNumber": request.args["phoneNumber"]
                }
            else:
                booked[str(request.args["seatNumber"])] = request.args["name"]
        else:
            return jsonify(-1, "Denna plats är redan bokad!")
    
    with open('booked.json', 'w', encoding="utf-8") as f:
        json.dump(booked, f)

    return jsonify(0, "ok")

@app.route("/readBooked")
@cross_origin(supports_credentials=True)
def readBooked():
    with open('booked.json', "r", encoding="utf-8") as f:
        booked = json.load(f)

        toReturn = {}

        for x in booked:
            if type(booked[x]) == str:
                toReturn[x] = booked[x]
            elif type(booked[x]) == dict:
                toReturn[x] = booked[x]['name']
            else:
                toReturn[x] = ""
        
        return jsonify(toReturn)

# Admin routes
@app.route("/admin/readBooked")
def admin_readBooked():
    if (not 'password' in request.args) or (request.args['password'] != options['password']): return "bad password"

    with open('booked.json', "r", encoding="utf-8") as f:
        booked = json.load(f)
        return jsonify(booked)

@app.route("/admin/book")
def admin_book():
    if (not 'password' in request.args) or (request.args['password'] != options['password']): return "bad password"

    with open('booked.json', "r", encoding="utf-8") as f:
        booked = json.load(f)

        if "clear" in request.args:
            booked[str(request.args["seatNumber"])] = ""
        else:
            if "phoneNumber" in request.args:
                booked[str(request.args["seatNumber"])] = {
                    "name": request.args["name"],
                    "phoneNumber": request.args["phoneNumber"]
                }
            else:
                booked[str(request.args["seatNumber"])] = request.args["name"]

    with open('booked.json', 'w', encoding="utf-8") as f:
        json.dump(booked, f)

    return jsonify(0, "ok")

@app.route("/admin/getPrintable")
def admin_getPrintable():
    if (not 'password' in request.args) or (request.args['password'] != options['password']): return "bad password"

    with open('booked.json', "r", encoding="utf-8") as f:
        booked = json.load(f)

    toReturn = ""
    for key in booked:
        if booked[key] == "":continue

        toReturn += "<tr>"
        if type(booked[key]) == str:
            toReturn += "<td>%s</td>" % key
            toReturn += "<td>%s</td>" % booked[key]
            toReturn += "<td></td>"
        elif type(booked[key]) == dict:
            toReturn += "<td>%s</td>" % key
            for x in ("name", "phoneNumber"):
                toReturn += "<td>%s</td>" % booked[key][x]
        else:pass
        toReturn += "</tr>"
    
    return render_template("getPrintable.html", tableData=Markup(toReturn))

if __name__ == "__main__":
    # Set working dir to path of main.py
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # Create options.json and booked.json if they dont exist
    if not os.path.isfile("options.json"):
        with open("options.json", "w") as f:
            json.dump(
                {
                    "host": "127.0.0.1",
                    "port": "5000",
                    "debug": False,
                    "password": "password"
                },
                f
            )
    if not os.path.isfile("booked.json"):
        with open("booked.json", "w") as f:
            data = {}

            for x in range(64):
                data[str(x+1)] = ""
            
            json.dump(data, f)

    # Load settings.json
    with open('options.json', "r", encoding="utf-8") as f:
        options = json.load(f)

    # Start Flask
    app.run(
        host=options['host'],
        port=options['port'],
        debug=options['debug']
    )