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

#url = "opc.tcp://141.82.144.254:4840"
url = "opc.tcp://10.0.0.107:4840"

class ActionMyFirstBoolean(Action):

    def name(self) -> Text:
        return "action_utter_supply_myfirstboolean_info"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:  # TODO: check if domain necessary

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

        async with Client(url=url) as client:

            safety_zones_path = "ns=1;s=" + "AGENT.OBJECTS.Machine.SafetyZones"
            safety_zones_node = client.get_node(safety_zones_path)
            safety_zones = await safety_zones_node.get_children()

            for zone in safety_zones:

                safety_doors = await client.get_node(zone).get_children()

                for door in safety_doors:
                    if f'{door}'.rsplit('_', 1)[1] == door_number:
                        door_state = await client.get_node(f'{door}' + ".isOpen").read_value()

                        if door_state: 
                            dispatcher.utter_message(
                                text=f"Safety door {door_number} in safety zone {f'{zone}'.rsplit('e', 1)[1]} is currently unlocked.")
                        else:
                            dispatcher.utter_message(
                                text=f"Safety door {door_number} in safety zone {f'{zone}'.rsplit('e', 1)[1]} is currently locked.")

                        return []

            dispatcher.utter_message(
                                text=f"Safety door with the number {door_number} is not available.")
        return []


class ActionComponentLastChanged(Action):

    # When was the coil roll changed last time?
    # The coil roll was last changed today at 2:35 pm, i.e. 2hrs and 2min ago

    def name(self) -> Text:
        return "action_utter_supply_component_last_changed_info"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        component = next(tracker.get_latest_entity_values("component"), None)

        async with Client(url=url) as client:

            actions_path = "ns=1;s=" + "AGENT.OBJECTS.Machine.Actions"
            actions_node = client.get_node(actions_path)
            actions = await actions_node.get_children()

            for action in actions:
                name_path = f'{action}' + ".Name"
                name = await client.get_node(name_path).read_value()

                if name == component.lower():
                    last_fin_path = f'{action}' + ".lastFinished"
                    last_fin = await client.get_node(last_fin_path).read_value()
                    dispatcher.utter_message(
                    text="The {} was last changed on {}!".format(name, last_fin))
                    return []

            dispatcher.utter_message(text="Sorry but there is no component called {}...".format(name))

        return []


class ActionGetComponentLocation(Action):

    # Where is component [-Z2.3z2](component)?
    # Component is in...

    def name(self) -> Text:
        return "action_utter_supply_component_location_info"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        component_name = next(tracker.get_latest_entity_values("component"), None)

        async with Client(url=url) as client:

            stations_path = "ns=1;s=" + "AGENT.OBJECTS.Machine.Stations"
            stations_node = client.get_node(stations_path)
            stations = await stations_node.get_children()

            for station in stations:
                tips = await client.get_node(station).get_children()

                for tip in tips:
                    components = await client.get_node(f'{tip}' + ".Components").get_children()

                    for component in components:
                        master_data = client.get_node(f'{component}' + ".MasterData")
                        equipment_id_number = await client.get_node(f'{master_data}' + ".equipmentIdNumber").read_value()

                        if component_name == equipment_id_number.lower():
                            component = f'{component}'.rsplit('.', 1)[1]
                            tip = f'{tip}'.rsplit('.', 1)[1]
                            station = f'{station}'.rsplit('.', 1)[1]
                            
                            dispatcher.utter_message(text=f"The component {component_name} ist part of the {component} which is in {tip} of the {station}.")
                            return []

            dispatcher.utter_message(text=f"There is no component with the name {component_name}")

        return []
