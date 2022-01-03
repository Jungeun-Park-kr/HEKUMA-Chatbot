"""[summary]
This file runs with the actions code. Here we basically subscribe to some atvise (opcua) nodes which can give us an alarm and
ff an alarm occurs then we also handle it in here.
"""

from opcua import Client as Client, Node
import threading
import requests

url='opc.tcp://141.82.52.161:4840'

"""[summary]
SubscribeAll gets called in actions.py when a new conversation is started. We connect here to the opcua server
get certain alarm nodes and subscribe to these alarm nodes.
"""
class SubscribeAll():

    async def run(session_id):
        print("Trying to connect to opcua server...")
        client = Client(url=url)
        client.connect()
        print("Connected to opcua server! Trying to grab all the necessary nodes...")
        cylinder_node = client.get_node("ns=1;s=AGENT.OBJECTS.Machine.Alarms.General.CylinderAlarm_1.Alarm.Condition.value")
        jamming_node = client.get_node("ns=1;s=AGENT.OBJECTS.Machine.Alarms.General.JammingMaterialAlarm.Alarm.Condition.value")
        print("We got all nodes! Subscibe to handlers...")
        handler = SubscriptionHandler(session_id) 
        # We create a Client Subscription.
        subscription = client.create_subscription(500, handler)
        nodes = [
            cylinder_node,
            jamming_node
        ]
        # We subscribe to data changes for two nodes (variables).
        subscription.subscribe_data_change(nodes)
        print("We successfully subscribed to all handlers!")
        print("Waiting for events...")


"""[summary]
The datachange notification gets called, when a change in a node we subscribed to is found.
When in the subscribed node the alarm value is set to true we call PostAlarmToRasaServer.
"""
class SubscriptionHandler():
    def __init__(self, session_id):
        self.session_id = session_id

    def datachange_notification(self, node: Node, val, data):
        if val is True :
            t = PostAlarmToRasaServer(node, self.session_id)
            t.start()                    


"""[summary]
This gets called when an alarm on the opcua server occurs. When this happens we get the alarm message and the faulty part name
of the alarmed node from the opcua server and then notify tis alarm to our rasa server with a post message.
"""
class PostAlarmToRasaServer(threading.Thread):
    def __init__(self, node, session_id):
        super().__init__()
        self.node = node
        self.session_id = session_id

    def run(self):
        url = f'http://localhost:5005/conversations/{self.session_id}/trigger_intent?output_channel=latest'
        data = {}
        message = self.node.get_parent().get_child("1:active_message").get_value().Text
        cylinder_name = self.node.get_parent().get_parent().get_child("1:variable").get_value().Value

        if "CylinderAlarm" in self.node.nodeid.to_string():
            print("🛑 Clinder Alarm!\n", message)

            data = {
                "name": "EXTERNAL_warn_cylinder_alarm",
                "entities": {
                    "cylinder_with_alarm" : cylinder_name,
                    "alarm_message" : message,
                }
            }

        elif "JammingMaterialAlarm" in self.node.nodeid.to_string():
            message = self.node.get_parent().get_child("1:active_message").get_value().Text
            print("🛑 Jamming Material Alarm!\n", message)

            data = {
                "name": "EXTERNAL_warn_jamming_material_alarm",
                "entities": {
                    "alarm_message" : message,
                }
            }
        else:
            print("An event happened which is not defined! Stopping callback server!")
            raise SystemExit

        try:
            r = requests.post(url, json = data)
            print(f"POST-RESPONSE-MESSAGE: {r.text}")
        except Exception:
            raise SystemExit