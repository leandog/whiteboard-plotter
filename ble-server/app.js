#!/usr/bin/env node

var os = require('os');
var bleno = require('bleno');
var zerorpc = require("zerorpc");
var Characteristic = bleno.Characteristic;

var WhiteboardService = require('./whiteboard-service');
var primaryService = new WhiteboardService();
var draw = primaryService.drawCharacteristic();

var client = new zerorpc.Client();
client.connect("tcp://127.0.0.1:4242");

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
    client.invoke("on_connect", "test", function(error, res, more) {
      console.log(res);
    });
}.bind(client));

bleno.on('disconnect', function(address) {
    console.log('bluetooth disconnected: ' + address);
    client.invoke("on_disconnect", "test", function(error, res, more) {
      console.log(res);
    });
});

draw.on('draw', function(drawData) {
  client.invoke("draw", drawData, function(error, res, more) {
    console.log(res);
  });
}.bind(client));

