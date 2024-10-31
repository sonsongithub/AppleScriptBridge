//
//  AppDelegate.swift
//  AppleScriptBridge
//
//  Created by Yuichi Yoshida on 2024/10/14.
//

import Cocoa
import ScriptingBridge




@main
class AppDelegate: NSObject, NSApplicationDelegate {

    func applicationDidFinishLaunching(_ aNotification: Notification) {
        if let musicApp: MusicApplication = SBApplication(bundleIdentifier: "com.apple.Music") {
            if let playlist = musicApp.playlists?().first {
                print(playlist.name)
            }
            if let song = musicApp.currentTrack {
                print(song.name)
                print(song.artist)
            }
            musicApp.AirPlayDevices?().forEach { device in
                print(device.name)
            }
            if let device = musicApp.AirPlayDevices?().first {
            }
        }
    }

    func applicationWillTerminate(_ aNotification: Notification) {
        // Insert code here to tear down your application
    }

    func applicationSupportsSecureRestorableState(_ app: NSApplication) -> Bool {
        return true
    }
}

