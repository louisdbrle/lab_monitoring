import paho.mqtt.client as mqtt


client = mqtt.Client()
client.connect("192.168.1.119", 1883, 60)

client.subscribe("test")


def on_message(client, userdata, msg):
    print(msg.payload.decode())


client.on_message = on_message

client.loop_forever()
