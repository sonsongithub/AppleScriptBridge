# AppleScriptBridge
Swift code to manage "Music.app" using AppleScript.

# Capability and privacy setting

At first, you have to add the following privacy authentication phrase to the `Info.plist`.

<img src="https://github.com/user-attachments/assets/0fc516b3-2b51-46b2-ae11-c7d0f63e85c7">

## Permit the application to use AppleEvent.

<img src="https://github.com/user-attachments/assets/915f8ab9-8b79-4747-a5b2-bd459c596aa0">

## Permit to communicate with Music.app.

<img src="https://github.com/user-attachments/assets/f067a910-3460-4388-8045-424acdfa2cd4">

# ScriptBridge

## Create Music.h using `sdef`

```
sdef /System/Applications/Music.app | sdp -fh --basename Music
```

## Import header file

Added Music.h to the Xcode project.

## Create Bridging Header

At first, create a dummy objective-c sources and then Xcode will ask you to create a bridging header.

<img src="https://github.com/user-attachments/assets/e02c4c85-4b30-4f4d-bfde-c8293e96d14f" width=600>

<img src="https://github.com/user-attachments/assets/acea7e87-3727-402d-b49f-aa7a4c417b09" width=600>

<img src="https://github.com/user-attachments/assets/3e6a889d-1c54-42e1-9f92-d8a170ff040e" width=600>

You can add the following line to the bridging header.

```objc
//
//  Use this file to import your target's public headers that you would like to expose to Swift.
//

#import "Music.h"
```

## Prepare interface to write Swift code

You have to prepare the interface to write Swift code.
But, I've already implemented [the python script](https://github.com/sonsongithub/AppleScriptBridge/blob/main/converter.py) to extract the Swift interface from the header file.

```bash
python converter.py ./AppleScriptBridge/Music.h ./AppleScriptBridge/Music.swift
```

## Write Swift code

```swift
if let musicApp: MusicApplication = SBApplication(bundleIdentifier: "com.apple.Music") {
    if let song = musicApp.currentTrack {
        print(song.name)
        print(song.artist)
    }
}
```

# NSAppleScript

We can also use `NSAppleScript` to execute AppleScript.
This way requres us to write AppleScript codes and implement some classes or structs to handle the result. Refer to [the example](https://github.com/sonsongithub/AppleScriptBridge/blob/main/AppleScriptBridge/AppleScriptManager.swift).
