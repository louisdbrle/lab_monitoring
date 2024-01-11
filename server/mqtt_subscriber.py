import paho.mqtt.client as mqtt
import sqlite3

topics = [
    "C2H6O",
    "NH3",
    "CO",
    "NO2",
    "C3H8",
    "C4H10",
    "CH4",
    "H2",
    "C2H5OH",
    "RFID/1",
    "RFID/2",
]

client = mqtt.Client()
client.connect("localhost", 1883, 60)


for topic in topics:
    client.subscribe(topic)


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

    conn = sqlite3.connect("laboratoire.db")
    c = conn.cursor()

    if msg.topic.startswith("RFID"):
        c.execute(f"SELECT * FROM MesureRFID WHERE idCapteurRFID = {msg.topic[-1]}")
        row = c.fetchone()

        if row is None:
            c.execute(
                f"INSERT INTO MesureRFID(valeur, idCapteurRFID) VALUES ('{msg.payload.decode('utf-8')}', {int(msg.topic[-1])})"
            )
        else:
            c.execute(
                f"UPDATE MesureRFID SET valeur = '{msg.payload.decode('utf-8')}' WHERE idCapteurRFID = {int(msg.topic[-1])}"
            )
    else:
        c.execute(
            f"INSERT INTO MesureGaz(valeur, idCapteurGaz, idTypeGaz) VALUES ({float(msg.payload.decode('utf-8'))}, {1 if topics.index(msg.topic) < 8 else 2}, {topics.index(msg.topic) + 1})"
        )

    conn.commit()
    conn.close()


client.on_message = on_message

client.loop_forever()
