import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { isPrivacyMode } from "@/lib/privacy"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

const MASK = "•••••";

/**
 * Format a numeric string or number as money using Indian grouping.
 * E.g. 1234567.89 → "₹12,34,567.89"
 * Returns masked value when privacy mode is active.
 */
export function formatMoney(
  value: string | number | null | undefined,
  currency = "INR",
  isPublic = false,
): string {
  if (value == null || value === "") return "—";
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(num)) return "—";
  if (!isPublic && isPrivacyMode()) return MASK;

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num);
}

/**
 * Format percentage.
 */
export function formatPct(value: string | number | null | undefined): string {
  if (value == null || value === "") return "—";
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(num)) return "—";
  return `${num >= 0 ? "+" : ""}${num.toFixed(2)}%`;
}

/**
 * Format a quantity (shares, units) respecting up to 6 decimal places.
 * Trailing zeros are trimmed automatically by toLocaleString.
 */
export function formatQty(value: string | number | null | undefined): string {
  if (value == null || value === "") return "—";
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(num)) return "—";
  return num.toLocaleString("en-IN", { maximumFractionDigits: 6 });
}

/**
 * Return CSS class for positive/negative money values.
 */
export function moneyColor(value: string | number | null | undefined): string {
  if (value == null) return "text-muted-foreground";
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (num > 0) return "text-green-500";
  if (num < 0) return "text-red-500";
  return "text-muted-foreground";
}
