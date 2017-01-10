import logging
import requests

from flask import Flask
from flask_ask import Ask, request, session, question, statement


app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)


@ask.launch
def launch():
    speech_text = 'Shed control ready '
    return question(speech_text).reprompt(speech_text).simple_card('ControlShed', speech_text)


@ask.intent('ControlShedDeviceIntent', mapping={'device': 'Device', 'group': 'Group', 'action': 'Action'})
def toggle_1lights(device, group, action):
    flag = False
    if device is None:
        device = 'No device'
        flag = True
    if group is None:
        group = 'No group'
        flag = True
    if action is None:
        action = 'No action'
        flag = True
    if flag:
        speech_text = 'Sorry control could not find ' + device.title() + ' ' + group.title() + ' ' + action.title()
    else:
        speech_text = 'Control is putting ' + device.title() + ' ' + group.title() + ' ' + action.title()
        payload = {'name': device.title(), 'action': action.title()}
        r = requests.get('http://shed.lan/deviceg', params=payload)
        print payload
    return statement(speech_text).simple_card('Control', speech_text)

@ask.intent('ControlShedGroupIntent', mapping={'group': 'Group', 'action': 'Action'})
def toggle_1lights(group, action):
    flag = False
    if group is None:
        group = 'No group'
        flag = True
    if action is None:
        action = 'No action'
        flag = True
    if flag:
        speech_text = 'Sorry control could not find ' + group.title() + ' ' + action.title()
    else:
        speech_text = 'Control is putting all ' + group.title() + ' ' + action.title()
        payload = {'name': group.title().strip('-s'), 'action': action.title()}
        r = requests.get('http://shed.lan/groupg', params=payload)
        print payload
    return statement(speech_text).simple_card('Control', speech_text)


@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'Say Control Device Name, action'
    return question(speech_text).reprompt(speech_text).simple_card('ControlShed', speech_text)


@ask.session_ended
def session_ended():
    return "", 200


if __name__ == '__main__':
    app.run(debug=True)

