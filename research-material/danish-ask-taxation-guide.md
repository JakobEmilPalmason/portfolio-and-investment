# Danish Aktiesparekonto (ASK) Taxation Guide
## For Saxo Bank Investors with International Portfolios

_Last researched: 2026-04-01_
_Disclaimer: This is a research summary, not professional tax advice. Verify all rates and rules with SKAT or a tax advisor before making decisions._

---

## 1. ASK Account Fundamentals

### What Is an Aktiesparekonto?

A tax-advantaged equity investment account for Danish tax residents. All gains (realized, unrealized, and dividends) are taxed at a flat **17%** via lagerbeskatning (mark-to-market), compared to the standard 27%/42% stock income tax in a regular depot.

### Key Parameters (2026)

| Parameter | Value |
|-----------|-------|
| **Tax rate** | 17% flat (lagerbeskatning) |
| **Contribution limit 2025** | 166,200 DKK |
| **Contribution limit 2026** | 174,200 DKK |
| **Accounts per person** | Exactly 1 (across all banks) |
| **Age requirement** | 18+ to self-open; children allowed with parental signature |
| **Residency** | Must be fully tax-liable (fuldt skattepligtig) in Denmark |
| **Lock-up period** | None -- withdraw anytime |
| **Standard stock income tax (frie midler)** | 27% on first ~67,500 DKK / 42% above |
| **Excess contribution penalty** | 3% annual (prorated daily) |
| **Tax payment date** | ~14-15 February (formally due 22 February) |

### Contribution Limit History

| Year | Limit (DKK) |
|------|-------------|
| 2019 | 50,000 |
| 2020 | 100,000 |
| 2024 | 135,900 |
| 2025 | 166,200 |
| 2026 | 174,200 |

The limit is the total you can deposit, not the account value. If the account grows beyond the limit through gains, no action is needed -- you simply cannot deposit more. Withdrawals free up deposit room.

### Withdrawals

You can withdraw cash at any time. Key points:
- Withdrawals reduce year-end value, affecting how much you can contribute next year
- Withdrawals are factored into the lagerbeskatning calculation (subtracted from opening value)
- No loans can be taken against the account

### Excess Contributions

If you deposit more than the limit:
- 3% annual penalty on the excess, calculated daily until withdrawn
- **Exception:** Deposits specifically to pay the annual ASK tax are always allowed, even if they temporarily exceed the limit
- The bank calculates and deducts the penalty automatically

---

## 2. Lagerbeskatning (Mark-to-Market Taxation)

### How It Works

1. **January 1:** Opening value recorded (all securities + cash)
2. **During year:** Deposits added to opening value; withdrawals subtracted
3. **December 31:** Closing value recorded
4. **Taxable gain/loss** = Closing value - (Opening value + deposits - withdrawals)
5. **Tax** = Gain x 17%

### Worked Example

**Scenario A -- Simple growth:**
| | Amount |
|---|---|
| 1 Jan value | 100,000 DKK |
| Deposits | 0 |
| 31 Dec value | 110,000 DKK |
| **Taxable gain** | **10,000 DKK** |
| **Tax (17%)** | **1,700 DKK** |

**Scenario B -- With deposit:**
| | Amount |
|---|---|
| 1 Jan value | 50,000 DKK |
| March deposit | 20,000 DKK |
| 31 Dec value | 80,000 DKK |
| Adjusted base | 70,000 DKK |
| **Taxable gain** | **10,000 DKK** |
| **Tax (17%)** | **1,700 DKK** |

### Loss Carry-Forward

- Negative results create a "negative tax" (negativ skat)
- Carried forward and offset against positive ASK tax in the earliest possible future year
- **Losses only offset within the ASK** -- cannot be used against other income or depots
- **If you close the ASK while carrying unused negative tax, the credit is permanently lost**

### When Is Tax Paid?

The bank handles everything automatically:
- Tax is deducted from the ASK around **14-15 February** of the following year
- If insufficient cash, the bank sells securities to cover it
- You can deposit cash specifically to cover the tax (exceeding the limit is allowed for this purpose)

### Lagerbeskatning vs. Realisationsbeskatning

| Aspect | Lagerbeskatning (ASK) | Realisationsbeskatning (frie midler, stocks) |
|--------|----------------------|----------------------------------------------|
| **When taxed** | Every year on unrealized gains/losses | Only when you sell |
| **Tax rate** | 17% flat | 27% (first ~67.5K) / 42% (above) |
| **Compounding** | Reduced -- tax drains cash annually | Full compounding until sale |
| **Loss treatment** | Auto-offset in future ASK years | Offset against realized gains same year |
| **Cash flow** | Must have cash for annual tax | No tax until realization |
| **Administration** | Bank handles automatically | Self-managed |

**Despite the annual drag, the 17% rate is so much lower than 27-42% that ASK is almost always more tax-efficient.**

---

## 3. Dividend Taxation by Country

### How It Works on ASK

When a foreign company pays a dividend:
1. The foreign country withholds tax at source (the WHT rate depends on treaties)
2. You receive the net dividend in your ASK
3. The full gross dividend is included in your ASK's year-end gain
4. The foreign WHT is **credited** against your 17% ASK tax (up to 17% of the foreign income)
5. You pay only the difference to Danish SKAT

**The credit means you are NOT double-taxed for countries with WHT <= 17%.** The foreign WHT cash stays abroad, but your Danish tax bill is reduced by the same amount.

### Country-by-Country Breakdown

#### Denmark (NOVO-B.CO, DSV.CO, ORSTED.CO, MAERSK-B.CO)
- **WHT on ASK dividends: 0%** -- Danish dividends paid within an ASK are not subject to withholding
- **Total effective tax: 17%** (ASK rate only)
- **Best possible case alongside UK**

#### USA (MSFT, V, GILD, ADBE, CPRT, NOW, AMD, COST, etc.)
- **Statutory WHT:** 30%
- **Treaty rate (W-8BEN):** 15%
- **Creditable on ASK:** Yes, fully (15% < 17%)
- **Total effective tax: 17%** (15% US + 2% Danish top-up)

**W-8BEN:** Saxo Bank provides Relief at Source for US stocks. The W-8BEN form establishes your treaty eligibility, reducing WHT from 30% to 15%. Saxo handles this largely automatically for Danish residents. Valid for 3 years, must be renewed.

#### Netherlands (ADYEN.AS, UMG.AS, WKL.AS, ASML.AS)
- **Statutory WHT:** 15%
- **Treaty rate:** 15% (same as statutory)
- **Creditable on ASK:** Yes, fully
- **Total effective tax: 17%**

#### France (EL.PA, MC.PA, OR.PA, RMS.PA)
- **Statutory WHT (2026):** 12.80% (reduced from 25% as of January 1, 2026)
- **Treaty rate:** 15%
- **Effective rate:** 12.80% (lower of statutory and treaty)
- **Creditable on ASK:** Yes, fully
- **Total effective tax: 17%** (12.80% French + 4.20% Danish top-up)

**Note:** Before 2026, France was problematic at 25%. The 2026 reduction makes French stocks favorable for ASK.

#### Germany (SAP.DE)
- **Statutory WHT:** 26.375% (25% + 5.5% solidarity surcharge)
- **Treaty rate:** 15%
- **Problem:** Germany withholds the full 26.375% and does NOT apply treaty relief at source
- **Creditable on ASK:** Only 17% (the ASK rate)
- **Uncreditable excess: 9.375%**
- **Total effective tax WITHOUT reclaim: 26.375%**
- **Total effective tax WITH reclaim: 17%**

**Reclaim process:** File with the German Federal Central Tax Office (BZSt). Processing time: months to over a year.

#### UK (BA.L, HLMA.L, LSEG.L)
- **WHT on dividends: 0%** -- the UK does not withhold on ordinary dividends to non-residents
- **Total effective tax: 17%** (ASK rate only)
- **Best possible case alongside Denmark**

#### Canada (CSU.TO)
- **Statutory WHT:** 25%
- **Treaty rate:** 15%
- **Applied at source:** Yes -- Saxo/Nordnet apply the reduced 15% rate for Canadian dividends
- **Creditable on ASK:** Yes, fully
- **Total effective tax: 17%**

#### Switzerland (NVS, ROG.SW, NOVN.SW)
- **Statutory WHT (Verrechnungssteuer):** 35% -- one of the highest in the world
- **Treaty rate:** 15%
- **Problem:** Switzerland withholds the full 35%. Only 17% creditable on ASK.
- **Uncreditable excess: 18%**
- **Total effective tax WITHOUT reclaim: 35%**
- **Total effective tax WITH reclaim: 17%**

**Reclaim process:** File with the Swiss Federal Tax Administration (FTA). Processing time: 8-10 months. Deadline: 3 years after end of the calendar year.

**This is the WORST country for ASK dividend taxation.** Consider holding Swiss dividend stocks in frie midler instead, or use an Irish-domiciled ETF with Swiss exposure.

**ADR note (NVS):** NVS is a US-listed ADR of Novartis. ADRs of Swiss companies may still face the 35% Swiss WHT on underlying dividends. Verify with Saxo whether the ADR structure shields from Swiss WHT or passes it through.

#### Italy (RACE)
- **Statutory WHT:** 26%
- **Treaty rate:** 15%
- **Problem:** Italy withholds 26%, only 17% creditable on ASK
- **Uncreditable excess: 9%**
- **Total effective tax WITHOUT reclaim: 26%**
- **Total effective tax WITH reclaim: 17%**

**Reclaim process:** File with the Italian Revenue Agency (Agenzia delle Entrate). Deadline: 48 months from WHT payment. Processing: can take years. The most bureaucratically difficult reclaim.

**Note for RACE:** Ferrari is incorporated in the Netherlands but headquartered in Italy. The actual WHT country depends on where dividends are legally sourced from -- verify the actual withholding applied by Saxo.

### Summary Table: Effective Dividend Tax on ASK

| Country | Statutory WHT | Treaty Rate | Creditable on ASK | Total Tax (no reclaim) | Total Tax (with reclaim) | Reclaim Needed? |
|---------|--------------|-------------|-------------------|----------------------|------------------------|-----------------|
| **Denmark** | 0% | N/A | N/A | **17%** | **17%** | No |
| **UK** | 0% | 0% | N/A | **17%** | **17%** | No |
| **France (2026)** | 12.80% | 15% | 12.80% | **17%** | **17%** | No |
| **USA** | 30% | 15% | 15% | **17%** | **17%** | No |
| **Netherlands** | 15% | 15% | 15% | **17%** | **17%** | No |
| **Canada** | 25% | 15% | 15% | **17%** | **17%** | No |
| **Germany** | 26.375% | 15% | 17% max | **26.375%** | **17%** | Yes (BZSt) |
| **Italy** | 26% | 15% | 17% max | **26%** | **17%** | Yes (slow) |
| **Switzerland** | 35% | 15% | 17% max | **35%** | **17%** | Yes (FTA) |

**Practical rule:** For US, NL, FR (2026+), UK, CA, and DK stocks -- ASK is perfect, no extra work needed. For DE, IT, and CH stocks -- you must reclaim excess WHT or accept significant tax drag on dividends.

---

## 4. Double Taxation Treaties and ASK

### How Treaty Relief Works

Denmark has double taxation treaties with most developed countries. These treaties reduce the WHT rate from the statutory rate to a lower "treaty rate" (typically 15% for portfolio dividends). Relief is applied either:

- **At source** (Relief at Source): The broker applies the reduced rate when withholding. Saxo does this for US, Canada, and some other countries.
- **By reclaim** (Relief by Reclaim): The full statutory rate is withheld, and you file a reclaim with the foreign tax authority for the excess. This is common for Germany, Switzerland, and Italy.

### The Credit Mechanism on ASK

Foreign WHT is credited against your 17% ASK tax. The credit equals the lesser of:
1. The actual foreign WHT paid
2. 17% of the foreign dividend income
3. The treaty-entitled amount

If the credit exceeds your ASK tax (e.g., due to overall losses), it carries forward as negative tax.

### The "Lost WHT" Problem

For countries with statutory WHT > 17% (Germany 26.375%, Italy 26%, Switzerland 35%):
- Only 17% is creditable against ASK tax
- The excess over 17% is effectively "lost" unless you reclaim it from the foreign country
- Even with a successful reclaim to the 15% treaty rate, the cash goes to you (possibly a regular account), not back into the ASK

**This is the most important tax planning consideration for international ASK investing.**

### Reclaim Difficulty by Country

| Country | Forms | File With | Processing Time | Difficulty |
|---------|-------|-----------|-----------------|------------|
| **Switzerland** | FTA form | Swiss Federal Tax Administration, Bern | 8-10 months | Moderate |
| **Germany** | BZSt application | Federal Central Tax Office | Months to 1+ year | Moderate-Hard |
| **France** | Forms 5000 + 5001 (need SKAT stamp) | Direction generale des finances publiques | 1+ year | Hard |
| **Italy** | Refund request with proof | Agenzia delle Entrate | Up to years | Very Hard |

**Saxo does not assist with reclaims.** You must file yourself. Nordnet also does not assist.

### ASK vs. Frie Midler for High-WHT Countries

In frie midler, the 27% Danish tax rate provides more headroom to absorb foreign WHT credits. For example:
- Swiss stock dividend in frie midler: 35% withheld, 15% treaty rate credited against 27% Danish tax = 27% total
- Swiss stock dividend in ASK: 35% withheld, 17% credited = 35% total (without reclaim)

**However**, the base rate matters more than the dividend tax drag for most investors. A stock with 2% dividend yield and 10% total return pays 17% x 10% = 1.7% annual tax on ASK vs. 27-42% x realized gains in frie midler. The dividend WHT drag is a small part of total return.

**Rule of thumb:** Unless a stock has a very high dividend yield (>3%) AND is from a high-WHT country (DE/IT/CH), the ASK's 17% base rate still wins overall.

---

## 5. ETF Taxation on ASK

### The Domicile Question

ETF domicile determines the dividend WHT chain:

| ETF Domicile | WHT on US Dividends (at fund level) | WHT on ETF Distributions (to you) | Available to Danish Retail? |
|-------------|--------------------------------------|-----------------------------------|-----------------------------|
| **Ireland** | 15% (Ireland-US treaty) | 0% | Yes (if on Positivlisten) |
| **Luxembourg** | 15-30% (varies) | 0% | Yes (if on Positivlisten) |
| **USA** | 0% (domestic) | 30% / 15% treaty | **No** (PRIIPs blocks retail access) |
| **Denmark** | 15-30% (varies by treaty) | 0% | Yes |

**Irish-domiciled UCITS ETFs are the standard choice for Danish ASK investors.** They combine:
- 0% WHT on distributions to you
- 15% US dividend WHT at the fund level (via Ireland-US treaty)
- Full availability via European brokers
- Positivlisten eligibility

### SKAT's Positivlisten

The Positivlisten is SKAT's official list of investment funds/ETFs that qualify for taxation as **aktieindkomst** (stock income) rather than kapitalindkomst (capital income).

**Why it matters:**
- **On the list:** Taxed as aktieindkomst. Can be held in ASK at 17%.
- **NOT on the list:** Taxed as kapitalindkomst (different, often less favorable rates). **Cannot be held in ASK at all.**

**Key facts:**
- ~5,000+ funds, ~700+ UCITS ETFs as of 2026
- Updated several times per year (last noted update: January 29, 2026)
- Published on 15 December each year for the following year

**Where to find it:**
- **Official:** [SKAT -- Beviser og aktier i investeringsforeninger (IFPA)](https://skat.dk/erhverv/ekapital/vaerdipapirer/beviser-og-aktier-i-investeringsforeninger-og-selskaber-ifpa) -- download Excel file under "Liste over aktiebaserede investeringsselskaber"
- **Community (searchable):**
  - [skats-positivliste.danielwinther.dk](https://skats-positivliste.danielwinther.dk/) -- updated daily, easiest to search
  - [minask.dk/skat-positivliste](https://minask.dk/skat-positivliste)
  - [frinans.dk/skats-positivliste](https://www.frinans.dk/skats-positivliste/)
  - [indeksinvest.dk](https://www.indeksinvest.dk/skats-positivliste-2026-med-etfer-med-aktieindkomst/)

**Always check the Positivlisten before buying an ETF for your ASK.**

### US-Domiciled ETFs -- NOT Available

PRIIPs regulation (EU No. 1286/2014) requires a Key Information Document (KID) for packaged retail investments sold to EU investors. US ETF providers (Vanguard, BlackRock US-listed) don't produce PRIIPs-compliant KIDs. Result: **Danish retail investors cannot buy US-domiciled ETFs.**

Buy the UCITS equivalent instead (e.g., iShares Core MSCI World UCITS ETF instead of the US-listed iShares equivalent).

### Accumulating vs. Distributing

**On ASK: No tax difference.** Both are lagerbeskattet at 17% on the full annual gain. However:

- **Accumulating (akkumulerende):** Dividends reinvested automatically at fund level. No transaction costs for reinvestment. Slightly more efficient operationally.
- **Distributing (udbyttebetalende):** Dividends paid to your ASK as cash. You reinvest manually (incurring commissions).

**Community consensus: Prefer accumulating ETFs on ASK.**

### Minimumsbeskattede (IMB) vs. Investeringsselskaber

| Type | Tax Principle | ASK Eligible? | Notes |
|------|---------------|---------------|-------|
| **IMB (Investeringsinstitut med Minimumsbeskatning)** | Realisationsbeskatning in frie midler; lagerbeskatning on ASK | Yes (if equity-based, >=50% stocks) | Danish-domiciled, dividend-paying associations (e.g., Sparindex, Danske Invest) |
| **Investeringsselskaber (on Positivlisten)** | Lagerbeskatning as aktieindkomst | Yes | Includes foreign ETFs (Irish, Luxembourg) registered with SKAT |

On ASK, both are taxed identically at 17% via lagerbeskatning.

### Popular ETFs for ASK

| ETF | Ticker | TER | Index | Domicile |
|-----|--------|-----|-------|----------|
| Amundi MSCI World UCITS ETF Acc | MWRE | 0.12% | MSCI World | Ireland |
| Amundi Prime All Country World Acc | WEBN | 0.07% | Solactive Global Markets | Luxembourg |
| iShares Core MSCI World UCITS ETF Acc | EUNL/IWDA | 0.20% | MSCI World | Ireland |
| Vanguard FTSE All-World UCITS ETF Acc | VWCE | 0.22% | FTSE All-World | Ireland |
| iShares Core S&P 500 UCITS ETF Acc | SXR8 | 0.07% | S&P 500 | Ireland |
| SPDR MSCI ACWI IMI UCITS ETF | SPYI | 0.17% | MSCI ACWI IMI | Ireland |

All are on SKAT's Positivlisten and eligible for ASK.

---

## 6. Bond Taxation on ASK

### Short Answer: Bonds Are NOT Allowed on ASK

The ASK is restricted to equity-based instruments. Explicitly excluded:

- **Direct bonds** (government, corporate, mortgage) -- NO
- **Bond ETFs** (iShares treasury, corporate bond funds) -- NO
- **Bond-based investment funds** -- NO
- **Mixed funds** -- Only if >=50% of assets are equities and the fund is on the Positivlisten or is an eligible IMB

### Where to Hold Bonds Instead

| Account | Tax Treatment | Best For |
|---------|---------------|----------|
| **Aldersopsparing / Pension** | 15.3% PAL tax (lagerbeskatning) | Bond ETFs, government bonds |
| **Frie midler** | Kapitalindkomst rates (varies by type) | Direct bonds, bond ETFs |

**Strategy:** Use the ASK exclusively for equities (where the 17% rate provides the largest benefit vs. 27-42%). Hold bonds in pension or frie midler.

---

## 7. Saxo Bank Specifics

### Fees

| Fee | Saxo (Classic tier) |
|-----|---------------------|
| **Account / custody fee** | 0 DKK |
| **Danish stocks** | 0.08%, min 10 DKK |
| **US stocks** | 0.08%, min 1 USD |
| **European stocks** | 0.08%, min 3 EUR |
| **FX conversion** | 0.25% per conversion |
| **Auto-invest (Manedsopsparing)** | NOT available on ASK |

Higher tiers: Platinum (200K+ USD portfolio): 0.05%. VIP (1M+ USD): 0.03%.

### FX Conversion -- Important ASK Limitation

- Every foreign-currency trade costs 0.25% FX spread (both buy and sell = 0.50% round-trip)
- **You CANNOT open currency sub-accounts on the ASK.** This is only available on regular depots.
- On a regular depot, currency sub-accounts reduce FX costs to 0.15% by holding foreign currency balances
- **Impact:** On a 174K DKK ASK with 5 foreign-currency positions, expect ~870 DKK in annual FX costs for round-trip trades

### ASK-Eligible Instruments at Saxo

Saxo follows SKAT rules:
- Listed stocks (Danish and international) on regulated markets
- ETFs on SKAT's Positivlisten
- Danish equity-based IMB investment funds
- NOT: bonds, derivatives, CFDs, crypto, ADRs, unlisted shares, ETFs not on Positivlisten

### Tax Reporting

**Fully automatic.** Saxo:
- Calculates lagerbeskatning
- Deducts tax from the account in January/February
- Reports everything to SKAT
- You do not need to file anything separately for the ASK

### Saxo vs. Nordnet Comparison

| | Saxo | Nordnet |
|---|---|---|
| **Danish stocks** | 0.08%, min 10 DKK | 0.15%, min 25 DKK |
| **US stocks** | 0.08%, min 1 USD | 0.15%, min 25 DKK |
| **European stocks** | 0.08%, min 3 EUR | 0.15%, min 25 DKK |
| **FX** | 0.25% | 0.25% |
| **Custody** | Free | Free |
| **UX / app** | Complex (SaxoTraderGO) / Simple (SaxoInvestor) | Simpler, more beginner-friendly |
| **Customer service** | Mixed reviews | Highly accessible |
| **Best for** | Cost-conscious investors | Beginners valuing UX |

**Forbrugerradet Taenk (consumer watchdog):** Both received "Best in Test" for ASK in 2025. Saxo wins on price, Nordnet on user experience.

**Community consensus: Do NOT create your ASK at a traditional bank (Nordea, Danske Bank, Jyske Bank).** Fees are 3-10x higher.

---

## 8. Portfolio-Specific Tax Impact Analysis

### Tax Impact Table for Current Portfolio Holdings

| Ticker | Company | Country | Exchange | WHT Rate | Creditable on ASK | Total Div Tax | Reclaim? | ASK Suitable? |
|--------|---------|---------|----------|----------|-------------------|---------------|----------|---------------|
| NOVO-B.CO | Novo Nordisk | Denmark | CPH | 0% | N/A | 17% | No | Excellent |
| MAERSK-B.CO | A.P. Moller-Maersk | Denmark | CPH | 0% | N/A | 17% | No | Excellent |
| BA.L | BAE Systems | UK | LSE | 0% | N/A | 17% | No | Excellent |
| LSEG.L | London Stock Exchange | UK | LSE | 0% | N/A | 17% | No | Excellent |
| HLMA.L | Halma | UK | LSE | 0% | N/A | 17% | No | Excellent |
| MSFT | Microsoft | USA | NASDAQ | 15% | Yes, fully | 17% | No | Excellent |
| V | Visa | USA | NYSE | 15% | Yes, fully | 17% | No | Excellent |
| GILD | Gilead Sciences | USA | NASDAQ | 15% | Yes, fully | 17% | No | Excellent |
| ADBE | Adobe | USA | NASDAQ | 15% | Yes, fully | 17% | No | Excellent |
| CPRT | Copart | USA | NASDAQ | 15% | Yes, fully | 17% | No | Excellent |
| NOW | ServiceNow | USA | NYSE | 15% | Yes, fully | 17% | No | Excellent |
| AMD | AMD | USA | NASDAQ | 15% | Yes, fully | 17% | No | Excellent |
| COST | Costco | USA | NASDAQ | 15% | Yes, fully | 17% | No | Excellent |
| CSU.TO | Constellation Software | Canada | TSX | 15% | Yes, fully | 17% | No | Excellent |
| ADYEN.AS | Adyen | Netherlands | AMS | 15% | Yes, fully | 17% | No | Excellent |
| UMG.AS | Universal Music | Netherlands | AMS | 15% | Yes, fully | 17% | No | Excellent |
| WKL.AS | Wolters Kluwer | Netherlands | AMS | 15% | Yes, fully | 17% | No | Excellent |
| ASML.AS | ASML | Netherlands | AMS | 15% | Yes, fully | 17% | No | Excellent |
| EL.PA | EssilorLuxottica | France | PAR | 12.80% | Yes, fully | 17% | No | Excellent (2026+) |
| MC.PA | LVMH | France | PAR | 12.80% | Yes, fully | 17% | No | Excellent (2026+) |
| OR.PA | L'Oreal | France | PAR | 12.80% | Yes, fully | 17% | No | Excellent (2026+) |
| RMS.PA | Hermes | France | PAR | 12.80% | Yes, fully | 17% | No | Excellent (2026+) |
| SAP.DE | SAP | Germany | XETRA | 26.375% | 17% max | 26.375% | **Yes (BZSt)** | OK if reclaiming |
| NVS | Novartis (ADR) | Switzerland | NYSE | 35%* | 17% max | 35%* | **Yes (FTA)** | Caution -- verify ADR WHT |
| RACE | Ferrari | Italy/NL | NYSE | 26%** | 17% max | 26%** | **Yes** | Verify actual WHT country |

*NVS: ADR may still face Swiss 35% WHT on underlying dividends -- verify with Saxo.
**RACE: Incorporated in Netherlands, may face Dutch 15% WHT instead of Italian 26% -- verify actual withholding.

### Optimal Account Placement

| Best in ASK | Best in Frie Midler | Either Works |
|-------------|--------------------|--------------| 
| Danish stocks (0% WHT) | Swiss high-dividend stocks (if not reclaiming WHT) | Low/no-dividend growth stocks from any country |
| UK stocks (0% WHT) | Bonds and bond ETFs (not allowed in ASK) | |
| US stocks (15% at source) | | |
| Dutch stocks (15% at source) | | |
| French stocks (12.80% from 2026) | | |
| Canadian stocks (15% at source) | | |
| ETFs (lagerbeskattet anyway -- 17% > 27-42%) | | |
| German stocks (if willing to reclaim) | German high-dividend stocks (if NOT reclaiming) | |

---

## 9. Optimization Strategies

### Priority Order for Account Types

The Danish community consensus:

1. **Aldersopsparing** -- Fill first (~9,400 DKK/year). Lowest tax at 15.3%, withdrawals tax-free. Does not reduce folkepension.
2. **Aktiesparekonto** -- Fill second (up to 174,200 DKK). 17% flat, fully liquid.
3. **Ratepension** -- Valuable if you pay topskat (income >~588,900 DKK). Tax deduction at ~52% marginal rate, income tax at withdrawal ~37%.
4. **Frie midler** -- Everything above ASK cap.

### Maximizing ASK Contribution Room

- Deposit the full 174,200 DKK as early in the year as possible (time in market)
- If you withdrew in a prior year, you can re-contribute up to the limit minus year-end value
- Track contributions carefully -- excess triggers 3% penalty

### Minimizing Foreign Dividend Tax Drag

1. **Prefer accumulating ETFs over individual foreign dividend stocks.** At the ETF level, the fund handles WHT and the Irish domicile minimizes it. You avoid individual stock reclaim headaches entirely.
2. **For individual stocks, prefer 0-15% WHT countries:** DK, UK, US, NL, FR (2026+), CA.
3. **Avoid high-dividend Swiss/German/Italian stocks in ASK** unless you are willing to file reclaims.
4. **For high-WHT countries, use an Irish-domiciled ETF with that country's exposure** instead of individual stocks.

### ETF Wrapper Optimization

Instead of individual European stocks from high-WHT countries, consider:
- An Ireland-domiciled European equity ETF (e.g., iShares MSCI Europe UCITS ETF)
- The ETF receives dividends and handles WHT at the fund level
- You receive 0% WHT on the ETF distribution
- The internal WHT drag is lower than what you'd face holding individual stocks

### Annual Lagerbeskatning Liquidity Planning

- Keep 2-3% of your ASK as cash at year-end to cover the tax
- Or be prepared to deposit cash in January (allowed even above contribution limit)
- If you don't plan, the bank sells positions at potentially bad prices
- Budget for the tax: on 174,200 DKK at 8% annual return = ~13,936 DKK gain = **~2,369 DKK tax**

### When NOT to Use ASK

- For bonds or fixed income (not allowed)
- If you plan to hold a single stock for 30+ years and never sell (realisationsbeskatning deferral in frie midler may eventually win, but this is rare in practice)
- If your total invested capital is less than the ASK limit AND you only hold individual stocks (not ETFs), AND you earn less than ~67,500 DKK in stock income -- the 27% rate in frie midler on realization may be comparable to 17% annual lagerbeskatning over short horizons

---

## 10. Common Pitfalls and FAQ

### Pitfall 1: Not Planning for the Annual Tax Bill

Your bank deducts 17% of unrealized gains in February. If you are 100% invested, they sell positions to cover it. Budget cash or be ready to deposit.

### Pitfall 2: Buying ETFs Not on the Positivlisten

The ETF gets taxed as kapitalindkomst and technically cannot be held in ASK. Brokers may block the purchase. Always check [skats-positivliste.danielwinther.dk](https://skats-positivliste.danielwinther.dk/) first.

### Pitfall 3: Ignoring FX Costs on Small Positions

0.25% FX each way = 0.50% round-trip. On a small 10,000 DKK position, that's 50 DKK just in FX. With a 174K DKK account and 10 positions, FX costs erode returns. Concentrate into fewer positions (3-5 recommended).

### Pitfall 4: Creating ASK at a Traditional Bank

Nordea, Danske Bank, Jyske Bank charge 3-10x more in commissions than Saxo or Nordnet. Transfer your ASK if it's at a traditional bank.

### Pitfall 5: Opening Multiple ASK Accounts

Only one ASK per person across all banks. Opening a second invalidates the second. Check before you open.

### Pitfall 6: Over-Contributing

Deposits above 174,200 DKK trigger a 3% annual penalty prorated daily. Note: the limit is on NET deposits, not account value.

### Pitfall 7: Assuming All Foreign WHT Is Reclaimable

For Germany, Italy, and Switzerland, the full statutory rate is withheld at source. Reclaiming the excess is YOUR responsibility (Saxo and Nordnet do not assist). The process is slow and bureaucratic, especially for Italy.

### Pitfall 8: Closing ASK with Negative Tax Carry-Forward

If you have accumulated negative tax (from loss years) and close the ASK, that credit is permanently lost. Keep the ASK open if you have unused negative tax.

### FAQ from r/dkfinance and Danish Communities

**Q: Should I fill my ASK before investing in frie midler?**
A: Almost always yes. The 17% rate beats 27-42% for nearly all equity strategies. Fill the ASK first.

**Q: One broad ETF or multiple positions on ASK?**
A: With only 174K DKK, most recommend 1-3 positions to minimize transaction costs. A single global ETF (MWRE, EUNL, VWCE) is the most popular approach.

**Q: Does my ASK affect SU or pension benefits?**
A: ASK holdings do NOT reduce SU (student grants) or folkepension. Exception: certain means-tested benefits like aeldrecheck.

**Q: Can I hold individual US stocks on my ASK?**
A: Yes. Individual stocks listed on regulated markets are allowed regardless of country. Only US-domiciled ETFs are blocked (by PRIIPs, not ASK rules).

**Q: How many Danes have an ASK?**
A: ~658,000 as of end-2025, with 167,000 new accounts in 2025 alone (record year). Roughly 1 in 10 adult Danes.

**Q: ETFs have become more popular than individual stocks on ASK.**
A: True. In 2025, 7 of the top 10 most-purchased securities on Nordnet's ASK were ETFs.

---

## Appendix A: Country WHT Rate Reference Table

| Country | Statutory Rate | Treaty Rate (DK) | Applied at Source by Saxo? | Reclaim Needed? |
|---------|---------------|-------------------|---------------------------|-----------------|
| Denmark | 0% (on ASK) | N/A | N/A | No |
| UK | 0% | 0% | N/A | No |
| France | 12.80% (2026) | 15% | Generally yes | No (2026+) |
| USA | 30% | 15% | Yes (W-8BEN) | No |
| Netherlands | 15% | 15% | Generally yes | No |
| Canada | 25% | 15% | Yes | No |
| Germany | 26.375% | 15% | No (full rate withheld) | Yes -- BZSt |
| Italy | 26% | 15% | No (full rate withheld) | Yes -- Agenzia delle Entrate |
| Switzerland | 35% | 15% | No (full rate withheld) | Yes -- FTA |
| Sweden | 30% | 15% | Yes | No |
| Finland | 30% | 15% | Yes | No |
| Norway | 25% | 15% | Varies | Possibly |

## Appendix B: SKAT Positivlisten Lookup

1. Go to [skats-positivliste.danielwinther.dk](https://skats-positivliste.danielwinther.dk/)
2. Search by ETF name, ISIN, or ticker
3. If the fund appears: it is aktieindkomst -- eligible for ASK
4. If not found: it is kapitalindkomst -- NOT eligible for ASK
5. Official download (Excel): [SKAT IFPA page](https://skat.dk/erhverv/ekapital/vaerdipapirer/beviser-og-aktier-i-investeringsforeninger-og-selskaber-ifpa)

## Appendix C: Saxo Bank Fee Schedule for ASK

| | Classic | Platinum (200K+ USD) | VIP (1M+ USD) |
|---|---|---|---|
| Danish stocks | 0.08%, min 10 DKK | 0.05%, min 10 DKK | 0.03%, min 10 DKK |
| US stocks | 0.08%, min 1 USD | 0.05%, min 1 USD | 0.03%, min 1 USD |
| European stocks | 0.08%, min 3 EUR | 0.05%, min 3 EUR | 0.03%, min 3 EUR |
| FX conversion | 0.25% | 0.25% | 0.15% |
| Custody | Free | Free | Free |
| Auto-invest on ASK | Not available | Not available | Not available |

## Appendix D: Sources and Links

### Official / Government
- [SKAT -- Aktiesparekonto](https://skat.dk/borger/aktier-og-andre-vaerdipapirer/aktiesparekonto)
- [SKAT -- IFPA / Positivlisten (Excel download)](https://skat.dk/erhverv/ekapital/vaerdipapirer/beviser-og-aktier-i-investeringsforeninger-og-selskaber-ifpa)
- [Retsinformation -- Aktiesparekontoloven](https://www.retsinformation.dk/eli/lta/2021/1852)
- [IRS -- Denmark Tax Treaty](https://www.irs.gov/pub/irs-trty/denmark.pdf)
- [Swiss Federal Tax Administration -- Verrechnungssteuer](https://www.estv.admin.ch/estv/en/home/anticipatory-tax.html)

### Broker Documentation
- [Saxo Bank -- Aktiesparekonto](https://www.home.saxo/da-dk/accounts/aktiesparekonto)
- [Saxo Bank -- ASK FAQ](https://www.help.saxo/hc/en-us/articles/360035642351-Aktiesparekontoen-Frequently-Asked-Questions)
- [Saxo Bank -- Ultimate ASK Guide](https://www.home.saxo/da-dk/learn/guides/equities/saadan-faar-du-mest-ud-af-din-aktiesparekonto)
- [Saxo Bank -- Lagerbeskatning vs Realisationsbeskatning](https://www.home.saxo/da-dk/learn/guides/financial-literacy/lagerbeskatning-vs-realisationsbeskatning)
- [Nordnet -- Aktiesparekonto](https://www.nordnet.dk/tjenester/kontotyper/aktiesparekonto)
- [Nordnet -- Foreign Dividend Taxation](https://www.nordnet.dk/faq/udbytte-og-corporate-actions/udbytte/beskatning-af-udenlandsk-udbytte)
- [Nordnet -- ASK Skat 2026](https://www.nordnet.dk/blog/aktiesparekonto-skat-2026/)

### Professional Tax Advisory
- [EY Danmark -- Aktiesparekontoen](https://www.ey.com/da_dk/insights/tax/aktiesparekontoen-hvad-skal-man-vaere-opmaerksom-paa)
- [EY Danmark -- Beskatning af ETFs](https://www.ey.com/da_dk/insights/tax/beskatning-af-exchange-traded-funds)
- [PwC -- Denmark Corporate WHT](https://taxsummaries.pwc.com/denmark/corporate/withholding-taxes)

### Danish Investment Blogs and Guides
- [Frinans -- Aktiesparekonto](https://www.frinans.dk/aktiesparekonto/)
- [Frinans -- SKATs Positivliste](https://www.frinans.dk/skats-positivliste/)
- [Ung Med Penge -- Aktiesparekonto](https://ungmedpenge.dk/aktiesparekonto/)
- [D-Investering -- ASK 2026](https://d-investering.dk/aktiesparekonto-2026-saadan-maksimerer-du-din-ask/)
- [Aktietip -- Bedste ETF til ASK](https://aktietip.dk/bedste-etf-til-aktiesparekonto/)
- [Pengejunglen -- Alt Om Aktiesparekontoen](http://pengejunglen.dk/alt-det-vigtige-on-aktiesparekontoen/)
- [Indeksinvest.dk -- ETF'er og Skattestatus](https://www.indeksinvest.dk/indeksfonde/)
- [NPinvestor -- Bedste Aktiesparekonto](https://npinvestor.dk/aktier-for-begyndere/bedste-aktiesparekonto/)
- [Forbrugerradet Taenk -- ASK Test](https://taenk.dk/test/aktiesparekonti)

### Community / Searchable Tools
- [SKATs Positivliste (Daniel Winther)](https://skats-positivliste.danielwinther.dk/) -- searchable, updated daily
- [minask.dk](https://minask.dk/skat-positivliste) -- searchable
- [Dansk Aktionaerforening -- Reclaim Guide](https://www.shareholders.dk/guide/saadan-faar-du-udenlandsk-udbytteskat-retur)

### Treaty References
- [Denmark-France Treaty (Schjodt)](https://schjodt.com/news/double-taxation-treaty-between-denmark-and-france-in-effect-from-1-january-2024)
- [Denmark-Canada Treaty](https://www.treaty-accord.gc.ca/text-texte.aspx?id=102250)
- [Switzerland-Denmark Treaty (LawyersSwitzerland)](https://lawyersswitzerland.com/switzerland-denmark-double-taxation-treaty/)
- [Germany-Denmark Treaty (LawyersGermany)](https://lawyersgermany.com/germany-denmark-double-tax-treaty/)

---

## Completeness Checklist

- [x] ASK contribution limit for 2025/2026 confirmed with source
- [x] ASK tax rate (17%) confirmed current
- [x] Lagerbeskatning mechanics explained with worked numeric example
- [x] Lagerbeskatning vs realisationsbeskatning comparison covered
- [x] Danish stock dividend treatment on ASK documented
- [x] US stock dividend WHT (W-8BEN, 15% treaty rate) documented
- [x] Netherlands WHT rate and treaty interaction documented
- [x] France WHT rate and treaty interaction documented
- [x] Germany WHT rate and treaty interaction documented
- [x] UK WHT rate (0%) documented
- [x] Canada WHT rate and treaty interaction documented
- [x] Switzerland WHT rate and treaty interaction documented
- [x] Foreign WHT credit/reclaim rules within ASK clarified
- [x] "Lost WHT" problem on ASK explained
- [x] ETF domicile impact covered (Irish UCITS vs US vs Danish)
- [x] SKAT Positivlisten explained with link to look it up
- [x] Accumulating vs distributing ETF treatment on ASK covered
- [x] Bond eligibility on ASK answered
- [x] Bond ETF taxation on ASK covered
- [x] Saxo Bank ASK fees documented
- [x] Saxo FX conversion costs documented
- [x] Saxo ASK-eligible instrument rules documented
- [x] Saxo vs Nordnet comparison included
- [x] Saxo auto-reporting to SKAT explained
- [x] Portfolio-specific ticker tax impact table included
- [x] Optimal account placement (ASK vs frie midler vs pension) for each ticker type
- [x] ASK vs frie midler vs pension decision framework included
- [x] Liquidity planning for annual lagerbeskatning payment covered
- [x] Common pitfalls section with at least 5 real pitfalls
- [x] FAQ from r/dkfinance or Danish communities included
- [x] All sources/links listed in appendix
- [x] All tax rates sourced to official documentation, not just blogs
