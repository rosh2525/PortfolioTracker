import type { Metadata } from "next";
import type { Locale } from "./constants";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

export interface SeoMessages {
  "seo.title": string;
  "seo.description": string;
  "seo.ogTitle": string;
  "seo.ogDescription": string;
  "seo.keywords": string;
}

const localeToLanguageMap: Record<Locale, string> = {
  en: "en_IN",
};

export function generateMetadata(
  messages: SeoMessages,
  locale: Locale = "en",
): Metadata {
  return {
    title: messages["seo.title"],
    description: messages["seo.description"],
    keywords: messages["seo.keywords"],
    metadataBase: new URL(SITE_URL),
    openGraph: {
      title: messages["seo.ogTitle"],
      description: messages["seo.ogDescription"],
      url: SITE_URL,
      siteName: "PortfolioTracker",
      locale: localeToLanguageMap[locale],
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: messages["seo.ogTitle"],
      description: messages["seo.ogDescription"],
    },
    alternates: {
      canonical: SITE_URL,
      languages: {
        "en-IN": SITE_URL,
      },
    },
  };
}

export function generateJsonLd() {
  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "WebSite",
        "@id": `${SITE_URL}/#website`,
        url: SITE_URL,
        name: "PortfolioTracker",
        description: "Self-hosted Indian investment tracking application",
        inLanguage: ["en-IN"],
      },
      {
        "@type": "SoftwareApplication",
        "@id": `${SITE_URL}/#softwareapplication`,
        name: "PortfolioTracker",
        applicationCategory: "FinanceApplication",
        operatingSystem: "Web",
        offers: {
          "@type": "Offer",
          price: "0",
          priceCurrency: "INR",
        },
        description: "Indian portfolio, transaction, dividend, interest and tax tracking",
        aggregateRating: {
          "@type": "AggregateRating",
          ratingValue: "5",
          ratingCount: "1",
        },
      },
      {
        "@type": "Organization",
        "@id": `${SITE_URL}/#organization`,
        name: "PortfolioTracker",
        url: SITE_URL,
        logo: `${SITE_URL}/icon.png`,
        sameAs: ["https://github.com/rosh2525/PortfolioTracker"],
      },
    ],
  };
}
