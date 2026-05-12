//
//  DetailView.swift
//  iPhoneCompanion
//
//  Created by QueryQuest Agent
// 詳細表示ビュー（オプション）
//

import SwiftUI

struct DetailView: View {
    let status: CompanionStatus?
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("詳細情報")
                .font(.headline)
            
            if let status = status {
                // メモリ使用状況
                VStack(alignment: .leading, spacing: 4) {
                    Text("メモリ使用状況")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                    
                    Text("作業メモリ：\(status.memoryUsage.working) エントリ")
                    Text("短期メモリ：\(status.memoryUsage.shortTerm) エントリ")
                    Text("長期メモリ：\(status.memoryUsage.longTerm) エントリ")
                    Text("意味的メモリ：\(status.memoryUsage.semantic) エントリ")
                    Text("合計：\(status.memoryUsage.total) エントリ")
                }
                .font(.caption)
                .padding()
                .background {
                    RoundedRectangle(cornerRadius: 8)
                        .fill(.thinMaterial)
                }
                
                // ヘルスステータス
                VStack(alignment: .leading, spacing: 4) {
                    Text("ヘルスステータス")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                    
                    Text("状態：\(status.healthStatus)")
                    Text("エラー率：\(String(format: "%.2f", status.errorRate * 100))%")
                }
                .font(.caption)
                .padding()
                .background {
                    RoundedRectangle(cornerRadius: 8)
                        .fill(.thinMaterial)
                }
            }
        }
        .padding()
        .background {
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
        }
        .padding(.horizontal, 20)
    }
}

#Preview {
    DetailView(status: CompanionStatus(
        state: "RUNNING",
        isRunning: true,
        memoryUsage: MemoryStatus(working: 10, shortTerm: 20, longTerm: 50, semantic: 5, total: 85),
        healthStatus: "healthy",
        errorRate: 0.01
    ))
}
