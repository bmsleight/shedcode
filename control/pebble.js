var method = 'GET';
var url = 'http://blueberrypi.lan/';

// Create the request
var request = new XMLHttpRequest();
var json;
var menu = [];
var menui = 0;
var maxlines = 5;

function makeMenu()  {
    var item;
    var l = json.lights.length;
    var k = json.lightActions.length;
    var i = 0;
    var j = 0;
    for (i = 0; i < l ; i++) {
        for (j = 0; j < k ; j++) {
            item = {name: json.lights[i].DisplayName, address: json.lights[i].address, action: json.lightActions[j], put: 'light'};        
            menu.push(item);
        }        
    } 
    l = json.locks.length;
    k = json.lockActions.length;
    for (i = 0; i < l ; i++) {
        for (j = 0; j < k ; j++) {
            item = {name: json.locks[i].DisplayName, address: json.locks[i].address, action: json.lockActions[j], put: 'lock'};        
            menu.push(item);
        }        
    }   
}

function drawMenu()  {
    var l = 0;
    var s  = 0;
    if (menui<maxlines-1){
        s = 0;
        l = maxlines;
    } else if (menui>menu.length-maxlines)
    {
        s = menu.length-maxlines;
        l = menu.length;
    } else {
        s = menui;
        l = menui + maxlines;
    }
    var body = "";
    for (var i = s; i < l ; i++) {
        if (i == menui) {
            body = body + "»";    
        } else {
            body = body + "  ";                
        }
        body = body + menu[i].name + " " + menu[i].action + "\n";
    }    
    simply.text({
        title: 'Control Shed',
        body: body,
    }, true); 
}

function  takeControl()
{
    console.log(menu[menui]);
    var xhr = new XMLHttpRequest();
    xhr.open('PUT', url+menu[menui].put);
    xhr.withCredentials = true;
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.responseType = 'text';
    var data = "address="+menu[menui].address+"&action="+menu[menui].action;
    xhr.onload = function () {
        if (xhr.readyState === xhr.DONE) {
                console.log(xhr.response);
                console.log(xhr.responseText);
                console.log(data);        
        }
    };
    xhr.send(data);
}

// Specify the callback for when the request is completed
request.onload = function() {
  try {
    // Transform in to JSON
    json = JSON.parse(this.responseText);
    console.log(json);
    makeMenu();
    drawMenu();
  } catch(err) {
    console.log('Error parsing JSON response!');
  }
};

// Send the request
request.open(method, url+'config');
request.send();




console.log('Control Shed!');

simply.on('singleClick', function(e) {
    console.log(util2.format('single clicked $button!', e));
    if (e.button === 'down') {
        menui++;
        if (menui === menu.length) {
            menui = 0;
        } 
    } else if (e.button === 'up') {
        menui--;
        if (menui < 0) {
            menui = menu.length-1;
        }
    } 
    console.log(menui);
    drawMenu();
    if (e.button === 'select') {
        takeControl();
    }
});

/*
simply.on('longClick', function(e) {
  console.log(util2.format('long clicked $button!', e));
  simply.vibe();
  simply.scrollable(e.button !== 'select');
});

simply.on('accelTap', function(e) {
  console.log(util2.format('tapped accel axis $axis $direction!', e));
  simply.subtitle('Tapped ' + (e.direction > 0 ? '+' : '-') + e.axis + '!');
});

simply.text({
  title: 'Control Shed',
  body: 'This is a demo. Press buttons or tap the watch!',
}, true);

*/
