// Runs the in-app self-test suite and fails on any regression.
// The suite lives in index.html (<script type="text/plain" id="selftest-src">) and is
// started automatically by the ?test query parameter; it publishes its result on
// window.SELFTEST_RESULT. This runner only observes - it never modifies the app.
const { chromium } = require('playwright');
const path = require('path');
const { pathToFileURL } = require('url');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.CHROMIUM_PATH || undefined,
    args: ['--no-sandbox'],
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));

  const target = pathToFileURL(path.resolve(__dirname, '..', 'index.html')).href + '?test=1';
  await page.goto(target, { waitUntil: 'load' });
  await page.waitForFunction(() => window.SELFTEST_RESULT && Array.isArray(window.SELFTEST_RESULT.results), null, { timeout: 60000 });

  const result = await page.evaluate(() => {
    const r = window.SELFTEST_RESULT;
    return {
      passed: r.passed,
      total: r.total,
      skipped: r.skipped,
      failed: r.results.filter(x => x.ok === false).map(x => x.name + (x.info ? ' :: ' + x.info : '')),
    };
  });

  await browser.close();

  const ok = result.failed.length === 0 && errors.length === 0 && result.passed === result.total;
  console.log(`App-Selbsttest: ${result.passed}/${result.total} bestanden, ${result.skipped} uebersprungen`);
  for (const failure of result.failed) console.log('  FEHLER: ' + failure);
  for (const error of errors) console.log('  PAGEERROR: ' + error);
  if (!ok) {
    console.log('selftest-app: FEHLGESCHLAGEN');
    process.exit(1);
  }
  console.log('selftest-app: OK');
})();