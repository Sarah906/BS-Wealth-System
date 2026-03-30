"use client";
import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import EmptyState from "@/components/ui/EmptyState";
import { analyticsApi } from "@/lib/api";
import { BrokeragePerformance, DealPerformance } from "@/types";
import { formatCurrency, formatPct, pnlColor, cn } from "@/lib/utils";
import { TrendingUp, Briefcase, AlertCircle } from "lucide-react";

type Tab = "brokerage" | "deals";

function StatusBadge({ status }: { status: string }) {
  const color =
    status === "active" ? "bg-emerald-100 text-emerald-700" :
    status === "exited" || status === "matured" ? "bg-gray-100 text-gray-600" :
    "bg-amber-100 text-amber-700";
  return <span className={cn("badge", color)}>{status}</span>;
}

export default function InvestmentsPage() {
  const [tab, setTab] = useState<Tab>("brokerage");
  const [brokerage, setBrokerage] = useState<BrokeragePerformance[]>([]);
  const [deals, setDeals] = useState<DealPerformance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([analyticsApi.brokerage(), analyticsApi.deals()])
      .then(([b, d]) => {
        setBrokerage(b.data);
        setDeals(d.data);
      })
      .catch((e) => setError(e.response?.data?.detail || "Failed to load"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <AppLayout><LoadingSpinner text="Loading investments..." /></AppLayout>;

  return (
    <AppLayout>
      <div className="space-y-5">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Investments</h1>
          <p className="text-sm text-gray-500 mt-0.5">Performance across all accounts and deals</p>
        </div>

        {error && (
          <div className="flex items-center gap-2 text-red-600 bg-red-50 px-4 py-3 rounded-lg text-sm">
            <AlertCircle className="w-4 h-4" /> {error}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-1 bg-gray-100 p-1 rounded-lg w-fit">
          {(["brokerage", "deals"] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={cn(
                "px-4 py-1.5 text-sm font-medium rounded-md transition-colors capitalize",
                tab === t ? "bg-white text-gray-900 shadow-sm" : "text-gray-500 hover:text-gray-700"
              )}
            >
              {t === "brokerage" ? "Brokerage" : "Deals & Funds"}
            </button>
          ))}
        </div>

        {/* Brokerage Table */}
        {tab === "brokerage" && (
          brokerage.length === 0 ? (
            <EmptyState icon={TrendingUp} title="No brokerage accounts" description="Create an account and import transactions to see performance." />
          ) : (
            <div className="card overflow-x-auto p-0">
              <table className="w-full text-sm">
                <thead className="border-b border-gray-100">
                  <tr className="text-left">
                    {["Account", "Platform", "Current Value", "Invested", "Realized P&L", "Unrealized P&L", "ROI", "Dividends", "W/L", "Win Rate"].map((h) => (
                      <th key={h} className="px-4 py-3 text-xs font-semibold text-gray-500 whitespace-nowrap">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {brokerage.map((row) => (
                    <tr key={row.account_id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium text-gray-900">{row.account_name}</td>
                      <td className="px-4 py-3 text-gray-600">{row.platform_name}</td>
                      <td className="px-4 py-3 font-medium">{formatCurrency(row.current_value)}</td>
                      <td className="px-4 py-3 text-gray-600">{formatCurrency(row.invested_capital)}</td>
                      <td className={cn("px-4 py-3 font-medium", pnlColor(row.realized_pnl))}>{formatCurrency(row.realized_pnl)}</td>
                      <td className={cn("px-4 py-3 font-medium", pnlColor(row.unrealized_pnl))}>{formatCurrency(row.unrealized_pnl)}</td>
                      <td className={cn("px-4 py-3 font-medium", pnlColor(row.roi_pct))}>{formatPct(row.roi_pct)}</td>
                      <td className="px-4 py-3 text-emerald-600">{formatCurrency(row.dividend_income)}</td>
                      <td className="px-4 py-3 text-gray-600">{row.win_count}W / {row.loss_count}L</td>
                      <td className="px-4 py-3 text-gray-600">{formatPct(row.win_rate_pct)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        )}

        {/* Deals Table */}
        {tab === "deals" && (
          deals.length === 0 ? (
            <EmptyState icon={Briefcase} title="No deals recorded" description="Add deals or import deal data to see performance." />
          ) : (
            <div className="card overflow-x-auto p-0">
              <table className="w-full text-sm">
                <thead className="border-b border-gray-100">
                  <tr className="text-left">
                    {["Deal", "Platform", "Type", "Status", "Invested", "Returned", "Current Val", "ROI", "IRR", "Duration"].map((h) => (
                      <th key={h} className="px-4 py-3 text-xs font-semibold text-gray-500 whitespace-nowrap">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {deals.map((row) => (
                    <tr key={row.deal_id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div className="font-medium text-gray-900 max-w-[200px] truncate">{row.deal_name}</div>
                        {row.maturity_date && <div className="text-xs text-gray-400 mt-0.5">Matures: {row.maturity_date}</div>}
                      </td>
                      <td className="px-4 py-3 text-gray-600">{row.platform_name}</td>
                      <td className="px-4 py-3 text-gray-600 capitalize">{row.deal_type.replace("_", " ")}</td>
                      <td className="px-4 py-3"><StatusBadge status={row.status} /></td>
                      <td className="px-4 py-3">{formatCurrency(row.invested_capital)}</td>
                      <td className="px-4 py-3 text-emerald-600">{formatCurrency(row.returned_capital)}</td>
                      <td className="px-4 py-3 font-medium">{formatCurrency(row.current_value)}</td>
                      <td className={cn("px-4 py-3 font-medium", pnlColor(row.roi_pct))}>{formatPct(row.roi_pct)}</td>
                      <td className={cn("px-4 py-3", row.irr_pct ? pnlColor(row.irr_pct) : "text-gray-400")}>
                        {row.irr_pct != null ? formatPct(row.irr_pct) : "—"}
                      </td>
                      <td className="px-4 py-3 text-gray-500">
                        {row.duration_days != null ? `${Math.floor(row.duration_days / 30)}mo` : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        )}
      </div>
    </AppLayout>
  );
}
