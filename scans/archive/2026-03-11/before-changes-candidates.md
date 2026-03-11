> **Note on seed-origin names:** Tickers tagged `source_bucket=seed` are curated inputs from `seeds/watchlist.json`, not discovered names. They reflect prior knowledge or personal watchlist intent rather than fresh market signals.

---

## Scan Summary — 2026-03-11

**Total candidates: 58**

### Counts by source_bucket
- `tracked`: 19
- `seed`: 19
- `sector_leader`: 14 (several overlap with tracked/seed)
- `52wk_low`: 6
- `fcf_roic`: 8
- `post_earnings`: 1

### Counts by sector
- Technology: 23
- Industrials: 12
- Healthcare: 9
- Consumer: 8
- Financials: 7
- Communication Services: 3
- Utilities: 1

### Counts by priority
- `high`: 29
- `medium`: 29
- `low`: 0

### Triage rec=yes tickers
NOW, CRM, MSFT, GOOG, META, AMD, V, BRK-B, NVS, BKNG, AMAT, CMCSA, HD, BSX, VZ, GILD, T

---

## Full Candidate Table

| ticker | company | sector | style_tag | source_bucket | short_reason | possible_disqualifier | mkt_cap_tier | priority | triage_rec | confidence |
|--------|---------|--------|-----------|---------------|-------------|----------------------|-------------|----------|------------|------------|
| AAPL | Apple Inc. | Technology | compounder | tracked\|sector_leader | Services mix shift expands margins; installed base moat | China revenue concentration; iPhone saturation | mega | high | maybe | high |
| NVDA | NVIDIA Corp. | Technology | compounder | tracked\|sector_leader | AI GPU monopoly; data center demand still accelerating | Valuation extreme; China export restrictions | mega | high | maybe | high |
| ASML | ASML Holding N.V. | Technology | compounder | tracked\|sector_leader | Sole EUV supplier; irreplaceable in chip supply chain | China export ban risk; cyclical capex slowdown | mega | high | maybe | high |
| TSM | Taiwan Semiconductor Mfg. | Technology | compounder | tracked\|sector_leader | World's dominant foundry; AI chip demand drives capacity | Taiwan geopolitical risk; customer concentration | mega | high | maybe | high |
| AVGO | Broadcom Inc. | Technology | compounder | tracked\|sector_leader | Custom AI ASICs + VMware integration expanding TAM | Heavy debt post-VMware; integration execution risk | mega | high | maybe | high |
| NOW | ServiceNow Inc. | Technology | compounder | tracked\|52wk_low | AI-native enterprise platform near multi-month low | Premium valuation even at lows; macro IT spend risk | mega | high | **yes** | high |
| CRM | Salesforce Inc. | Technology | compounder | tracked\|52wk_low | Agentforce AI pivot; trading near 52-week low at $194 | Slowing ARR growth; competition from Microsoft Copilot | large | high | **yes** | high |
| MSFT | Microsoft Corp. | Technology | compounder | seed\|sector_leader | Azure + Copilot AI monetization at scale; durable moat | Antitrust scrutiny; OpenAI dependency and cost | mega | high | **yes** | high |
| GOOG | Alphabet Inc. | Technology | compounder | seed\|sector_leader | Search monopoly + GCP + Gemini AI; FCF machine | AI search disruption to core ad revenue model | mega | high | **yes** | high |
| META | Meta Platforms Inc. | Technology | compounder | seed\|sector_leader | 3B+ user ad network; Llama AI cuts costs and moats | Regulatory breakup risk; Reality Labs cash burn | mega | high | **yes** | high |
| AMD | Advanced Micro Devices Inc. | Technology | compounder | post_earnings | Q4 beat; MI300 AI GPU revenue surging 34% YoY | NVIDIA entrenched in AI; datacenter share still thin | large | high | **yes** | medium |
| NOVO-B.CO | Novo Nordisk A/S | Healthcare | compounder | tracked | GLP-1 weight-loss drug dominance; massive demand runway | Ozempic pricing pressure; Eli Lilly competition | mega | high | maybe | high |
| ARM | Arm Holdings plc | Technology | compounder | tracked | CPU IP royalties growing with AI edge compute buildout | Lofty valuation; customer RISC-V defection risk | mega | high | maybe | high |
| SNOW | Snowflake Inc. | Technology | compounder | tracked | AI Data Cloud gaining traction; new CEO driving focus | Not yet profitable; intense competition from Databricks | large | high | maybe | medium |
| ALAB | Astera Labs Inc. | Technology | speculative | tracked | PCIe/CXL connectivity chips critical for AI server racks | Small cap pre-scale; customer concentration in hyperscalers | mid | high | maybe | medium |
| V | Visa Inc. | Financials | compounder | seed\|52wk_low | Global payment network near 52-week low; toll-road model | Crypto/stablecoin payments disintermediation risk | mega | high | **yes** | high |
| BRK-B | Berkshire Hathaway B | Financials | value | seed\|52wk_low | Buffett's own vehicle at 52-week low; massive cash reserve | Succession uncertainty; no single business to underwrite | mega | high | **yes** | high |
| NVS | Novartis AG | Healthcare | value | fcf_roic | Mega-cap pharma with top FCF yield; Kisqali/Entresto growth | Patent cliffs; generic competition on key drugs | mega | high | **yes** | medium |
| BKNG | Booking Holdings Inc. | Consumer | value | fcf_roic | 8% unlevered FCF yield; dominant OTA with pricing power | Travel demand cyclicality; Google Hotels competition | large | high | **yes** | medium |
| AMAT | Applied Materials Inc. | Technology | compounder | fcf_roic\|sector_leader | Semicon equipment leader with solid FCF; AI capex beneficiary | China export restrictions shrink addressable market | mega | high | **yes** | medium |
| CMCSA | Comcast Corp. | Communication Services | value | fcf_roic | 9% unlevered FCF yield; broadband infrastructure monopoly | Cord-cutting accelerates; streaming losses at Peacock | large | high | **yes** | medium |
| HD | Home Depot Inc. | Consumer | recovery | 52wk_low\|sector_leader | Pro contractor channel + SRS acquisition near 52-week low | Housing market freeze dampens DIY and remodel spend | mega | high | **yes** | medium |
| BSX | Boston Scientific Corp. | Healthcare | recovery | 52wk_low | MedTech compounder near 52-week low; cardiac/endo growth | Premium MedTech multiple even at lows; procedure volume risk | large | high | **yes** | medium |
| VZ | Verizon Communications Inc. | Communication Services | income | fcf_roic | High FCF yield; 5G infrastructure asset-heavy but stable | Massive debt load; subscriber growth near ceiling | mega | high | **yes** | low |
| GILD | Gilead Sciences Inc. | Healthcare | value | fcf_roic | 6%+ FCF yield; HIV franchise durable; oncology optionality | HIV growth ceiling; oncology pipeline binary risk | large | high | **yes** | medium |
| T | AT&T Inc. | Communication Services | income | fcf_roic | High FCF yield post-DirecTV exit; fiber rollout catalyst | Extreme debt burden; subscriber growth limited | mega | high | **yes** | low |
| ADBE | Adobe Inc. | Technology | compounder | tracked | Creative AI tools defend moat; Firefly monetization ahead | AI image generators commoditize core creative software | large | high | maybe | high |
| QCOM | Qualcomm Inc. | Technology | compounder | tracked | On-device AI in Snapdragon; auto and IoT diversification | Apple designing out Qualcomm modem; ARM licensing threat | large | high | maybe | medium |
| DSV.CO | DSV A/S | Industrials | compounder | tracked | Serial M&A compounder in global logistics; DB Schenker deal | Integration risk post-Schenker; freight rate cyclicality | large | high | maybe | high |
| MA | Mastercard Inc. | Financials | compounder | seed | Duopoly payment rail; high-margin asset-light compounder | Regulatory fee caps; fintech bypass risk | mega | medium | maybe | high |
| UNH | UnitedHealth Group Inc. | Healthcare | compounder | sector_leader | Largest US health insurer + Optum; durable earnings machine | CMS reimbursement cuts; medical cost ratio pressure | mega | medium | maybe | high |
| JNJ | Johnson & Johnson | Healthcare | compounder | sector_leader | MedTech + pharma dual engine; 60+ years dividend growth | Talc litigation overhang; pipeline lacks blockbusters | mega | medium | maybe | high |
| GE | GE Aerospace | Industrials | compounder | sector_leader | Pure-play aerospace; aftermarket services drive recurring revenue | Boeing production issues reduce engine demand | mega | medium | maybe | high |
| RTX | RTX Corp. (Raytheon) | Industrials | compounder | sector_leader | Defense + Pratt engines; NATO rearmament tailwind | GTF engine recall costs; defense budget uncertainty | mega | medium | maybe | high |
| WMT | Walmart Inc. | Consumer | compounder | sector_leader | Retail dominance + advertising + fintech expanding margins | Premium valuation for a retailer; tariff cost pass-through | mega | medium | maybe | high |
| COST | Costco Wholesale Corp. | Consumer | compounder | sector_leader | Membership loyalty flywheel; near-zero inventory risk model | Expensive on any earnings multiple; low FCF yield | mega | medium | maybe | high |
| CSU.TO | Constellation Software | Technology | compounder | seed | VMS acqui-machine; capital allocation excellence no debt needed | Pricey; TAM of niche VMS shrinking per-spinoff | large | medium | maybe | high |
| DHR | Danaher Corp. | Industrials | compounder | seed | DBS operating system drives serial acquisition returns | Biotech funding slowdown dampens instrument demand | mega | medium | maybe | high |
| MCO | Moody's Corp. | Financials | compounder | seed | Regulated ratings duopoly + analytics growth; high margins | Debt issuance slowdown cuts ratings revenue cyclically | large | medium | maybe | high |
| SPGI | S&P Global Inc. | Financials | compounder | seed | Ratings + market data + Platts; recurring data flywheel | Debt issuance cyclicality; Platts integration still ongoing | mega | medium | maybe | high |
| FICO | Fair Isaac Corp. | Technology | compounder | seed | FICO score is legally mandated in US mortgage underwriting | CFPB push for alternative scores; price regulation risk | large | medium | maybe | high |
| ROP | Roper Technologies | Industrials | compounder | seed | Asset-light niche software acquirer; FCF conversion excellent | Holding company discount; dependent on M&A pipeline quality | large | medium | maybe | high |
| IDXX | IDEXX Laboratories | Healthcare | compounder | seed | Installed base razor/blade in vet diagnostics; pricing power | Pet spending discretionary; vet visit frequency falling | large | medium | maybe | high |
| TDG | TransDigm Group | Industrials | compounder | seed | Sole-source aerospace aftermarket; pricing power unmatched | DOD audit/pricing scrutiny; highly leveraged balance sheet | large | medium | maybe | high |
| ODFL | Old Dominion Freight Line | Industrials | compounder | seed | Best-in-class LTL margins; service quality compounds share gains | Freight cycle downturn; macro-sensitive revenue | large | medium | maybe | high |
| SHW | Sherwin-Williams Co. | Consumer | compounder | seed | Paint distribution dominance; pro contractor loyalty deep | Housing remodel cycle slowdown; raw material inflation | mega | medium | maybe | high |
| FAST | Fastenal Co. | Industrials | compounder | seed | On-site vending lock-in; industrial cycle recovery beneficiary | Industrial capex softness; Amazon Business undercutting | large | medium | maybe | high |
| POOL | Pool Corp. | Consumer | compounder | seed | Dominant pool supply distributor; installed base non-discretionary | New pool construction halted; housing market stall | mid | medium | maybe | high |
| MTD | Mettler-Toledo Intl. | Industrials | compounder | seed | Lab/industrial precision instruments; pricing power and switching costs | Pharma and China lab capex slowdown | large | medium | maybe | high |
| WST | West Pharmaceutical Services | Healthcare | compounder | seed | Sole-source injectable packaging; GLP-1 injectable wave tailwind | Destocking cycle hit revenue; GLP-1 ramp slower than hoped | mid | medium | maybe | high |
| MU | Micron Technology Inc. | Technology | cyclical | sector_leader | HBM memory for AI GPUs; 240% return reflects structural shift | Memory is inherently cyclical; DRAM oversupply risk | large | medium | maybe | medium |
| LRCX | Lam Research Corp. | Technology | compounder | sector_leader | Etch/deposition equipment leader; NAND recovery + AI capex | China export controls; semicon capex cyclicality | large | medium | maybe | medium |
| PG | Procter & Gamble Co. | Consumer | income | sector_leader | Defensive consumer staples with pricing power; 67-year dividend | Volume loss to private label; limited growth at this scale | mega | medium | no | high |
| RKLB | Rocket Lab USA | Industrials | speculative | tracked | Electron launch monopoly in small-sat; Neutron development | Pre-profit; SpaceX Falcon 9 competitive pressure | mid | medium | no | medium |
| TSLA | Tesla Inc. | Consumer | speculative | tracked | FSD + energy storage expanding beyond EV; optionality play | Brand damage; EV market share erosion; premium valuation | mega | medium | no | medium |
| HIMS | Hims & Hers Health Inc. | Healthcare | speculative | tracked | GLP-1 compounding + telehealth platform scaling fast | Regulatory risk on GLP-1 compounding; pre-scale economics | mid | medium | no | medium |
| MAERSK-B.CO | AP Møller-Maersk B | Industrials | cyclical | tracked | Integrated logistics pivot; shipping rates stabilizing | Shipping overcapacity cycle; commodity earnings volatility | large | medium | no | medium |
| ORSTED.CO | Ørsted A/S | Utilities | recovery | tracked | Offshore wind leader post-restructuring; US policy clarity | US offshore wind policy reversal; high leverage | mid | medium | no | low |

---

**Next step:** Run Stage B triage on all `triage_rec=yes` names — pull trailing financials, check valuation vs. intrinsic value range, and select which proceed to full Stage C umbrella analysis.
