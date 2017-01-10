# Custom Slot Types
import json
with open('../../devices.json') as json_data:
    devices = d = json.load(json_data)

f=open('./LIST_OF_DEVICES', 'w')
for device in devices['device']:
    print >>f, device['name']
f.close()

groups_all=[]
f=open('./LIST_OF_GROUPS', 'w')
for device in devices['device']:
    groups_all.append(device['group'])
f=open('./LIST_OF_GROUPS', 'w')
for group in set(groups_all):
    print >>f, group
f.close()

actions_all=[]
for device in devices['device']:
    for action in device['action']:
        actions_all.append(action['name'])
f=open('./LIST_OF_ACTIONS', 'w')
for action_unique in set(actions_all):
    print >>f, action_unique
f.close()
