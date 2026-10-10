#!/usr/bin/env node
// Automated WCAG 2.1 A/AA audit of every browser view with axe-core.
//
//   python3 backend/omapit.py --db /tmp/a11y.sqlite3 --static preview/dist/client --seed-demo --serve 4199 &
//   node scripts/a11y-audit.mjs [http://127.0.0.1:4199/]
//
// Use a throwaway database: the crawl clicks through the demo journal.
// Set CHROMIUM_PATH to use an existing Chromium. Exits 1 on any violation.
// Automated rules catch a subset of problems; this is not a screen-reader test.
import { chromium } from "playwright";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";

const base = process.argv[2] || "http://127.0.0.1:4199/";
const axeSource = readFileSync(createRequire(import.meta.url).resolve("axe-core/axe.min.js"), "utf8");
const explorers = ["cuts", "sauces", "hotsauces", "rubs", "veggies", "peppers", "bread", "sides", "cutting", "field", "equipment", "market"];
const viewports = { desktop: { width: 1280, height: 900 }, phone: { width: 390, height: 844 } };

const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM_PATH || undefined,
  args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
});
let violations = 0;

async function audit(page, label) {
  await page.waitForTimeout(600);
  await page.addScriptTag({ content: axeSource });
  const found = await page.evaluate(async () => (await axe.run(document, {
    runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"] },
    resultTypes: ["violations"],
  })).violations.map((v) => ({ id: v.id, impact: v.impact, help: v.help, targets: v.nodes.map((n) => n.target.join(" ")) })));
  console.log(`${found.length ? "FAIL" : "ok  "} ${label}`);
  for (const v of found) console.log(`     ${v.id} (${v.impact}): ${v.help}\n       ${v.targets.join("\n       ")}`);
  violations += found.length;
}

for (const [size, viewport] of Object.entries(viewports)) {
  const page = await browser.newPage({ viewport });
  await page.goto(base, { waitUntil: "networkidle" });
  const main = page.locator('nav[aria-label="Main navigation"] button');
  for (let a = 0; a < await main.count(); a++) {
    const area = (await main.nth(a).innerText()).trim();
    await main.nth(a).click();
    await page.waitForTimeout(300);
    const sub = page.locator("nav").nth(1).locator("button");
    const count = (await page.locator("nav").count()) > 1 ? await sub.count() : 0;
    if (!count) { await audit(page, `${size} ${area}`); continue; }
    for (let s = 0; s < count; s++) {
      const view = (await sub.nth(s).innerText()).trim();
      if (!(await sub.nth(s).isVisible())) continue;
      await sub.nth(s).click();
      await audit(page, `${size} ${area} › ${view}`);
    }
  }
  for (const hash of ["settings", "grill", ...explorers]) {
    await page.goto(`${base}#${hash}`);
    await page.reload({ waitUntil: "networkidle" });
    await audit(page, `${size} #${hash}`);
  }
  await page.close();
}
await browser.close();
console.log(violations ? `\n${violations} accessibility violation(s).` : "\nNo automated accessibility violations.");
process.exit(violations ? 1 : 0);
