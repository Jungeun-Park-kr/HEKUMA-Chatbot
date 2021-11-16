# This files contains your custom actions which can be used to run
# custom Python code.

# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# Add codes for using OPCUA
from asyncua import Client
import asyncio
import time


class ActionSafetyDoor(Action):

    def name(self) -> Text:
        return "action_utter_supply_safety_door_info"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        door_number = next(tracker.get_latest_entity_values("door_number"), None)

        url = "opc.tcp://localhost:4840/freeopcua/server/" #"opc.tcp://0.0.0.0:4840/freeopcua/server/" 
        async with Client(url=url) as client:
            uri = 'http://examples.freeopcua.github.io'
            idx = await client.get_namespace_index(uri)
            
            # getting a variable node using its browse path
            Doors = await client.nodes.root.get_child(["0:Objects", f"{idx}:MyObject", f"{idx}:MyVariable"])
            DoorStates = await Doors.read_value()

            # # Check user input value and safety door value
            # dispatcher.utter_message(text=f"User input safety door number: {door_number}")
            # dispatcher.utter_message(text=f"Door state of number {door_number}: {DoorStates[int(door_number)]}")

            if DoorStates[int(door_number)-1]: # True:open, False:closed
                dispatcher.utter_message(text=f"Safety door {door_number} is currently unlocked.") 
            else : 
                dispatcher.utter_message(text=f"Safety door {door_number} is currently locked.")

        return []


class ActionSafetyDoors(Action):

    def name(self) -> Text:
        return "action_utter_supply_all_safety_doors_info"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        url = "opc.tcp://localhost:4840/freeopcua/server/" #"opc.tcp://0.0.0.0:4840/freeopcua/server/"
        async with Client(url=url) as client:
            uri = 'http://examples.freeopcua.github.io'
            idx = await client.get_namespace_index(uri)
            
            # getting a variable node using its browse path
            Doors = await client.nodes.root.get_child(["0:Objects", f"{idx}:MyObject", f"{idx}:MyVariable"])
        
            dispatcher.utter_message(text=f"**** door state (1-10) : {await Doors.read_value()} ****")

            for idx, val in enumerate(await Doors.read_value()):
                if val:
                    dispatcher.utter_message(text=f"Safety door {idx+1} is currently unlocked.") #True:open
                else :
                    dispatcher.utter_message(text=f"Safety door {idx+1} is currently locked.") #False:closed 

        return []
