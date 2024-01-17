from flask import Flask, render_template, send_from_directory, jsonify, request, Response
import sqlite3
import json
import paho.mqtt.client as mqtt

# Create a client instance
client = mqtt.Client()

# Connect to the broker
client.connect("localhost", 1883, 60)  # replace "localhost" with your broker's IP

app = Flask(__name__)

gazIds = ["C2H6O","NH3", "CO", "NO2", "C3H8", "C4H10", "CH4", "H2", "C2H5OH"]

#List of object in stock
stock = {"Erlenmeyer": 10, "Ballon": 5, "Becher": 3, "Pipette": 15, "Tube": 20, "Burette": 5, "Flacon": 10, "Microscope": 2}

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
    conn = sqlite3.connect("laboratoire.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    data = [
        {"NO2": []},
        {"NH3": [], "CO": [], "H2": [], "C2H5OH": [], "C2H6O": []},
        {"C3H8": [], "C4H10": [], "CH4": []},
    ]
    for gaz in gazIds:
        c.execute(
            f"SELECT * FROM MesureGaz WHERE idTypeGaz = {gazIds.index(gaz) + 1} ORDER BY dateInsertion DESC LIMIT {request.args.get('limit', 10)}"
        )

        for d in data:
            if gaz in d:
                for row in c.fetchall():
                    # add to d[gaz] row["valeur"] on the left
                    d[gaz].insert(0, row["valeur"])
                    #d[gaz].append(row["valeur"])

    conn.commit()
    conn.close()


    return render_template("index.html", fan_mode_value=fanMode, data=data, stock=stock)

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
        c.execute(
            f"SELECT * FROM MesureRFID WHERE idCapteurRFID = {idCapteurRFID}",
        )
        if c.fetchone() is None or c.fetchone()[3]=='':
            object = " "
        else:    
            object = rfidIds[c.fetchone()[3]]
        print (object)
        TableActuelRFID[idCapteurRFID-1] = object
        return object

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

@app.route("/add_or_update_object", methods=["POST"])
def add_or_update_object():
    if request.method == "POST":
        jsondata = request.get_data()
        data = json.loads(jsondata)
        object_name = data.get("object_name")

        if object_name in stock:
            stock[object_name] += 1
        else:
            stock[object_name] = 1

        return str(stock[object_name])


@app.route("/add_new_object", methods=["POST"])
def add_new_object():
    try:
        if request.method == "POST":
            jsondata = request.get_data()
            data = json.loads(jsondata)
            object_name = data.get("object_name")
            object_count = int(data.get("object_count", 0)) 

            if object_name in stock:
                stock[object_name] += object_count
            else:
                stock[object_name] = object_count

            return jsonify({"object_name": object_name, "object_count": stock[object_name]})
    except Exception as e:
        print(f"Error in add_new_object: {str(e)}")
        return jsonify({"error": "Internal Server Error", "details": str(e)})

# Add other routes for different endpoints

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, threaded=True)
    print("\nServer stopped")