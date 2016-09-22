import os, os.path

import cherrypy
import pygatt


def control_light(address, action):
    magic_handle =  0x0043
    adapter = pygatt.GATTToolBackend()
    try:
        adapter.start()
        device = adapter.connect(address)
        if action == "on":
            magic_bytes = bytearray([0xcc, 0x23, 0x33])
        elif action == "off":
            magic_bytes = bytearray([0xcc, 0x24, 0x33])
        else:
            magic_bytes = bytearray([0xcc, 0x23, 0x33])
        device.char_write_handle(magic_handle, magic_bytes, wait_for_response=True)
    finally:
        adapter.stop()


class Control(object):
    @cherrypy.expose
    def index(self):
        return open('index.html')
    @cherrypy.expose
    def config(self):
        return open('config.json')

@cherrypy.expose
class ControlLightWebService(object):
    @cherrypy.tools.accept(media='text/plain')
    def PUT(self, action, address):
#        print("Light", action, address)
        control_light(address, action)
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
        '/css': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './css'
        }
    }
    webapp = Control()
    webapp.light = ControlLightWebService()
    cherrypy.quickstart(webapp, '/', conf)

