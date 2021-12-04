from opcua import Client as ClientOld, Node
import threading
import requests # https://www.geeksforgeeks.org/get-post-requests-using-python/


class SubscribeAll():

    async def run(session_id):
        print("Trying to connect to opcua server...")
        client = ClientOld(url='opc.tcp://141.82.52.161:4840')
        client.connect()
        print("Connected to opcua server! Trying to grab all the necessary nodes...")
        CylinderNode = client.get_node("ns=1;s=AGENT.OBJECTS.Machine.Alarms.General.CylinderAlarm_1.Alarm.Condition.value")
        JammingNode = client.get_node("ns=1;s=AGENT.OBJECTS.Machine.Alarms.General.JammingMaterialAlarm.Alarm.Condition.value")
        print("We got all nodes! Subscibe to handlers...")
        handler = SubscriptionHandler(session_id) 
        # We create a Client Subscription.
        subscription = client.create_subscription(500, handler)
        nodes = [
            CylinderNode,
            JammingNode
        ]
        # We subscribe to data changes for two nodes (variables).
        subscription.subscribe_data_change(nodes)
        print("We successfully subscribed to all handlers!")
        print("Waiting for events...")


class SubscriptionHandler():
    def __init__(self, session_id):
        self.session_id = session_id

    def datachange_notification(self, node: Node, val, data):
        if val is True :
            t = PostAlarmToRasaServer(node, self.session_id)
            t.start()                    


class PostAlarmToRasaServer(threading.Thread):
    def __init__(self, node, session_id):
        super().__init__()
        self.node = node
        self.session_id = session_id

    def run(self):
        url = f'http://localhost:5005/conversations/{self.session_id}/trigger_intent?output_channel=latest'
        data = {}
        message = self.node.get_parent().get_child("1:active_message").get_value().Text

        if "CylinderAlarm" in self.node.nodeid.to_string():
            print("🛑 Clinder Alarm!\n", message)

            data = {
                "name": "warn_external_alarm",
                "entities": {
                    "component_with_alarm" : "-Z2.3z2",
                }
            }

        elif "JammingMaterialAlarm" in self.node.nodeid.to_string():
            message = self.node.get_parent().get_child("1:active_message").get_value().Text
            print("🛑 Jamming Material Alarm!\n", message)

            data = {
                "name": "warn_external_alarm",
                "entities": {
                    "component_with_alarm" : "SomeOtherComponent",
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