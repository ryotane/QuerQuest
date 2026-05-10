"""
Observability Integration - Observabilityとの統合
Project_036: P2 - iPhone Companion Implementation

Observability Managerとの統合を提供します。
"""

from typing import Dict, List, Optional


class ObservabilityIntegration:
    """Observabilityとの統合"""
    
    def __init__(self, observability_manager):
        """
        ObservabilityIntegrationを初期化
        
        Args:
            observability_manager: Observability Managerインスタンス
        """
        self.observability = observability_manager
    
    def get_health_status(self) -> dict:
        """
        ヘルスステータスを取得
        
        Returns:
            dict: ヘルスステータス
        """
        return self.observability.get_health_status()
    
    def get_metrics_summary(self) -> dict:
        """
        メトリクスサマリーを取得
        
        Returns:
            dict: メトリクスサマリー
        """
        return self.observability.get_metrics_summary()
    
    def get_alerts(self) -> List[Dict]:
        """
        アラート一覧を取得
        
        Returns:
            List[Dict]: アラート一覧
        """
        return self.observability.get_alerts()
    
    def get_status_export(self, format: str = "json") -> str:
        """
        ステータスエクスポートを取得
        
        Args:
            format: エクスポート形式 (json/text)
            
        Returns:
            str: エクスポートされたステータス
        """
        if format == "json":
            return self.observability.export_json()
        elif format == "text":
            return self.observability.export_text()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def is_healthy(self) -> bool:
        """
        システムが健全か判定
        
        Returns:
            bool: 健全か
        """
        health = self.observability.get_health_status()
        return health.get("status") == "healthy"
    
    def has_critical_alerts(self) -> bool:
        """
        重大なアラートがあるか判定
        
        Returns:
            bool: 重大なアラートがあるか
        """
        alerts = self.observability.get_alerts()
        return any(alert.get("severity") == "critical" for alert in alerts)
