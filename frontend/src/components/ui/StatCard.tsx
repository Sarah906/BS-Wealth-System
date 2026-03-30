import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string;
  sub?: string;
  icon?: LucideIcon;
  trend?: "up" | "down" | "neutral";
  className?: string;
}

export default function StatCard({ label, value, sub, icon: Icon, trend, className }: StatCardProps) {
  return (
    <div className={cn("card", className)}>
      <div className="flex items-start justify-between">
        <div>
          <p className="stat-label">{label}</p>
          <p className="stat-value">{value}</p>
          {sub && (
            <p
              className={cn(
                "text-sm mt-0.5",
                trend === "up" ? "text-emerald-600" :
                trend === "down" ? "text-red-500" :
                "text-gray-500"
              )}
            >
              {sub}
            </p>
          )}
        </div>
        {Icon && (
          <div className="bg-brand-50 p-2.5 rounded-lg">
            <Icon className="w-5 h-5 text-brand-600" />
          </div>
        )}
      </div>
    </div>
  );
}
