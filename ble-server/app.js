var os = require('os');
var bleno = require('bleno');
var Characteristic = bleno.Characteristic;

var WhiteboardService = require('./whiteboard-service');
var primaryService = new WhiteboardService();
var draw = primaryService.drawCharacteristic();

bleno.on('stateChange', function(state) {
    console.log('on -> stateChange: ' + state);

    if (state === 'poweredOn') {
        bleno.startAdvertising('WHITEBOARD', [primaryService.uuid]);
    } else {
        bleno.stopAdvertising();
    }
});

bleno.on('advertisingStart', function(error) {
    console.log('on -> advertisingStart: ' + (error ? 'error ' + error : 'success'));

    if (!error) {
        bleno.setServices([primaryService], function(error){
            console.log('setServices: '  + (error ? 'error ' + error : 'success'));
        });
    }
});

bleno.on('accept', function(address) {
    console.log('bluetooth connected: ' + address);
});

bleno.on('disconnect', function(address) {
    console.log('bluetooth disconnected: ' + address);
});

draw.on('writeRequest', function(data, offset, writeWithoutResponse, callback) {
  console.log('data: ' + data.toString('hex'));
});
