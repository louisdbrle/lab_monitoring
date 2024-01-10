#include <Arduino.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <Wire.h>

#include "MutichannelGasSensor.h"

#define DEBUG 1

#define MAX_FLOAT 3.4028235E+38

#define I2C_ADDR 0x04
#define MQ3_PIN 34
#define FAN_PIN 18

#define LOOP_DELAY_S 10

float c_NH3, c_CO, c_NO2, c_C3H8, c_C4H10, c_CH4, c_H2, c_C2H5OH, c_C2H6O;

float thresholds[9] = {MAX_FLOAT, MAX_FLOAT, MAX_FLOAT, MAX_FLOAT, MAX_FLOAT,
                       MAX_FLOAT, MAX_FLOAT, MAX_FLOAT, MAX_FLOAT};
int index_gas;

int fan_auto = 0;

int tick = millis();

const char* ssid = "iPhone de Louis";
const char* password = "connexion11";
const char* mqtt_server = "172.20.10.11";

WiFiClient wifiClient;
PubSubClient client(wifiClient);

void read_mgs();
void read_mq3();
void fan(int on);
void gas_auto();
void callback(char* topic, byte* message, unsigned int length);

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
        if (client.connect("ESP32Client_GAS")) {
            client.subscribe("FAN");
            Serial.println("Connected");
            break;
        } else {
            delay(2000);
        }
    }

    client.setCallback(callback);

    gas.begin(0x04);
    gas.powerOn();

    pinMode(FAN_PIN, OUTPUT);
    digitalWrite(FAN_PIN, LOW);

    pinMode(MQ3_PIN, INPUT);
}

void loop() {
    client.loop();

    if (millis() - tick > LOOP_DELAY_S * 1000) {
        tick = millis();
        read_mgs();
        read_mq3();
        gas_auto();
    }
}

void read_mgs() {
    c_NH3 = (gas.measure_NH3() >= 0) ? gas.measure_NH3() : -1;
    c_CO = (gas.measure_CO() >= 0) ? gas.measure_CO() : -1;
    c_NO2 = (gas.measure_NO2() >= 0) ? gas.measure_NO2() : -1;
    c_C3H8 = (gas.measure_C3H8() >= 0) ? gas.measure_C3H8() : -1;
    c_C4H10 = (gas.measure_C4H10() >= 0) ? gas.measure_C4H10() : -1;
    c_CH4 = (gas.measure_CH4() >= 0) ? gas.measure_CH4() : -1;
    c_H2 = (gas.measure_H2() >= 0) ? gas.measure_H2() : -1;
    c_C2H5OH = (gas.measure_C2H5OH() >= 0) ? gas.measure_C2H5OH() : -1;

    if (DEBUG) {
        Serial.print("NH3: ");
        Serial.println(c_NH3);
        Serial.print("CO: ");
        Serial.println(c_CO);
        Serial.print("NO2: ");
        Serial.println(c_NO2);
        Serial.print("C3H8: ");
        Serial.println(c_C3H8);
        Serial.print("C4H10: ");
        Serial.println(c_C4H10);
        Serial.print("CH4: ");
        Serial.println(c_CH4);
        Serial.print("H2: ");
        Serial.println(c_H2);
        Serial.print("C2H5OH: ");
        Serial.println(c_C2H5OH);
        Serial.println();
    }

    client.publish("NH3", String(c_NH3).c_str());
    client.publish("CO", String(c_CO).c_str());
    client.publish("NO2", String(c_NO2).c_str());
    client.publish("C3H8", String(c_C3H8).c_str());
    client.publish("C4H10", String(c_C4H10).c_str());
    client.publish("CH4", String(c_CH4).c_str());
    client.publish("H2", String(c_H2).c_str());
    client.publish("C2H5OH", String(c_C2H5OH).c_str());
}

void read_mq3() {
    float sensor_volt;
    float RS_gas;
    float ratio;
    int sensorValue = analogRead(MQ3_PIN);
    sensor_volt = sensorValue / 4096.0 * 3.3;
    RS_gas = (3.3 - sensor_volt) / sensor_volt;
    ratio = RS_gas / 9.8;
    c_C2H6O = pow(10, ((log10(ratio) - (-0.38)) / (-0.91)));

    client.publish("C2H6O", String(c_C2H6O).c_str());

    if (DEBUG) {
        Serial.print("sensor_volt = ");
        Serial.println(sensor_volt);
        Serial.print("RS_ratio = ");
        Serial.println(ratio);
        Serial.print("Rs/R0 = ");
        Serial.println(RS_gas);
        Serial.print("MQ3 = ");
        Serial.println(c_C2H6O);
        Serial.println();
    }
}

void fan(int on) { digitalWrite(FAN_PIN, on); }

void gas_auto() {
    switch (index_gas) {
        case 0:
            if (c_NH3 > thresholds[0]) {
                fan(1);
            } else {
                fan(0);
            }
            break;

        case 1:
            if (c_CO > thresholds[1]) {
                fan(1);
            } else {
                fan(0);
            }
            break;

        case 2:
            if (c_NO2 > thresholds[2]) {
                fan(1);
            } else {
                fan(0);
            }
            break;

        case 3:
            if (c_C3H8 > thresholds[3]) {
                fan(1);
            } else {
                fan(0);
            }
            break;

        case 4:
            if (c_C4H10 > thresholds[4]) {
                fan(1);
            } else {
                fan(0);
            }
            break;

        case 5:
            if (c_CH4 > thresholds[5]) {
                fan(1);
            } else {
                fan(0);
            }
            break;

        case 6:
            if (c_H2 > thresholds[6]) {
                fan(1);
            } else {
                fan(0);
            }
            break;

        case 7:
            if (c_C2H5OH > thresholds[7]) {
                fan(1);
            } else {
                fan(0);
            }
            break;

        case 8:
            if (c_C2H6O > thresholds[8]) {
                fan(1);
            } else {
                fan(0);
            }
            break;

        default:
            break;
    }
}

void callback(char* topic, byte* message, unsigned int length) {
    String messageTemp;

    for (int i = 0; i < length; i++) {
        messageTemp += (char)message[i];
    }

    if (String(topic) == "FAN") {
        if (messageTemp == "on") {
            fan(1);
            fan_auto = 0;
        } else if (messageTemp == "off") {
            fan(0);
            fan_auto = 0;
        } else if (messageTemp == "auto") {
            fan_auto = 1;
        }
    } else if (String(topic) == "THRESHOLDS") {
        sscanf(messageTemp.c_str(), "%d %f", &index_gas,
               thresholds + index_gas);
    }

    if (DEBUG) {
        Serial.print("Message arrived on topic: ");
        Serial.print(topic);
        Serial.print(". Message: ");
        Serial.println(messageTemp);
        Serial.println();
    }
}