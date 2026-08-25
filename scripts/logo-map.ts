/**
 * Company → brand mark resolution.
 *
 * `simple-icons` ships monochrome single-path SVGs, which is what we want: a
 * chip rendered in the brand's own hex reads as that brand, stays crisp at
 * 14px, and looks like one system next to 600 others — where a grab-bag of
 * 48px favicons does not.
 *
 * Two wrinkles this map exists to absorb:
 *  1. Recent simple-icons releases dropped several major marks (Amazon,
 *     Microsoft, LinkedIn, Adobe, Oracle, IBM, Salesforce, OpenAI…) over
 *     trademark requests, so `fetch-logos.ts` walks a version ladder and we
 *     carry the brand hex here.
 *  2. Upstream folder ids don't always match icon slugs (`walmart-labs` →
 *     `walmart`, `snapchat` → `snapchat`, `x` → `x`).
 *
 * Anything not listed here is resolved by slug guess, then falls back to a
 * deterministic monogram. A monogram is always better than a confident wrong
 * logo, so we never guess a favicon domain.
 */

export interface BrandEntry {
  /** simple-icons slug. */
  icon?: string
  /** Brand hex without `#`. Needed when the package no longer carries the icon. */
  hex?: string
  /** Display name override, when `prettyName()` would get it wrong. */
  name?: string
}

export const BRANDS: Record<string, BrandEntry> = {
  // --- core six ---------------------------------------------------------
  google: { icon: 'google', hex: '4285F4' },
  meta: { icon: 'meta', hex: '0467DF' },
  amazon: { icon: 'amazon', hex: 'FF9900' },
  microsoft: { icon: 'microsoft', hex: '5E5E5E' },
  apple: { icon: 'apple', hex: '000000' },
  netflix: { icon: 'netflix', hex: 'E50914' },

  // --- high-frequency adjacents ----------------------------------------
  bloomberg: { icon: 'bloomberg', hex: '000000' },
  linkedin: { icon: 'linkedin', hex: '0A66C2' },
  uber: { icon: 'uber', hex: '000000' },
  tiktok: { icon: 'tiktok', hex: '000000', name: 'TikTok' },
  bytedance: { icon: 'bytedance', hex: '325AB4', name: 'ByteDance' },
  oracle: { icon: 'oracle', hex: 'F80000' },
  salesforce: { icon: 'salesforce', hex: '00A1E0' },
  adobe: { icon: 'adobe', hex: 'FF0000' },
  ibm: { icon: 'ibm', hex: '052FAD', name: 'IBM' },
  nvidia: { icon: 'nvidia', hex: '76B900', name: 'NVIDIA' },
  openai: { icon: 'openai', hex: '412991', name: 'OpenAI' },
  snowflake: { icon: 'snowflake', hex: '29B5E8' },
  databricks: { icon: 'databricks', hex: 'FF3621' },
  visa: { icon: 'visa', hex: '1A1F71' },
  paypal: { icon: 'paypal', hex: '003087', name: 'PayPal' },
  stripe: { icon: 'stripe', hex: '635BFF' },
  airbnb: { icon: 'airbnb', hex: 'FF5A5F' },
  doordash: { icon: 'doordash', hex: 'FF3008', name: 'DoorDash' },
  lyft: { icon: 'lyft', hex: 'FF00BF' },
  instacart: { icon: 'instacart', hex: '43B02A' },
  pinterest: { icon: 'pinterest', hex: 'BD081C' },
  snapchat: { icon: 'snapchat', hex: 'FFFC00' },
  spotify: { icon: 'spotify', hex: '1DB954' },
  roblox: { icon: 'roblox', hex: '000000' },
  tesla: { icon: 'tesla', hex: 'CC0000' },
  atlassian: { icon: 'atlassian', hex: '0052CC' },
  cloudflare: { icon: 'cloudflare', hex: 'F38020' },
  mongodb: { icon: 'mongodb', hex: '47A248', name: 'MongoDB' },
  palantir: { icon: 'palantir', hex: '101113' },
  qualcomm: { icon: 'qualcomm', hex: '3253DC' },
  cisco: { icon: 'cisco', hex: '1BA0D7' },
  intuit: { icon: 'intuit', hex: '236CFF' },
  ebay: { icon: 'ebay', hex: 'E53238', name: 'eBay' },
  expedia: { icon: 'expedia', hex: 'FFC94A' },
  yandex: { icon: 'yandex', hex: 'FF0000' },
  samsung: { icon: 'samsung', hex: '1428A0' },
  sap: { icon: 'sap', hex: '0FAAFF', name: 'SAP' },
  vmware: { icon: 'vmware', hex: '607078', name: 'VMware' },
  zoho: { icon: 'zoho', hex: '226DB4' },
  grammarly: { icon: 'grammarly', hex: '15C39A' },
  confluent: { icon: 'confluent', hex: '173361' },
  docusign: { icon: 'docusign', hex: 'FFCC22', name: 'DocuSign' },
  flipkart: { icon: 'flipkart', hex: '2874F0' },
  coupang: { icon: 'coupang', hex: 'CC0C2F' },
  wise: { icon: 'wise', hex: '9FE870' },
  box: { icon: 'box', hex: '0061D5' },
  autodesk: { icon: 'autodesk', hex: '0696D7' },
  walmart: { icon: 'walmart', hex: '0071CE' },
  'walmart-labs': { icon: 'walmart', hex: '0071CE', name: 'Walmart Labs' },
  accenture: { icon: 'accenture', hex: 'A100FF' },
  infosys: { icon: 'infosys', hex: '007CC3' },
  tcs: { icon: 'tcs', hex: 'EE3124', name: 'TCS' },
  wipro: { icon: 'wipro', hex: '341A5D' },
  capgemini: { icon: 'capgemini', hex: '0070AD' },
  cognizant: { icon: 'cognizant', hex: '1E4EA1' },
  deloitte: { icon: 'deloitte', hex: '86BC25' },
  phonepe: { icon: 'phonepe', hex: '5F259F', name: 'PhonePe' },
  paytm: { icon: 'paytm', hex: '20336B' },
  swiggy: { icon: 'swiggy', hex: 'FC8019' },
  zomato: { icon: 'zomato', hex: 'E23744' },
  razorpay: { icon: 'razorpay', hex: '0C2451' },
  freshworks: { icon: 'freshworks', hex: 'FF6600' },
  hcl: { name: 'HCLTech' },

  // --- no public mark in simple-icons; monogram is the honest answer ----
  'goldman-sachs': { hex: '7399C6', name: 'Goldman Sachs' },
  'morgan-stanley': { hex: '00295B', name: 'Morgan Stanley' },
  jpmorgan: { hex: '5C2D2D', name: 'JPMorgan Chase' },
  'capital-one': { hex: 'D03027', name: 'Capital One' },
  citadel: { hex: '0C2340' },
  'de-shaw': { hex: '004B87', name: 'D. E. Shaw' },
  'two-sigma': { hex: '1A1A1A', name: 'Two Sigma' },
  'jane-street': { hex: '1F3A5F', name: 'Jane Street' },
  anduril: { hex: '1E1E1E' },
  waymo: { hex: '4285F4' },
  aurora: { hex: '4B31C8' },
  'palo-alto-networks': { hex: 'F04E23', name: 'Palo Alto Networks' },
  agoda: { hex: 'E02A6E' },
  axon: { hex: 'F5A623' },
  sofi: { hex: '00A0DF', name: 'SoFi' },
  turing: { hex: '4A2FE7' },
  'epam-systems': { hex: '4EA5D9', name: 'EPAM Systems' },
  'general-motors': { hex: '004B8D', name: 'General Motors' },
  juspay: { hex: '00B4D8' },
  'josh-technology': { hex: 'F26722', name: 'Josh Technology' },
  hashedin: { hex: '00857D', name: 'HashedIn' },
  zopsmart: { hex: '2F6DF6', name: 'ZopSmart' },
  micro1: { hex: '6D28D9', name: 'micro1' },
  hive: { hex: 'FDEE21' },
}

/**
 * jsDelivr version ladder, newest first.
 *
 * 16.x dropped a number of major marks; `latest` and 11.14.0 still serve
 * them. We take the first version that has the file and vendor it, so the
 * built site never talks to a CDN.
 */
export const SIMPLE_ICONS_VERSIONS = ['latest', '11.14.0'] as const
