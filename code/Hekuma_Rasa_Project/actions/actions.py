"""[summary]
This files contains your custom actions which can be used to run custom Python code.
"""

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SessionStarted, ActionExecuted
from asyncua import Client

# The next 4 lines are needed if you have problems importing the handler.py in opcua_server
from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

from callback_server.server import SubscribeAll

# This should point to the ip address of the opc ua (atvise) server
url = "opc.tcp://141.82.52.161:4840"
#url = "opc.tcp://10.0.0.107:4840"


"""[summary]
ActionSessionStart is a default rasa action which is always called when a new conversation starts.
By defining the action in the actions.py we override this actions and adjust it to our needs.
What we added is the async SubscribeAll call which subscribe to all alarm nodes defined on the opcua atvise server.
"""
class ActionSessionStart(Action):

    def name(self) -> Text:
        return "action_session_start"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # the session should begin with a `session_started` event
        events = [SessionStarted()]

        # an `action_listen` should be added at the end as a user message follows
        events.append(ActionExecuted("action_listen"))

        await SubscribeAll.run(tracker.sender_id)

        return events


"""[summary]
This action gets called on the question if a certain door is closed or not.

use case example:

User: Is safety door 1 closed?
Bot: Safety door 1 is currently unlocked.
"""
class ActionSafetyDoor(Action):

    def name(self) -> Text:
        return "action_utter_supply_safety_door_info"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

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

            dispatcher.utter_message(text=f"Safety door with the number {door_number} is not available.")

        return []


"""[summary]
This action gets called on the question when was a component changed the last time

use case example:

User: When was the coil roll cahnged the last time?
Bot: The coil roll was last changed today at 2:35 pm, i.e. 2 hours and 20 minutes ago.
"""
class ActionComponentLastChanged(Action):

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


"""[summary]
This action gets called on the question where a certain component is located

use case example:

User: Where is component -Z2.3z2?
Bot: The component -Z2.3z2 ist part of the coil roll which is in tip1 of the clamping station.
"""
class ActionGetComponentLocation(Action):

    def name(self) -> Text:
        return "action_utter_supply_component_location_info"

    async def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        component_name = next(tracker.get_latest_entity_values("component"), None)

        if component_name is None:
            print("Rasa could'nt determine any entities!")
            return []

        result = await get_component_location_from_opcua(component_name)

        if result:
            dispatcher.utter_message(text=f"The component {component_name} ist part of the {result['component']} which is in {result['tip']} of the {result['station']}.")
            return []
        else:
            dispatcher.utter_message(text=f"There is no component with the name {component_name}")
            return []


"""[summary]
Very similar to ActionGetComponentLocation but this operated on slots instead of entities.
"""
class ActionGetAlarmCylinderLocation(Action):
    def name(self) -> Text:
        return "action_utter_supply_alarm_cylinder_location_info"

    async def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        component_name = tracker.get_slot('cylinder_with_alarm')
        if component_name is None:
            print("Rasa could'nt determine any slot with the name: cylinder_with_alarm!")
            return []

        result = await get_component_location_from_opcua(component_name)

        if result:
            dispatcher.utter_message(text=f"The component {component_name} ist part of the {result['component']} which is in {result['tip']} of the {result['station']}.")
            return []
        else:
            dispatcher.utter_message(text=f"There is no component with the name {component_name}")
            return []


"""[summary]
This action gets called on the intent EXTERNAL_warn_cylinder_alarm which is called in the handler.py
This just prints an alarm message to our console
"""
class ActionUtterWarnCylinderAlarm(Action):
    def name(self) -> Text:
        return "action_utter_warn_cylinder_alarm"

    async def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

                alarm_message = next(tracker.get_latest_entity_values("alarm_message"), None)
                message = "Attention!\n" + alarm_message
                dispatcher.utter_message(text=message)
                return[]


"""[summary]
This action gets called on the intent EXTERNAL_warn_jamming_material_alarm which is called in the handler.py
This just prints an alarm message to our console
"""
class ActionUtterWarnJammingMaterialAlarm(Action):
    def name(self) -> Text:
        return "action_utter_warn_jamming_material_alarm"

    async def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

                alarm_message = next(tracker.get_latest_entity_values("alarm_message"), None)
                message = "Alarm!\n" + alarm_message
                dispatcher.utter_message(text=message)
                return[]


"""[summary]
This action gets called after we asked the machine how to fix the current occured problem. We
get the solution from a opcua server node. 
"""
class ActionHowToFixJammingMaterialAlarm(Action):
    def name(self) -> Text:
        return "action_how_to_fix_jamming_material_alarm"

    async def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

                async with Client(url=url) as client:
                    # get the solution from opcua server
                    solution = await client.get_node("ns=1;s=AGENT.OBJECTS.Machine.Alarms.General.JammingMaterialAlarm.Alarm.solution_info").get_value()
                    dispatcher.utter_message(text=solution)
                return[]


"""[summary]
This action gets called if we demanded to open a certain door. We check if this door exists and if the 
door is closed we then open it by changing a value on the opcua server
"""
class ActionOpenSafetyDoor(Action):
    def name(self) -> Text:
        return "action_open_safety_door"

    async def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

                door_number = next(tracker.get_latest_entity_values("door_number"), None)
                if door_number is None:
                    dispatcher.utter_message("Door number is missing. Just try again")
                else :
                    async with Client(url=url) as client:

                        safety_zones_path = "ns=1;s=" + "AGENT.OBJECTS.Machine.SafetyZones"
                        safety_zones_node = client.get_node(safety_zones_path)
                        safety_zones = await safety_zones_node.get_children()

                        for zone in safety_zones:

                            safety_doors = await client.get_node(zone).get_children()

                            for door in safety_doors:
                                if f'{door}'.rsplit('_', 1)[1] == door_number:
                                    door_state = client.get_node(f'{door}' + ".isOpen")
                                    door_value = await client.get_node(f'{door}' + ".isOpen").read_value()
                                    if door_value is False:
                                        await door_state.write_value(True)
                                        message = "Safety door "+door_number+" is opened"
                                        dispatcher.utter_message(text=message)
                                    else:
                                        message = "Safety door "+door_number+" is already opened"
                                        dispatcher.utter_message(text=message)
                return[]


"""[summary]
This action gets called after we demanded a restart of a specific module. 
We check here if the module is faulty and if so we then get asked for confirmation.

use case example:

Bot: Do you want to restart the faulty module „+TIP1“?
User: Yes
"""
class ActionInfoRestartModuleSpecific(Action):
    
    def name(self) -> Text:
        return "action_utter_supply_module_specific_info"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        module_number = next(tracker.get_latest_entity_values("module_number"), None)

        async with Client(url=url) as client:
            
            acp = client.get_node("ns=1;s=AGENT.OBJECTS.Machine.Alarms.General.JammingMaterialAlarm.Alarm.Condition.value")
            
            module_status=await acp.read_value()

            if module_status: # True:faulty module
                dispatcher.utter_message(text=f"Do you want to restart faulty module {module_number}?") 
            else : 
                dispatcher.utter_message(text=f"Module {module_number} isn't a faulty module")
            
        return []


"""[summary]
This action is the followup to the action ActionInfoRestartModuleSpecific. Here we actually resart the module
by changing a value on the opcua server.
"""
class ActionRestartFaultyModule(Action):
    
    def name(self) -> Text:
        return "action_restart_faulty_module"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        async with Client(url=url) as client:
            
            acb = client.get_node("ns=1;s=AGENT.OBJECTS.Machine.Alarms.General.JammingMaterialAlarm.Alarm.Condition.value")
            
            module_status=await acb.read_value()

            if module_status: # True:faulty module
                await acb.write_value(False)
                dispatcher.utter_message(text=f"Module restarted") 
            
        return []


"""[summary]
This function gets the location from the opcua server by searching all station subfolders for the component we 
look for and then return on a hit all parent folders the component is actually located.

[returns]
dict with three components: component, tip, station
"""
async def get_component_location_from_opcua(component_name):
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
                    if component_name.lower() == equipment_id_number.lower():

                        component = f'{component}'.rsplit('.', 1)[1]
                        tip = f'{tip}'.rsplit('.', 1)[1]
                        station = f'{station}'.rsplit('.', 1)[1]
                        return {
                              "component": component,
                              "tip": tip,
                              "station": station
                            }
        
        return False