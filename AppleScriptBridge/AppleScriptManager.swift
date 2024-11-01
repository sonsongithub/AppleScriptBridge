//
//  applescript.swift
//  AppleScriptBridge
//
//  Created by Yuichi Yoshida on 2024/11/01.
//

import Foundation

protocol CreatableFromNSAppleEventDescriptor {
    static func get(a:NSAppleEventDescriptor) throws -> Self
}

extension Int : CreatableFromNSAppleEventDescriptor {
    static func get(a:NSAppleEventDescriptor) throws -> Self {
        return Int(a.int32Value)
    }
}

extension String : CreatableFromNSAppleEventDescriptor {
    static func get(a:NSAppleEventDescriptor) throws -> Self {
        guard let string = a.stringValue else {
            throw MyError.canNotGetString
        }
        return string
    }
}

enum MyError: Error {
    case appleScriptError
    case appleScriptExecutionError(Dictionary<String, Any>)
    case canNotGetString
}

class AppleScriptManager {
    
    func call(script: String) throws -> NSAppleEventDescriptor {
        var error: NSDictionary?
        guard let scriptObject = NSAppleScript(source: script) else {
            throw MyError.appleScriptError
        }
        let output = scriptObject.executeAndReturnError(&error)
        if let error {
            var dicitonary: [String: Any] = [:]
            for key in error.allKeys {
                if let key = key as? String {
                    dicitonary[key] = error[key]
                }
            }
            throw MyError.appleScriptExecutionError(dicitonary)
        }
        return output
    }

    func execute<A: CreatableFromNSAppleEventDescriptor>(script: String) throws -> A {
        let output = try call(script: script)
        return try A.get(a: output)
    }
    
    func execute<A: CreatableFromNSAppleEventDescriptor>(script: String) throws -> [A] {
        let output = try call(script: script)
        var array: [A] = []
        for i in 0..<output.numberOfItems {
            if let obj = output.atIndex(i) {
                array.append(try A.get(a: obj))
            }
        }
        return array
    }
    
    func getVolume() throws -> Int {
        let script = """
        tell application "Music"
            set sound_volume to sound volume
        end tell 
        sound_volume
        """
        return try execute(script: script)
    }
    
    func getAirplayDevices() throws -> [String] {
        let script = """
        tell application "Music"
            set device_list to AirPlay devices
            set device_names to {}
            repeat with aDevice in device_list
                set end of device_names to name of aDevice
            end repeat
        end tell
        return device_names
        """
        return try execute(script: script)
    }
}
