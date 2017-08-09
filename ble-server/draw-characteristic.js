var util = require('util');
var bleno = require('bleno');

var CHARACTERISTIC_NAME = 'DRAW';
var PACKET_SIZE=17;

function DrawCharacteristic(state) {
  DrawCharacteristic.super_.call(this, {
    uuid: '00029CE3-83FE-496D-866B-4E3A580994CB',
    properties: ['write'],
    secure: [],
    descriptors: [
        new bleno.Descriptor({
            uuid: '2901',
            value: CHARACTERISTIC_NAME,
        }),
    ],
  });
}

util.inherits(DrawCharacteristic, bleno.Characteristic);

DrawCharacteristic.prototype.onWriteRequest = function(data, offset, withoutResponse, callback) {
    console.log('onWriteRequest');
    if(offset) {
        console.log("ATTR_NOT_LONG");
        callback(this.RESULT_ATTR_NOT_LONG);
    }
    else if (data.length !== PACKET_SIZE) {
        console.log("INVALID_LENGTH: " + data.length);
        callback(this.RESULT_INVALID_ATTRIBUTE_LENGTH);
    }
    else {
        var x = data.readUIntBE(0, 4);
        var y = data.readUIntBE(4, 4);
        var timestamp = data.readUIntBE(8, 8);
        var lift = data.readUIntBE(16, 1);
        console.log("x: " + x);
        console.log("y: " + y);
        console.log("timestamp: " + timestamp);
        console.log("lift: " + lift);
        callback(this.RESULT_SUCCESS);
    }
};

module.exports = DrawCharacteristic;


