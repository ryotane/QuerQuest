//
//  iPhoneCompanionApp.swift
//  iPhoneCompanion
//
//  Created by QueryQuest Agent
// 静かな remote runtime window
//

import SwiftUI

@main
struct iPhoneCompanionApp: App {
    @StateObject private var companionClient = CompanionClient()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(companionClient)
        }
    }
}
