import type { Locale } from "@/lib/constants";

const dictionaries: Record<Locale, () => Promise<Record<string, string>>> = {
  en: () => import("./messages/en.json").then((m) => m.default),
};

export async function getDictionary(locale: Locale): Promise<Record<string, string>> {
  const loader = dictionaries[locale] || dictionaries.en;
  return loader();
}
