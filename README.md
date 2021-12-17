# HEKUMA Chatbot

This is the repository of the project group chatbots 2021 

# Project members:

| Name | E-Mail |
|-----------|-----------|
| Saliu Bah | Saliu.Bah@HS-Augsburg.DE |
| Cristina Vizan Olmedo | - |
| Jung Eun Park | - |
| Marco Lenz | Marco.Lenz@HS-Augsburg.DE |

# Installation

To use rasa and rasa x please follow the installation instructions in help\raza_installation_guide.md


# Notes

- The .db files store the conversions that have already been made using rasa x. If you do not want this, then you have to delete the .db files.
- The index.html is a basic chatbot interface ui which you can use to interact with your rasa server
- callback_server/server.py is a non rasa file. This file is used to attach handlers to our opc ua server nodes and continually checking these nodes for changes which then informs our rasa action server about this change. This file gets automatically called if you run the rasa actions server 