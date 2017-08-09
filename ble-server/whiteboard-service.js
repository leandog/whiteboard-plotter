var util = require('util');
var bleno = require('bleno');

var DrawCharacteristic = require('./draw-characteristic');

function WhiteboardService(state) {
    bleno.PrimaryService.call(this, {
        uuid: '00019CE3-83FE-496D-866B-4E3A580994CB',
        characteristics: [
            new DrawCharacteristic(state),
        ]
    });
}

util.inherits(WhiteboardService, bleno.PrimaryService);

WhiteboardService.prototype.drawCharacteristic = function() {
  return this.characteristics[0];
};

module.exports = WhiteboardService;
