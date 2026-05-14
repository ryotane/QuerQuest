//
//  StatusView.swift
//  iPhoneCompanion
//
//  Created by QueryQuest Agent
// 最小限の状態表示ビュー
//

import SwiftUI

struct StatusView: View {
    let status: CompanionStatus?
    
    var body: some View {
        VStack(spacing: 8) {
            // 状態アイコン
            Image(systemName: status?.icon ?? "questionmark.circle")
                .font(.system(size: 64))
                .foregroundStyle(status?.color ?? .gray)
                .symbolEffect(.variableColor.iterative, isActive: status?.isRunning ?? false)
            
            // 状態テキスト
            Text(status?.state ?? "UNKNOWN")
                .font(.title2)
                .fontWeight(.semibold)
            
            // サブタイトル
            if let lastUpdate = status?.lastUpdate {
                Text("最終更新：\(formatDate(lastUpdate))")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .padding()
        .background {
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
        }
        .padding(.horizontal, 20)
    }
    
    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm:ss"
        return formatter.string(from: date)
    }
}

#Preview {
    VStack(spacing: 20) {
        StatusView(status: CompanionStatus(state: "RUNNING", isRunning: true))
        StatusView(status: CompanionStatus(state: "WAITING", isRunning: false))
        StatusView(status: CompanionStatus(state: "COMPLETE", isRunning: false))
    }
}
