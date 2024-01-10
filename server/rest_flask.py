from flask import Flask, render_template, send_from_directory, jsonify, request, Response
import sqlite3



app = Flask(__name__)

gazIds = ["C2H6O", "NH3", "CO", "NO2", "C3H8", "C4H10", "CH4", "H2", "C2H5OH"]

@app.route('/image.gif')
def image():
    return send_from_directory('static', 'image.gif')

@app.route('/')
def index():
    return render_template("index.html")

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
        else:
            c.execute("SELECT * FROM MesureRFID")

        return c.fetchall()

    conn.commit()
    conn.close()

    return "OK"

# Add other routes for different endpoints

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, threaded=True)
    print("\nServer stopped")