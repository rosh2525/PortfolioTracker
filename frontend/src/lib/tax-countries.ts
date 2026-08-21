/**
 * Country-related helpers for the fiscal-residence dropdown.
 *
 * Pure utilities — no React, no adapter knowledge. The list of *supported*
 * countries (ones that have a tax-declaration adapter) lives next to the
 * adapter registry at
 * ``app/(dashboard)/tax/adapters/index.ts``.
 */

/**
 * PortfolioTracker is configured for the Indian market, so fiscal residence
 * is fixed to India in the settings experience.
 */
export const TAX_COUNTRY_OPTIONS: readonly string[] = ["IN"];

/**
 * Resolve a localized country name. Falls back to the ISO code if the locale
 * or runtime does not support `Intl.DisplayNames`.
 */
export function localizedCountryName(code: string, locale: string): string {
  try {
    const dn = new Intl.DisplayNames([locale], { type: "region" });
    return dn.of(code.toUpperCase()) || code;
  } catch {
    return code;
  }
}
