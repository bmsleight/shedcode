import machine
import network
import socket

import config_mc

def do_connect(ssid, passwd):
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, passwd)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

def http_get(url):
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    while True:
        data = s.recv(100)
        if data:
            print(str(data, 'utf8'), end='')
        else:
            break

# LED ON to give visual feedback
led = machine.PWM(machine.Pin(2), freq=1000)
do_connect(config_mc.ssid, config_mc.passwd)
if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print('woke from a deep sleep')
    http_get(config_mc.resetURL)
else:
    print('power on or hard reset')
    http_get(config_mc.powerOnURL)

machine.deepsleep()
