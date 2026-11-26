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
    const trimAsciiWhitespace = value => value.replace(
      /^[ \t\n\f\r]+|[ \t\n\f\r]+$/g,
      ''
    );
    const normalize = value => trimAsciiWhitespace(
      (value || '').replace(/[ \t\n\f\r]+/g, ' ')
    );
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
    const cssLengthIsZero = value => {
      const match = /^([+-]?(?:\d+(?:\.\d*)?|\.\d+))([a-z%]*)$/i.exec(
        (value || '').trim()
      );
      return !!match && Number(match[1]) === 0;
    };
    const polygonFullyClips = value => {
      const match = /^polygon\((.*)\)$/i.exec((value || '').trim());
      if (!match) return false;
      const points = splitTopLevel(match[1], ',').map(point => point.trim().split(/\s+/));
      if (points.length < 3 || points.some(point => point.length !== 2)) return false;
      const parsed = points.map(point => point.map(coordinate => {
        const length = /^([+-]?(?:\d+(?:\.\d*)?|\.\d+))([a-z%]*)$/i.exec(coordinate);
        return length ? { value: Number(length[1]), unit: length[2].toLowerCase() } : null;
      }));
      if (parsed.some(point => point.some(coordinate => !coordinate))) return false;
      if (parsed.every(point => point.every(coordinate => coordinate.value === 0))) return true;
      const units = new Set(parsed.flatMap(point => point.map(coordinate => coordinate.unit)));
      if (units.size !== 1) return false;
      if (!parsed.every(point => point.every(coordinate => Number.isInteger(coordinate.value)))) {
        return false;
      }
      const first = parsed[0];
      const second = parsed.find(point =>
        point[0].value !== first[0].value || point[1].value !== first[1].value
      );
      if (!second) return true;
      const deltaX = second[0].value - first[0].value;
      const deltaY = second[1].value - first[1].value;
      return parsed.every(point =>
        deltaX * (point[1].value - first[1].value) -
          deltaY * (point[0].value - first[0].value) === 0
      );
    };
    const clipPathFullyClips = (value, box) => {
      const normalized = (value || '').trim();
      const circle = /^circle\((.*)\)$/i.exec(normalized);
      if (circle) {
        const radius = circle[1].split(/\bat\b/i)[0].trim();
        return cssLengthIsZero(radius);
      }
      const ellipse = /^ellipse\((.*)\)$/i.exec(normalized);
      if (ellipse) {
        const radii = ellipse[1].split(/\bat\b/i)[0].trim().split(/\s+/);
        return radii.length === 2 && radii.some(radius => cssLengthIsZero(radius));
      }
      if (polygonFullyClips(normalized)) return true;
      return insetFullyClips(normalized, box);
    };
    const legacyClipFullyClips = (value, position) => {
      if (!['absolute', 'fixed'].includes((position || '').toLowerCase())) return false;
      const match = /^rect\((.*)\)$/i.exec((value || '').trim());
      if (!match) return false;
      const sides = splitTopLevel(match[1], ',').map(side => side.trim());
      return sides.length === 4 && sides.every(side => cssLengthIsZero(side));
    };
    const transformHasZeroArea = style => {
      const transform = (style.transform || style.webkitTransform || 'none').trim();
      const matrix = /^matrix\((.*)\)$/i.exec(transform);
      if (matrix) {
        const values = matrix[1].split(',').map(Number);
        if (values.length !== 6 || values.some(value => !Number.isFinite(value))) return false;
        return values[0] * values[3] - values[1] * values[2] === 0;
      }
      const matrix3d = /^matrix3d\((.*)\)$/i.exec(transform);
      if (matrix3d) {
        const values = matrix3d[1].split(',').map(Number);
        if (values.length !== 16 || values.some(value => !Number.isFinite(value))) return false;
        const determinant =
          values[0] * (values[5] * values[15] - values[13] * values[7]) -
          values[4] * (values[1] * values[15] - values[13] * values[3]) +
          values[12] * (values[1] * values[7] - values[5] * values[3]);
        return determinant === 0;
      }
      const scale = (style.scale || '').trim().toLowerCase();
      if (scale === 'none' || !scale) return false;
      const scaleFunction = /^scale\((.*)\)$/i.exec(scale);
      const factorValues = scaleFunction
        ? scaleFunction[1].trim().split(/[\s,]+/)
        : scale.split(/[\s,]+/);
      const factors = factorValues.map(value => {
        const normalized = value.endsWith('%')
          ? Number.parseFloat(value) / 100
          : Number(value);
        return normalized;
      });
      return factors.length >= 1 && factors.length <= 3 &&
        factors.every(value => Number.isFinite(value)) && factors.includes(0);
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
    const isGradientDirectionPrelude = value => {
      const normalized = (value || '').trim().toLowerCase();
      if (
        /^to\s+(?:left|right|top|bottom)$/.test(normalized) ||
        /^to\s+(?:top|bottom)\s+(?:left|right)$/.test(normalized) ||
        /^to\s+(?:left|right)\s+(?:top|bottom)$/.test(normalized)
      ) return true;
      const angle = /^([+-]?(?:\d+(?:\.\d+)?|\.\d+))(deg|grad|rad|turn)?$/i
        .exec(normalized);
      return !!angle && (!!angle[2] || Number(angle[1]) === 0);
    };
    const isSupportedColor = value => {
      try {
        return typeof CSS !== 'undefined' &&
          typeof CSS.supports === 'function' &&
          CSS.supports('color', value);
      } catch (_) {
        return false;
      }
    };
    const colorHasZeroLuminance = value => {
      const normalized = (value || '').trim().toLowerCase();
      if (normalized === 'none') return true;
      if (!isSupportedColor(value)) return false;
      const canvas = document.createElement('canvas');
      canvas.width = canvas.height = 1;
      const context = canvas.getContext('2d', { willReadFrequently: true });
      if (!context) return false;
      context.fillStyle = '#010203';
      context.fillStyle = value;
      if (context.fillStyle === '#010203') return false;
      context.clearRect(0, 0, 1, 1);
      context.fillStyle = value;
      context.fillRect(0, 0, 1, 1);
      const pixel = context.getImageData(0, 0, 1, 1).data;
      return pixel[3] === 0 || (pixel[0] === 0 && pixel[1] === 0 && pixel[2] === 0);
    };
    const svgPresentationProperty = (element, name) => {
      const style = element.getAttribute?.('style') || '';
      const match = new RegExp(`(?:^|;)\\s*${name}\\s*:\\s*([^;]+)`, 'i').exec(style);
      if (match) return match[1].trim();
      let current = element;
      while (current && current.nodeType === 1) {
        const value = current.getAttribute?.(name);
        if (value !== null && value !== undefined) return value.trim();
        current = current.parentElement;
      }
      return null;
    };
    const svgElementHasZeroLuminancePaint = (element, computedStyle = null) => {
      const styleValue = name => computedStyle
        ? (computedStyle.getPropertyValue?.(name) || computedStyle[name] || '')
        : svgPresentationProperty(element, name);
      const fill = styleValue('fill') || 'black';
      const stroke = styleValue('stroke');
      if (!colorHasZeroLuminance(fill)) return false;
      if (stroke && stroke !== 'none' && !colorHasZeroLuminance(stroke)) return false;
      const filter = styleValue('filter');
      if (filter && filter !== 'none') return false;
      const mask = styleValue('mask');
      if (mask && mask !== 'none') return false;
      const blend = styleValue('mix-blend-mode');
      if (blend && blend !== 'normal') return false;
      return true;
    };
    const svgPaintElementsAreZeroLuminance = (root, useComputedStyles) => {
      if (root.querySelector('image,use,text,foreignObject')) return false;
      const paintElements = root.querySelectorAll(
        'rect,circle,ellipse,line,polyline,polygon,path'
      );
      if (paintElements.length === 0) return false;
      return Array.from(paintElements).every(element => {
        const computedStyle = useComputedStyles ? getComputedStyle(element) : null;
        return svgElementHasZeroLuminancePaint(element, computedStyle);
      });
    };
    const dataSvgIsZeroLuminance = url => {
      const comma = url.indexOf(',');
      if (comma === -1) return false;
      const metadata = url.slice(5, comma).toLowerCase();
      if (!metadata.startsWith('image/svg+xml')) return false;
      const payload = url.slice(comma + 1);
      let source;
      try {
        source = metadata.includes(';base64') ? atob(payload) : decodeURIComponent(payload);
      } catch (_) {
        return false;
      }
      const documentNode = new DOMParser().parseFromString(source, 'image/svg+xml');
      const root = documentNode.documentElement;
      if (!root || root.localName.toLowerCase() !== 'svg') return false;
      if (root.querySelector('style')) return false;
      return svgPaintElementsAreZeroLuminance(root, false);
    };
    const localSvgMaskIsZeroLuminance = url => {
      if (!url.startsWith('#')) return false;
      let id;
      try {
        id = decodeURIComponent(url.slice(1));
      } catch (_) {
        return false;
      }
      const target = document.getElementById(id);
      if (!target || target.localName.toLowerCase() !== 'mask') return false;
      if ((getComputedStyle(target).maskType || '').toLowerCase() !== 'luminance') return false;
      return svgPaintElementsAreZeroLuminance(target, true);
    };
    const svgUrlIsZeroLuminance = (value, mode) => {
      const match = /^url\((.*)\)$/i.exec((value || '').trim());
      if (!match) return false;
      let url = match[1].trim();
      if (
        url.length >= 2 &&
        ((url.startsWith('"') && url.endsWith('"')) ||
          (url.startsWith("'") && url.endsWith("'")))
      ) {
        url = url.slice(1, -1);
      }
      if (url.startsWith('#')) {
        if (mode === 'alpha') return false;
        return localSvgMaskIsZeroLuminance(url);
      }
      if (url.toLowerCase().startsWith('data:image/svg+xml')) {
        return mode === 'luminance' && dataSvgIsZeroLuminance(url);
      }
      return false;
    };
    const maskGradientFullyTransparent = (layer, mode) => {
      const gradient = /^(?:repeating-)?(?:linear|radial|conic)-gradient\((.*)\)$/i.exec(layer);
      if (!gradient) return false;
      const parts = splitTopLevel(gradient[1], ',');
      const candidateStops = parts.length > 1 && isGradientDirectionPrelude(parts[0])
        ? parts.slice(1)
        : parts;
      const stops = candidateStops
        .map(stop => stopColor(stop))
        .filter(color => color && isSupportedColor(color));
      if (stops.length === 0) return false;
      return mode === 'luminance'
        ? stops.every(color => colorHasZeroLuminance(color))
        : stops.every(color => colorIsFullyTransparent(color));
    };
    const maskLayerFullyTransparent = (layer, mode = 'match-source') => {
      if (/^(?:repeating-)?(?:linear|radial|conic)-gradient\(/i.test(layer)) {
        return maskGradientFullyTransparent(layer, mode);
      }
      return svgUrlIsZeroLuminance(layer, mode);
    };
    const maskFullyTransparent = (value, composite = 'add', modes = 'match-source') => {
      const normalized = (value || '').trim();
      if (!normalized || normalized.toLowerCase() === 'none') return false;
      const layers = splitTopLevel(normalized, ',');
      if (layers.length === 0) return false;
      const modeList = splitTopLevel(modes, ',')
        .map(mode => mode.trim().toLowerCase());
      const layerStates = layers.map((layer, index) => {
        const mode = modeList.length
          ? modeList[index % modeList.length]
          : 'match-source';
        return maskLayerFullyTransparent(layer, mode);
      });
      const operators = splitTopLevel(composite, ',')
        .map(operator => operator.trim().toLowerCase());
      let fullyTransparent = layerStates[layerStates.length - 1];
      for (let index = layerStates.length - 2; index >= 0; index -= 1) {
        const operator = operators.length
          ? operators[index % operators.length]
          : 'add';
        if (operator === 'add') {
          fullyTransparent = fullyTransparent && layerStates[index];
        } else if (operator === 'intersect') {
          fullyTransparent = fullyTransparent || layerStates[index];
        } else {
          return layerStates.every(Boolean);
        }
      }
      return fullyTransparent;
    };
    const hasPaintSuppression = (style, element) => {
      const clipPath = style.clipPath || 'none';
      const legacyClip = style.clip || 'auto';
      const maskImage = [style.maskImage, style.webkitMaskImage]
        .find(value => value && value !== 'none') || 'none';
      const maskComposite = style.maskComposite || style.webkitMaskComposite || 'add';
      const maskModes = [style.maskMode, style.webkitMaskMode]
        .find(value => value && value !== 'none') || 'match-source';
      return filterHasZeroOpacity(style.filter) ||
        clipPathFullyClips(clipPath, element?.getBoundingClientRect()) ||
        legacyClipFullyClips(legacyClip, style.position) ||
        transformHasZeroArea(style) ||
        maskFullyTransparent(maskImage, maskComposite, maskModes);
    };
    const styleHidesElement = (element, style) =>
      element.hidden ||
      style.display === 'none' ||
      Number(style.opacity) === 0 ||
      style.contentVisibility === 'hidden';
    const computedVisibilityHides = style =>
      style.visibility === 'hidden' || style.visibility === 'collapse';
    const textRunsFor = element => {
      const runs = [];
      const nonRenderedTextTags = new Set(['noscript', 'script', 'style', 'textarea']);
      const collectTextRuns = node => {
        for (const child of node.childNodes) {
          if (child.nodeType === 3) {
            if (child.nodeValue) {
              runs.push({ owner: node, text: child.nodeValue });
            }
          } else if (
            child.nodeType === 1 &&
            !nonRenderedTextTags.has(child.localName)
          ) {
            collectTextRuns(child);
          }
        }
      };
      collectTextRuns(element);
      return runs;
    };
    const textOwnerCanPaint = owner => {
      if (!owner) return false;
      const style = getComputedStyle(owner);
      const textFill = style.getPropertyValue('-webkit-text-fill-color');
      if (
        styleHidesElement(owner, style) ||
        computedVisibilityHides(style) ||
        colorAlpha(style.color) === 0 ||
        colorIsFullyTransparent(style.color) ||
        (textFill && (colorAlpha(textFill) === 0 || colorIsFullyTransparent(textFill)))
      ) return false;
      for (let current = owner; current; current = current.parentElement) {
        const currentStyle = getComputedStyle(current);
        if (
          styleHidesElement(current, currentStyle) ||
          hasPaintSuppression(currentStyle, current)
        ) return false;
      }
      return true;
    };
    const paintableLabelText = element => textRunsFor(element)
      .filter(run => textOwnerCanPaint(run.owner))
      .map(run => run.text)
      .join('');
    const isRendered = element => {
      if (typeof element.checkVisibility === 'function' && !element.checkVisibility({
        opacityProperty: true,
        visibilityProperty: false,
        contentVisibilityAuto: true,
        checkOpacity: true
      })) return false;
      for (let current = element; current; current = current.parentElement) {
        const style = getComputedStyle(current);
        if (
          styleHidesElement(current, style) ||
          hasPaintSuppression(style, current)
        ) return false;
      }
      if (normalize(paintableLabelText(element)) !== expectedLabel) return false;
      const rect = element.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    };
    const pseudoContentIsPainted = owner => {
      if (
        typeof owner.checkVisibility === 'function' &&
        !owner.checkVisibility({
          opacityProperty: true,
          visibilityProperty: false,
          contentVisibilityAuto: true,
          checkOpacity: true
        })
      ) return false;
      for (let current = owner; current; current = current.parentElement) {
        const style = getComputedStyle(current);
        if (
          styleHidesElement(current, style) ||
          hasPaintSuppression(style, current)
        ) return false;
      }
      return true;
    };
    const generatedContentPaintValue = value => {
      const source = value || '';
      let depth = 0;
      let quote = null;
      for (let index = 0; index < source.length; index += 1) {
        const character = source[index];
        if (quote) {
          if (character === '\\') index += 1;
          else if (character === quote) quote = null;
        } else if (character === '"' || character === "'") {
          quote = character;
        } else if (character === '(') {
          depth += 1;
        } else if (character === ')') {
          depth = Math.max(0, depth - 1);
        } else if (character === '/' && depth === 0) {
          return source.slice(0, index);
        }
      }
      return source;
    };
    const generatedContentStrings = value => {
      const strings = [];
      let depth = 0;
      let quote = null;
      let text = '';
      for (let index = 0; index < value.length; index += 1) {
        const character = value[index];
        if (!quote) {
          if (character === '(') depth += 1;
          else if (character === ')') depth = Math.max(0, depth - 1);
          else if (depth === 0 && (character === '"' || character === "'")) {
            quote = character;
            text = '';
          }
          continue;
        }
        if (character === '\\') {
          index += 1;
          if (index < value.length) text += value[index];
        } else if (character === quote) {
          strings.push(text);
          quote = null;
        } else {
          text += character;
        }
      }
      return strings;
    };
    const generatedContentHasVisibleText = value => {
      const normalized = (value || '').trim().toLowerCase();
      if (!normalized || normalized === 'none' || normalized === 'normal') return false;
      const paintValue = generatedContentPaintValue(value).trim();
      const strings = generatedContentStrings(paintValue);
      if (strings.length > 0) {
        return strings.some(text => normalize(text) !== '');
      }
      if (!paintValue) return false;
      if (/^url\(.*\)$/is.test(paintValue)) return false;
      return true;
    };
    const hasVisibleGeneratedContent = element => {
      for (const owner of [element, ...element.querySelectorAll('*')]) {
        if (!pseudoContentIsPainted(owner)) continue;
        for (const pseudo of ['::before', '::after']) {
          let style;
          try {
            style = getComputedStyle(owner, pseudo);
          } catch (_) {
            continue;
          }
          const textFill = style.getPropertyValue('-webkit-text-fill-color');
          if (
            style.display === 'none' ||
            computedVisibilityHides(style) ||
            Number(style.opacity) === 0 ||
            colorAlpha(style.color) === 0 ||
            colorIsFullyTransparent(style.color) ||
            (textFill && (colorAlpha(textFill) === 0 || colorIsFullyTransparent(textFill))) ||
            hasPaintSuppression(style, owner)
          ) continue;
          if (generatedContentHasVisibleText(style.content)) return true;
        }
      }
      return false;
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
      anchor => normalize(paintableLabelText(anchor)) === expectedLabel &&
        !hasVisibleGeneratedContent(anchor)
    );
    const visibleFor = anchors => exactLabelsFor(anchors).filter(anchor => {
      if (!isRendered(anchor)) return false;
      const rect = anchor.getBoundingClientRect();
      return rect.bottom > 0 && rect.right > 0 &&
        rect.top < innerHeight && rect.left < innerWidth;
    });
    const runVisibleLabelProbe = populate => {
      const host = document.createElement('div');
      const anchor = document.createElement('a');
      anchor.href = expectedHref;
      populate(anchor);
      host.appendChild(anchor);
      document.body.appendChild(host);
      anchor.scrollIntoView({ block: 'center' });
      const accepted = visibleFor([anchor]).includes(anchor);
      host.remove();
      return accepted;
    };
    const exactLabels = exactLabelsFor(candidates);
    const visible = visibleFor(candidates);

    const runLabelProbe = label => {
      const host = document.createElement('div');
      const anchor = document.createElement('a');
      anchor.href = expectedHref;
      anchor.textContent = label;
      host.appendChild(anchor);
      document.body.appendChild(host);
      const accepted = exactLabelsFor([anchor]).length === 1;
      host.remove();
      return accepted;
    };
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
    const runDescendantProbe = (
      descendantStyle,
      descendantText,
      anchorText = '',
      anchorStyle = {}
    ) => {
      const host = document.createElement('div');
      const anchor = document.createElement('a');
      anchor.href = expectedHref;
      anchor.textContent = anchorText;
      Object.assign(anchor.style, anchorStyle);
      const descendant = document.createElement('span');
      descendant.textContent = descendantText;
      Object.assign(descendant.style, descendantStyle);
      anchor.appendChild(descendant);
      host.appendChild(anchor);
      document.body.appendChild(host);
      const accepted = isRendered(anchor);
      host.remove();
      return accepted;
    };
    const runNestedVisibilityOverrideProbe = () => {
      const host = document.createElement('div');
      const anchor = document.createElement('a');
      anchor.href = expectedHref;
      anchor.style.visibility = 'hidden';
      const descendant = document.createElement('span');
      descendant.style.visibility = 'visible';
      descendant.textContent = expectedLabel;
      anchor.appendChild(descendant);
      host.appendChild(anchor);
      document.body.appendChild(host);
      const accepted = isRendered(anchor);
      host.remove();
      return accepted;
    };
    const runGeneratedContentProbe = (
      content,
      pseudo = '::after',
      additionalCss = ''
    ) => {
      const host = document.createElement('div');
      const style = document.createElement('style');
      style.textContent =
        `.generated-content-probe${pseudo} { content: ${content}; ${additionalCss} }`;
      const anchor = document.createElement('a');
      anchor.href = expectedHref;
      anchor.className = 'generated-content-probe';
      anchor.textContent = expectedLabel;
      host.append(style, anchor);
      document.body.appendChild(host);
      const accepted = exactLabelsFor([anchor]).length === 1;
      host.remove();
      return accepted;
    };
    const runSplitLabelProbe = (suppressedIndex, descendantStyle) => {
      const host = document.createElement('div');
      const anchor = document.createElement('a');
      anchor.href = expectedHref;
      const labelParts = [expectedLabel.slice(0, 5), expectedLabel.slice(5)];
      labelParts.forEach((text, index) => {
        const descendant = document.createElement('span');
        descendant.textContent = text;
        if (index === suppressedIndex) Object.assign(descendant.style, descendantStyle);
        anchor.appendChild(descendant);
      });
      host.appendChild(anchor);
      document.body.appendChild(host);
      anchor.scrollIntoView({ block: 'center' });
      const accepted = visibleFor([anchor]).includes(anchor);
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
    const compositeMaskLayers =
      'linear-gradient(transparent, transparent), linear-gradient(black, black)';
    const localMaskId = 'smoke-local-luminance-mask';
    const localSvgMask = document.createElementNS(
      'http://www.w3.org/2000/svg',
      'svg'
    );
    localSvgMask.setAttribute('width', '0');
    localSvgMask.setAttribute('height', '0');
    localSvgMask.setAttribute('aria-hidden', 'true');
    localSvgMask.style.position = 'absolute';
    const localDefs = document.createElementNS(
      'http://www.w3.org/2000/svg',
      'defs'
    );
    const localMask = document.createElementNS(
      'http://www.w3.org/2000/svg',
      'mask'
    );
    localMask.setAttribute('id', localMaskId);
    localMask.setAttribute('maskUnits', 'userSpaceOnUse');
    localMask.setAttribute('maskContentUnits', 'userSpaceOnUse');
    localMask.setAttribute('x', '0');
    localMask.setAttribute('y', '0');
    localMask.setAttribute('width', '100');
    localMask.setAttribute('height', '100');
    const localMaskRect = document.createElementNS(
      'http://www.w3.org/2000/svg',
      'rect'
    );
    localMaskRect.setAttribute('width', '100');
    localMaskRect.setAttribute('height', '100');
    localMaskRect.setAttribute('fill', 'black');
    localMask.appendChild(localMaskRect);
    localDefs.appendChild(localMask);
    localSvgMask.appendChild(localDefs);
    document.body.appendChild(localSvgMask);
    const svgDataUrl = fill => 'data:image/svg+xml,' + encodeURIComponent(
      `<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">` +
      `<rect width="100" height="100" fill="${fill}"/></svg>`
    );
    const blackSvgDataUrl = svgDataUrl('black');
    const whiteSvgDataUrl = svgDataUrl('white');
    const probes = {
      normalAccepted: runProbe(),
      asciiWhitespaceLabelAccepted: runLabelProbe(` \t${expectedLabel}\r\n `),
      nonBreakingSpaceLabelRejected: !runLabelProbe(`${expectedLabel}\u00A0`),
      displayNoneRejected: !runProbe({ display: 'none' }),
      visibilityHiddenRejected: !runProbe({ visibility: 'hidden' }),
      nestedVisibilityOverrideAccepted: runNestedVisibilityOverrideProbe(),
      paintSuppressedCopiesRejected: !runVisibleLabelProbe(anchor => {
        const opacityCopy = document.createElement('span');
        opacityCopy.style.opacity = '0';
        opacityCopy.textContent = expectedLabel;
        const displayCopy = document.createElement('span');
        displayCopy.style.display = 'none';
        displayCopy.textContent = expectedLabel;
        anchor.append(opacityCopy, displayCopy);
      }),
      paintableEmailWithFilteredTextAccepted: runVisibleLabelProbe(anchor => {
        anchor.append(document.createTextNode(expectedLabel));
        const filteredText = document.createElement('span');
        filteredText.style.filter = 'opacity(0)';
        filteredText.textContent = ' unrelated';
        anchor.append(filteredText);
      }),
      opacityZeroRejected: !runProbe({ opacity: '0' }),
      filterOpacityZeroRejected: !runProbe({ filter: 'opacity(0)' }),
      unrelatedFilteredDescendantAccepted: runDescendantProbe(
        { filter: 'opacity(0)' },
        '',
        expectedLabel
      ),
      unrelatedTextFilteredDescendantAccepted: runDescendantProbe(
        { filter: 'opacity(0)' },
        'unrelated',
        expectedLabel
      ),
      filteredEmailDescendantRejected: !runDescendantProbe(
        { filter: 'opacity(0)' },
        expectedLabel
      ),
      splitLabelFirstFilteredRejected: !runSplitLabelProbe(
        0,
        { filter: 'opacity(0)' }
      ),
      splitLabelSecondHiddenRejected: !runSplitLabelProbe(
        1,
        { visibility: 'hidden' }
      ),
      transparentTextRejected: !runProbe({ color: 'transparent' }),
      transparentRgbaTextRejected: !runProbe({ color: 'rgba(1, 2, 3, 0)' }),
      transparentHexTextRejected: !runProbe({ color: '#1230' }),
      partiallyClippedAccepted: runProbe({ clipPath: 'inset(25%)' }),
      opaqueMaskAccepted: runProbe({ maskImage: 'linear-gradient(black, black)' }),
      mixedStopMaskAccepted: runProbe({
        maskImage: 'linear-gradient(black, transparent)'
      }),
      mixedStopDirectedMaskAccepted: runProbe({
        maskImage: 'linear-gradient(to right, black, transparent)'
      }),
      unitlessZeroDirectionRecognized: isGradientDirectionPrelude('0'),
      nonzeroUnitlessAngleRejected: !isGradientDirectionPrelude('45'),
      rightTopDirectionRecognized: isGradientDirectionPrelude('to right top'),
      unitlessZeroDirectionMaskRejected: !runProbe({
        maskImage: 'linear-gradient(0, transparent, transparent)'
      }),
      rightTopDirectionMaskRejected: !runProbe({
        maskImage: 'linear-gradient(to right top, transparent, transparent)'
      }),
      fullyClippedRejected: !runProbe({ clipPath: 'inset(50%)' }),
      overFullyClippedRejected: !runProbe({ clipPath: 'inset(100%)' }),
      transparentMaskRejected: !runProbe({
        maskImage: 'linear-gradient(transparent, transparent)'
      }),
      transparentRadialMaskRejected: !runProbe({
        maskImage: 'radial-gradient(circle at center, transparent, transparent)'
      }),
      transparentConicMaskRejected: !runProbe({
        maskImage: 'conic-gradient(from 45deg, transparent, transparent)'
      }),
      mixedRadialMaskAccepted: runProbe({
        maskImage: 'radial-gradient(circle at center, black, transparent)'
      }),
      mixedConicMaskAccepted: runProbe({
        maskImage: 'conic-gradient(from 45deg, black, transparent)'
      }),
      intersectCompositeMaskRejected: !runProbe({
        maskImage: compositeMaskLayers,
        maskComposite: 'intersect'
      }),
      addCompositeMaskAccepted: runProbe({
        maskImage: compositeMaskLayers,
        maskComposite: 'add'
      }),
      cycledCompositeMaskRejected: !runProbe({
        maskImage: [
          'linear-gradient(black, black)',
          'linear-gradient(transparent, transparent)',
          'linear-gradient(transparent, transparent)',
          'linear-gradient(black, black)'
        ].join(', '),
        maskComposite: 'intersect, add'
      }),
      cycledMaskModeRejected: !runProbe({
        maskImage: [
          'linear-gradient(black, black)',
          'linear-gradient(transparent, transparent)'
        ].join(', '),
        maskMode: 'luminance, alpha'
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
    outsideAnchor.scrollIntoView({ block: 'center' });
    const outsideControlVisible = visibleFor([outsideAnchor]).includes(outsideAnchor);
    const outsideCandidates = collectCandidates(document);
    const outsideCandidateExcluded = !outsideCandidates.includes(outsideAnchor);
    const outsideExactLabels = exactLabelsFor(outsideCandidates);
    const outsideVisible = visibleFor(outsideCandidates);
    const outsideGateWouldPass = scopeValid &&
      outsideControlVisible &&
      outsideCandidates.length === 1 &&
      outsideExactLabels.length === 1 &&
      outsideVisible.length === 1;
    probes.outsideControlVisible = outsideControlVisible;
    probes.outsideCandidateExcluded = outsideCandidateExcluded;
    outsideAnchor.remove();
    removedAnchors.reverse().forEach(({ anchor, parent, nextSibling }) => {
      if (!parent) return;
      if (nextSibling?.parentNode === parent) {
        parent.insertBefore(anchor, nextSibling);
      } else {
        parent.appendChild(anchor);
      }
    });
    const outsideFooterRejected = !outsideGateWouldPass && outsideCandidateExcluded;

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
      outsideControlVisible,
      outsideCandidateExcluded,
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
    !contactChecks.outsideControlVisible ||
    !contactChecks.outsideCandidateExcluded ||
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
