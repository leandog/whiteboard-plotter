import UIKit
import CoreBluetooth
import NotificationCenter

class BleWhiteboard: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate {

    let WHITEBOARD_SERVICE_UUID = CBUUID(string: "00019CE3-83FE-496D-866B-4E3A580994CB")
    let DRAW_CHARACTERISTIC_UUID = CBUUID(string: "00029CE3-83FE-496D-866B-4E3A580994CB")
    let dispatchQueue = DispatchQueue.init(label: "com.usefulbits.plotty.BleQueue")
    let operationQueue = OperationQueue.init()

    let notificationCenter = NotificationCenter.default

    var centralManager:CBCentralManager?
    var whiteboard:CBPeripheral?
    var whiteboardService:CBService?
    var drawCharacteristic:CBCharacteristic?
    var isStarted:Bool
    var delegate: BleWhiteboardDelegate

    struct drawData {
        var x: UInt32; // 4
        var y: UInt32; // 4
        var timestamp: UInt32; // 4
        var ratio: UInt32; // 4
        var lift: Bool; // 1
    }

    init(_ bleDelegate: BleWhiteboardDelegate) {
        isStarted = false
        delegate = bleDelegate
        super.init()

        centralManager = CBCentralManager.init(delegate: self, queue: self.dispatchQueue)
        notificationCenter.addObserver(forName: Notification.Name.init("DRAW_POINT"), object:nil, queue: self.operationQueue, using: self.onDraw)
    }

    func onDraw(_ notification: Notification) {
        if let userInfo = notification.userInfo {
            
            //todo: fixed point + round
            var x = CGFloat(0)
            if let userX = userInfo["x"] as? CGFloat {
                x = (userX * 1000000).rounded()
            }
            
            var y = CGFloat(0)
            if let userY = userInfo["y"] as? CGFloat {
                y = (userY * 1000000).rounded()
            }
            
            let ratio = ((userInfo["ratio"] as! CGFloat) * 1000000).rounded()
            
            var timestamp = Double(0)
            if let userTimestamp = userInfo["timestamp"] as? Double {
                timestamp = userTimestamp * 1000
            }
            
            let lift =  userInfo["lift"] as! Bool
 
            var dataStruct = drawData(x: UInt32(x), y: UInt32(y), timestamp: UInt32(timestamp), ratio: UInt32(ratio), lift: lift)
            //var dataStruct = drawData(x: 1, y: 2, ratio: 3, timestamp: 4, lift: true)
            let data = Data(bytes: &dataStruct, count: MemoryLayout<drawData>.size)
                
            self.whiteboard!.writeValue(data, for: drawCharacteristic!, type: .withResponse)
        }
    }

    func startScan() {
        isStarted = true
        startScanIfPoweredUp()
    }

    func stop() {
        isStarted = false
        if let manager = centralManager {
            manager.stopScan()
        }
    }

    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        if(isStarted) {
            startScanIfPoweredUp()
        } else {
            //delegate.onError()
        }
    }

    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, advertisementData: [String: Any], rssi RSSI: NSNumber) {
        print("discovered")
        whiteboard = peripheral
        peripheral.delegate = self
        central.connect(peripheral, options: nil)
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        print("peripheral connected")
        peripheral.delegate = self
        discoverCharacteristicsOnPeripheral(peripheral)
        peripheral.discoverServices([WHITEBOARD_SERVICE_UUID])
    }

    func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) {
        print("error")
    }

    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        print("disconnected")
        whiteboardService = nil
        whiteboard = nil
        drawCharacteristic = nil
        delegate.onWhiteboardDisconnected()
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        discoverCharacteristicsOnPeripheral(peripheral)
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverIncludedServicesFor service: CBService, error: Error?) {
        print("didDiscoverIncludedServices: %@", service)
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        if let characteristics = service.characteristics {
            for characteristic in characteristics {
                if characteristic.uuid.isEqual(DRAW_CHARACTERISTIC_UUID) {
                    drawCharacteristic = characteristic
                    whiteboard = peripheral
                    delegate.onWhiteboardConnected()
                }
            }
        }
    }

    private func discoverCharacteristicsOnPeripheral(_ peripheral:CBPeripheral) {
        if let services = peripheral.services {
            for service in services {
                if service.uuid.isEqual(WHITEBOARD_SERVICE_UUID) {
                    whiteboardService = service
                    break
                }
            }
        }

        if let service = whiteboardService {
            if let peripheral = whiteboard {
                peripheral.discoverCharacteristics([DRAW_CHARACTERISTIC_UUID], for: service)
            }
        }
    }

    private func startScanIfPoweredUp() {
        if let manager = centralManager {
            if(manager.state == .poweredOn) {
                manager.scanForPeripherals(withServices: [WHITEBOARD_SERVICE_UUID])
            }
        }
    }
}
