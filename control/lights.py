import os, os.path

import cherrypy
import pygatt
import requests

def control_light(address, action):
    magic_handle =  0x0043
    adapter = pygatt.GATTToolBackend()
    try:
        adapter.start()
        device = adapter.connect(address)
        if action == "On":
            magic_bytes = bytearray([0xcc, 0x23, 0x33])
        elif action == "Off":
            magic_bytes = bytearray([0xcc, 0x24, 0x33])
        else:
            magic_bytes = bytearray([0xcc, 0x23, 0x33])
        device.char_write_handle(magic_handle, magic_bytes, wait_for_response=True)
    finally:
        adapter.stop()

def control_lock(address, action):
    if action == "Open":
        para = "on"
    elif action == "Closed":
        para = "off"
    else:
        para = off
    uri = "http://" + address + ".lan/cgi-bin/json.cgi?set=" + para
    r = requests.get(uri)
    return r.status_code

class Control(object):
    @cherrypy.expose
    def index(self):
        return open('index.html')
    @cherrypy.expose
    def config(self):
        return open('config.json')
    @cherrypy.expose
    def slight(self, address, action):
        control_light(address, action)
        return "Ok"

@cherrypy.expose
class ControlLightWebService(object):
    @cherrypy.tools.accept(media='text/plain')
    def PUT(self, action, address):
        control_light(address, action)
        return "Ok"
    # Easy for esp8266


@cherrypy.expose
class ControlLockWebService(object):
    @cherrypy.tools.accept(media='text/plain')
    def PUT(self, action, address):
        control_lock(address, action)
        return "Ok"

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
        '/light': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/lock': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/css': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './css'
        }
    }
    webapp = Control()
    webapp.light = ControlLightWebService()
    webapp.lock  = ControlLockWebService()
    cherrypy.quickstart(webapp, '/', conf)

