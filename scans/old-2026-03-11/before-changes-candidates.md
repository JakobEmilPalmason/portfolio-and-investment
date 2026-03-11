> **Note on seed-origin names:** Tickers tagged `source_bucket=seed` are curated inputs from `seeds/watchlist.json`, not discovered names. They reflect prior knowledge or personal watchlist intent rather than fresh market signals.

# Stage A2 Candidate Filter — 2026-03-11

## Summary
- **Total candidates:** 227
- **Priority:** high=35  medium=164  low=28
- **Triage rec:** yes=22  maybe=13  no=192

### Counts by bucket
  - 52wk_high: 6
  - 52wk_low: 10
  - consumer_quality: 15
  - fcf_roic: 8
  - financial_quality: 15
  - healthcare_quality: 13
  - industrial_compounders: 15
  - large_cap_europe_quality: 40
  - large_cap_us_quality: 30
  - post_earnings: 5
  - sector_leader: 58
  - seed: 20
  - semis_and_infra: 16
  - tracked: 19

### Counts by sector
  - Communication Services: 7
  - Consumer: 32
  - Energy: 4
  - Financials: 35
  - Healthcare: 37
  - Industrials: 40
  - Materials: 6
  - Real Estate: 4
  - Technology: 58
  - Utilities: 4

### triage_rec=yes tickers
  CAT, ORCL, HD, MU, COHR, VZ, GILD, TEAM, FLUT, RDDT, NOVN.SW, SAN.PA, APP, MMM, CVS, INTC, PFE, DIS, MDT, BIIB, AMGN, HUM

### triage_rec=maybe tickers
  AAPL, ARM, ADBE, ALAB, AVGO, CRM, DSV.CO, NOW, NVDA, NOVO-B.CO, QCOM, RKLB, SNOW

---

## Full Candidate Table

| ticker | company | sector | style_tag | source_bucket | short_reason | possible_disqualifier | mkt_cap_tier | priority | triage_rec | confidence |
|--------|---------|--------|-----------|---------------|-------------|----------------------|--------------|----------|------------|------------|
| CAT | Caterpillar Inc. | Industrials | cyclical | post_earnings|sector_leader | Earnings beat; construction/mining cycle still resilient | Deep cyclical; no durable moat beyond brand/distribution | mega | high | yes | high |
| ORCL | Oracle Corp. | Technology | compounder | post_earnings|sector_leader | Cloud infrastructure wins accelerating; AI data demand | Legacy enterprise dependency; AWS/Azure competition | mega | high | yes | high |
| HD | Home Depot Inc. | Consumer | value | 52wk_low | Home improvement duopoly; Pro segment growing vs DIY | Housing market rate sensitivity; consumer spending risk | mega | high | yes | high |
| MU | Micron Technology Inc. | Technology | cyclical | 52wk_high | Memory cycle recovery; HBM for AI servers structural | Memory highly cyclical; Samsung/SK Hynix competition | mega | high | yes | high |
| COHR | Coherent Corp. | Technology | compounder | 52wk_high | Datacom transceivers for AI networking; design wins growing | Execution history poor; margin recovery unproven | large | high | yes | medium |
| VZ | Verizon Communications Inc. | Communication Services | income | fcf_roic | Fixed wireless access broadband growing; high FCF yield | Debt-heavy; revenue growth limited; dividend sustainability | mega | high | yes | high |
| GILD | Gilead Sciences Inc. | Healthcare | value | fcf_roic | HIV franchise durable; oncology diversification underway | HIV franchise plateau; oncology pipeline has binary risks | large | high | yes | high |
| TEAM | Atlassian Corp. | Technology | compounder | post_earnings | Dev tools sticky; Data Center migration to cloud complete | Slower enterprise seat expansion; GitHub Copilot threat | large | high | yes | high |
| FLUT | Flutter Entertainment plc | Consumer | compounder | post_earnings | FanDuel US market share leader; profitability inflecting | Regulatory risk on gambling; state-by-state expansion | large | high | yes | high |
| RDDT | Reddit Inc. | Communication Services | compounder | post_earnings | Data licensing and ad monetization early; user growth solid | Pre-mature moat; ad targeting less precise than Meta | large | high | yes | medium |
| NOVN.SW | Novartis AG | Healthcare | value | large_cap_europe_quality|fcf_roic | Post-Sandoz spin; focused biopharma with FCF generation | Patent cliffs mid-decade; pipeline execution risk | mega | high | yes | high |
| SAN.PA | Sanofi S.A. | Healthcare | value | large_cap_europe_quality|fcf_roic | Rare disease + vaccines; Dupixent blockbuster sustaining | Dupixent concentration risk; pipeline execution | mega | high | yes | high |
| APP | AppLovin Corp. | Technology | compounder | 52wk_high | Mobile ad targeting with AI; monetization scaling fast | Concentrated AI-driven revenue; regulatory ad risk | mega | high | yes | high |
| MMM | 3M Co. | Industrials | recovery | 52wk_low | Combat Arms settlement behind; portfolio simplification path | Litigation tail risk; core organic growth still weak | large | high | yes | high |
| CVS | CVS Health Corp. | Healthcare | recovery | 52wk_low | Oak Street + Aetna integration; PBM reform risk quantified | PBM legislative risk; debt from Aetna acquisition | large | high | yes | high |
| INTC | Intel Corp. | Technology | speculative | 52wk_low | Foundry pivot; 18A node could restore competitiveness | Execution risk extreme; AMD/TSMC dominance entrenched | large | high | yes | high |
| PFE | Pfizer Inc. | Healthcare | recovery | 52wk_low | Post-COVID rebase; oncology/RSV pipeline rebuilding | Pipeline needs to deliver; COVID revenue cliff steep | large | high | yes | high |
| DIS | Walt Disney Co. | Communication Services | recovery | 52wk_low | Streaming profitability achieved; parks resilient | Linear TV decline accelerating; ESPN streaming transition | large | high | yes | high |
| MDT | Medtronic plc | Healthcare | recovery | 52wk_low | Simplification strategy; Cardiac Rhythm and Spine recovering | Slow execution on turnaround; China VBP pricing risk | large | high | yes | high |
| BIIB | Biogen Inc. | Healthcare | recovery | 52wk_low | Leqembi Alzheimer's approval; commercial launch early | Leqembi uptake slow; Alzheimer's payer coverage risk | large | high | yes | high |
| AMGN | Amgen Inc. | Healthcare | value | sector_leader|fcf_roic | Biosimilar portfolio + obesity pipeline; high FCF yield | Horizon acquisition debt; biosimilar erosion risk | mega | high | yes | high |
| HUM | Humana Inc. | Healthcare | recovery | 52wk_low | Medicare Advantage repricing; Stars rating recovery path | MA margin pressure deep; medical cost trend uncertain | large | high | yes | high |
| AAPL | Apple Inc. | Technology | compounder | tracked | Services flywheel extending hardware ecosystem moat | China revenue concentration; hardware saturation risk | mega | high | maybe | high |
| ARM | Arm Holdings plc | Technology | compounder | tracked|semis_and_infra | IP licensing monopoly on mobile and AI chip design | Rich valuation; customer concentration in Qualcomm/Apple | mega | high | maybe | high |
| ADBE | Adobe Inc. | Technology | compounder | tracked | Creative cloud lock-in; AI features defending moat | Figma threat; AI commoditization risk to core products | mega | high | maybe | high |
| ALAB | Astera Labs Inc. | Technology | compounder | tracked | Connectivity fabric critical for AI cluster scale-out | Early-stage; customer concentration in hyperscalers | large | high | maybe | medium |
| AVGO | Broadcom Inc. | Technology | compounder | tracked|semis_and_infra | Custom AI chip designs plus networking dominance | Acquisition debt load; semi cyclicality exposure | mega | high | maybe | high |
| CRM | Salesforce Inc. | Technology | compounder | tracked | Sticky enterprise CRM plus Agentforce AI platform | Competition from Microsoft Copilot; margin under pressure | mega | high | maybe | high |
| DSV.CO | DSV A/S | Industrials | compounder | tracked|large_cap_europe_quality | Asset-light freight forwarding with M&A compounding track record | Deep cyclical exposure; DB Schenker integration risk | large | high | maybe | high |
| NOW | ServiceNow Inc. | Technology | compounder | tracked | AI-native workflow platform; deep enterprise entrenchment | Premium valuation; revenue concentration in IT ops | mega | high | maybe | high |
| NVDA | NVIDIA Corp. | Technology | compounder | tracked|semis_and_infra | AI accelerator monopoly; CUDA ecosystem lock-in | Extreme valuation; custom ASIC competitive threat | mega | high | maybe | high |
| NOVO-B.CO | Novo Nordisk A/S | Healthcare | compounder | tracked|large_cap_europe_quality | GLP-1 obesity market still early; strong IP position | Pipeline risk; pricing pressure from US PBM negotiations | mega | high | maybe | high |
| QCOM | Qualcomm Inc. | Technology | compounder | tracked|semis_and_infra | Mobile chip dominance; AI PC and auto diversification | Apple in-house modem risk; China revenue concentration | mega | high | maybe | high |
| RKLB | Rocket Lab USA Inc. | Industrials | speculative | tracked | Smallsat launch monopoly; Neutron rocket in development | Pre-profit; high capex; execution risk on Neutron | mid | high | maybe | medium |
| SNOW | Snowflake Inc. | Technology | compounder | tracked | Data cloud platform; AI Data Cloud positioning | High valuation; intense competition from Databricks, AWS | large | high | maybe | medium |
| ASML.AS | ASML Holding N.V. | Technology | compounder | tracked|large_cap_europe_quality|semis_and_infra | Only supplier of EUV lithography; zero substitutes | Geopolitical China export controls; lumpy capex cycles | mega | medium | no | high |
| ORSTED.CO | Ørsted A/S | Utilities | recovery | tracked|large_cap_europe_quality | Offshore wind leader; project impairments mostly taken | Execution risk; rising capex costs; no pricing power | large | medium | no | medium |
| TSM | Taiwan Semiconductor Manufacturing Co. | Technology | compounder | tracked|semis_and_infra | Advanced node foundry monopoly; no credible 2nm competitor | Taiwan geopolitical risk; US capex overhang | mega | medium | no | high |
| MSFT | Microsoft Corp. | Technology | compounder | seed | Cloud + Copilot AI integration across entire enterprise stack | Azure growth slowdown risk; antitrust scrutiny | mega | medium | no | high |
| GOOG | Alphabet Inc. | Technology | compounder | seed | Search monopoly plus cloud acceleration; cheap vs peers | AI search disruption risk; DOJ antitrust outcome | mega | medium | no | high |
| META | Meta Platforms Inc. | Communication Services | compounder | seed | Social ad duopoly; Llama AI cost advantage growing | Regulatory risk; Reality Labs cash burn | mega | medium | no | high |
| V | Visa Inc. | Financials | compounder | seed | Payments network with zero marginal cost growth | Disintermediation risk from stablecoins / BNPL long-term | mega | medium | no | high |
| MA | Mastercard Inc. | Financials | compounder | seed | Duopoly payments rail; fee-based model scales without risk | Same risks as Visa; regulatory pressure on interchange | mega | medium | no | high |
| BRK-B | Berkshire Hathaway B | Financials | compounder | seed | Capital allocation machine; insurance float + equity portfolio | Succession risk post-Buffett; conglomerate discount | mega | medium | no | high |
| CSU.TO | Constellation Software Inc. | Technology | compounder | seed | VMS serial acquirer; consistent >20% ROIC; decentralized | Premium valuation; acquisition treadmill must continue | mega | medium | no | high |
| DHR | Danaher Corp. | Industrials | compounder | seed | Life sciences tools; sticky recurring reagent revenue | Post-COVID demand hangover; biopharma capex weakness | mega | medium | no | high |
| MCO | Moody's Corp. | Financials | compounder | seed | Rating agency oligopoly; mandatory for debt issuance | Regulatory cap risk; conflict-of-interest model scrutiny | large | medium | no | high |
| SPGI | S&P Global Inc. | Financials | compounder | seed | Ratings + indices + data; multi-segment compounding | Market data competition; regulatory oversight | mega | medium | no | high |
| FICO | Fair Isaac Corp. | Technology | compounder | seed | Score monopoly embedded in US mortgage system | CFPB disruption risk; VantageScore push from banks | large | medium | no | high |
| ROP | Roper Technologies | Industrials | compounder | seed | Software-heavy industrial acquirer; high recurring revenue | Declining organic growth; acquisition pace must sustain | large | medium | no | high |
| IDXX | IDEXX Laboratories | Healthcare | compounder | seed|healthcare_quality | Vet diagnostics consumables with installed base lock-in | Pet spending slowdown; pricing power tested in downturn | large | medium | no | high |
| TDG | TransDigm Group | Industrials | compounder | seed|industrial_compounders | Sole-source aerospace parts; 80%+ gross margins | Heavy leverage by design; defense cycle exposure | large | medium | no | high |
| ODFL | Old Dominion Freight Line | Industrials | compounder | seed|industrial_compounders | Best LTL operator; service premium commands pricing power | LTL cycle turning; volume weakness in freight recession | large | medium | no | high |
| SHW | Sherwin-Williams Co. | Consumer | compounder | seed|consumer_quality | Pro painter channel dominance; pricing power in coatings | Housing market sensitivity; raw material cost swings | mega | medium | no | high |
| FAST | Fastenal Co. | Industrials | compounder | seed | Vending machines create embedded industrial distribution moat | Cyclical industrial end markets; slower store growth | large | medium | no | high |
| POOL | Pool Corp. | Consumer | compounder | seed|consumer_quality | Pool aftermarket consumables recession-resistant | New pool installation cyclical; housing slowdown risk | large | medium | no | high |
| MTD | Mettler-Toledo Intl. | Industrials | compounder | seed|healthcare_quality | Precision lab instruments with consumable pull-through | Pharma capex spending cycles; China weakness | large | medium | no | high |
| WST | West Pharmaceutical Services | Healthcare | compounder | seed|healthcare_quality | Drug delivery components; injectable biologics demand growing | Customer concentration in top pharma; capacity overshoot | large | medium | no | high |
| COST | Costco Wholesale Corp. | Consumer | compounder | large_cap_us_quality|consumer_quality | Membership model creates captive repeat spend | Premium valuation; limited international upside near-term | mega | medium | no | high |
| ADP | Automatic Data Processing Inc. | Technology | compounder | large_cap_us_quality | Payroll processing with multi-year sticky enterprise contracts | Mature growth; fintech payroll disruptors nibbling | mega | medium | no | high |
| CTAS | Cintas Corp. | Industrials | compounder | large_cap_us_quality | Uniform route density moat; recurring contract revenue | Low-growth mature market; labor cost sensitivity | mega | medium | no | high |
| CPRT | Copart Inc. | Industrials | compounder | large_cap_us_quality | Used vehicle auction network; land-based moat | Cyclical used car volumes; insurance industry linkage | mega | medium | no | high |
| ROL | Rollins Inc. | Industrials | compounder | large_cap_us_quality | Pest control recurring revenue; fragmented M&A runway | Slow organic growth; weather sensitivity | large | medium | no | high |
| BR | Broadridge Financial Solutions | Technology | compounder | large_cap_us_quality | Proxy/investor comms processing; near-monopoly position | Low-growth utility-like; limited re-rating potential | large | medium | no | high |
| PAYX | Paychex Inc. | Technology | compounder | large_cap_us_quality | SMB payroll/HR sticky recurring; float income benefit | ADP and Gusto competition; rate sensitivity on float | large | medium | no | high |
| SSNC | SS&C Technologies Holdings | Technology | compounder | large_cap_us_quality | Fund admin software; sticky institutional client base | Heavy debt from acquisitions; slower organic growth | large | medium | no | medium |
| MKTX | MarketAxess Holdings | Financials | compounder | large_cap_us_quality|financial_quality | Electronic bond trading; network effects deepening | Market share ceiling approaching; IB desk competition | large | medium | no | high |
| NFLX | Netflix Inc. | Communication Services | compounder | large_cap_us_quality | Global streaming with ad tier expanding TAM | Content cost inflation; competition from Disney+/Apple TV | mega | medium | no | high |
| VRSK | Verisk Analytics Inc. | Industrials | compounder | large_cap_us_quality | Insurance analytics data monopoly; no substitutes | Mature growth; limited new market expansion | large | medium | no | high |
| CSGP | CoStar Group Inc. | Real Estate | compounder | large_cap_us_quality | CRE data monopoly; expanding residential with Homes.com | Heavy Homes.com investment depressing near-term margins | large | medium | no | high |
| FDS | FactSet Research Systems | Financials | compounder | large_cap_us_quality|financial_quality | Financial data terminal with sticky workflow integration | Bloomberg/Refinitiv competition; slower seat growth | large | medium | no | high |
| ICE | Intercontinental Exchange Inc. | Financials | compounder | large_cap_us_quality|financial_quality | Exchange + mortgage data; recurring data revenue growing | Regulatory risk on clearing; rate cycle sensitivity | mega | medium | no | high |
| CME | CME Group Inc. | Financials | compounder | large_cap_us_quality|financial_quality | Derivatives exchange monopoly; volumes surge in volatility | Low-volatility environments compress trading volumes | mega | medium | no | high |
| CBOE | Cboe Global Markets | Financials | compounder | large_cap_us_quality | VIX franchise; options market structural growth | Volatility-dependent revenue; exchange competition | large | medium | no | high |
| NDAQ | Nasdaq Inc. | Financials | compounder | large_cap_us_quality|financial_quality | Exchange + fintech data; diversifying away from listings | Adenza integration execution risk; listings cyclical | large | medium | no | high |
| MSCI | MSCI Inc. | Financials | compounder | large_cap_us_quality|financial_quality | Index licensing with AUM-linked fee model compounds | Passive investing shift could slow new AUM growth | large | medium | no | high |
| NKE | Nike Inc. | Consumer | recovery | large_cap_us_quality|consumer_quality | Brand reset underway; DTC strategy rebuilding margins | China softness; competitor gains from On/Hoka | large | medium | no | high |
| SBUX | Starbucks Corp. | Consumer | recovery | large_cap_us_quality|consumer_quality | New CEO turnaround; operational efficiency focus | China store economics deteriorating; traffic down | large | medium | no | high |
| MCD | McDonald's Corp. | Consumer | compounder | large_cap_us_quality|consumer_quality | Franchise model with real estate; global brand durability | Affordability pressure on low-income consumer | mega | medium | no | high |
| YUM | Yum! Brands Inc. | Consumer | compounder | large_cap_us_quality|consumer_quality | Asset-light franchise model; emerging market growth | Developing market FX risk; franchisor execution | large | medium | no | medium |
| HSY | Hershey Co. | Consumer | compounder | large_cap_us_quality|consumer_quality | Confectionery brand moat; pricing power demonstrated | Cocoa commodity price shock pressuring margins | large | medium | no | high |
| CHD | Church & Dwight Co. | Consumer | compounder | large_cap_us_quality|consumer_quality | Household staples with consistent mid-single digit growth | Premium valuation for staples grower; limited upside | large | medium | no | high |
| EL | Estée Lauder Companies | Consumer | recovery | large_cap_us_quality|consumer_quality | Luxury beauty reset; Asia travel retail recovery path | Asia consumption weakness; leadership transition | large | medium | no | high |
| TPX | Tempur Sealy International | Consumer | value | large_cap_us_quality|consumer_quality | Bedding leader; Serta Simmons acquisition adds scale | Housing cycle sensitivity; mattress replacement deferral | large | medium | no | medium |
| MCK | McKesson Corp. | Healthcare | value | large_cap_us_quality|healthcare_quality | Drug distribution scale; opioid settlement largely cleared | Thin margins; Amazon Pharmacy long-term threat | mega | medium | no | high |
| IQV | IQVIA Holdings | Healthcare | compounder | large_cap_us_quality | CRO + data platform; clinical trials demand structural | Pharma R&D spending cycles; competition from ICON | large | medium | no | high |
| ISRG | Intuitive Surgical Inc. | Healthcare | compounder | large_cap_us_quality | Robotic surgery installed base; consumables razor/blade | Premium valuation; reimbursement policy risk | mega | medium | no | high |
| EW | Edwards Lifesciences Corp. | Healthcare | compounder | large_cap_us_quality|healthcare_quality | TAVR structural heart leadership; TMTT pipeline building | TAVR market maturity; new entrants from Medtronic/Abbott | large | medium | no | high |
| MC.PA | LVMH Moët Hennessy Louis Vuitton | Consumer | compounder | large_cap_europe_quality | Luxury conglomerate with irreplaceable brand portfolio | China aspirational spending slowdown; currency headwinds | mega | medium | no | high |
| RMS.PA | Hermès International | Consumer | compounder | large_cap_europe_quality | Hermès scarcity model; pricing power without volume concession | No real disqualifier; valuation reflects quality | mega | medium | no | high |
| SAP.DE | SAP SE | Technology | compounder | large_cap_europe_quality | ERP system of record; S/4HANA cloud migration accelerating | Migration complexity; intense partner dependency | mega | medium | no | high |
| WKL.AS | Wolters Kluwer N.V. | Technology | compounder | large_cap_europe_quality | Professional info services; B2B subscription compounding | Slow organic growth; niche European footprint | large | medium | no | high |
| OR.PA | L'Oréal S.A. | Consumer | compounder | large_cap_europe_quality | Mass and luxury beauty; #1 global market position | Asia weakness; premium valuation | mega | medium | no | high |
| CFR.SW | Compagnie Financière Richemont | Consumer | compounder | large_cap_europe_quality | Jewelry/watches with Cartier and Van Cleef pricing power | China luxury slowdown; watches channel inventory | mega | medium | no | high |
| ADYEN.AS | Adyen N.V. | Financials | compounder | large_cap_europe_quality | Single payments platform; enterprise client expansion ongoing | Intensified competition; headcount scaling affecting margins | large | medium | no | high |
| DSY.PA | Dassault Systèmes SE | Technology | compounder | large_cap_europe_quality | PLM/3D design software; aerospace and life sciences verticals | Slow growth cycle; Ansys merger blocked by regulators | large | medium | no | high |
| EL.PA | EssilorLuxottica S.A. | Healthcare | compounder | large_cap_europe_quality | Eyewear platform monopoly; Essilor/Luxottica integration upside | Integration complexity; slow market penetration pace | mega | medium | no | high |
| KER.PA | Kering S.A. | Consumer | recovery | large_cap_europe_quality | Gucci undergoing brand reset; cheap vs luxury peers | Gucci brand equity damaged; China recovery uncertain | large | medium | no | high |
| STMN.SW | Straumann Holding AG | Healthcare | compounder | large_cap_europe_quality | Dental implant leader; recurring implant consumable model | Dental market cycle softness; pricing pressure in China | large | medium | no | high |
| LONN.SW | Lonza Group AG | Healthcare | compounder | large_cap_europe_quality | CDMO with GLP-1 manufacturing capacity in demand | Customer concentration; biotech funding cycle risk | large | medium | no | high |
| RKT.L | Reckitt Benckiser Group | Consumer | value | large_cap_europe_quality | Hygiene/health brands; portfolio rationalization underway | Weak brand investment track record; volume decline | large | medium | no | medium |
| ICG.L | InterContinental Hotels Group | Consumer | compounder | large_cap_europe_quality | Asset-light hotel franchise; loyalty program moat | Leisure travel cyclical; limited pricing power in downturn | large | medium | no | high |
| AMAT | Applied Materials Inc. | Technology | compounder | semis_and_infra | Largest WFE supplier; CVD/etch equipment dominance | Semi equipment cycle peak; China restriction risk | mega | medium | no | high |
| LRCX | Lam Research Corp. | Technology | compounder | semis_and_infra | Etch/deposition leadership; memory cycle recovery underway | Memory capex volatile; China export restrictions | mega | medium | no | high |
| KLAC | KLA Corp. | Technology | compounder | semis_and_infra | Process control monopoly; quality inspection no substitute | Semi cycle dependency; limited customer diversification | mega | medium | no | high |
| MRVL | Marvell Technology Inc. | Technology | compounder | semis_and_infra | Custom AI chip design wins at AWS and Google accelerating | Non-AI revenue still weak; execution on custom ASIC | large | medium | no | high |
| ADI | Analog Devices Inc. | Technology | compounder | semis_and_infra | Analog signal chain; industrial and auto sticky design-ins | Industrial inventory correction ongoing; slow recovery | mega | medium | no | high |
| TXN | Texas Instruments Inc. | Technology | compounder | semis_and_infra | Analog/embedded with 14-year capital return discipline | Inventory correction; new fab capacity overhang | mega | medium | no | high |
| MPWR | Monolithic Power Systems | Technology | compounder | semis_and_infra | Power management for AI servers; design-in momentum | High valuation; semi cycle exposure | large | medium | no | high |
| ON | ON Semiconductor Corp. | Technology | value | semis_and_infra | EV power semi exposure; correction may be overdone | Auto/EV cycle weakness; inventory normalization slow | large | medium | no | medium |
| LLY | Eli Lilly and Co. | Healthcare | compounder | healthcare_quality | GLP-1 obesity market; manufacturing capacity expanding | Capacity constraint risk; pipeline failure risk | mega | medium | no | high |
| AZN | AstraZeneca plc | Healthcare | compounder | healthcare_quality | Oncology pipeline depth; consistent double-digit growth | Pipeline binary risks; emerging market execution | mega | medium | no | high |
| ABBV | AbbVie Inc. | Healthcare | value | healthcare_quality | Post-Humira diversification working; Skyrizi/Rinvoq growing | Patent cliffs on new drugs eventual; acquisition risk | mega | medium | no | high |
| UNH | UnitedHealth Group Inc. | Healthcare | compounder | healthcare_quality | Managed care + Optum data platform; vertical integration | Government program reimbursement cuts risk; fraud probes | mega | medium | no | high |
| BSX | Boston Scientific Corp. | Healthcare | compounder | healthcare_quality | MedTech innovation pipeline; EP ablation structural growth | Premium valuation; competition from J&J, Medtronic | mega | medium | no | high |
| STE | STERIS plc | Healthcare | compounder | healthcare_quality | Sterilization services outsourcing; recurring hospital spend | Slow growth; government pricing pressure on services | large | medium | no | high |
| VEEV | Veeva Systems Inc. | Technology | compounder | healthcare_quality | Life sciences CRM/vault monopoly; 95%+ retention rate | Vault platform slowdown; potential Salesforce conflict | large | medium | no | high |
| DOCS | Doximity Inc. | Healthcare | compounder | healthcare_quality | Physician network monetization; ad platform growing | Small scale; network defensibility unclear long-term | large | medium | no | medium |
| ITW | Illinois Tool Works Inc. | Industrials | compounder | industrial_compounders | 80/20 simplification drives margins; consistent ROIC | Industrial end market cyclicality; slow organic growth | mega | medium | no | high |
| EMR | Emerson Electric Co. | Industrials | compounder | industrial_compounders | Process automation focus; software transition underway | Aspen acquisition integration complexity | large | medium | no | high |
| PH | Parker Hannifin Corp. | Industrials | compounder | industrial_compounders | Motion control with Meggitt aerospace integration upside | Aerospace aftermarket cycle dependency | mega | medium | no | high |
| AME | AMETEK Inc. | Industrials | compounder | industrial_compounders | Niche instrument acquirer; consistent margin expansion | Premium valuation; acquisition execution risk | large | medium | no | high |
| WCN | Waste Connections Inc. | Industrials | compounder | industrial_compounders | Waste collection with suburban density moat | Premium valuation vs WM/RSG; slower growth market | large | medium | no | high |
| RSG | Republic Services Inc. | Industrials | compounder | industrial_compounders | Waste management with environmental services growth | Competitive with WM; limited pricing differentiation | large | medium | no | high |
| GWW | W.W. Grainger Inc. | Industrials | compounder | industrial_compounders | MRO distribution with online channel expanding share | Amazon Business long-term threat; gross margin pressure | large | medium | no | high |
| CSX | CSX Corp. | Industrials | compounder | industrial_compounders | Eastern US railroad with intermodal pricing power | Volume sensitivity to industrial production levels | large | medium | no | high |
| NSC | Norfolk Southern Corp. | Industrials | compounder | industrial_compounders | Eastern railroad; post-Ohio derailment recovery underway | Derailment liability tail; slower volume recovery | large | medium | no | high |
| UNP | Union Pacific Corp. | Industrials | compounder | industrial_compounders | Western US rail monopoly; pricing power over trucking | Volume cyclical; agricultural commodity exposure | mega | medium | no | high |
| XPO | XPO Inc. | Industrials | recovery | industrial_compounders | LTL restructuring gaining market share from Yellow closure | Not fully proven franchise; execution risk remains | large | medium | no | medium |
| EXPD | Expeditors International of Washington | Industrials | compounder | industrial_compounders | Asset-light logistics; employee-owned culture drives service | Freight forwarding commoditization; rate normalization | large | medium | no | high |
| JPM | JPMorgan Chase & Co. | Financials | compounder | financial_quality | Best-managed diversified bank; Dimon capital discipline | Interest rate sensitivity; credit cycle exposure | mega | medium | no | high |
| CB | Chubb Ltd. | Financials | compounder | financial_quality | P&C insurance underwriting excellence; global diversification | Catastrophe loss risk; reinsurance cost inflation | mega | medium | no | high |
| AJG | Arthur J. Gallagher & Co. | Financials | compounder | financial_quality | Insurance broker with organic plus M&A growth compounding | Acquisition integration risk; premium valuation | large | medium | no | high |
| AFL | Aflac Inc. | Financials | compounder | financial_quality | Supplemental insurance cash generator; Japan franchise | Japan FX exposure; low growth domestic market | large | medium | no | high |
| MKL | Markel Group Inc. | Financials | value | financial_quality | Mini-Berkshire model; insurance float + venture investments | Smaller scale; insurance underwriting can disappoint | large | medium | no | high |
| BX | Blackstone Inc. | Financials | compounder | financial_quality | Alt asset management fee stream; perpetual capital growing | Rate cycle reduces deal flow; fee compression risk | mega | medium | no | high |
| KKR | KKR & Co. Inc. | Financials | compounder | financial_quality | Alt asset management; insurance capital integration unique | Cyclical deal flow; carried interest mark-to-market noise | mega | medium | no | high |
| GS | Goldman Sachs Group Inc. | Financials | compounder | financial_quality | Investment banking franchise; asset/wealth management growing | Cyclical IB revenue; capital markets dependent | mega | medium | no | high |
| PG | Procter & Gamble Co. | Consumer | compounder | consumer_quality | Household staples pricing power; 5% organic growth discipline | Volume elasticity risk as pricing normalizes | mega | medium | no | high |
| KO | Coca-Cola Co. | Consumer | compounder | consumer_quality | Beverage distribution moat; brand portfolio irreplaceable | Slow growth; health trend headwinds long-term | mega | medium | no | high |
| PEP | PepsiCo Inc. | Consumer | compounder | consumer_quality | Snacks + beverages dual engine; Frito-Lay dominance | Volume weakness in North America; PBNA margin drag | mega | medium | no | high |
| DXCM | DexCom Inc. | Healthcare | compounder | consumer_quality | CGM leader; GLP-1 patients still need glucose monitoring | Abbott Libre competition; reimbursement coverage risk | large | medium | no | high |
| SIE.DE | Siemens AG | Industrials | compounder | sector_leader|large_cap_europe_quality | Industrial automation + smart infra; digital twin leadership | Cyclical automation demand; energy business drag | mega | medium | no | high |
| AMZN | Amazon.com Inc. | Technology | compounder | sector_leader | AWS growth reaccelerating; ad business structurally profitable | Retail margin volatility; regulatory antitrust risk | mega | medium | no | high |
| WM | Waste Management Inc. | Industrials | compounder | sector_leader | Waste Management scale and pricing power; recurring contracts | Slow growth; environmental compliance cost risk | mega | medium | no | high |
| LOW | Lowe's Companies Inc. | Consumer | value | sector_leader | Home improvement duopoly; margin improvement vs HD | Weaker Pro mix vs HD; housing market sensitivity | mega | medium | no | high |
| TGT | Target Corp. | Consumer | value | sector_leader | Inventory rightsizing done; margins recovering toward 6%+ | Consumer trade-down risk; shrink/theft cost headwinds | large | medium | no | high |
| WMT | Walmart Inc. | Consumer | compounder | sector_leader | Grocery dominance plus ad/fintech layer building | Low margins; Flipkart emerging market execution risk | mega | medium | no | high |
| UBER | Uber Technologies Inc. | Technology | compounder | sector_leader | Ride/delivery network effects; autonomous disruption risk hedge | AV risk to core business long-term from Waymo | mega | medium | no | high |
| SPOT | Spotify Technology S.A. | Communication Services | compounder | sector_leader | Audio platform with podcast/audiobook; margin expansion underway | Content cost; Apple/Amazon ecosystem competition | large | medium | no | high |
| INTU | Intuit Inc. | Technology | compounder | sector_leader | TurboTax/QuickBooks ecosystem; SMB financial OS | IRS free filing threat; AI tax prep disruption risk | mega | medium | no | high |
| CDNS | Cadence Design Systems | Technology | compounder | sector_leader | EDA duopoly; semiconductor design tool monopoly | Synopsys merger scrutiny; customer concentration in semis | mega | medium | no | high |
| SNPS | Synopsys Inc. | Technology | compounder | sector_leader | EDA + semiconductor IP; Ansys acquisition adds simulation | Ansys integration risk; merger required regulatory approval | mega | medium | no | high |
| WDAY | Workday Inc. | Technology | compounder | sector_leader | HR/finance cloud with high retention; AI copilot adding value | Competition from SAP, Oracle; slower SMB expansion | large | medium | no | high |
| RACE | Ferrari N.V. | Consumer | compounder | large_cap_europe_quality | Demand always exceeds supply; pricing power unconstrained | No real disqualifier; rich valuation reflects the model | mega | medium | no | high |
| AIR.PA | Airbus SE | Industrials | compounder | large_cap_europe_quality | Commercial aviation duopoly; 12,000+ aircraft backlog | Defense/commercial mix complexity; supply chain delays | mega | medium | no | high |
| NESN.SW | Nestlé S.A. | Consumer | value | large_cap_europe_quality | Global food/beverage with pricing power; portfolio simplifying | Volume decline as pricing normalizes; category disruption | mega | medium | no | high |
| ROG.SW | Roche Holding AG | Healthcare | value | large_cap_europe_quality | Diagnostics + pharma duality; consistent cash generation | Pipeline losses in Alzheimer's; biosimilar pressure | mega | medium | no | high |
| ULVR.L | Unilever plc | Consumer | value | large_cap_europe_quality | Brand portfolio rationalization; Hein Schumacher pricing focus | Slow growth; portfolio complexity; EM FX headwinds | mega | medium | no | high |
| GSK.L | GSK plc | Healthcare | value | large_cap_europe_quality | Vaccines + specialty medicines diversifying; Zantac behind | Shingrix slowdown; pipeline binary risks | large | medium | no | high |
| ALV.DE | Allianz SE | Financials | compounder | large_cap_europe_quality | Insurance + asset management; consistent combined ratio | Catastrophe exposure; Allianz Global Investors risk | mega | medium | no | high |
| MUV2.DE | Munich Re | Financials | compounder | large_cap_europe_quality | Reinsurance pricing power; discipline through the cycle | Catastrophe loss concentration; climate risk repricing | mega | medium | no | high |
| RHM.DE | Rheinmetall AG | Industrials | compounder | large_cap_europe_quality | European defense rearming; Leopard tank and ammunition | Defense budget cyclicality; political risk | large | medium | no | high |
| CS.PA | AXA S.A. | Financials | compounder | large_cap_europe_quality | Insurance + asset management; strong Solvency II capital | European insurance regulatory complexity | large | medium | no | high |
| PANW | Palo Alto Networks Inc. | Technology | compounder | sector_leader | Platform consolidation winning; platformization strategy sticky | High valuation; SentinelOne and CrowdStrike competition | mega | medium | no | high |
| CRWD | CrowdStrike Holdings Inc. | Technology | compounder | sector_leader | Falcon platform dominance; AI-native endpoint leader | Rich valuation; CrowdStrike incident reputational risk | mega | medium | no | high |
| ZS | Zscaler Inc. | Technology | compounder | sector_leader | Zero Trust cloud security leader; large enterprise wins | High valuation; PANW and Microsoft competitive pressure | large | medium | no | high |
| FTNT | Fortinet Inc. | Technology | compounder | sector_leader | Firewall leader with SASE transition; diversified product line | Transition from hardware to cloud slower than peers | large | medium | no | high |
| DDOG | Datadog Inc. | Technology | compounder | sector_leader | Observability platform with AI monitoring expansion | High valuation; multi-cloud fragmentation risk | large | medium | no | high |
| MDB | MongoDB Inc. | Technology | compounder | sector_leader | Document DB with Atlas cloud growth; developer-first moat | High valuation; PostgreSQL/DynamoDB substitution risk | large | medium | no | high |
| HUBS | HubSpot Inc. | Technology | compounder | sector_leader | SMB CRM platform; AI marketing tools expanding TAM | Salesforce SMB push; high valuation for growth rate | large | medium | no | high |
| TTD | The Trade Desk Inc. | Technology | compounder | sector_leader | Buy-side DSP with CTV dominance; Kokai AI platform | Google/Amazon ad tech competition; cookie deprecation | large | medium | no | high |
| SQ | Block Inc. | Financials | recovery | sector_leader | Cash App monetization; Afterpay integration simplifying | Competitive pressure from Stripe/PayPal; no clear moat | large | medium | no | medium |
| PYPL | PayPal Holdings Inc. | Financials | recovery | sector_leader | New CEO turnaround; branded checkout defending share | Competition from Apple Pay and Stripe; margin compression | large | medium | no | high |
| BAC | Bank of America Corp. | Financials | compounder | sector_leader | Moynihan capital discipline; NII leverage to rate environment | Rate sensitivity to cuts; consumer credit cycle risk | mega | medium | no | high |
| WFC | Wells Fargo & Co. | Financials | recovery | sector_leader | Asset cap removal path; margins improving post-restructuring | Asset cap still constrains growth; reputational risk | mega | medium | no | high |
| UPS | United Parcel Service Inc. | Industrials | value | sector_leader | Ground network repricing; margin recovery from Teamsters | Amazon insourcing secular pressure; volume still weak | large | medium | no | high |
| FDX | FedEx Corp. | Industrials | value | sector_leader | DRIVE restructuring cutting costs; margin recovery story | Structural volume loss to USPS/Amazon; execution risk | large | medium | no | high |
| DE | Deere & Company | Industrials | compounder | sector_leader | Precision agriculture tech moat; John Deere OS stickiness | Ag equipment cycle deep correction; farmer income weak | mega | medium | no | high |
| HON | Honeywell International Inc. | Industrials | compounder | sector_leader | Portfolio simplification underway; automation and aerospace | Restructuring multiple execution risks; slow near-term | mega | medium | no | high |
| RTX | RTX Corp. | Industrials | compounder | sector_leader | Defense + Pratt jet engine aftermarket; GTF resolution path | GTF powder metal recall cost; defense budget uncertainty | mega | medium | no | high |
| LMT | Lockheed Martin Corp. | Industrials | compounder | sector_leader | F-35 sustainment + missile defense; govt budget dependent | Defense budget cuts risk; F-35 margin pressure | mega | medium | no | high |
| NOC | Northrop Grumman Corp. | Industrials | compounder | sector_leader | B-21 Raider strategic bomber; space and cyber growth | Cost-plus contract limited upside; budget dependency | large | medium | no | high |
| GD | General Dynamics Corp. | Industrials | compounder | sector_leader | Gulfstream jets + defense mix; cash return discipline | Defense budget risk; Gulfstream backlog normalization | large | medium | no | high |
| BABA | Alibaba Group Holding | Technology | value | sector_leader | Regulatory overhang mostly cleared; deep value on FCF | China consumer spending weak; Pinduoduo/JD competition | mega | medium | no | high |
| TCEHY | Tencent Holdings Ltd. | Technology | compounder | sector_leader | Gaming + WeChat + ads; capital return accelerating | China regulatory risk; VIE structure; geopolitical risk | mega | medium | no | high |
| SONY | Sony Group Corp. | Technology | compounder | sector_leader | Gaming + entertainment + sensors; diversified cash generation | Cyclical gaming console cycle; film/music volatile | mega | medium | no | high |
| TM | Toyota Motor Corp. | Consumer | value | sector_leader | Hybrid dominance; EV transition paced; loyal customer base | EV transition risk; Japan currency headwinds | mega | medium | no | high |
| SYK | Stryker Corp. | Healthcare | compounder | sector_leader | MedTech innovation + Mako robotic surgery installed base | Premium valuation; procedure volume sensitivity | mega | medium | no | high |
| ZTS | Zoetis Inc. | Healthcare | compounder | sector_leader | Animal health pricing power; pet humanization tailwind | IDXX and Merck Animal competition; slower growth | large | medium | no | high |
| TMO | Thermo Fisher Scientific | Healthcare | compounder | sector_leader | Life sciences tools + CDMO; recurring consumable revenue | Biopharma capex cycle weakness; China end market | mega | medium | no | high |
| A | Agilent Technologies | Healthcare | value | sector_leader | Instruments + consumables; pharma and food testing demand | Post-COVID instrument demand normalization | large | medium | no | high |
| REGN | Regeneron Pharmaceuticals | Healthcare | compounder | sector_leader | Eylea + Dupixent dual blockbusters; pipeline depth | Eylea biosimilar pressure imminent; Dupixent competition | large | medium | no | high |
| CI | Cigna Group | Healthcare | compounder | sector_leader | Evernorth PBM + Cigna Health; vertically integrated HMO | PBM legislative risk; Medicare Advantage repricing | large | medium | no | high |
| AMT | American Tower Corp. | Real Estate | compounder | sector_leader | Cell tower REIT; 5G densification structural tailwind | High leverage; carrier consolidation reduces lease demand | large | medium | no | high |
| PLD | Prologis Inc. | Real Estate | compounder | sector_leader | Industrial REIT with e-commerce structural demand | Interest rate sensitive; vacancy rising in some markets | mega | medium | no | high |
| EQIX | Equinix Inc. | Real Estate | compounder | sector_leader | Data center REIT with network density moat; AI demand | High leverage; power availability constraints | mega | medium | no | high |
| APD | Air Products and Chemicals | Materials | compounder | sector_leader | Industrial gases; project pipeline for clean hydrogen | CEO departure overhang; mega-project execution risk | large | medium | no | high |
| ECL | Ecolab Inc. | Materials | compounder | sector_leader | Water treatment + hygiene chemicals; embedded recurring spend | Chemical input costs; slow margin recovery pace | large | medium | no | high |
| HIMS | Hims & Hers Health Inc. | Healthcare | speculative | tracked | Telehealth GLP-1 prescribing tailwind; brand building | Regulatory risk on compounded GLP-1; pre-mature moat | mid | low | no | medium |
| MAERSK-B.CO | A.P. Møller-Mærsk A/S | Industrials | cyclical | tracked|large_cap_europe_quality | Container shipping normalizing; logistics pivot underway | Pure cyclical shipping with no durable pricing power | large | low | no | high |
| TSLA | Tesla Inc. | Consumer | recovery | tracked | FSD and energy business rerate potential | Musk distraction; brand damage; margin compression | mega | low | no | high |
| CRH | CRH plc | Materials | compounder | large_cap_europe_quality | Infrastructure materials consolidator; US reshoring beneficiary | Cyclical construction exposure; commodity-like product | mega | low | no | medium |
| ACLS | Axcelis Technologies Inc. | Technology | value | semis_and_infra | Ion implant equipment; mid-cap with niche technology | Small customer base; semi cycle highly exposed | mid | low | no | medium |
| ONTO | Onto Innovation Inc. | Technology | value | semis_and_infra | Metrology equipment; critical for advanced node yield | Small scale; semi equipment cycle risk | mid | low | no | medium |
| MSC | MSC Industrial Direct Co. | Industrials | value | industrial_compounders | Industrial distribution; operating leverage on recovery | Small cap; Amazon Business threat; slow growth | mid | low | no | medium |
| RLI | RLI Corp. | Financials | compounder | financial_quality | Specialty insurer with consistent underwriting discipline | Small scale; CAT exposure in specialty lines | mid | low | no | medium |
| T | AT&T Inc. | Communication Services | income | fcf_roic | Fiber broadband growing post-DirecTV separation | High debt; slow revenue growth; commodity telecom | large | low | no | high |
| UCG.MI | UniCredit S.p.A. | Financials | value | large_cap_europe_quality | European bank re-rating; capital returns accelerating | European banking systemic risk; rates sensitivity | large | low | no | medium |
| CNQ | Canadian Natural Resources Ltd. | Energy | cyclical | 52wk_high | Oil sands low-decline long life; best cost operator | Commodity oil price; no pricing power | mega | low | no | medium |
| ABI.BR | Anheuser-Busch InBev S.A. | Consumer | value | large_cap_europe_quality | Beer volume stabilizing; deleveraging narrative progressing | Heavy debt; volume structural decline in developed markets | mega | low | no | high |
| DBK.DE | Deutsche Bank AG | Financials | value | large_cap_europe_quality | German bank restructuring; capital returns beginning | European banking systemic risk; litigation tail | large | low | no | medium |
| BAS.DE | BASF SE | Materials | value | large_cap_europe_quality | Chemical giant; restructuring and energy cost normalization | Commodity chemicals with limited moat; China competition | large | low | no | medium |
| BARC.L | Barclays plc | Financials | value | large_cap_europe_quality | UK bank re-rating; capital returns accelerating under CS Venkatakrishnan | European banking systemic risk; UK macro exposure | large | low | no | medium |
| BNP.PA | BNP Paribas S.A. | Financials | value | large_cap_europe_quality | European banking leader; CIB and retail diversified | Sovereign debt exposure; rates sensitivity | large | low | no | medium |
| BBVA.MC | Banco Bilbao Vizcaya Argentaria | Financials | value | large_cap_europe_quality | EM bank with Spain domestic strength; Turkey exposure risk | Turkey hyperinflation risk; EM currency volatility | large | low | no | medium |
| COIN | Coinbase Global Inc. | Financials | speculative | sector_leader | Crypto exchange leader; regulatory clarity improving | Crypto cycle volatility; regulatory overhang | large | low | no | high |
| BIDU | Baidu Inc. | Technology | speculative | sector_leader | AI large model; ERNIE Bot early lead in China | VIE structure risk; China tech regulation; competition | large | low | no | medium |
| MRNA | Moderna Inc. | Healthcare | speculative | 52wk_low | mRNA platform beyond COVID; RSV vaccine approved | Revenue cliff post-COVID; pipeline execution unproven | large | low | no | high |
| CVX | Chevron Corp. | Energy | cyclical | sector_leader|fcf_roic | FCF yield; Permian scale; Gulf of Mexico assets | Commodity price cyclical; no durable moat | mega | low | no | high |
| XOM | Exxon Mobil Corp. | Energy | cyclical | sector_leader|fcf_roic | FCF yield; upstream + downstream integration; Permian | Commodity price; no durable moat; carbon transition | mega | low | no | high |
| COP | ConocoPhillips | Energy | cyclical | sector_leader | E&P with low breakeven; variable dividend discipline | Oil price commodity; no durable moat | mega | low | no | high |
| NEE | NextEra Energy Inc. | Utilities | income | sector_leader | Largest renewable utility; regulated + unregulated growth | Highly leveraged; rate sensitivity; no pricing power | mega | low | no | high |
| AEP | American Electric Power | Utilities | income | sector_leader | Electric utility with data center load growth | Regulated utility with limited pricing power | large | low | no | medium |
| SO | Southern Company | Utilities | income | sector_leader | Georgia electric utility; Vogtle nuclear finally online | Regulated utility; limited returns above cost of capital | large | low | no | medium |
| NEM | Newmont Corp. | Materials | cyclical | 52wk_high | Gold miner; costs improving; gold price structural tailwind | Commodity miner with no pricing power or moat | large | low | no | medium |
| FCX | Freeport-McMoRan Inc. | Materials | cyclical | 52wk_high | Copper leverage to energy transition demand | Pure commodity cyclical; no moat | large | low | no | medium |

---

Next step: Run Stage B triage on all triage_rec=yes names.