import os, os.path

import cherrypy
import pygatt
import requests
import json

def bluetooth_action(domain, path, parameters):
    rcode = "{\"action\":false}"
    try:
        adapter = pygatt.GATTToolBackend()
        adapter.start()
        device = adapter.connect(domain, address_type=pygatt.BLEAddressType.random)
        magic_bytes = bytearray(b'')
        for p in parameters.split(','):
            magic_bytes = magic_bytes + bytearray([int(p,16)])
        device.char_write_handle(int(path,16), magic_bytes, wait_for_response=True)
        rcode = "{\"action\":true}"
    finally:
        adapter.stop()
    return rcode

def http_action(domain, path, parameters):
    uri = "http://" + domain + path + parameters
    rcode = requests.get(uri)
    return rcode.status_code

def do_device_action(protocol, domain, path, parameters):
    print(protocol, domain, path, parameters)
    if protocol == u'bluetooth':
        rcode = bluetooth_action(domain, path, parameters)
    elif protocol == u'http':
        rcode = http_action(domain, path, parameters)
    return rcode

def do_toggle(device):
    toggle = toggles[device['name']]
    toggle += 1
    num_actions = len(device['action'])
    if toggle >= num_actions:
        toggle = 0
    toggles[device['name']] = toggle
    parameters = device['action'][toggle]['parameters']
    rcode = do_device_action(device['protocol'], device['domain'], device['path'], parameters)
    return rcode

def device_action(name, action):
    rcode = "{\"device\":false}"
    for device in devices['device']:
        if device['name'] == name:
            if action == "Toggle":
                rcode = do_toggle(device)
            else:
                toggle = 0
                for a in device['action']:
                    if a['name'] == action:
                        # Update toggle on the new action
                        toggles[device['name']] = toggle
                        rcode = do_device_action(device['protocol'], device['domain'], device['path'], a['parameters'])
                    else:
                        toggle += 1
    return rcode

def group_action(name, action):
    for device in devices['device']:
        if device['group'] == name:
            device_action(device['name'], action)
    return "{\"group\":ok}"

class Control(object):
    @cherrypy.expose
    def index(self):
        return open('newindex.html')
    @cherrypy.expose
    def config(self):
        return open('devices.json')

    # Allows a simple get 
    # curl "http://blueberrypi.lan/deviceg?name=Main%20Light&action=Toggle"
    @cherrypy.expose
    def deviceg(self, name, action):
        rcode = device_action(name, action)
        return rcode
    @cherrypy.expose
    def groupg(self, name, action):
        rcode = group_action(name, action)
        return rcode

@cherrypy.expose
class ControlDeviceWebService(object):
    @cherrypy.tools.accept(media='text/plain')
    def PUT(self, name, action):
        rcode = device_action(name, action)
        return rcode

@cherrypy.expose
class ControlGroupWebService(object):
    @cherrypy.tools.accept(media='text/plain')
    def PUT(self, name, action):
        rcode = group_action(name, action)
        return rcode

if __name__ == '__main__':
    conf = {
        'global': {
            'server.socket_host': '0.0.0.0',
            'server.socket_port': 8080,
        },

        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/device': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/group': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/css': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './css'
        }
    }
    with open('devices.json') as json_data:
        devices = d = json.load(json_data)
    toggles = {}
    for device in devices['device']:
        toggles[device['name']] = 0
    print(toggles)

    webapp = Control()
    webapp.device = ControlDeviceWebService()
    webapp.group = ControlGroupWebService()
    cherrypy.quickstart(webapp, '/', conf)

