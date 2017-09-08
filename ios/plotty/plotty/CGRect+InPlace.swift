import Foundation
import UIKit

extension CGRect {
    mutating func offsetInPlace(dx: CGFloat, dy: CGFloat) {
        self = self.offsetBy(dx: dx, dy: dy)
    }
    mutating func unionInPlace(_ rect:CGRect) {
        self = self.union(rect)
    }
    mutating func insetInPlace(dx: CGFloat, dy: CGFloat) {
        self = self.insetBy(dx: dx, dy: dy)
    }
}
