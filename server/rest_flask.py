from flask import Flask, render_template, send_from_directory, jsonify, request, Response
import sqlite3
import json
import paho.mqtt.client as mqtt

# Create a client instance
client = mqtt.Client()

# Connect to the broker
client.connect("localhost", 1883, 60)  # replace "localhost" with your broker's IP

app = Flask(__name__)

gazIds = ["C2H6O", "NH3", "CO", "NO2", "C3H8", "C4H10", "CH4", "H2", "C2H5OH"]

#table of correspondance between RFID IDS and objects names
rfidIds = {"1D1EB7EC00": "chimique", "1D1BB7EC00": "microscope"}
TableActuelRFID = ["",""]
TableCorrespondanceRFID = ["chimique", "microscope"]

#Global variables for fanmode and threshold values
fanMode = "AUTO"
threshold_value = 2000
threshold_gas = "C2H6O"

@app.route('/image.gif')
def image():
    return send_from_directory('static', 'image.gif')

@app.route('/')
def index():
    return render_template("index.html", fan_mode_value=fanMode)

@app.route("/mesure/gaz/<string:gaz>", methods=["POST"])
def mesure_gaz(gaz: str):
    conn = sqlite3.connect("laboratoire.db")
    c = conn.cursor()

    if request.method == "POST":
        data = request.get_data()
        #print(data)
        valeur = float(data.decode("utf-8"))
        idCapteurGaz = c.execute(f"SELECT idCapteurGaz FROM TypeGaz WHERE nomTypeGaz = '{gaz}'").fetchone()[0]
        #print(idCapteurGaz)
        c.execute(
            f"INSERT INTO MesureGaz(valeur, idCapteurGaz, idTypeGaz) VALUES ({valeur}, {idCapteurGaz}, {gazIds.index(gaz) + 1})"
        )

    conn.commit()
    conn.close()

    return "OK"

@app.route("/mesure/gaz", methods=["GET"])
def mesure_gaz_all():
    conn = sqlite3.connect("laboratoire.db")
    c = conn.cursor()
    if request.args.get("idTypeGaz"):
        c.execute(
            "SELECT * FROM MesureGaz WHERE idTypeGaz = ?", request.args["idTypeGaz"]
        )
    elif request.args.get("idCapteurGaz"):
        c.execute(
            "SELECT * FROM MesureGaz WHERE idCapteurGaz = ?",
            request.args["idCapteurGaz"],
        )
    else:
        c.execute("SELECT * FROM MesureGaz")

    
    conn.commit()
    conn.close()

    return c.fetchall()

#Route for threshold values where you set the threshold value and the gas
@app.route("/THRESHOLD", methods=["GET", "POST"])
def threshold():
    global threshold_value
    global threshold_gas
    if request.method == "POST":
        jsondata = request.get_data()
        data = json.loads(jsondata)
        threshold_value = data.get("threshold")
        threshold_gas = data.get("gas")
        print(threshold_value)
        print(threshold_gas)

    #publish to correspond to the esp32 format: "gasId threshold_value"
    client.publish("THRESHOLD", f"{gazIds.index(threshold_gas)} {threshold_value}")
    
    if request.method == "GET":
        #return a json object with 2 keys: gas and threshold for the value
        return jsonify({"gas": threshold_gas, "threshold": threshold_value})
    return "OK"

#Route for fan mode where you set the fan mode, when get send the value of the fan mode
@app.route("/FANMODE", methods=["GET", "POST"])
def fanmode():
    global fanMode
    if request.method == "POST":
        jsondata = request.get_data()
        data = json.loads(jsondata)
        fanMode = data.get("fanmode")
        print(fanMode)
        #Publish on mqtt  topic "FAN" "on" "off" or "auto" based on fanMode value
        client.publish("FAN", fanMode.lower())
        
    if request.method == "GET":
        return fanMode

    return "OK"


@app.route("/mesure/RFID/<int:idCapteurRFID>", methods=["POST", "GET"])
def mesure_rfid(idCapteurRFID):
    conn = sqlite3.connect("laboratoire.db")
    c = conn.cursor()

    data = request.get_data()
    #print(data)
    idObject = str(data.decode("utf-8"))
    idObject = '-'.join(idObject[i:i+2] for i in range(0, len(idObject), 2))
    #print(str(idObject))

    #print(idCapteurRFID)

    if request.method == "POST":
        c.execute(
            f"INSERT INTO MesureRFID(idCapteurRFID, valeur) VALUES ({idCapteurRFID}, '{str(idObject)}')"
        )
    elif request.method == "GET":
        if request.args.get("idCapteurRFID"):
            c.execute(
                f"SELECT * FROM MesureRFID WHERE idCapteurRFID = {request.args['idCapteurRFID']}",
            )
            object = rfidIds[c.fetchone()]
            if idCapteurRFID == 1:
                object = "chimique"
            else:
                object = "microscope"

            TableActuelRFID[idCapteurRFID-1] = object
            return object
        else:
            return "_____"

@app.route("/mesure/RFID_RW/<int:idCapteurRFID>", methods=["GET"])
def mesure_rfid_RW(idCapteurRFID):

    if request.method == "GET":
        if TableActuelRFID[idCapteurRFID-1] == TableCorrespondanceRFID[idCapteurRFID-1]:
            return "right"
        elif TableActuelRFID[idCapteurRFID-1] != TableCorrespondanceRFID[0] and TableActuelRFID[idCapteurRFID-1] != TableCorrespondanceRFID[1]:
            return "_____"
        else:
            return "wrong"

    return "OK"

# Add other routes for different endpoints

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, threaded=True)
    print("\nServer stopped")