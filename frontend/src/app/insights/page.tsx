"use client";
import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import EmptyState from "@/components/ui/EmptyState";
import { analyticsApi } from "@/lib/api";
import { RiskAlert } from "@/types";
import { severityColor, cn } from "@/lib/utils";
import { Lightbulb, CheckCircle, AlertTriangle, AlertCircle, Info } from "lucide-react";

function SeverityIcon({ severity }: { severity: string }) {
  if (severity === "high") return <AlertCircle className="w-4 h-4 text-red-500" />;
  if (severity === "medium") return <AlertTriangle className="w-4 h-4 text-amber-500" />;
  return <Info className="w-4 h-4 text-blue-500" />;
}

export default function InsightsPage() {
  const [alerts, setAlerts] = useState<RiskAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    analyticsApi.alerts()
      .then((r) => setAlerts(r.data))
      .catch((e) => setError(e.response?.data?.detail || "Failed to load"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <AppLayout><LoadingSpinner text="Analyzing portfolio..." /></AppLayout>;

  const high = alerts.filter((a) => a.severity === "high");
  const medium = alerts.filter((a) => a.severity === "medium");
  const low = alerts.filter((a) => a.severity === "low");

  return (
    <AppLayout>
      <div className="space-y-5">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Insights & Alerts</h1>
          <p className="text-sm text-gray-500 mt-0.5">Rules-based risk analysis of your portfolio</p>
        </div>

        {error && (
          <div className="flex items-center gap-2 text-red-600 bg-red-50 px-4 py-3 rounded-lg text-sm">
            <AlertCircle className="w-4 h-4" /> {error}
          </div>
        )}

        {/* Summary bar */}
        <div className="grid grid-cols-3 gap-4">
          <div className="card border-red-200 bg-red-50">
            <p className="stat-label text-red-600">High Priority</p>
            <p className="text-3xl font-bold text-red-700 mt-1">{high.length}</p>
          </div>
          <div className="card border-amber-200 bg-amber-50">
            <p className="stat-label text-amber-600">Medium</p>
            <p className="text-3xl font-bold text-amber-700 mt-1">{medium.length}</p>
          </div>
          <div className="card border-blue-200 bg-blue-50">
            <p className="stat-label text-blue-600">Low / Info</p>
            <p className="text-3xl font-bold text-blue-700 mt-1">{low.length}</p>
          </div>
        </div>

        {alerts.length === 0 && (
          <EmptyState
            icon={CheckCircle}
            title="No alerts found"
            description="Your portfolio looks healthy based on current data. Add more data to enable deeper analysis."
          />
        )}

        {/* Alert cards */}
        <div className="space-y-3">
          {[...high, ...medium, ...low].map((alert, i) => (
            <div
              key={i}
              className={cn("border rounded-xl p-4", severityColor(alert.severity))}
            >
              <div className="flex items-start gap-3">
                <SeverityIcon severity={alert.severity} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <h3 className="font-semibold text-sm">{alert.title}</h3>
                    <span className="badge bg-white/60 text-xs capitalize shrink-0">
                      {alert.alert_type.replace(/_/g, " ")}
                    </span>
                  </div>
                  <p className="text-sm mt-1 opacity-80">{alert.description}</p>
                  <div className="mt-2 bg-white/50 rounded-lg px-3 py-2 text-sm">
                    <span className="font-medium">Recommendation: </span>
                    {alert.recommendation}
                  </div>
                  {alert.affected_items.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {alert.affected_items.map((item, j) => (
                        <span key={j} className="badge bg-white/60 text-xs">{item}</span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Future: LLM summary placeholder */}
        <div className="card border-dashed border-gray-300 bg-gray-50">
          <div className="flex items-center gap-2 text-gray-400">
            <Lightbulb className="w-4 h-4" />
            <span className="text-sm font-medium">AI Portfolio Summary</span>
            <span className="badge bg-gray-200 text-gray-500 text-xs">Coming Soon</span>
          </div>
          <p className="text-xs text-gray-400 mt-2">
            Natural language portfolio summaries and risk explanations powered by Claude will be available when enabled.
          </p>
        </div>
      </div>
    </AppLayout>
  );
}
