//
//  ContentView.swift
//  iPhoneCompanion
//
//  Created by QueryQuest Agent
// メインビュー - 最小限のステータス表示
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var companionClient: CompanionClient
    
    var body: some View {
        VStack(spacing: 16) {
            // 状態表示
            StatusView(status: companionClient.status)
                .padding(.top, 40)
            
            // 更新ボタン
            Button(action: {
                Task {
                    await companionClient.refreshStatus()
                }
            }) {
                Label("更新", systemImage: "arrow.clockwise")
            }
            .buttonStyle(.borderedProminent)
            .padding(.horizontal, 40)
            
            Spacer()
            
            // 詳細表示（オプション）
            if companionClient.showDetail {
                DetailView(status: companionClient.status)
                    .transition(.move(edge: .bottom))
            }
        }
        .padding(.bottom, 40)
    }
}

#Preview {
    ContentView()
        .environmentObject(CompanionClient())
}
