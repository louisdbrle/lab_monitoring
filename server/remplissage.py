import sqlite3

# Ouverture/initialisation de la base de donnee
conn = sqlite3.connect("laboratoire.db")
conn.row_factory = sqlite3.Row
c = conn.cursor()

# On supprime les tables si elles existent
c.execute("drop table if exists Capteur")
c.execute("drop table if exists Objet")
c.execute("drop table if exists TypeGaz")
c.execute("drop table if exists MesureGaz")
c.execute("drop table if exists MesureRFID")

# On rajoute 2 lecteurs RFID
c.execute("insert into Capteur (nom,type) values ('RFID_1','RFID')")
c.execute("insert into Capteur (nom,type) values ('RFID_2','RFID')")

# On rajoute 2 capteurs de gaz
c.execute("insert into Capteur (nom,type) values ('MQ3','GAZ')")
c.execute("insert into Capteur (nom,type) values ('MGS','GAZ')")

# On rajoute 2 objets (étiquettes rfid)
c.execute("insert into Objet (id_objet, idCapteurRFID) values ('1D-1E-B7-EC',1)")
c.execute("insert into Objet (id_objet, idCapteurRFID) values ('1D-1B-B7-EC',2)")

# On rajoute les types de gaz
c.execute("insert into TypeGaz (nomTypeGaz, idCapteurGaz) values ('C2H6O', 1)")
c.execute("insert into TypeGaz (nomTypeGaz, idCapteurGaz) values ('NH3', 2)")
c.execute("insert into TypeGaz (nomTypeGaz, idCapteurGaz) values ('CO', 2)")
c.execute("insert into TypeGaz (nomTypeGaz, idCapteurGaz) values ('NO2', 2)")
c.execute("insert into TypeGaz (nomTypeGaz, idCapteurGaz) values ('C3H8', 2)")
c.execute("insert into TypeGaz (nomTypeGaz, idCapteurGaz) values ('C4H10', 2)")
c.execute("insert into TypeGaz (nomTypeGaz, idCapteurGaz) values ('CH4', 2)")
c.execute("insert into TypeGaz (nomTypeGaz, idCapteurGaz) values ('H2', 2)")
c.execute("insert into TypeGaz (nomTypeGaz, idCapteurGaz) values ('C2H5OH', 2)")


# fermeture
conn.commit()
conn.close()
