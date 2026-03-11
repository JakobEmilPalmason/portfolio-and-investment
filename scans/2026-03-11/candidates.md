# Stage A2 Candidates — 2026-03-11

> **Note on seed-origin names:** Tickers tagged `source_bucket=seed` are curated inputs from `seeds/watchlist.json`, not discovered names. They reflect prior knowledge or personal watchlist intent rather than fresh market signals.

---

## Summary

| Metric | Count |
|--------|-------|
| Total candidates | 172 |
| Removed from A1 | 1 (NVO consolidated → NOVO-B.CO primary listing) |
| Priority: high | 13 |
| Priority: medium | 141 |
| Priority: low | 18 |
| triage_rec: yes | 13 |
| triage_rec: maybe | 141 |
| triage_rec: no | 18 |

### Counts by Source Bucket (from A1 universe-meta)

| Bucket | Count |
|--------|-------|
| seed | 20 |
| large_cap_us_quality | 30 |
| large_cap_europe_quality | 47 |
| semis_and_infra | 15 |
| healthcare_quality | 15 |
| industrial_compounders | 15 |
| financial_quality | 15 |
| consumer_quality | 15 |
| post_earnings | 1 |
| 52wk_low | 6 |
| 52wk_high | 6 |
| fcf_roic | 6 |
| sector_leader | 24 |

### Counts by Sector

| Sector | Count |
|--------|-------|
| Technology | 51 |
| Industrials | 33 |
| Consumer | 28 |
| Financials | 25 |
| Healthcare | 26 |
| Communication Services | 4 |
| Energy | 2 |
| Materials | 2 |
| Utilities | 1 |

### triage_rec = yes (13 names)

These names have a fresh event catalyst (52wk_low, 52wk_high, post_earnings, or fcf_roic) combined with high or medium confidence and priority=high:

`V`, `BRK-B`, `HD`, `CRM`, `NOW`, `BSX`, `AMAT`, `NOVN.SW`, `APP`, `COHR`, `PLTR`, `SPOT`, `GILD`

### Disqualified / priority=low (18 names)

Marked low priority for failing Buffett-style quality filters or being commodity/cyclical without durable moat:

`TSLA` (speculative), `MAERSK-B.CO` (commodity shipping), `ORSTED.CO` (regulated utility), `VWS.CO` (commodity equipment), `RIO.L` (commodity miner), `SHEL.L` (commodity oil), `CNQ` (commodity oil), `MU` (commodity memory), `VZ` (utility-like telecom), `T` (commodity telecom), `INGA.AS` (EU banking), `BNP.PA` (EU banking), `HSBA.L` (global banking), `CRH` (building materials), `DSV.CO` (freight commodity), `KNIN.SW` (freight commodity), `DG.PA` (construction-heavy conglomerate), `AIR.PA` (duopoly aerospace, but supply-chain constrained)

---

## Full Candidate Table

| Ticker | Company | Sector | Style | Source Bucket | Short Reason | Possible Disqualifier | Mkt Cap | Priority | Triage Rec | Confidence |
|--------|---------|--------|-------|---------------|--------------|----------------------|---------|----------|------------|------------|
| V | Visa Inc. | Financials | recovery | seed\|52wk_low | Duopoly payment rail near 52-week low; fee model unmatched | Regulatory pressure on interchange fees; BNPL disruption | mega | high | yes | high |
| BRK-B | Berkshire Hathaway B | Financials | recovery | seed\|52wk_low | Fortress balance sheet near 52-week low; Buffett-built flywheel | Succession risk; insurance cycle exposure | mega | high | yes | high |
| HD | Home Depot Inc. | Consumer | recovery | 52wk_low | Pro segment resilient; housing cycle recovery play near low | Housing slowdown prolonged; SRS acquisition integration risk | mega | high | yes | high |
| CRM | Salesforce Inc. | Technology | recovery | 52wk_low\|fcf_roic | CRM market leader; margin inflection and strong FCF near low | Slowing enterprise spend; Agentforce adoption unproven at scale | mega | high | yes | high |
| NOW | ServiceNow Inc. | Technology | recovery | 52wk_low | Workflow automation leader; AI agents expanding TAM near low | Premium valuation even at low; enterprise budget scrutiny | mega | high | yes | high |
| BSX | Boston Scientific Corp. | Healthcare | recovery | healthcare_quality\|52wk_low | Electrophysiology and structural heart growing fast; near low | Competitive intensity from Medtronic and Abbott | mega | high | yes | high |
| AMAT | Applied Materials Inc. | Technology | compounder | semis_and_infra\|fcf_roic\|sector_leader | Broadest semi equipment portfolio; AI capex cycle sustaining demand | Semi equipment cycle downturn; China export restrictions | mega | high | yes | high |
| NOVN.SW | Novartis AG | Healthcare | value | large_cap_europe_quality\|fcf_roic | Post-Sandoz spinoff; high FCF yield with refocused innovative pipeline | Patent cliffs on key drugs; pipeline execution risk | mega | high | yes | high |
| APP | AppLovin Corp. | Technology | compounder | 52wk_high\|post_earnings | AI-driven ad targeting showing exceptional ROAS; strong earnings beat | Advertising cyclicality; regulatory scrutiny of data practices | large | high | yes | medium |
| COHR | Coherent Corp. | Technology | compounder | 52wk_high | AI datacenter optical interconnect demand surging; near 52-week high | High debt from II-VI merger; component commoditization risk | large | high | yes | medium |
| PLTR | Palantir Technologies Inc. | Technology | compounder | 52wk_high | AIP platform driving commercial acceleration; government moat real | Extreme valuation; stock-based comp dilution historically high | large | high | yes | medium |
| SPOT | Spotify Technology SA | Communication Services | compounder | 52wk_high | Margin inflection underway; global audio monopoly at 52-week high | Content cost inflation from labels; Apple/Google platform risk | large | high | yes | medium |
| GILD | Gilead Sciences Inc. | Healthcare | value | fcf_roic | HIV franchise generates exceptional FCF; oncology pipeline underappreciated | HIV franchise maturity; lenacapavir price pressure globally | large | high | yes | high |
| MSFT | Microsoft Corp. | Technology | compounder | seed\|sector_leader | Azure + Copilot compounding; deepest enterprise AI monetization | Regulatory antitrust scrutiny; valuation already reflects optimism | mega | medium | maybe | high |
| GOOG | Alphabet Inc. | Technology | compounder | seed\|sector_leader | Search moat intact; GCP accelerating; YouTube ad recovery | AI search disintermediation risk; DOJ antitrust remedies pending | mega | medium | maybe | high |
| META | Meta Platforms Inc. | Technology | compounder | seed\|sector_leader | Ads efficiency gains from AI; Reels and WhatsApp monetization maturing | Reality Labs losses ongoing; regulatory pressure in Europe | mega | medium | maybe | high |
| MA | Mastercard Inc. | Financials | compounder | seed | Duopoly payment rail; cross-border volume and value-added services growing | Regulatory interchange caps; real-time payment alternatives | mega | medium | maybe | high |
| CSU.TO | Constellation Software Inc. | Technology | compounder | seed | Serial VMS acquirer; unmatched capital allocation discipline | Acquisition pipeline may thin at scale; Canadian listing friction | large | medium | maybe | high |
| DHR | Danaher Corp. | Industrials | compounder | seed | DBS system drives compounding; bioprocessing recovery underway | Bioprocessing destocking not fully resolved; Veralto spinoff complexity | mega | medium | maybe | high |
| MCO | Moody's Corp. | Financials | compounder | seed | Oligopoly ratings franchise; MA analytics growing recurring mix | Bond issuance cyclicality; regulatory intervention risk | large | medium | maybe | high |
| SPGI | S&P Global Inc. | Financials | compounder | seed | Indices + ratings duopoly; Market Intelligence growing fast | Bond market cyclicality; IHS Markit integration costs normalized | mega | medium | maybe | high |
| FICO | Fair Isaac Corp. | Technology | compounder | seed | FICO score is the credit standard; pricing power unmatched | CFPB regulatory pressure; VantageScore alternative gaining lenders | large | medium | maybe | high |
| ROP | Roper Technologies Inc. | Industrials | compounder | seed | Asset-light software compounder; disciplined niche acquisitions | Acquisition pace depends on deal flow; premium multiple persistent | large | medium | maybe | high |
| IDXX | IDEXX Laboratories Inc. | Healthcare | compounder | seed\|healthcare_quality | Installed base of analyzers creates captive reagent annuity revenue | Pet spending softness; premium valuation historically | large | medium | maybe | high |
| TDG | TransDigm Group Inc. | Industrials | compounder | seed\|industrial_compounders | Sole-source aftermarket aerospace parts; pricing power exceptional | High leverage by design; DoD scrutiny of sole-source pricing | large | medium | maybe | high |
| ODFL | Old Dominion Freight Line Inc. | Industrials | compounder | seed\|industrial_compounders | Best-in-class LTL service ratio; takes share in every cycle | LTL freight market soft; macro-sensitive volumes | large | medium | maybe | high |
| SHW | Sherwin-Williams Co. | Consumer | compounder | seed\|consumer_quality | Paint distribution moat; pro contractor loyalty irreplaceable | Housing market sensitivity; raw material cost pressure | mega | medium | maybe | high |
| FAST | Fastenal Co. | Industrials | compounder | seed | On-site vending and Onsite program deepens customer switching costs | Industrial cycle sensitivity; slow Onsite expansion pace | large | medium | maybe | high |
| POOL | Pool Corp. | Consumer | compounder | seed\|consumer_quality | Near-monopoly pool distribution; installed base drives recurring MRO | Pool construction down; repair-only demand softer than expected | large | medium | maybe | high |
| MTD | Mettler-Toledo International Inc. | Industrials | compounder | seed\|healthcare_quality | Global balance/analytics leader; lab and pharma repeat consumables | China revenue significant; lab spending weak post-COVID boom | large | medium | maybe | high |
| WST | West Pharmaceutical Services Inc. | Healthcare | compounder | seed\|healthcare_quality | Essential drug closure components; HVP mix drives margin expansion | BioPharma capex cycle downturn; normalization from COVID volumes | large | medium | maybe | high |
| COST | Costco Wholesale Corp. | Consumer | compounder | large_cap_us_quality\|consumer_quality | Membership model creates captive repeat spend; renewal rate near 93% | Premium valuation; limited international upside near-term | mega | medium | maybe | high |
| ADP | Automatic Data Processing Inc. | Technology | compounder | large_cap_us_quality | Payroll processing float and switching costs; reliable margin expansion | Rate sensitivity on float income; HCM competition from Workday | mega | medium | maybe | high |
| CTAS | Cintas Corp. | Industrials | compounder | large_cap_us_quality | Route density moat in uniform services; expanding into safety products | Premium valuation; labor cost inflation sensitivity | mega | medium | maybe | high |
| CPRT | Copart Inc. | Industrials | compounder | large_cap_us_quality | Two-sided vehicle auction platform; land moat irreproducible | Total loss rate normalization; international expansion slower | large | medium | maybe | high |
| ROL | Rollins Inc. | Industrials | compounder | large_cap_us_quality | Route density in pest control; non-discretionary demand with pricing power | Premium valuation for a slow-growth business | large | medium | maybe | high |
| BR | Broadridge Financial Solutions Inc. | Technology | compounder | large_cap_us_quality | Mission-critical proxy and investor comms; near-captive recurring revenue | Slow organic growth; competitive pressure in wealth management tech | large | medium | maybe | high |
| PAYX | Paychex Inc. | Technology | compounder | large_cap_us_quality | SMB payroll leader; float income and PEO growing recurring base | Rate cuts reduce float income; ADP competition in SMB | large | medium | maybe | high |
| SSNC | SS&C Technologies Holdings Inc. | Technology | compounder | large_cap_us_quality | Mission-critical fund admin and software for asset managers | High debt load from acquisitions; PE ownership risk | large | medium | maybe | medium |
| MKTX | MarketAxess Holdings Inc. | Financials | compounder | large_cap_us_quality\|financial_quality | Electronic bond trading platform; liquidity network effects durable | Competition from Bloomberg; equity-like bond market slowdown | large | medium | maybe | medium |
| NFLX | Netflix Inc. | Communication Services | compounder | large_cap_us_quality | Ad-supported tier and live sports driving new monetization layer | Content cost inflation; streaming competition intensifies again | mega | medium | maybe | high |
| VRSK | Verisk Analytics Inc. | Industrials | compounder | large_cap_us_quality | Insurance data monopoly; P&C rate hardening drives growth | Post-Energy/Financial Services divestitures now pure-play; re-rating risk | large | medium | maybe | high |
| CSGP | CoStar Group Inc. | Technology | compounder | large_cap_us_quality | CRE data monopoly; Homes.com investment phase creating optionality | Residential bet expensive; profitability diluted near-term | large | medium | maybe | medium |
| FDS | FactSet Research Systems Inc. | Financials | compounder | large_cap_us_quality\|financial_quality | Buy-side financial data; loyal client base with high switching costs | Bloomberg dominance; AI may unbundle research workflows | large | medium | maybe | high |
| ICE | Intercontinental Exchange Inc. | Financials | compounder | large_cap_us_quality\|financial_quality | Energy futures and mortgage data (ICE Mortgage Technology) compounding | Black Knight integration; mortgage volume cyclicality | mega | medium | maybe | high |
| CME | CME Group Inc. | Financials | compounder | large_cap_us_quality\|financial_quality | Global derivatives clearing monopoly; rate volatility boosts volumes | Volumes normalize as rates stabilize; FTX-era crypto competition faded | mega | medium | maybe | high |
| CBOE | Cboe Global Markets Inc. | Financials | compounder | large_cap_us_quality | SPX options near-monopoly; 0DTE options driving structural volume uplift | Regulatory change to options market structure; vol normalization | large | medium | maybe | high |
| NDAQ | Nasdaq Inc. | Financials | compounder | large_cap_us_quality\|financial_quality | Shifting to recurring tech/data revenues; Adenza acquisition adds risk | Adenza integration cost; legacy trading revenues declining | large | medium | maybe | medium |
| MSCI | MSCI Inc. | Financials | compounder | large_cap_us_quality\|financial_quality | Passive AUM growth taxed via index licensing; pricing power sticky | Active-to-passive shift plateauing; fee pressure on index products | large | medium | maybe | high |
| NKE | Nike Inc. | Consumer | recovery | large_cap_us_quality\|consumer_quality | DTC pullback under new CEO; Elliot Hill stabilizing brand trajectory | China exposure; Hoka/On Running taking share in key categories | large | medium | maybe | medium |
| SBUX | Starbucks Corp. | Consumer | recovery | large_cap_us_quality\|consumer_quality | Brian Niccol early-stage turnaround; brand value intact globally | China recovery slow; menu complexity reductions take time | large | medium | maybe | medium |
| MCD | McDonald's Corp. | Consumer | compounder | large_cap_us_quality\|consumer_quality | Franchise model insulates from cost inflation; value positioning resilient | E. coli incident reputational overhang; consumer trade-down already priced | mega | medium | maybe | high |
| YUM | Yum! Brands Inc. | Consumer | compounder | large_cap_us_quality\|consumer_quality | Asset-light franchise model; Taco Bell US unit economics best in QSR | High leverage; international exposed to EM macro | large | medium | maybe | high |
| HSY | Hershey Co. | Consumer | compounder | large_cap_us_quality\|consumer_quality | Cocoa cost normalization could restore margins; iconic brand loyalty | Cocoa prices elevated; GLP-1 weight-loss headwind to snacking | large | medium | maybe | medium |
| CHD | Church & Dwight Co. | Consumer | compounder | large_cap_us_quality\|consumer_quality | OxiClean/Arm & Hammer portfolio; consistent 4-5% organic growth compounder | Premium valuation relative to peers; private label competition | large | medium | maybe | high |
| EL | Estee Lauder Companies Inc. | Consumer | recovery | large_cap_us_quality\|consumer_quality | China prestige beauty recovery; management reset underway post-collapse | China recovery trajectory uncertain; execution risk in restructuring | large | medium | maybe | low |
| TPX | Tempur Sealy International Inc. | Consumer | cyclical | large_cap_us_quality\|consumer_quality | Sealy acquisition closes distribution; Tempur brand premium durable | Housing-linked cyclical; Mattress Firm distribution integration risk | large | medium | maybe | medium |
| MCK | McKesson Corp. | Healthcare | compounder | large_cap_us_quality\|healthcare_quality | Drug distribution oligopoly; oncology services diversifying revenue | Drug pricing reform threat; opioid liability tail | mega | medium | maybe | high |
| IQV | IQVIA Holdings Inc. | Healthcare | compounder | large_cap_us_quality\|healthcare_quality | CRO + real-world data asset creates unique AI-enabled trial platform | Biotech funding cycle sensitivity; GLP-1 trial surge may plateau | large | medium | maybe | high |
| ISRG | Intuitive Surgical Inc. | Healthcare | compounder | large_cap_us_quality | da Vinci installed base creates instrument and service annuity | Competition from Medtronic Hugo and J&J Ottava | mega | medium | maybe | high |
| EW | Edwards Lifesciences Corp. | Healthcare | compounder | large_cap_us_quality\|healthcare_quality | TAVR market leader; TMVR expansion large untapped opportunity | Medtronic and Abbott TAVR competition intensifying; TMVR slow uptake | large | medium | maybe | high |
| MC.PA | LVMH Moet Hennessy Louis Vuitton SE | Consumer | compounder | large_cap_europe_quality | Portfolio breadth across luxury unmatched; aspirational demand resilient | China luxury spending soft; organic volume growth normalizing | mega | medium | maybe | high |
| RMS.PA | Hermes International SCA | Consumer | compounder | large_cap_europe_quality | Intentional scarcity of Birkin; pricing power with no ceiling | Extreme valuation; family control limits shareholder-friendly actions | mega | medium | maybe | high |
| SAP.DE | SAP SE | Technology | compounder | large_cap_europe_quality | ERP cloud migration to S/4HANA driving multi-year revenue step-up | Cloud transition margin drag; hyperscaler CRM/ERP competition | mega | medium | maybe | high |
| WKL.AS | Wolters Kluwer NV | Technology | compounder | large_cap_europe_quality | Mission-critical compliance software; digital revenues now 60%+ | AI disruption to legal/tax research; slow revenue growth historically | large | medium | maybe | high |
| OR.PA | L'Oreal SA | Consumer | compounder | large_cap_europe_quality | Broadest beauty portfolio; dermatology and active cosmetics growing | China prestige beauty softness; premium valuation | mega | medium | maybe | high |
| CFR.SW | Compagnie Financiere Richemont SA | Consumer | compounder | large_cap_europe_quality | Cartier and IWC jewellery moat; YNAP digital overhang clearing | China jewellery demand soft; YNAP disposal still pending | mega | medium | maybe | medium |
| ADYEN.AS | Adyen NV | Technology | compounder | large_cap_europe_quality | Unified commerce platform wins enterprise merchants vs legacy PSPs | Margin guidance disappointed in 2023; US expansion slower than expected | large | medium | maybe | medium |
| DSY.PA | Dassault Systemes SE | Technology | compounder | large_cap_europe_quality | 3DEXPERIENCE platform mission-critical in aerospace and life sciences | Life Sciences vertical slowdown; SAP competition in PLM | large | medium | maybe | high |
| EL.PA | EssilorLuxottica SA | Healthcare | compounder | large_cap_europe_quality | Lens+frame vertical integration; META smart glasses partnership growing | Integration complexity; luxury frame competition from independents | mega | medium | maybe | high |
| KER.PA | Kering SA | Consumer | recovery | large_cap_europe_quality | Gucci reset under new creative direction; depressed valuation vs peers | Gucci brand recovery trajectory uncertain; China dependence high | large | medium | maybe | medium |
| STMN.SW | Straumann Holding AG | Healthcare | compounder | large_cap_europe_quality | Premium implant brand with clear aligner optionality; global expansion | Clear aligner competition from Align; China pricing pressure | large | medium | maybe | high |
| LONN.SW | Lonza Group AG | Healthcare | compounder | large_cap_europe_quality | Top-tier CDMO for biologics; GLP-1 manufacturing demand surge | Roche Genentech site sale overhang; customer concentration risk | large | medium | maybe | high |
| NOVO-B.CO | Novo Nordisk A/S | Healthcare | compounder | large_cap_europe_quality\|healthcare_quality | GLP-1 category creator; Ozempic/Wegovy supply expansion underway | Eli Lilly competition; tirzepatide weight loss superiority data | mega | medium | maybe | high |
| ASML.AS | ASML Holding NV | Technology | compounder | large_cap_europe_quality | Sole EUV litho supplier; no replacement in sight; backlog multi-year | China export restrictions; order timing lumpy | mega | medium | maybe | high |
| RKT.L | Reckitt Benckiser Group plc | Consumer | value | large_cap_europe_quality | Dettol and Durex brands durable; depressed post-litigation; undervalued | NEC litigation tail; Mead Johnson divestiture still pending | large | medium | maybe | medium |
| ICG.L | InterContinental Hotels Group plc | Consumer | compounder | large_cap_europe_quality | Asset-light hotel franchise; IHG One Rewards loyalty platform growing | Travel slowdown risk; Airbnb structural pressure on leisure hotels | large | medium | maybe | medium |
| ABB.ST | ABB Ltd. | Industrials | compounder | large_cap_europe_quality | Electrification and automation megatrends; simplified portfolio post-restructuring | Industrial cycle exposure; European capex weakness | mega | medium | maybe | medium |
| SIE.DE | Siemens AG | Industrials | compounder | large_cap_europe_quality | Factory automation and building efficiency; Xcelerator platform SaaS shift | Siemens Energy stake overhang; conglomerate discount persists | mega | medium | maybe | medium |
| SAN.PA | Sanofi SA | Healthcare | recovery | large_cap_europe_quality | Dupixent blockbuster growing; consumer health spinoff unlocks value | Post-Dupixent growth pipeline execution risk | mega | medium | maybe | medium |
| ALC | Alcon Inc. | Healthcare | compounder | large_cap_europe_quality | Aging population drives cataract surgery and contact lens volumes | Post-Novartis standalone still building margins; J&J competition | large | medium | maybe | medium |
| NESN.SW | Nestle SA | Consumer | value | large_cap_europe_quality | Underperformance vs peers; brand portfolio rationalization underway | Organic growth stalled; margin pressure from input costs | mega | medium | maybe | medium |
| ROG.SW | Roche Holding AG | Healthcare | compounder | large_cap_europe_quality | Diagnostics plus oncology biologics; Alzheimer's drug pipeline promising | Biosimilar erosion on Avastin/Rituxan; weight-loss drug late entry | mega | medium | maybe | high |
| AZN.L | AstraZeneca plc | Healthcare | compounder | large_cap_europe_quality\|healthcare_quality | Oncology ADC and rare disease pipeline best-in-class execution | China accounting investigation overhang; blockbuster concentration | mega | medium | maybe | high |
| GSK.L | GSK plc | Healthcare | recovery | large_cap_europe_quality | Shingrix and HIV franchise solid; Haleon separation complete, cleaner story | Zantac litigation tail; RSV vaccine competition from Pfizer | large | medium | maybe | medium |
| LSEG.L | London Stock Exchange Group plc | Financials | compounder | large_cap_europe_quality | Refinitiv data now driving recurring revenue mix transformation | Refinitiv integration slow; Bloomberg competition entrenched | mega | medium | maybe | medium |
| ULVR.L | Unilever plc | Consumer | value | large_cap_europe_quality | Hein Schumacher restructuring improving portfolio quality and margins | Ice cream spinoff complexity; EM currency exposure | mega | medium | maybe | medium |
| BA.L | BAE Systems plc | Industrials | compounder | large_cap_europe_quality | European defense spending surge; backlog visibility multi-year | Government budget dependency; valuation already pricing re-armament | large | medium | maybe | high |
| RELX.L | RELX plc | Technology | compounder | large_cap_europe_quality | LexisNexis analytics and Elsevier science; AI-enhanced workflows sticky | Open access research threat to Elsevier; valuation already full | mega | medium | maybe | high |
| EXPN.L | Experian plc | Technology | compounder | large_cap_europe_quality | B2B credit bureau plus direct-to-consumer growing; EM expansion | CFPB regulatory risk in US; data breach liability | large | medium | maybe | high |
| NVDA | NVIDIA Corp. | Technology | compounder | semis_and_infra\|sector_leader | AI training and inference monopoly; CUDA ecosystem lock-in deep | Custom ASIC threat from hyperscalers; extreme valuation | mega | medium | maybe | high |
| TSM | Taiwan Semiconductor Manufacturing Co. Ltd. | Technology | compounder | semis_and_infra | Leading-edge fab monopoly; AI chip demand multiyear tailwind | Taiwan geopolitical risk; CHIPS Act complexity | mega | medium | maybe | high |
| LRCX | Lam Research Corp. | Technology | compounder | semis_and_infra\|sector_leader | Etch and deposition leader; 3D NAND recovery plus HBM demand rising | Memory equipment cycle; China export restriction risk | mega | medium | maybe | high |
| KLAC | KLA Corp. | Technology | compounder | semis_and_infra\|sector_leader | Process control monopoly; defect detection critical at leading edge | China revenue at risk from export controls; semi cycle timing | mega | medium | maybe | high |
| MRVL | Marvell Technology Inc. | Technology | compounder | semis_and_infra | Custom ASIC for hyperscalers; 800G networking chip design wins | Customer concentration in 2-3 hyperscalers; execution on ramp | large | medium | maybe | medium |
| AVGO | Broadcom Inc. | Technology | compounder | semis_and_infra\|sector_leader | VMware cross-sell + AI custom silicon; FCF conversion exceptional | VMware integration execution; high leverage post-acquisition | mega | medium | maybe | high |
| ARM | Arm Holdings plc | Technology | compounder | semis_and_infra | CPU IP in virtually every smartphone; AI edge and server expansion | Extreme valuation; RISC-V open-source long-term competitive threat | mega | medium | maybe | medium |
| QCOM | Qualcomm Inc. | Technology | compounder | semis_and_infra | Snapdragon AI on-device chip leadership; PC and auto expanding | Apple modem risk if Apple in-house succeeds; mobile cycle | large | medium | maybe | medium |
| ADI | Analog Devices Inc. | Technology | compounder | semis_and_infra\|sector_leader | Best analog portfolio; industrial and healthcare exposure high-quality | Industrial cycle destocking; inventory normalization ongoing | large | medium | maybe | high |
| TXN | Texas Instruments Inc. | Technology | compounder | semis_and_infra | Analog semiconductor franchise; manufacturing moat and FCF discipline | Heavy capex cycle with new fabs; inventory overhang | mega | medium | maybe | high |
| MPWR | Monolithic Power Systems Inc. | Technology | compounder | semis_and_infra | AI server power management wins; best-in-class efficiency | Valuation stretched; niche could attract TI/ADI competition | large | medium | maybe | medium |
| ON | ON Semiconductor Corp. | Technology | compounder | semis_and_infra | EV and industrial power content per vehicle expanding | EV market growth slowdown; pricing competition in SiC | large | medium | maybe | medium |
| LLY | Eli Lilly and Co. | Healthcare | compounder | healthcare_quality | Tirzepatide weight loss + diabetes; Alzheimer's drug Kisunla pipeline deep | GLP-1 capacity constraints; extreme valuation | mega | medium | maybe | high |
| ABBV | AbbVie Inc. | Healthcare | compounder | healthcare_quality | Skyrizi and Rinvoq offsetting Humira biosimilar erosion ahead of schedule | Skyrizi/Rinvoq patent timeline; M&A execution risk | mega | medium | maybe | high |
| UNH | UnitedHealth Group Inc. | Healthcare | compounder | healthcare_quality | Optum vertical integration creates unmatched managed care moat | Medical cost ratio elevated; DOJ antitrust investigation ongoing | mega | medium | maybe | high |
| STE | STERIS plc | Healthcare | compounder | healthcare_quality | Hospital sterilization services recurring model; expansion into pharma | Cantel integration costs; healthcare capex softness | large | medium | maybe | high |
| VEEV | Veeva Systems Inc. | Healthcare | compounder | healthcare_quality | CRM + data vault standard for pharma; Vault CRM migration de-risks Salesforce | Salesforce partnership unwind complete; growth may slow post-transition | large | medium | maybe | high |
| DOCS | Doximity Inc. | Healthcare | compounder | healthcare_quality | Physician network monopoly; pharma marketing pivot to digital ongoing | Pharma ad budget cyclicality; limited international moat | large | medium | maybe | medium |
| ITW | Illinois Tool Works Inc. | Industrials | compounder | industrial_compounders | 80/20 simplification model; best margins in industrial diversifieds | Industrial cycle sensitivity; limited organic growth upside | mega | medium | maybe | high |
| EMR | Emerson Electric Co. | Industrials | compounder | industrial_compounders | Process automation pure-play post-portfolio simplification; energy transition | Aspen Technology integration costs; industrial cycle timing | large | medium | maybe | medium |
| PH | Parker Hannifin Corp. | Industrials | compounder | industrial_compounders | Aerospace aftermarket mix growing; Win Strategy discipline proven | Meggitt integration complete but high leverage remains | mega | medium | maybe | high |
| AME | Ametek Inc. | Industrials | compounder | industrial_compounders | Niche instrument acquisitions compounding; consistent 20%+ EBITDA margins | Acquisition pace slowing; industrial instrumentation cycle soft | large | medium | maybe | high |
| WCN | Waste Connections Inc. | Industrials | compounder | industrial_compounders | Secondary-market waste focus reduces competition; superior pricing discipline | Premium valuation vs WM; slower organic growth | large | medium | maybe | high |
| RSG | Republic Services Inc. | Industrials | compounder | industrial_compounders | Solid waste oligopoly; environmental services digital transformation | Blue Triton integration; capex intensity for CNG fleet | large | medium | maybe | high |
| GWW | W.W. Grainger Inc. | Industrials | compounder | industrial_compounders | High-touch MRO model with Zoro digital flank; share gains durable | Industrial cycle; Amazon Business competition in spot MRO | large | medium | maybe | high |
| CSX | CSX Corp. | Industrials | compounder | industrial_compounders | East corridor rail oligopoly; pricing power over trucking secular | Volume sensitive to coal and intermodal cycles; PSR limits growth | large | medium | maybe | high |
| NSC | Norfolk Southern Corp. | Industrials | compounder | industrial_compounders | East rail network; operational improvements post-Ohio derailment reset | Ohio derailment liability overhang; activist pressure legacy | large | medium | maybe | medium |
| UNP | Union Pacific Corp. | Industrials | compounder | industrial_compounders | West rail monopoly; precision railroading drives consistent OR improvement | Volume leverage to US-Mexico trade; intermodal cycle | mega | medium | maybe | high |
| XPO | XPO Inc. | Industrials | recovery | industrial_compounders | LTL-focused post-spinoffs; operational gains catching ODFL and SAIA | LTL pricing environment soft; Yellow closure share may plateau | large | medium | maybe | medium |
| JPM | JPMorgan Chase & Co. | Financials | compounder | financial_quality | Best-in-class US bank; Dimon capital allocation disciplines returns | Rate cycle sensitivity; Basel III endgame capital requirements | mega | medium | maybe | high |
| CB | Chubb Ltd. | Financials | compounder | financial_quality | P&C rate hardening cycle; Evan Greenberg underwriting discipline best-in-class | Catastrophe loss exposure; P&C cycle eventual softening | mega | medium | maybe | high |
| AJG | Arthur J. Gallagher & Co. | Financials | compounder | financial_quality | Insurance brokerage compounder; M&A-fueled growth with pricing power | Insurance cycle softening; M&A integration risk at pace | large | medium | maybe | high |
| AFL | Aflac Inc. | Financials | compounder | financial_quality | Supplemental health insurance monopoly in Japan; consistent buybacks | Japan currency risk; US cancer insurance market saturation | large | medium | maybe | high |
| MKL | Markel Group Inc. | Financials | compounder | financial_quality | Mini-Berkshire model; Markel Ventures adds non-insurance compounding | Specialty insurance pricing cyclicality; smaller float than BRK | large | medium | maybe | high |
| BX | Blackstone Inc. | Financials | compounder | financial_quality | Largest alternative asset manager; BREIT and retail AUM channel growing | Real estate NAV pressure if rates stay high; fee-sensitive AUM | mega | medium | maybe | high |
| KKR | KKR & Co. Inc. | Financials | compounder | financial_quality | Insurance balance sheet (Global Atlantic) plus alts flywheel compounding | Credit cycle sensitivity; carried interest volatility | mega | medium | maybe | high |
| PG | Procter & Gamble Co. | Consumer | compounder | consumer_quality | Category-leading brands with pricing power; EM exposure growing | Private label substitution at margin; volume growth slow | mega | medium | maybe | high |
| KO | Coca-Cola Co. | Consumer | compounder | consumer_quality | Global distribution moat; pricing power proven through inflation cycle | GLP-1 weight-loss headwind; premium valuation for slow grower | mega | medium | maybe | high |
| PEP | PepsiCo Inc. | Consumer | compounder | consumer_quality | Frito-Lay snack moat diversifies; pricing power held in inflationary period | Snack volume normalization; GLP-1 headwind to caloric snacks | mega | medium | maybe | high |
| DXCM | DexCom Inc. | Healthcare | compounder | consumer_quality | CGM market expanding to type 2 non-insulin users; G7 competitive | Abbott FreeStyle Libre share pressure; Medicare reimbursement risk | large | medium | maybe | medium |
| AAPL | Apple Inc. | Technology | compounder | sector_leader | Services flywheel growing 15%+; installed base 2B+ with high loyalty | iPhone China exposure and tariff risk; services antitrust scrutiny | mega | medium | maybe | high |
| AMZN | Amazon.com Inc. | Technology | compounder | sector_leader | AWS margin expansion; advertising now $50B+ and high-margin | Retail capex remains heavy; antitrust breakup risk long-term | mega | medium | maybe | high |
| CDNS | Cadence Design Systems Inc. | Technology | compounder | sector_leader | EDA duopoly with SNPS; every AI chip designed on Cadence tools | SNPS/Ansys merger competitive response; China EDA restriction | large | medium | maybe | high |
| SNPS | Synopsys Inc. | Technology | compounder | sector_leader | EDA plus Ansys simulation acquisition creates chip-to-system platform | Ansys deal antitrust scrutiny; integration complexity | large | medium | maybe | high |
| ORCL | Oracle Corp. | Technology | compounder | sector_leader | OCI GPU cloud and database lock-in; AI training workloads growing fast | Hyperscaler cloud competition; database migration risk accelerating | mega | medium | maybe | medium |
| PANW | Palo Alto Networks Inc. | Technology | compounder | sector_leader | Platform consolidation strategy winning; Cortex AI growing billings | Platformization short-term billings pressure; CrowdStrike competition | large | medium | maybe | medium |
| INTU | Intuit Inc. | Technology | compounder | sector_leader | TurboTax moat plus SMB Quickbooks; Credit Karma adds consumer fin data | IRS free filing threat; Mailchimp integration slower than expected | mega | medium | maybe | high |
| UBER | Uber Technologies Inc. | Technology | compounder | sector_leader | Network density in both mobility and delivery creating profitable flywheel | Autonomous vehicle threat from Waymo could undermine driver model | large | medium | maybe | medium |
| ABNB | Airbnb Inc. | Consumer | compounder | sector_leader | Asset-light marketplace with host/guest loyalty; experiences layer growing | Regulatory risk in cities; hotels recovering competitive position | large | medium | maybe | medium |
| WDAY | Workday Inc. | Technology | compounder | sector_leader | HCM and Financials cloud suite; large enterprise loyalty extremely high | SAP S/4HANA integrated FINS competition; AI agents may commoditize HR | large | medium | maybe | high |
| TTD | The Trade Desk Inc. | Technology | compounder | sector_leader | Independent DSP standard; CTV and retail media beneficiary | Google Privacy Sandbox cookie alternative slows identity graph | large | medium | maybe | medium |
| RACE | Ferrari NV | Consumer | compounder | sector_leader | Intentional production scarcity; waitlist creates irreplaceable pricing power | EV transition execution risk; ultra-luxury demand China softness | mega | medium | maybe | high |
| HUBS | HubSpot Inc. | Technology | compounder | sector_leader | SMB CRM standard; AI features accelerating platform stickiness | Salesforce competitive pressure in mid-market; acquisition target premium | large | medium | maybe | medium |
| ANSS | ANSYS Inc. | Technology | compounder | sector_leader | Simulation software standard in aerospace/auto; Synopsys merger pending | Synopsys acquisition uncertainty; standalone disruption if deal falls | large | medium | maybe | medium |
| GEBN.SW | Geberit AG | Industrials | compounder | large_cap_europe_quality | European sanitary systems leader; specification-driven demand, pricing durable | European construction cycle sensitivity; limited US presence | large | medium | maybe | medium |
| IFX.DE | Infineon Technologies AG | Technology | compounder | large_cap_europe_quality | Power semi leader for EV and renewables; SiC position strong | EV slowdown hitting auto semi demand; inventory excess | large | medium | maybe | medium |
| EXPD | Expeditors International of Washington Inc. | Industrials | compounder | industrial_compounders | Asset-light freight forwarding with best culture; net cash balance sheet | Freight forwarding commoditized; volume and rate cycle sensitivity deep | large | medium | maybe | medium |
| PHIA.AS | Koninklijke Philips NV | Healthcare | recovery | large_cap_europe_quality | CPAP recall settlement complete; imaging systems backlog recovering | Brand damage from recall; Siemens Healthineers and GE competition | large | medium | maybe | low |
| ADS.DE | Adidas AG | Consumer | recovery | large_cap_europe_quality | Yeezy inventory cleared; Bjorn Borg era brand repositioning showing results | Nike and On Running competition; China brand perception complex | large | medium | maybe | medium |
| GS | Goldman Sachs Group Inc. | Financials | cyclical | financial_quality | M&A and IPO cycle recovering; asset management platform scaling | IB revenue deeply cyclical; consumer banking exit still complex | mega | medium | maybe | medium |
| RLI | RLI Corp. | Financials | compounder | financial_quality | Best combined ratio specialty insurer; disciplined niche underwriting | Small scale limits diversification; catastrophe event sensitivity | mid | medium | maybe | medium |
| ACLS | Axcelis Technologies Inc. | Technology | compounder | semis_and_infra | Ion implant niche leader; mature node and SiC EV chip demand | Smaller scale; customer concentration in mature node fabs | mid | medium | maybe | medium |
| ONTO | Onto Innovation Inc. | Technology | compounder | semis_and_infra | Advanced packaging inspection demand rising with AI chip complexity | KLA competitive threat; small scale limits pricing power | mid | medium | maybe | medium |
| MSC | MSC Industrial Direct Co. | Industrials | compounder | industrial_compounders | Metalworking and MRO niche with technical expertise differentiating | Amazon Business and Grainger competition; industrial cycle sensitivity | mid | medium | maybe | medium |
| TSLA | Tesla Inc. | Consumer | speculative | sector_leader | FSD and energy storage optionality real; brand reset needed post-Musk | Brand damage from Musk controversies; BYD price competition severe | mega | low | no | low |
| MAERSK-B.CO | A.P. Moller - Maersk A/S | Industrials | cyclical | large_cap_europe_quality | Container rate spike normalized; logistics transformation uncertain | Pure commodity shipping cycle; no durable pricing moat | large | low | no | low |
| ORSTED.CO | Orsted A/S | Utilities | cyclical | large_cap_europe_quality | Offshore wind regulated returns; US asset write-downs severe | Regulated utility; no pricing power; balance sheet stressed | large | low | no | low |
| VWS.CO | Vestas Wind Systems A/S | Industrials | cyclical | large_cap_europe_quality | Wind turbine OEM with margin recovery; policy-dependent demand | Capital-intensive; commodity competition from Siemens Gamesa and China | large | low | no | low |
| RIO.L | Rio Tinto plc | Materials | cyclical | large_cap_europe_quality | Iron ore and copper volumes; copper optionality for energy transition | Pure commodity miner; no pricing power; China demand risk | mega | low | no | low |
| SHEL.L | Shell plc | Energy | cyclical | large_cap_europe_quality | High FCF and buybacks; energy transition pivot modest | Commodity oil price dependence; energy transition stranded asset risk | mega | low | no | low |
| CNQ | Canadian Natural Resources Ltd. | Energy | cyclical | 52wk_high | Low-cost oil sands producer; long-life reserves dividend capacity | Commodity oil price dependence; no durable moat | large | low | no | low |
| MU | Micron Technology Inc. | Technology | cyclical | 52wk_high | HBM memory demand from AI accelerators; cycle at high point | Pure commodity memory pricing cycle; no moat in DRAM/NAND | large | low | no | low |
| VZ | Verizon Communications Inc. | Communication Services | income | fcf_roic | High dividend yield; FCF stable but growth limited | No pricing power; capex-heavy; secular subscriber pressure | mega | low | no | low |
| T | AT&T Inc. | Communication Services | income | fcf_roic | Debt reduction improving FCF; dividend yield attracts income investors | Massive debt legacy; no competitive differentiation | large | low | no | low |
| INGA.AS | ING Groep NV | Financials | value | large_cap_europe_quality | Digital bank model improving ROE; NIM expansion in rate environment | European banking regulation; credit cycle exposure; no durable moat | large | low | no | low |
| BNP.PA | BNP Paribas SA | Financials | value | large_cap_europe_quality | Largest EU bank by assets; capital return improving | European banking systemic risk; low ROE; no moat | large | low | no | low |
| HSBA.L | HSBC Holdings plc | Financials | value | large_cap_europe_quality | Asia-heavy bank benefiting from rate environment | China exposure; banking moat absent; restructuring ongoing | mega | low | no | low |
| CRH | CRH plc | Materials | cyclical | large_cap_europe_quality | Infrastructure materials play; US re-listing and infrastructure bill benefit | Building materials commodity; cycle-dependent; no moat | mega | low | no | low |
| DSV.CO | DSV A/S | Industrials | cyclical | large_cap_europe_quality | Serial freight M&A consolidator; DB Schenker acquisition transformative | Freight forwarding commodity service; DB Schenker integration risk | large | low | no | low |
| KNIN.SW | Kuehne + Nagel International AG | Industrials | cyclical | large_cap_europe_quality | Top freight forwarder; digital KNAPP logistics platform differentiating | Freight cycle commodity; volume and rate sensitivity deep | large | low | no | low |
| DG.PA | Vinci SA | Industrials | compounder | large_cap_europe_quality | Airport and motorway concessions provide high-quality annuity cash flows | Construction segment cyclical; French political risk on concessions | large | low | no | medium |
| AIR.PA | Airbus SE | Industrials | compounder | large_cap_europe_quality | Boeing delivery crisis creates multi-year Airbus order windfall | Supply chain constraints limit delivery upside; duopoly risk if Boeing recovers | mega | low | no | medium |

---

Next step: Run Stage B1 triage. B1 reads the full candidates.json and assigns a verdict (advance / hold / reject) to every name independently.
