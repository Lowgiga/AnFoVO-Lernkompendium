const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: process.env.CHROMIUM_PATH || undefined, args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  await page.goto(pathToFileURL(path.resolve(__dirname, '..', 'index.html')).href, { waitUntil: 'load' });
  await page.waitForTimeout(1200);
  const result = await page.evaluate(() => ({
    title: document.title,
    language: document.documentElement.lang,
    pageCount: document.querySelectorAll('#pages article.page').length,
    robotNavAvailable: typeof window.RobotNav !== 'undefined',
    robotNavVersion: window.RobotNav && window.RobotNav.inspect ? window.RobotNav.inspect().version : null,
    bookPresent: !!document.querySelector('.book3d'),
    robotPresent: !!document.querySelector('.robot3d'),
    backgroundCanvasPresent: !!document.querySelector('#bgc')
  }));

  const root = path.resolve(__dirname, '..');
  const manifest = JSON.parse(fs.readFileSync(path.join(root, 'manifest.json'), 'utf8'));
  const manifestIconsMissing = (manifest.icons || [])
    .filter(icon => !fs.existsSync(path.resolve(root, icon.src)))
    .map(icon => icon.src);
  const manifestLink = await page.evaluate(() =>
    document.querySelector('link[rel="manifest"]')?.getAttribute('href') || null
  );

  const contactChecks = await page.evaluate(() => {
    const expectedHref = 'mailto:Vid80gmx@gmail.com';
    const expectedLabel = 'Vid80gmx@gmail.com';
    const normalize = value => (value || '')
      .replace(/[ \t\n\f\r]+/g, ' ')
      .trim(' \t\n\f\r');
    const colorAlpha = value => {
      const normalized = (value || '').trim().toLowerCase();
      if (normalized === 'transparent') return 0;
      const match = normalized.match(/^rgba?\(([^)]*)\)$/);
      if (match) {
        const parts = match[1].split(',').map(part => part.trim());
        if (parts.length === 4) {
          const alpha = parts[3].endsWith('%')
            ? Number(parts[3].slice(0, -1)) / 100
            : Number(parts[3]);
          if (Number.isFinite(alpha)) return alpha;
        }
      }
      const canvas = document.createElement('canvas');
      canvas.width = canvas.height = 1;
      const context = canvas.getContext('2d', { willReadFrequently: true });
      if (!context) return 1;
      context.clearRect(0, 0, 1, 1);
      context.fillStyle = value;
      context.fillRect(0, 0, 1, 1);
      return context.getImageData(0, 0, 1, 1).data[3] / 255;
    };
    const filterHasZeroOpacity = value => {
      for (const match of (value || '').matchAll(/opacity\(\s*([^)]+)\)/gi)) {
        const number = match[1].trim().replace(/%$/, '');
        if (Number(number) === 0) return true;
      }
      return false;
    };
    const splitTopLevel = (value, separator) => {
      const parts = [];
      let depth = 0;
      let start = 0;
      for (let index = 0; index < value.length; index += 1) {
        const character = value[index];
        if (character === '(') depth += 1;
        else if (character === ')') depth -= 1;
        else if (character === separator && depth === 0) {
          parts.push(value.slice(start, index).trim());
          start = index + 1;
        }
      }
      parts.push(value.slice(start).trim());
      return parts;
    };
    const lengthRatio = (value, referenceSize) => {
      const normalized = (value || '').trim().toLowerCase();
      if (!normalized || normalized === 'auto') return 0;
      if (normalized.endsWith('%')) return Number.parseFloat(normalized) / 100;
      if (normalized.endsWith('px') && referenceSize > 0) {
        return Number.parseFloat(normalized) / referenceSize;
      }
      return null;
    };
    const insetFullyClips = (value, box) => {
      const match = /^inset\((.*)\)$/i.exec((value || '').trim());
      if (!match) return false;
      const parts = match[1].trim().split(/\s+/);
      if (parts.length < 1 || parts.length > 4) return false;
      const top = parts[0];
      const right = parts.length === 2 || parts.length === 3 ? parts[1] : parts[3];
      const bottom = parts.length === 1 || parts.length === 2 ? parts[0] : parts[2];
      const left = parts.length === 1
        ? parts[0]
        : parts.length === 2 || parts.length === 3 ? parts[1] : parts[3];
      const ratios = {
        top: lengthRatio(top, box?.height),
        right: lengthRatio(right, box?.width),
        bottom: lengthRatio(bottom, box?.height),
        left: lengthRatio(left, box?.width)
      };
      if (Object.values(ratios).some(ratio => ratio === null)) return false;
      return ratios.top >= 1 || ratios.right >= 1 || ratios.bottom >= 1 || ratios.left >= 1 ||
        ratios.top + ratios.bottom >= 1 || ratios.left + ratios.right >= 1;
    };
    const alphaIsZero = value => {
      const normalized = (value || '').trim().replace(/%$/, '');
      const number = Number(normalized);
      return Number.isFinite(number) && number === 0;
    };
    const colorIsFullyTransparent = value => {
      const normalized = (value || '').trim().toLowerCase();
      if (normalized === 'transparent') return true;
      const functional = /^(rgba?|hsla?)\((.*)\)$/i.exec(normalized);
      if (functional) {
        const body = functional[2];
        const slash = body.lastIndexOf('/');
        if (slash !== -1) return alphaIsZero(body.slice(slash + 1));
        const parts = body.split(',').map(part => part.trim());
        return parts.length === 4 && alphaIsZero(parts[3]);
      }
      const hex = /^#([0-9a-f]{3,8})$/i.exec(normalized);
      if (hex) {
        const digits = hex[1];
        if (digits.length === 4) return digits[3] === '0';
        if (digits.length === 8) return digits.slice(6, 8) === '00';
      }
      return false;
    };
    const stopColor = value => {
      const match = /^(rgba?|hsla?)\([^)]*\)|#[0-9a-f]{3,8}\b|transparent\b|[a-z]+/i.exec(
        (value || '').trim()
      );
      return match?.[0] || null;
    };
    const maskFullyTransparent = value => {
      const normalized = (value || '').trim();
      if (!normalized || normalized.toLowerCase() === 'none') return false;
      const layers = splitTopLevel(normalized, ',');
      return layers.length > 0 && layers.every(layer => {
        const gradient = /^(?:repeating-)?(?:linear|radial|conic)-gradient\((.*)\)$/i.exec(layer);
        if (!gradient) return false;
        const parts = splitTopLevel(gradient[1], ',');
        const stops = parts.length > 1 ? parts.slice(1) : parts;
        return stops.length > 0 && stops.every(stop => {
          const color = stopColor(stop);
          return color && colorIsFullyTransparent(color);
        });
      });
    };
    const hasPaintSuppression = (style, element) => {
      const clipPath = style.clipPath || 'none';
      const maskImage = [style.maskImage, style.webkitMaskImage]
        .find(value => value && value !== 'none') || 'none';
      return filterHasZeroOpacity(style.filter) ||
        insetFullyClips(clipPath, element?.getBoundingClientRect()) ||
        maskFullyTransparent(maskImage);
    };
    const isRendered = element => {
      if (typeof element.checkVisibility === 'function' && !element.checkVisibility({
        opacityProperty: true,
        visibilityProperty: true,
        contentVisibilityAuto: true,
        checkOpacity: true,
        checkVisibilityCSS: true
      })) return false;
      for (let current = element; current; current = current.parentElement) {
        const style = getComputedStyle(current);
        if (
          current.hidden ||
          style.display === 'none' ||
          style.visibility === 'hidden' ||
          style.visibility === 'collapse' ||
          Number(style.opacity) === 0 ||
          style.contentVisibility === 'hidden' ||
          hasPaintSuppression(style, current)
        ) return false;
      }
      for (const owner of [element, ...element.querySelectorAll('*')]) {
        const style = getComputedStyle(owner);
        const textFill = style.getPropertyValue('-webkit-text-fill-color');
        if (
          colorAlpha(style.color) === 0 ||
          colorIsFullyTransparent(style.color) ||
          (textFill && (colorAlpha(textFill) === 0 || colorIsFullyTransparent(textFill))) ||
          hasPaintSuppression(style, owner)
        ) return false;
      }
      const rect = element.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    };
    const findContactScope = root => {
      const scopedFooter = root.querySelector('footer#foot');
      const scopedRegion = scopedFooter?.querySelector(
        ':scope > section[aria-labelledby="imp-h"]'
      ) || null;
      const heading = scopedRegion?.querySelector(
        ':scope > :is(h1,h2,h3,h4,h5,h6)#imp-h'
      ) || null;
      const scopedCandidates = scopedRegion
        ? Array.from(scopedRegion.querySelectorAll('a[href]'))
          .filter(anchor => anchor.getAttribute('href') === expectedHref)
        : [];
      const labelledBy = scopedRegion?.getAttribute('aria-labelledby')?.split(/\s+/) || [];
      return {
        footer: scopedFooter,
        region: scopedRegion,
        heading,
        candidates: scopedCandidates,
        valid: !!scopedFooter && !!scopedRegion && !!heading &&
          labelledBy.includes(heading.id) && scopedCandidates.length > 0
      };
    };
    const collectCandidates = root => findContactScope(root).candidates;
    const contactScope = findContactScope(document);
    const footer = contactScope.footer;
    const region = contactScope.region;
    const heading = contactScope.heading;
    const scopeValid = contactScope.valid;
    const candidates = contactScope.candidates;
    candidates.forEach(anchor => anchor.scrollIntoView({ block: 'center' }));
    const exactLabelsFor = anchors => anchors.filter(
      anchor => normalize(anchor.innerText) === expectedLabel
    );
    const visibleFor = anchors => exactLabelsFor(anchors).filter(anchor => {
      if (!isRendered(anchor)) return false;
      const rect = anchor.getBoundingClientRect();
      return rect.bottom > 0 && rect.right > 0 &&
        rect.top < innerHeight && rect.left < innerWidth;
    });
    const exactLabels = exactLabelsFor(candidates);
    const visible = visibleFor(candidates);

    const runProbe = (targetStyle = {}, ancestorStyle = {}) => {
      const host = document.createElement('div');
      Object.assign(host.style, ancestorStyle);
      const anchor = document.createElement('a');
      anchor.href = expectedHref;
      anchor.textContent = expectedLabel;
      Object.assign(anchor.style, targetStyle);
      host.appendChild(anchor);
      document.body.appendChild(host);
      const accepted = isRendered(anchor);
      host.remove();
      return accepted;
    };
    const footerContactWithoutMatchingSectionRejected = (() => {
      if (!region) return false;
      const labelledBy = region.getAttribute('aria-labelledby');
      region.removeAttribute('aria-labelledby');
      const rejected = !findContactScope(document).valid;
      region.setAttribute('aria-labelledby', labelledBy);
      return rejected;
    })();
    const footerContactWithoutMatchingHeadingRejected = (() => {
      if (!heading) return false;
      const headingId = heading.id;
      heading.removeAttribute('id');
      const rejected = !findContactScope(document).valid;
      heading.id = headingId;
      return rejected;
    })();
    const probes = {
      normalAccepted: runProbe(),
      displayNoneRejected: !runProbe({ display: 'none' }),
      visibilityHiddenRejected: !runProbe({ visibility: 'hidden' }),
      opacityZeroRejected: !runProbe({ opacity: '0' }),
      filterOpacityZeroRejected: !runProbe({ filter: 'opacity(0)' }),
      transparentTextRejected: !runProbe({ color: 'transparent' }),
      transparentRgbaTextRejected: !runProbe({ color: 'rgba(1, 2, 3, 0)' }),
      transparentHexTextRejected: !runProbe({ color: '#1230' }),
      partiallyClippedAccepted: runProbe({ clipPath: 'inset(25%)' }),
      opaqueMaskAccepted: runProbe({ maskImage: 'linear-gradient(black, black)' }),
      fullyClippedRejected: !runProbe({ clipPath: 'inset(50%)' }),
      overFullyClippedRejected: !runProbe({ clipPath: 'inset(100%)' }),
      transparentMaskRejected: !runProbe({
        maskImage: 'linear-gradient(transparent, transparent)'
      }),
      ancestorDisplayNoneRejected: !runProbe({}, { display: 'none' }),
      ancestorVisibilityHiddenRejected: !runProbe({}, { visibility: 'hidden' }),
      ancestorOpacityZeroRejected: !runProbe({}, { opacity: '0' }),
      ancestorFilterOpacityZeroRejected: !runProbe({}, { filter: 'opacity(0)' }),
      ancestorPartiallyClippedAccepted: runProbe({}, { clipPath: 'inset(25%)' }),
      ancestorOpaqueMaskAccepted: runProbe({}, {
        maskImage: 'linear-gradient(black, black)'
      }),
      ancestorFullyClippedRejected: !runProbe({}, { clipPath: 'inset(50%)' }),
      ancestorOverFullyClippedRejected: !runProbe({}, { clipPath: 'inset(100%)' }),
      ancestorTransparentMaskRejected: !runProbe({}, {
        maskImage: 'linear-gradient(transparent, transparent)'
      }),
      footerContactWithoutMatchingSectionRejected,
      footerContactWithoutMatchingHeadingRejected
    };

    const removedAnchors = candidates.map(anchor => ({
      anchor,
      parent: anchor.parentNode,
      nextSibling: anchor.nextSibling
    }));
    removedAnchors.forEach(({ anchor }) => anchor.remove());
    const outsideAnchor = document.createElement('a');
    outsideAnchor.href = expectedHref;
    outsideAnchor.textContent = expectedLabel;
    document.body.appendChild(outsideAnchor);
    const outsideCandidates = collectCandidates(document);
    const outsideExactLabels = exactLabelsFor(outsideCandidates);
    const outsideVisible = visibleFor(outsideCandidates);
    const outsideGateWouldPass = scopeValid &&
      outsideCandidates.length === 1 &&
      outsideExactLabels.length === 1 &&
      outsideVisible.length === 1;
    outsideAnchor.remove();
    removedAnchors.reverse().forEach(({ anchor, parent, nextSibling }) => {
      if (!parent) return;
      if (nextSibling?.parentNode === parent) {
        parent.insertBefore(anchor, nextSibling);
      } else {
        parent.appendChild(anchor);
      }
    });
    const outsideFooterRejected = !outsideGateWouldPass;

    return {
      expectedHref,
      expectedLabel,
      scopeValid,
      regionHrefCount: candidates.length,
      exactHrefCount: candidates.length,
      exactLabelCount: exactLabels.length,
      visibleCount: visible.length,
      rawHref: candidates[0]?.getAttribute('href') || null,
      resolvedHref: visible[0]?.href || null,
      probes,
      outsideFooterRejected
    };
  });

  await page.setViewportSize({ width: 390, height: 844 });
  const mobileRobotDisplay = await page.locator('.robot3d').evaluate(el => getComputedStyle(el).display);

  const progressChecks = await page.evaluate(() => {
    const view = document.getElementById('view-fortschritt');
    const wasActive = view.classList.contains('active');
    view.classList.add('active');
    const rows = Array.from(document.querySelectorAll('#proglist .prog'));
    const rings = rows.filter(row => row.querySelector('.ring-wrap svg.ring') && row.querySelector('.ring-pct')).length;
    const countLabels = rows.filter(row => row.querySelector('.prog-count')).length;
    const bars = rows.filter(row => {
      const bar = row.querySelector('.bar');
      return !!bar && bar.getBoundingClientRect().width >= 32;
    }).length;
    const exercisePages = document.querySelectorAll('#pages article.page[data-fill="1"]').length;
    const overallText = document.getElementById('prog-overall-txt')?.textContent || '';
    if (!wasActive) view.classList.remove('active');
    return { rows: rows.length, rings, countLabels, bars, exercisePages, overallText };
  });

  const accessibilityChecks = await page.evaluate(() => {
    const dialog = document.getElementById('confirmDlg');
    const labelId = dialog.getAttribute('aria-labelledby');
    const descriptionId = dialog.getAttribute('aria-describedby');
    const dialogNamed = !!labelId && !!document.getElementById(labelId);
    const dialogDescribed = !!descriptionId && !!document.getElementById(descriptionId);

    window.dispatchEvent(new Event('kompendium:pagechange'));
    const pageChangeFeedback = document.querySelector('.robot3d')?.classList.contains('mood-ok') || false;

    const before = Array.from(document.querySelectorAll('.view'))
      .filter(view => view.classList.contains('active'))
      .map(view => view.id)
      .join(',');
    window.uiConfirm('Stabilitätstest', function () {});
    document.dispatchEvent(new KeyboardEvent('keydown', { key: '/', bubbles: true, cancelable: true }));
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', ctrlKey: true, bubbles: true, cancelable: true }));
    const focusStayedInDialog = dialog.contains(document.activeElement);
    const after = Array.from(document.querySelectorAll('.view'))
      .filter(view => view.classList.contains('active'))
      .map(view => view.id)
      .join(',');
    dialog.querySelector('.dlg-cancel').click();

    return {
      dialogNamed,
      dialogDescribed,
      pageChangeFeedback,
      focusStayedInDialog,
      shortcutsDidNotNavigate: before === after
    };
  });

  const interactionChecks = await page.evaluate(() => {
    const task = Array.from(document.querySelectorAll('.task')).find(candidate => {
      const gaps = Array.from(candidate.querySelectorAll('.gap'));
      return gaps.length >= 2 && gaps.every(gap => {
        try { return JSON.parse(gap.dataset.alts || '[]').some(answer => String(answer).trim().length > 0) && !!gap.querySelector('.gap-in'); }
        catch (_) { return false; }
      });
    });
    if (!task) return { gapScenarioFound: false };

    const solution = task.querySelector('details.loesung');
    if (!solution) return { gapScenarioFound: false };
    solution.open = false;
    solution.dispatchEvent(new Event('toggle'));

    const inputs = Array.from(task.querySelectorAll('.gap')).map(gap => gap.querySelector('.gap-in'));
    inputs.forEach(input => {
      const answers = JSON.parse(input.closest('.gap').dataset.alts || '[]');
      const correctAnswer = answers.find(answer => String(answer).trim().length > 0);
      input.value = String(correctAnswer);
      input.dispatchEvent(new Event('input', { bubbles: true }));
    });

    solution.open = true;
    solution.dispatchEvent(new Event('toggle'));
    const moodGreenAfterOpening = document.querySelector('.robot3d')?.classList.contains('mood-ok') || false;

    inputs[0].value = '__not_a_valid_answer__';
    inputs[0].dispatchEvent(new Event('input', { bubbles: true }));
    const moodBadAfterEditing = document.querySelector('.robot3d')?.classList.contains('mood-bad') || false;

    HTMLCanvasElement.prototype.getContext = function () { return null; };
    const markDone = document.getElementById('markdone');
    markDone.click();

    const currentPage = document.querySelector('article.page.current');
    let storageAvailable = false;
    let completionPersisted = false;
    try {
      storageAvailable = document.getElementById('storenote').hidden;
      if (storageAvailable && currentPage) {
        const raw = localStorage.getItem('anfoevo_v2_done');
        const done = raw ? JSON.parse(raw) : {};
        completionPersisted = done[currentPage.dataset.id] === true;
      }
    } catch (_) {
      storageAvailable = false;
    }

    return {
      gapScenarioFound: true,
      moodGreenAfterOpening,
      moodBadAfterEditing,
      markDonePressed: markDone.getAttribute('aria-pressed') === 'true',
      storageAvailable,
      completionPersisted
    };
  });

  await browser.close();
  const report = {
    ...result,
    manifestLink,
    manifestIconsMissing,
    contactChecks,
    mobileRobotDisplay,
    progressChecks,
    accessibilityChecks,
    interactionChecks,
    errors
  };
  console.log(JSON.stringify(report, null, 2));
  if (
    !result.title.includes('v2.9.5') ||
    result.pageCount < 1 ||
    !result.robotNavAvailable ||
    !result.bookPresent ||
    !result.robotPresent ||
    manifestLink !== './manifest.json' ||
    manifestIconsMissing.length > 0 ||
    !contactChecks.scopeValid ||
    contactChecks.exactHrefCount !== 1 ||
    contactChecks.exactLabelCount !== 1 ||
    contactChecks.visibleCount !== 1 ||
    contactChecks.rawHref !== contactChecks.expectedHref ||
    contactChecks.resolvedHref !== contactChecks.expectedHref ||
    !Object.values(contactChecks.probes).every(Boolean) ||
    !contactChecks.outsideFooterRejected ||
    mobileRobotDisplay === 'none' ||
    progressChecks.rings !== progressChecks.rows ||
    progressChecks.countLabels !== progressChecks.rows ||
    progressChecks.bars !== progressChecks.rows ||
    !progressChecks.overallText.endsWith('von ' + progressChecks.exercisePages + ' Aufgaben erledigt') ||
    !accessibilityChecks.dialogNamed ||
    !accessibilityChecks.dialogDescribed ||
    !accessibilityChecks.pageChangeFeedback ||
    !accessibilityChecks.focusStayedInDialog ||
    !accessibilityChecks.shortcutsDidNotNavigate ||
    !interactionChecks.gapScenarioFound ||
    !interactionChecks.moodGreenAfterOpening ||
    !interactionChecks.moodBadAfterEditing ||
    !interactionChecks.markDonePressed ||
    (interactionChecks.storageAvailable && !interactionChecks.completionPersisted) ||
    errors.length
  ) process.exit(1);
})().catch(error => { console.error(error); process.exit(1); });
