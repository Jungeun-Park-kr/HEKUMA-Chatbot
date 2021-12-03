# This files contains your custom actions which can be used to run
# custom Python code.

# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions



from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# Add codes for using OPCUA
from asyncua import Client
import asyncio
import time


class ActionMyFirstBoolean(Action):

    def name(self) -> Text:
        return "action_utter_supply_myfirstboolean_info"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: #TODO: check if domain necessary

        url = "opc.tcp://10.0.0.107:4840" 
        async with Client(url=url) as client:
            var = client.get_node("ns=1;s=AGENT.OBJECTS.MyFirstBoolean")
            dispatcher.utter_message(text=f"Value of my MyFirstBoolean is {await var.read_value()}") 

        return []


class ActionSafetyDoor(Action):

    def name(self) -> Text:
        return "action_utter_supply_safety_door_info"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: #TODO: check if domain necessary

        door_number = next(tracker.get_latest_entity_values("door_number"), None)

        url = "opc.tcp://10.0.0.107:4840" 
        async with Client(url=url) as client:
            
            s = "AGENT.OBJECTS.Machine.SafetyZones.SafetyZone1.SafetyDoor_" + door_number + ".isOpen"
            node_id = "ns=1;s=" + s
            #TODO: what if there is safety door with number 'door_number'
            door_status_async = client.get_node(node_id)
            door_status = await door_status_async.read_value()

            # # Check user input value and safety door value
            # dispatcher.utter_message(text=f"User input safety door number: {door_number}")
            # dispatcher.utter_message(text=f"Door state of number {door_number}: {DoorStates[int(door_number)]}")

            if door_status: # True:open, False:closed
                dispatcher.utter_message(text=f"Safety door {door_number} is currently unlocked.") 
            else : 
                dispatcher.utter_message(text=f"Safety door {door_number} is currently locked.")

        return []

class ActionAlarm(Action):
    
    def name(self) -> Text:
        return "action_utter_supply_alarm"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: #TODO: check if domain necessary

        #module_number = next(tracker.get_latest_entity_values("module_number"), None)

        url = "opc.tcp://10.0.0.107:4840" 
        async with Client(url=url) as client:
            
            #fetch alarm
            s = "AGENT.OBJECTS.Machine.SafetyZones.SafetyZone1.SafetyModule_" + module_number + ".isOpen"
            node_id = "ns=1;s=" + s
            #TODO: what if there is safety module with number 'module_number'
            module_status_async = client.get_node(node_id)
            module_status = await module_status_async.read_value()

            # # Check user input value and safety module value
            # dispatcher.utter_message(text=f"User input safety module number: {module_number}")
            # dispatcher.utter_message(text=f"Module state of number {module_number}: {ModuleStates[int(module_number)]}")

            if module_status: # True:on, False:off
                dispatcher.utter_message(text=f"Alarm! Jamming of materian in {module_number}.") 
            else : 
                dispatcher.utter_message(text=f"Stop?")

        return []

class ActionTellID(Action):
    """Informs the user about the conversation ID."""

    def name(self) -> Text:
        return "action_tell_id"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        conversation_id = tracker.sender_id

        dispatcher.utter_message(f"The ID of this conversation is '{conversation_id}'.")
        dispatcher.utter_message(
            f"Trigger an intent with: \n"
            f'curl -H "Content-Type: application/json" '
            f'-X POST -d \'{{"name": "EXTERNAL_dry_plant", '
            f'"entities": {{"plant": "Orchid"}}}}\' '
            f'"http://localhost:5005/conversations/{conversation_id}'
            f'/trigger_intent?output_channel=latest"'
        )

        return []