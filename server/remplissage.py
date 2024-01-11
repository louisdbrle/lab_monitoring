import sqlite3
import sqlite3

# Ouverture/initialisation de la base de donnee
conn = sqlite3.connect("laboratoire.db")
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Ouverture/initialisation de la base de données
conn = sqlite3.connect("laboratoire.db")
c = conn.cursor()

# Commandes de destruction des tables
c.execute("DROP TABLE IF EXISTS MesureGaz;")
c.execute("DROP TABLE IF EXISTS MesureRFID;")
c.execute("DROP TABLE IF EXISTS Capteur;")
c.execute("DROP TABLE IF EXISTS Objet;")
c.execute("DROP TABLE IF EXISTS TypeGaz;")

# Commandes de création des tables
c.execute(
    """
    CREATE TABLE Capteur (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        type TEXT NOT NULL,
        dateInsertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""
)

c.execute(
    """
    CREATE TABLE TypeGaz (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nomTypeGaz TEXT NOT NULL,
        idCapteurGaz INTEGER NOT NULL,
        FOREIGN KEY (idCapteurGaz) REFERENCES CapteurGaz(idCapteurGaz)
    );
"""
)

c.execute(
    """
    CREATE TABLE MesureGaz (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dateInsertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        valeur INTEGER NOT NULL,
        idCapteurGaz INTEGER NOT NULL,
        idTypeGaz INTEGER NOT NULL,
        FOREIGN KEY (idCapteurGaz) REFERENCES CapteurGaz(idCapteurGaz),
        FOREIGN KEY (idTypeGaz) REFERENCES TypeGaz(idTypeGaz)
    );
"""
)

c.execute(
    """
    CREATE TABLE MesureRFID (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        idCapteurRFID INTEGER NOT NULL,
        dateInsertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        valeur TEXT NOT NULL,
        FOREIGN KEY (idCapteurRFID) REFERENCES CapteurRFID(idCapteurRFID)
    );
"""
)

c.execute(
    """
    CREATE TABLE Objet (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_objet TEXT NOT NULL,
        dateInsertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        idCapteurRFID INTEGER NOT NULL,
        FOREIGN KEY (idCapteurRFID) REFERENCES CapteurRFID(idCapteurRFID)
    );
"""
)


# On rajoute 2 lecteurs RFID
c.execute("insert into Capteur (nom,type) values ('RFID_1','RFID')")
c.execute("insert into Capteur (nom,type) values ('RFID_2','RFID')")

# On rajoute 2 capteurs de gaz
c.execute("insert into Capteur (nom,type) values ('MQ3','GAZ')")
c.execute("insert into Capteur (nom,type) values ('MGS','GAZ')")

# On rajoute 2 objets (étiquettes rfid)
c.execute("insert into Objet (id_objet, idCapteurRFID) values ('1D1EB7EC00',1)")
c.execute("insert into Objet (id_objet, idCapteurRFID) values ('1D1BB7EC00',2)")

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
