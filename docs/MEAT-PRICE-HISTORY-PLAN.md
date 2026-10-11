# Historical meat-price trends

The current cards remain a reviewed October 2, 2026 USDA snapshot. Historical chart integration is proposed, not active.

## Recommended implementation

1. Add BLS monthly average-price series for explicitly supported meat definitions and national/regional geography. Verify series identifiers, coverage dates, units and missing periods before import. Do not label a broad steak average as ribeye or brisket.
2. Store original observations, publication period, retrieval timestamp, source and series definition in a separate market-price database/cache. Display missing months as gaps; preserve revisions and identify discontinued series.
3. Add an interactive chart with 1-year, 5-year and all-history ranges, region/series filters, accessible table, CSV export, latest observation and year-over-year changes only where matching periods exist. Show USD/lb and source publication date clearly.
4. Refresh from the local service on a bounded schedule and expose manual Refresh. Preserve the last successful dataset on failures and mark it cached. These are periodically published prices, not real-time store quotes.
5. Add USDA weekly advertised-price history through MyMarketNews after configuring its personal API key in the backend and verifying retail report availability/fields. Never place the key in frontend bundles. Keep cut, grade, region, product form and promotion type consistent across observations.
6. Keep actual local quotes and wholesale indicators as separate series and views. Never splice them into retail-average lines or silently replace a saved dinner price.

## Official sources checked October 5, 2026

- BLS Average Price Data: https://www.bls.gov/cpi/factsheets/average-prices.htm
  Monthly average retail prices, with national and four major regional coverage where sample size is sufficient. Changing sample composition can affect comparisons over time.
- BLS public API: https://www.bls.gov/developers/api_signature_v2.htm
- USDA historical API technical instructions: https://mymarketnews.ams.usda.gov/mars-api/getting-started/technical-instructions
  Published historical time series in JSON/XLSX; personal API key required. No current webhook support stated.
- USDA API basic instructions: https://mymarketnews.ams.usda.gov/mars-api/getting-started/basic-instructions
  Backend integration required; open browser calls are not supported.

Layout update: title/intro now occupy the left column and dated source note the right, aligned with the dinner workbench. Mobile stacks the two. Price controls and cards follow immediately. Existing saved dinner prices and active cook data are preserved.
