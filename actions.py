from typing import Dict, Text, Any, List, Union

from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
from rasa_sdk.events import SlotSet
import json

class CreateMailForm(FormAction):
    """custom form action."""

    def name(self) -> Text:
        """Unique identifier of the form."""

        return "createmail_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill."""

        return ["login", "domain"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
        or a list of them, where a first match will be picked."""

        return {
            "login": [self.from_entity(entity="user_in", intent=["login"]), self.from_text()],
            "domain": [self.from_entity(entity="user_in", intent=["domain"]), self.from_text() ],
        }

    @staticmethod
    def notlogin_db() -> List[Text]:
        """Database of not supported login."""

        return [
            "admin", "abuse", "webmaster", "contact", "postmaster", "hostmaster"
        ]

    def validate_login(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate login value."""

        if value.lower() not in self.notlogin_db():
            # validation succeeded, set the value of the "login" slot to value
            return {"login": value}
        else:
            dispatcher.utter_message(template="utter_wrong_login")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"login": None}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do after all required slots are filled."""

        mail = "{}@{}".format(tracker.get_slot("login"), tracker.get_slot("domain"))
        SlotSet("email", mail)
        dispatcher.utter_message("Temperory email created: {}".format(mail))

        return []


class ReadMailForm(Action):
    """Schedules a reminder, supplied with the last message's entities."""

    def name(self) -> Text:
        return "readmail_action"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        import requests
        resp = requests.get("https://www.1secmail.com/api/v1/?action=getMessages&login={}&domain={}".format(tracker.get_slot("login"),tracker.get_slot("domain")))
        resp = resp.json()
        if len(resp) == 0:
            dispatcher.utter_message("No email available in this email-address")
        else:
            for mail in resp:
                # dispatcher.utter_message(", please use id: {} for reading email".format(mail["from"], mail["subject"], mail["id"]))
                dispatcher.utter_button_message(text="You have a mail from: {}, with subject line: {}".format(mail["from"], mail["subject"]), buttons=[{
                    "title":"read", "payload": mail["id"]
                }])
        return []


class ReadSingleMailForm(Action):
    def name(self) -> Text:
        return "readsinglemail_action"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        import requests

        url = "https://www.1secmail.com/api/v1/?action=readMessage&login={}&domain={}&id={}".format(tracker.get_slot("login"),tracker.get_slot("domain"), next(tracker.get_latest_entity_values("mailid")))
        resp = requests.get(url)
        try:
            resp = resp.json()
            dispatcher.utter_message("{}".format(resp["textBody"]))
            SlotSet("mailid", None)
        except json.decoder.JSONDecodeError:
            dispatcher.utter_message("Mail not found")
            SlotSet("mailid", None)
        return []
