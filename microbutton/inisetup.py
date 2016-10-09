import uos
import network
from flashbdev import bdev

def wifi():
    import ubinascii
    ap_if = network.WLAN(network.AP_IF)
    essid = b"MicroButton-%s" % ubinascii.hexlify(ap_if.config("mac")[-3:])
    ap_if.config(essid=essid, authmode=network.AUTH_WPA_WPA2_PSK, password=b"microButton")

def check_bootsec():
    buf = bytearray(bdev.SEC_SIZE)
    bdev.readblocks(0, buf)
    empty = True
    for b in buf:
        if b != 0xff:
            empty = False
            break
    if empty:
        return True
    fs_corrupted()

def fs_corrupted():
    import time
    while 1:
        print("""\
FAT filesystem appears to be corrupted. If you had important data there, you
may want to make a flash snapshot to try to recover it. Otherwise, perform
factory reprogramming of MicroPython firmware (completely erase flash, followed
by firmware programming).
""")
        time.sleep(3)

def setup():
    check_bootsec()
    print("Performing initial setup")
    wifi()
    uos.VfsFat.mkfs(bdev)
    vfs = uos.VfsFat(bdev, "")
    setup_button()
    with open("/boot.py", "w") as f:
        f.write("""\
# This file is executed on every boot (including wake-boot from deepsleep)
import machine
import network
import socket
import time

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
    s.send(bytes('GET /%s HTTP/1.0\\r\\nHost: %s\\r\\n\\r\\n' % (path, host), 'utf8'))
    while True:
        data = s.recv(2048)
        if data:
            print(str(data, 'utf8'), end='')
        else:
            break

def flash_led(led, num):
    for l in range(num):
         time.sleep_ms(500)
         led.value(not led.value())
    time.sleep_ms(1500)

# LED ON to give visual feedback
led = machine.Pin(2, machine.Pin.OUT)
led.value(0)
try:
    do_connect(config_mc.ssid, config_mc.passwd)
except:
    flash_led(led, 8)
try:
    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        print('woke from a deep sleep')
        http_get(config_mc.resetURL)
    else:
        print('power on or hard reset')
        http_get(config_mc.powerOnURL)
except:
    flash_led(led, 4)
led.value(1)
machine.deepsleep()
""")
    return vfs


def setup_button():
    import socket
    import machine
    import network
    import json

# Every byte counts, hence poor indenting 
    html = """
<html><body><head><meta charset="utf-8"></meta><title>MicroButton</title></head>
<form action="#"><div id="n">%s:</div><input type="text" id="v" value="" maxlength="80"/><br><input type="hidden" id="k" value="%s" /><input type="button" id="s" value="Set" onclick="sV();"/><br/></form><p id="l"></p>
<script>
function sV() {
var v=document.getElementById('v').value;
var k=document.getElementById('k').value;
var obj ={};
obj[k] =v;
var j=JSON.stringify(obj);
var x=new XMLHttpRequest();
x.open("POST", "/");
x.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
x.send(j);
x.onloadend = function () {
var r=(x.responseText);
if ( r == "D" ) {
 document.getElementById("s").style.visibility = "hidden"
 d = document.getElementById('l');
 d.innerHTML = d.innerHTML + 'Set ' + j + '<br/>Done';
 } else {
 d = document.getElementById('l');
 d.innerHTML = d.innerHTML + 'Set ' + j + '<br/>';
 document.getElementById("n").innerHTML = r;
 document.getElementById("v").value = "";
 document.getElementById("k").value = r;
}
}
};
</script></body></html>"""

    config_names = ["ssid", "passwd", "resetURL", "powerOnURL", "D"]
    #Setup Socket WebServer
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(0)
    i = 0
    config = {}
    while i < len(config_names)-2 :
        conn, addr = s.accept()
        request = conn.recv(2048)
        srequest = str(request)
        print("Content = %s" % srequest)
        j = srequest.find('{')
        if j != -1:
            je = srequest.find('}')
            if je != -1:
                print(j, je, srequest[j:je+1])
                t = json.loads(srequest[j:je+1])
                k = list(t.keys())[0]
                rvalue = t[k]
                print(k, rvalue)
                i = config_names.index(k)
                response = config_names[i+1]
                config[k] = rvalue
            else:
                response = config_names[0]
        else:
            response = html % (config_names[0], config_names[0])
        conn.send(response)
        conn.close()
        
    f = open('config_mc.py', 'w')
    for c in range(0, len(config)):
        f.write("%s = %r\n" % (list(config.keys())[c], list(config.values())[c]))
    f.close()

