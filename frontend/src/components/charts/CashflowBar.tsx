"use client";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import { MonthlyCashflow } from "@/types";

interface Props {
  data: MonthlyCashflow[];
}

export default function CashflowBar({ data }: Props) {
  if (!data || data.length === 0) return null;

  // Show last 24 months
  const slice = data.slice(-24);

  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">Monthly Cashflow</h3>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={slice} margin={{ top: 0, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
          <XAxis
            dataKey="month"
            tick={{ fontSize: 10, fill: "#6b7280" }}
            tickFormatter={(v) => v.slice(2)}
          />
          <YAxis
            tick={{ fontSize: 10, fill: "#6b7280" }}
            tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
          />
          <Tooltip
            formatter={(value: number) => [`SAR ${value.toLocaleString()}`, ""]}
            labelStyle={{ fontSize: 11 }}
          />
          <Legend iconSize={8} wrapperStyle={{ fontSize: 11 }} />
          <Bar dataKey="inflows" name="Inflows" fill="#10b981" radius={[2, 2, 0, 0]} />
          <Bar dataKey="outflows" name="Outflows" fill="#ef4444" radius={[2, 2, 0, 0]} />
          <Bar dataKey="distributions" name="Distributions" fill="#0ea5e9" radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
