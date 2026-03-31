export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface Platform {
  id: number;
  name: string;
  category: string;
  country: string;
  currency: string;
  active: boolean;
}

export interface Account {
  id: number;
  user_id: number;
  platform_id: number;
  name: string;
  account_number?: string;
  base_currency: string;
  account_type: string;
}

export interface AllocationItem {
  label: string;
  value: number;
  percentage: number;
}

export interface PortfolioSummary {
  total_portfolio_value: number;
  total_invested_capital: number;
  total_realized_pnl: number;
  total_unrealized_pnl: number;
  total_fees_paid: number;
  total_distributions: number;
  overall_roi_pct: number;
  monthly_income: number;
  allocation_by_platform: AllocationItem[];
  allocation_by_asset_type: AllocationItem[];
  allocation_by_currency: AllocationItem[];
}

export interface BrokeragePerformance {
  account_id: number;
  account_name: string;
  platform_name: string;
  current_value: number;
  invested_capital: number;
  realized_pnl: number;
  unrealized_pnl: number;
  total_fees: number;
  dividend_income: number;
  roi_pct: number;
  win_count: number;
  loss_count: number;
  win_rate_pct: number;
}

export interface DealPerformance {
  deal_id: number;
  deal_name: string;
  platform_name: string;
  deal_type: string;
  status: string;
  invested_capital: number;
  returned_capital: number;
  current_value: number;
  cumulative_distributions: number;
  roi_pct: number;
  irr_pct?: number;
  duration_days?: number;
  maturity_date?: string;
  target_return_pct?: number;
}

export interface MonthlyCashflow {
  month: string;
  inflows: number;
  outflows: number;
  net: number;
  distributions: number;
}

export interface RiskAlert {
  alert_type: string;
  severity: "low" | "medium" | "high";
  title: string;
  description: string;
  recommendation: string;
  affected_items: string[];
}
