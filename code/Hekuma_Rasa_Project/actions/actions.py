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
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:  # TODO: check if domain necessary

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
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:  # TODO: check if domain necessary

        door_number = next(
            tracker.get_latest_entity_values("door_number"), None)

        url = "opc.tcp://10.0.0.107:4840"
        async with Client(url=url) as client:

            s = "AGENT.OBJECTS.Machine.SafetyZones.SafetyZone1.SafetyDoor_" + door_number + ".isOpen"
            node_id = "ns=1;s=" + s
            # TODO: what if there is safety door with number 'door_number'
            door_status_async = client.get_node(node_id)
            door_status = await door_status_async.read_value()

            # # Check user input value and safety door value
            # dispatcher.utter_message(text=f"User input safety door number: {door_number}")
            # dispatcher.utter_message(text=f"Door state of number {door_number}: {DoorStates[int(door_number)]}")

            if door_status:  # True:open, False:closed
                dispatcher.utter_message(
                    text=f"Safety door {door_number} is currently unlocked.")
            else:
                dispatcher.utter_message(
                    text=f"Safety door {door_number} is currently locked.")

        return []


class ActionComponentLastChanged(Action):

    # When was the coil roll changed last time?
    # The coil roll was last changed today at 2:35 pm, i.e. 2hrs and 2min ago

    def name(self) -> Text:
        return "action_utter_supply_component_last_changed_info"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        door_number = next(
            tracker.get_latest_entity_values("door_number"), None)

        url = "opc.tcp://10.0.0.107:4840"
        async with Client(url=url) as client:

            s = "AGENT.OBJECTS.Machine.SafetyZones.SafetyZone1.SafetyDoor_" + door_number + ".isOpen"
            node_id = "ns=1;s=" + s
            # TODO: what if there is safety door with number 'door_number'
            door_status_async = client.get_node(node_id)
            door_status = await door_status_async.read_value()

            # # Check user input value and safety door value
            # dispatcher.utter_message(text=f"User input safety door number: {door_number}")
            # dispatcher.utter_message(text=f"Door state of number {door_number}: {DoorStates[int(door_number)]}")

            if door_status:  # True:open, False:closed
                dispatcher.utter_message(
                    text=f"Safety door {door_number} is currently unlocked.")
            else:
                dispatcher.utter_message(
                    text=f"Safety door {door_number} is currently locked.")

        return []


class ActionGetComponentLocation(Action):

    # When was the coil roll changed last time?
    # The coil roll was last changed today at 2:35 pm, i.e. 2hrs and 2min ago

    def name(self) -> Text:
        return "action_utter_supply_component_location_info"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        door_number = next(
            tracker.get_latest_entity_values("door_number"), None)

        url = "opc.tcp://10.0.0.107:4840"
        async with Client(url=url) as client:

            s = "AGENT.OBJECTS.Machine.SafetyZones.SafetyZone1.SafetyDoor_" + door_number + ".isOpen"
            node_id = "ns=1;s=" + s
            # TODO: what if there is safety door with number 'door_number'
            door_status_async = client.get_node(node_id)
            door_status = await door_status_async.read_value()

            # # Check user input value and safety door value
            # dispatcher.utter_message(text=f"User input safety door number: {door_number}")
            # dispatcher.utter_message(text=f"Door state of number {door_number}: {DoorStates[int(door_number)]}")

            if door_status:  # True:open, False:closed
                dispatcher.utter_message(
                    text=f"Safety door {door_number} is currently unlocked.")
            else:
                dispatcher.utter_message(
                    text=f"Safety door {door_number} is currently locked.")

        return []
