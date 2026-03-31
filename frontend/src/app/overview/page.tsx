"use client";
import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import StatCard from "@/components/ui/StatCard";
import AllocationPie from "@/components/charts/AllocationPie";
import CashflowBar from "@/components/charts/CashflowBar";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import { analyticsApi } from "@/lib/api";
import { PortfolioSummary, MonthlyCashflow } from "@/types";
import { formatCurrency, formatPct, pnlColor } from "@/lib/utils";
import { TrendingUp, TrendingDown, DollarSign, Percent, ArrowUpRight, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export default function OverviewPage() {
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [cashflows, setCashflows] = useState<MonthlyCashflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      analyticsApi.summary(),
      analyticsApi.monthlyCashflow(),
    ])
      .then(([s, c]) => {
        setSummary(s.data);
        setCashflows(c.data);
      })
      .catch((e) => setError(e.response?.data?.detail || "Failed to load data"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <AppLayout><LoadingSpinner text="Loading portfolio..." /></AppLayout>;

  if (error) return (
    <AppLayout>
      <div className="flex items-center gap-2 text-red-600 bg-red-50 px-4 py-3 rounded-lg">
        <AlertCircle className="w-4 h-4" /> {error}
      </div>
    </AppLayout>
  );

  const s = summary!;
  const totalPnl = Number(s.total_realized_pnl) + Number(s.total_unrealized_pnl);

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Portfolio Overview</h1>
          <p className="text-sm text-gray-500 mt-0.5">Your complete wealth snapshot</p>
        </div>

        {/* Top stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Total Portfolio Value"
            value={formatCurrency(s.total_portfolio_value)}
            icon={DollarSign}
          />
          <StatCard
            label="Total Invested"
            value={formatCurrency(s.total_invested_capital)}
            icon={TrendingUp}
          />
          <StatCard
            label="Total P&L"
            value={formatCurrency(Math.abs(totalPnl))}
            sub={formatPct(Number(s.overall_roi_pct))}
            trend={totalPnl >= 0 ? "up" : "down"}
            icon={totalPnl >= 0 ? TrendingUp : TrendingDown}
          />
          <StatCard
            label="Monthly Income"
            value={formatCurrency(s.monthly_income)}
            sub="avg distributions"
            icon={ArrowUpRight}
          />
        </div>

        {/* Secondary stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="card">
            <p className="stat-label">Realized P&L</p>
            <p className={cn("text-xl font-bold mt-1", pnlColor(Number(s.total_realized_pnl)))}>
              {formatCurrency(s.total_realized_pnl)}
            </p>
          </div>
          <div className="card">
            <p className="stat-label">Unrealized P&L</p>
            <p className={cn("text-xl font-bold mt-1", pnlColor(Number(s.total_unrealized_pnl)))}>
              {formatCurrency(s.total_unrealized_pnl)}
            </p>
          </div>
          <div className="card">
            <p className="stat-label">Total Distributions</p>
            <p className="text-xl font-bold mt-1 text-gray-900">
              {formatCurrency(s.total_distributions)}
            </p>
          </div>
          <div className="card">
            <p className="stat-label">Fees Paid</p>
            <p className="text-xl font-bold mt-1 text-gray-900">
              {formatCurrency(s.total_fees_paid)}
            </p>
          </div>
        </div>

        {/* Charts row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <AllocationPie data={s.allocation_by_platform} title="By Platform" />
          <AllocationPie data={s.allocation_by_asset_type} title="By Asset Type" />
          <AllocationPie data={s.allocation_by_currency} title="By Currency" />
        </div>

        {/* Cashflow chart */}
        <CashflowBar data={cashflows} />
      </div>
    </AppLayout>
  );
}
