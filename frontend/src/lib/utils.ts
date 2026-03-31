import { clsx, type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatCurrency(value: number | string, currency = "SAR"): string {
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(num)) return "—";
  return new Intl.NumberFormat("en-SA", {
    style: "currency",
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(num);
}

export function formatPct(value: number | string): string {
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(num)) return "—";
  const sign = num > 0 ? "+" : "";
  return `${sign}${num.toFixed(2)}%`;
}

export function formatNumber(value: number | string, decimals = 2): string {
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(num)) return "—";
  return new Intl.NumberFormat("en", { minimumFractionDigits: decimals, maximumFractionDigits: decimals }).format(num);
}

export function pnlColor(value: number | string): string {
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (num > 0) return "text-emerald-600";
  if (num < 0) return "text-red-500";
  return "text-gray-500";
}

export function severityColor(severity: string): string {
  switch (severity) {
    case "high": return "bg-red-100 text-red-800 border-red-200";
    case "medium": return "bg-amber-100 text-amber-800 border-amber-200";
    default: return "bg-blue-50 text-blue-800 border-blue-200";
  }
}
