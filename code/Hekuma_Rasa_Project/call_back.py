class getMessageFromAlarm(threading.Thread):
    def __init__(self, node, dispatcher):
        super().__init__()
        self.node = node
        self.dispather = dispatcher

    def run(self):
        if "CylinderAlarm" in self.node.nodeid.to_string():
            message = self.node.get_parent().get_child("1:active_message").get_value().Text
            print("🛑 Clinder Alarm!\n", message)
            self.dispather.utter_message("🛑 Clinder Alarm!\n", message)

        elif "JammingMaterialAlarm" in self.node.nodeid.to_string():
            message = self.node.get_parent().get_child("1:active_message").get_value().Text
            print("🛑 Jamming Material Alarm!\n", message)
            self.dispather.utter_message("🛑 Jamming Material Alarm!\n", message)

class SubscriptionHandler():
    def __init__(self, dispatcher) -> None:
        self._dispatcher = dispatcher

    def datachange_notification(self, node: Node, val, data):
        if val is True :
            t = getMessageFromAlarm(node, self._dispatcher)
            t.start()                    


class ActionRegisterListener(Action):
    def name(self) -> Text:
        return "action_register_listener"
    
    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
            client = ClientOld(url='opc.tcp://10.0.0.107:4840')
            client.connect()

            CylinderNode = client.get_node("ns=1;s=AGENT.OBJECTS.Machine.Alarms.General.CylinderAlarm_1.Alarm.Condition.value")
            JammingNode = client.get_node("ns=1;s=AGENT.OBJECTS.Machine.Alarms.General.JammingMaterialAlarm.Alarm.Condition.value")

            handler = SubscriptionHandler(dispatcher) 
            # We create a Client Subscription.
            subscription = client.create_subscription(500, handler)
            nodes = [
                CylinderNode,
                JammingNode
            ]
            # We subscribe to data changes for two nodes (variables).
            subscription.subscribe_data_change(nodes)
            dispatcher.utter_message(text="Register Alarm Listeners Succeeded")
            return []

class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_session_start"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        client = ClientOld(url='opc.tcp://10.0.0.107:4840')
        client.connect()

        CylinderNode = client.get_node("ns=1;s=AGENT.OBJECTS.Machine.Alarms.General.CylinderAlarm_1.Alarm.Condition.value")
        JammingNode = client.get_node("ns=1;s=AGENT.OBJECTS.Machine.Alarms.General.JammingMaterialAlarm.Alarm.Condition.value")

        handler = SubscriptionHandler(dispatcher) 
        # We create a Client Subscription.
        subscription = client.create_subscription(500, handler)
        nodes = [
            CylinderNode,
            JammingNode
        ]
        # We subscribe to data changes for two nodes (variables).
        subscription.subscribe_data_change(nodes)
        return []

