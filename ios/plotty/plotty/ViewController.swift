/*
    Copyright (C) 2016 Apple Inc. All Rights Reserved.
    See LICENSE.txt for this sample’s licensing information
    
    Abstract:
    The primary view controller that hosts a `CanvasView` for the user to interact with.
*/

import UIKit

class ViewController: UIViewController, BleWhiteboardDelegate {
   
    let notificationCenter = NotificationCenter.default
    var lastTouch: UITouch?
    
    // MARK: Properties
    var visualizeAzimuth = false
    var whiteboard:BleWhiteboard?
    
    func onWhiteboardConnected() {
        
    }
    
    func onWhiteboardDisconnected(){
        
    }

    let reticleView: ReticleView = {
        let view = ReticleView(frame: CGRect.null)
        view.translatesAutoresizingMaskIntoConstraints = false
        view.isHidden = true
        
        return view
    }()

    var canvasView: CanvasView {
        return view as! CanvasView
    }
    
    // MARK: View Life Cycle
    override func viewDidLoad() {
        self.whiteboard = BleWhiteboard(self)
        self.whiteboard?.startScan()
        canvasView.addSubview(reticleView)
    }
    
    func postTouchNotification(touch: UITouch, lift: Bool) {
        let view = touch.view!
        let frame = view.frame
        let ratio = frame.width / frame.height
        
        let location = touch.preciseLocation(in: view)
        
        let userInfo: [String:Any] = ["x": location.x / frame.width, "y": location.y / frame.height, "timestamp": touch.timestamp, "lift": lift, "ratio": ratio]
        self.notificationCenter.post(name: Notification.Name.init("DRAW_POINT"), object: self, userInfo: userInfo)
    }
    
    // MARK: Touch Handling
    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        
        if let touch = touches.first {
            self.lastTouch = touch
            postTouchNotification(touch: touch, lift: false)
        }
        
        canvasView.drawTouches(touches, withEvent: event)
        
        if visualizeAzimuth {
            for touch in touches {
                if touch.type == .stylus {
                    reticleView.isHidden = false
                    updateReticleViewWithTouch(touch, event: event)
                }
            }
        }
    }
    
    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        
        for touch in touches {
            if self.lastTouch != nil && self.lastTouch! == touch {
                postTouchNotification(touch: touch, lift: false)
                break
            }
        }
        
        canvasView.drawTouches(touches, withEvent: event)
        
        if visualizeAzimuth {
            for touch in touches {
                if touch.type == .stylus {
                    updateReticleViewWithTouch(touch, event: event)
                    
                    // Use the last predicted touch to update the reticle.
                    guard let predictedTouch = event?.predictedTouches(for: touch)?.last else { return }
                    
                    updateReticleViewWithTouch(predictedTouch, event: event, isPredicted: true)
                }
            }
        }
    }
    
    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        
        for touch in touches {
            if self.lastTouch != nil && self.lastTouch! == touch {
                postTouchNotification(touch: touch, lift: true)
                self.lastTouch = nil
                break
            }
        }
        
        canvasView.drawTouches(touches, withEvent: event)
        canvasView.endTouches(touches, cancel: false)
        
        if visualizeAzimuth {
            for touch in touches {
                if touch.type == .stylus {
                    reticleView.isHidden = true
                }
            }
        }
    }
    
    override func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent?) {
		canvasView.endTouches(touches, cancel: true)
        
        if visualizeAzimuth {
            for touch in touches {
                if touch.type == .stylus {
                    reticleView.isHidden = true
                }
            }
        }
    }
    
    override func touchesEstimatedPropertiesUpdated(_ touches: Set<UITouch>) {
        canvasView.updateEstimatedPropertiesForTouches(touches)
    }
    
    // MARK: Actions
    
    @IBAction func clearView(_ sender: UIBarButtonItem) {
        canvasView.clear()
    }
    
    @IBAction func toggleDebugDrawing(_ sender: UIButton) {
        canvasView.isDebuggingEnabled = !canvasView.isDebuggingEnabled
        visualizeAzimuth = !visualizeAzimuth
        sender.isSelected = canvasView.isDebuggingEnabled
    }
    
    @IBAction func toggleUsePreciseLocations(_ sender: UIButton) {
        canvasView.usePreciseLocations = !canvasView.usePreciseLocations
        sender.isSelected = canvasView.usePreciseLocations
    }
    
    // MARK: Rotation
    
    override var shouldAutorotate : Bool {
        return true
    }
    
    override var supportedInterfaceOrientations : UIInterfaceOrientationMask {
        return [.landscapeLeft, .landscapeRight]
    }
    
    // MARK: Convenience
    
    func updateReticleViewWithTouch(_ touch: UITouch?, event: UIEvent?, isPredicted: Bool = false) {
        guard let touch = touch, touch.type == .stylus else { return }
        
        reticleView.predictedDotLayer.isHidden = !isPredicted
        reticleView.predictedLineLayer.isHidden = !isPredicted
        
        let azimuthAngle = touch.azimuthAngle(in: view)
        let azimuthUnitVector = touch.azimuthUnitVector(in: view)
        let altitudeAngle = touch.altitudeAngle
        
        if isPredicted {
            reticleView.predictedAzimuthAngle = azimuthAngle
            reticleView.predictedAzimuthUnitVector = azimuthUnitVector
            reticleView.predictedAltitudeAngle = altitudeAngle
        }
        else {
            let location = touch.preciseLocation(in: view)
            reticleView.center = location
            reticleView.actualAzimuthAngle = azimuthAngle
            reticleView.actualAzimuthUnitVector = azimuthUnitVector
            reticleView.actualAltitudeAngle = altitudeAngle
        }
    }
}
