#include <Arduino.h>
#include <MFRC522.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <WiFi.h>

#define SS_PIN_1 25   // SS pin for the first RC522
#define RST_PIN_1 33  // RST pin for the first RC522

#define SS_PIN_2 26   // SS pin for the second RC522
#define RST_PIN_2 32  // RST pin for the second RC522

const char* ssid = "iPhone de Louis";
const char* password = "connexion11";
const char* mqtt_server = "172.20.10.11";

int isobject1 = 0;
int isobject2 = 0;

MFRC522 mfrc522_1(SS_PIN_1,
                  RST_PIN_1);  // Create MFRC522 instance for the first reader
MFRC522 mfrc522_2(SS_PIN_2,
                  RST_PIN_2);  // Create MFRC522 instance for the second reader

WiFiClient wifiClient;
PubSubClient client(wifiClient);

// buffer for the MFRC522 uid to publish
char uidString[10];
char uidString2[10];

void printUid(MFRC522::Uid uid) {
    for (byte i = 0; i < uid.size; i++) {
        Serial.print(uid.uidByte[i] < 0x10 ? " 0" : " ");
        Serial.print(uid.uidByte[i], HEX);
        if (i == uid.size - 1) {
            Serial.println();
        }
    }
}

void setup() {
    Serial.begin(9600);
    WiFi.begin(ssid, password);
    Serial.println("Connecting to WiFi...");
    while (!WL_CONNECTED)
        ;
    Serial.println("Connected");

    client.setServer(mqtt_server, 1883);

    while (!client.connected()) {
        Serial.println("Connecting to MQTT...");
        if (client.connect("ESP32ClientRFID")) {
            Serial.println("Connected");
            break;
        } else {
            delay(2000);
        }
    }

    SPI.begin();
    mfrc522_1.PCD_Init();
    mfrc522_2.PCD_Init();
}

void loop() {
    int tick = millis();

    isobject1 = 0;
    mfrc522_1.PCD_AntennaOn();
    mfrc522_2.PCD_AntennaOff();
    while (millis() - tick < 1000) {
        if (mfrc522_1.PICC_IsNewCardPresent() &&
            mfrc522_1.PICC_ReadCardSerial()) {
            // Serial.print("Reader 1 UID: ");
            // printUid(mfrc522_1.uid);
            // Write the uid to the buffer
            sprintf(uidString, "%02X%02X%02X%02X%02X", mfrc522_1.uid.uidByte[0],
                    mfrc522_1.uid.uidByte[1], mfrc522_1.uid.uidByte[2],
                    mfrc522_1.uid.uidByte[3], mfrc522_1.uid.uidByte[4]);
            isobject1 = 1;
        }
    }
    if (isobject1 == 0) {
        // Serial.println("No object detected");
        client.publish("RFID/1", "");
    } else {
        // Serial.println("Object detected");
        client.publish("RFID/1", String(uidString).c_str());
    }

    mfrc522_2.PCD_AntennaOn();
    mfrc522_1.PCD_AntennaOff();
    isobject2 = 0;
    while (millis() - tick < 2000) {
        if (mfrc522_2.PICC_IsNewCardPresent() &&
            mfrc522_2.PICC_ReadCardSerial()) {
            // Serial.print("Reader 2 UID: ");
            // printUid(mfrc522_2.uid);
            // Write the uid to the buffer
            sprintf(uidString2, "%02X%02X%02X%02X%02X",
                    mfrc522_2.uid.uidByte[0], mfrc522_2.uid.uidByte[1],
                    mfrc522_2.uid.uidByte[2], mfrc522_2.uid.uidByte[3],
                    mfrc522_2.uid.uidByte[4]);
            isobject2 = 1;
        }
    }
    if (isobject2 == 0) {
        // Serial.println("No object detected");
        client.publish("RFID/2", "");
    } else {
        // Serial.println("Object detected");
        client.publish("RFID/2", String(uidString2).c_str());
    }
}