//
//  CompanionClient.swift
//  iPhoneCompanion
//
//  Created by QueryQuest Agent
// Python Companion Core との HTTP 連携
//

import Foundation
import Combine

class CompanionClient: ObservableObject {
    @Published var status: CompanionStatus?
    @Published var showDetail: Bool = false
    @Published var errorMessage: String?
    
    private let baseURL: String
    private var timer: Timer?
    
    init(baseURL: String = "http://localhost:8000") {
        self.baseURL = baseURL
        // 自動更新（30 秒ごと）
        startAutoRefresh()
    }
    
    deinit {
        stopAutoRefresh()
    }
    
    // ステータス更新
    func refreshStatus() async {
        do {
            let (data, response) = try await URLSession.shared.data(
                from: URL(string: "\(baseURL)/api/status")!
            )
            
            if let httpResponse = response as? HTTPURLResponse {
                guard httpResponse.statusCode == 200 else {
                    throw CompanionError.httpError(httpResponse.statusCode)
                }
            }
            
            let decoded = try JSONDecoder().decode(CompanionStatus.self, from: data)
            await MainActor.run {
                self.status = decoded
                self.errorMessage = nil
            }
        } catch {
            await MainActor.run {
                self.errorMessage = "ステータスの取得に失敗しました：\(error.localizedDescription)"
            }
        }
    }
    
    // 詳細表示の切り替え
    func toggleDetail() {
        showDetail.toggle()
    }
    
    // 自動更新の開始
    private func startAutoRefresh() {
        stopAutoRefresh()
        timer = Timer.scheduledTimer(withTimeInterval: 30.0, repeats: true) { [weak self] _ in
            Task {
                await self?.refreshStatus()
            }
        }
    }
    
    // 自動更新の停止
    private func stopAutoRefresh() {
        timer?.invalidate()
        timer = nil
    }
}

enum CompanionError: Error {
    case httpError(Int)
    case decodingError
    case networkError
}
