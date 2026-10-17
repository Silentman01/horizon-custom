#!/usr/bin/env node
/*
 * render_sections.js - local QA render of a Shopify theme template (any OS 2.0 theme: Horizon, Dawn, ...).
 *
 * Renders the template's custom sections with liquidjs and Shopify-like stubs into ONE static HTML page
 * (collected {% stylesheet %}/{% javascript %}, eager images), optionally with a static buy-box mock of the
 * main product section, and optionally screenshots it with headless Edge/Chrome (desktop + 390px mobile).
 *
 * Requires liquidjs 10 (not shipped with the theme):
 *   npm i liquidjs@10 --prefix <scratch>/qa        then pass  --modules <scratch>/qa/node_modules
 *   (or set NODE_PATH=<scratch>/qa/node_modules before running node)
 *
 * Usage:
 *   node render_sections.js --theme DIR --template templates/product.json --out page.html
 *        [--sections ALL|key1,key2] [--buybox] [--prefix noxis,nx] [--product p.json] [--title "..."]
 *        [--images DIR] [--css base.css,...] [--currency USD] [--locale en] [--fonts google|none]
 *        [--modules DIR] [--shot] [--browser PATH] [--width 1280]
 *
 * Limits (by design): the theme's main product section, header/footer groups and app blocks are NOT rendered
 * (they need real Shopify objects). --buybox renders custom buy-box blocks for real (with a mock product) and
 * native blocks as labeled stand-ins, so layout/colors of the offer area can still be reviewed.
 */
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const { pathToFileURL } = require('url');
const { spawnSync } = require('child_process');

// ───────────────────────────── CLI ─────────────────────────────
function parseArgs(argv) {
  const o = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) continue;
    const k = a.slice(2);
    const n = argv[i + 1];
    if (n === undefined || n.startsWith('--')) o[k] = true;
    else { o[k] = n; i++; }
  }
  return o;
}
const args = parseArgs(process.argv.slice(2));
if (args.help || !args.template) {
  console.log(fs.readFileSync(__filename, 'utf8').split('\n').slice(1, 21).map((l) => l.replace(/^ \*\/?/, '')).join('\n'));
  process.exit(args.help ? 0 : 2);
}

function loadLiquid() {
  const tries = [];
  if (args.modules) tries.push(path.resolve(args.modules, 'liquidjs'));
  tries.push('liquidjs', path.join(__dirname, 'node_modules', 'liquidjs'), path.join(process.cwd(), 'node_modules', 'liquidjs'));
  for (const t of tries) {
    try { return require(t); } catch (e) { /* next */ }
  }
  console.error('liquidjs not found. Install it in a scratch dir (never in the theme repo):\n' +
    '  npm i liquidjs@10 --prefix <scratch>/qa\nthen re-run with --modules <scratch>/qa/node_modules (or NODE_PATH).');
  process.exit(3);
}
const { Liquid, Tag, Drop } = loadLiquid();

const THEME = path.resolve(args.theme || process.cwd());
const TPL_PATH = path.isAbsolute(args.template) ? args.template : path.join(THEME, args.template);
const OUT = path.resolve(args.out || 'render.html');
const OUT_DIR = path.dirname(OUT);
fs.mkdirSync(OUT_DIR, { recursive: true });
const fileUrl = (p) => pathToFileURL(p).href;
const exists = (p) => { try { return fs.statSync(p).isFile(); } catch { return false; } };
// Theme JSON files are JSONC: a /* auto-generated */ header and sometimes // comments (locales). Strip comments outside strings.
function stripJsonComments(s) {
  let out = '', i = 0, inStr = false;
  while (i < s.length) {
    const c = s[i], n = s[i + 1];
    if (inStr) { out += c; if (c === '\\') { out += n; i += 2; continue; } if (c === '"') inStr = false; i++; continue; }
    if (c === '"') { inStr = true; out += c; i++; continue; }
    if (c === '/' && n === '/') { while (i < s.length && s[i] !== '\n') i++; continue; }
    if (c === '/' && n === '*') { const e = s.indexOf('*/', i + 2); i = e < 0 ? s.length : e + 2; continue; }
    out += c; i++;
  }
  return out;
}
const readJson = (p) => JSON.parse(stripJsonComments(fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, '')));
const esc = (s) => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const warnings = new Set();
const errors = [];

// ───────────────────────────── Theme settings → Liquid objects ─────────────────────────────
function parseColor(s) {
  s = String(s).trim();
  let r = 0, g = 0, b = 0, a = 1;
  if (s[0] === '#') {
    let h = s.slice(1);
    if (h.length === 3 || h.length === 4) h = [...h].map((c) => c + c).join('');
    r = parseInt(h.slice(0, 2), 16); g = parseInt(h.slice(2, 4), 16); b = parseInt(h.slice(4, 6), 16);
    if (h.length === 8) a = Math.round((parseInt(h.slice(6, 8), 16) / 255) * 100) / 100;
  } else {
    const m = s.match(/rgba?\(([^)]+)\)/i);
    const p = m ? m[1].split(/[\s,/]+/).filter(Boolean).map(Number) : [0, 0, 0];
    [r, g, b] = p; if (p[3] !== undefined) a = p[3];
  }
  return { r, g, b, a };
}
const isColorStr = (v) => typeof v === 'string' && /^(#[0-9a-f]{3,8}|rgba?\([^)]*\))$/i.test(v.trim());
class Color extends Drop {
  constructor(str) {
    super();
    const c = parseColor(str);
    this.hex = str.trim(); this.red = c.r; this.green = c.g; this.blue = c.b; this.alpha = c.a;
    this.rgb = `${c.r} ${c.g} ${c.b}`; this.rgba = `${c.r} ${c.g} ${c.b} / ${c.a}`;
  }
  valueOf() { return this.hex; }
  toString() { return this.hex; }
}
const toColor = (v) => (v instanceof Color ? v : isColorStr(v) ? new Color(v) : v);

const FONT_FALLBACK = { serif: 'serif', mono: 'monospace' };
class Font extends Drop {
  constructor(handle) {
    super();
    const m = handle.match(/^(.*)_([nio])([1-9])$/);
    const name = (m ? m[1] : handle).split('_').map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
    this.handle = handle; this.family = name; this.weight = m ? Number(m[3]) * 100 : 400;
    this.style = m && m[2] === 'i' ? 'italic' : 'normal';
    this.fallback_families = /serif|garamond|playfair|lora|merriweather|baskerville/i.test(name) && !/sans/i.test(name) ? FONT_FALLBACK.serif : 'sans-serif';
    this.system = false;
  }
  valueOf() { return this.family; }
  toString() { return this.family; }
}
const isFontKey = (k, v) => /^type_.*font$/.test(k) && typeof v === 'string' && /^[a-z0-9_]+_[nio][1-9]$/.test(v);

const rawSettings = (() => {
  const p = path.join(THEME, 'config', 'settings_data.json');
  if (!exists(p)) { warnings.add('config/settings_data.json missing - using empty settings'); return {}; }
  const d = readJson(p);
  let cur = d.current;
  if (typeof cur === 'string') cur = (d.presets || {})[cur] || {};
  return cur || {};
})();
const themeInfo = (() => {
  try { return readJson(path.join(THEME, 'config', 'settings_schema.json')).find((s) => s.name === 'theme_info') || {}; } catch { return {}; }
})();

// Resolve "{{ settings.color_palette.color1 }}" style references against the raw settings.
const lookup = (obj, dotted) => dotted.split('.').reduce((o, k) => (o == null ? undefined : o[k]), obj);
function resolveRefs(v, depth = 0) {
  if (typeof v !== 'string' || depth > 5) return v;
  const m = v.trim().match(/^\{\{\s*settings\.([\w.]+)\s*\}\}$/);
  return m ? resolveRefs(lookup(rawSettings, m[1]), depth + 1) : v;
}

function buildSettings() {
  const s = {};
  for (const [k, v0] of Object.entries(rawSettings)) {
    if (k === 'sections' || k === 'content_for_index' || k === 'blocks') continue;
    const v = resolveRefs(v0);
    if (k === 'color_palette' && v && typeof v === 'object') {
      s[k] = Object.fromEntries(Object.entries(v).map(([pk, pv]) => [pk, toColor(pv)]));
    } else if (k === 'color_schemes' && v && typeof v === 'object') {
      const arr = Object.entries(v).map(([id, sch]) => ({
        id, toString() { return id; },
        settings: Object.fromEntries(Object.entries((sch && sch.settings) || {}).map(([sk, sv]) => [sk, toColor(resolveRefs(sv))])),
      }));
      arr.forEach((sch) => { arr[sch.id] = sch; });
      s[k] = arr;
    } else if (isFontKey(k, v)) s[k] = new Font(v);
    else s[k] = toColor(v);
  }
  return s;
}
const settings = buildSettings();
const headingFont = settings.type_heading_font || settings.type_header_font || new Font('helvetica_n7');
const bodyFont = settings.type_body_font || new Font('helvetica_n4');

// Palette summary (also drives the page background/foreground of the render).
const palette = (() => {
  if (settings.color_palette) {
    const p = settings.color_palette;
    return { source: 'color_palette', bg: String(p.background || '#ffffff'), fg: String(p.foreground || '#000000'), all: Object.fromEntries(Object.entries(p).map(([k, v]) => [k, String(v)])) };
  }
  if (settings.color_schemes && settings.color_schemes.length) {
    const sc = settings.color_schemes[0].settings;
    return { source: `color_schemes.${settings.color_schemes[0].id}`, bg: String(sc.background || '#ffffff'), fg: String(sc.text || sc.foreground || '#000000'), all: Object.fromEntries(Object.entries(sc).filter(([, v]) => v instanceof Color).map(([k, v]) => [k, String(v)])) };
  }
  warnings.add('no color_palette or color_schemes in settings_data.json - render uses white/black');
  return { source: 'none', bg: '#ffffff', fg: '#000000', all: {} };
})();

function schemeCss() {
  if (!settings.color_schemes) return '';
  const trip = (c) => (c instanceof Color ? `${c.red},${c.green},${c.blue}` : null);
  return settings.color_schemes.map((sch) => {
    const st = sch.settings;
    const bg = st.background, fg = st.text || st.foreground, btn = st.button || st.primary_button_background || st.primary, btnT = st.button_label || st.primary_button_text;
    const vars = [['--color-background', trip(bg)], ['--color-foreground', trip(fg)], ['--color-button', trip(btn)], ['--color-button-text', trip(btnT)], ['--color-link', trip(fg)]]
      .filter(([, v]) => v).map(([k, v]) => `${k}:${v};`).join('');
    return `.color-${sch.id}{${vars}background:${bg || 'transparent'};color:${fg || 'inherit'}}`;
  }).join('\n');
}

// Locale strings for the `t` filter.
const locale = (() => {
  const want = args.locale || 'en';
  const dir = path.join(THEME, 'locales');
  const cands = [`${want}.default.json`, `${want}.json`];
  try { cands.push(...fs.readdirSync(dir).filter((f) => f.endsWith('.default.json'))); } catch { return {}; }
  for (const f of cands) if (exists(path.join(dir, f))) { try { return readJson(path.join(dir, f)); } catch { /* next */ } }
  return {};
})();

// ───────────────────────────── Images, money, product mock ─────────────────────────────
const placeholderSvg = (label, w = 1200, h = 1200) => 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(
  `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}"><rect width="100%" height="100%" fill="#e4e4e4"/>` +
  `<text x="50%" y="50%" font-family="Arial" font-size="${Math.round(w / 18)}" fill="#777" text-anchor="middle" dominant-baseline="middle">${esc(label)}</text></svg>`);

function imageFromRef(ref) {
  const name = String(ref).replace(/^shopify:\/\/(shop_images|files)\//, '');
  let src = null;
  if (args.images) {
    const p = path.resolve(args.images, name);
    if (exists(p)) src = fileUrl(p);
  }
  if (!src) { src = placeholderSvg(name); warnings.add(`image setting not found locally (placeholder shown): ${name}${args.images ? '' : ' - pass --images DIR'}`); }
  return { src, url: src, alt: '', width: 1200, height: 1200, aspect_ratio: 1, toString() { return src; } };
}
function convertRefs(v) {
  if (typeof v === 'string' && /^shopify:\/\/(shop_images|files)\//.test(v)) return imageFromRef(v);
  if (Array.isArray(v)) return v.map(convertRefs);
  return v;
}

const CURRENCY = (args.currency || (rawSettings.currency_code) || 'USD').toUpperCase();
const SYMBOL = { USD: '$', CAD: '$', AUD: '$', NZD: '$', EUR: '€', GBP: '£', CHF: 'CHF ', SEK: 'kr ', DKK: 'kr ', NOK: 'kr ', JPY: '¥' };
function money(cents, mode) {
  const n = Number(cents) || 0;
  let amount = (n / 100).toFixed(2);
  if (mode === 'trim' && amount.endsWith('.00')) amount = amount.slice(0, -3);
  if (CURRENCY === 'EUR') return amount.replace('.', ',') + ' €' + (mode === 'code' ? ' EUR' : '');
  if (mode === 'plain') return amount;
  return (SYMBOL[CURRENCY] || '') + amount + (mode === 'code' ? ` ${CURRENCY}` : '');
}
const toCents = (v) => (v == null || v === '' ? null : typeof v === 'number' ? v : Math.round(parseFloat(v) * 100));

function buildProduct() {
  let p = null;
  if (args.product) {
    const d = JSON.parse(fs.readFileSync(path.resolve(args.product), 'utf8'));
    p = d.product || d;
  }
  if (!p) {
    warnings.add('no --product given: mock product with 3 variants (Buy 1/2/3, placeholder prices)');
    p = {
      id: 1, title: args.title || 'Product title', handle: 'product', body_html: '<p>Product description.</p>', options: [{ name: 'Bundle' }],
      variants: [
        { id: 101, title: 'Buy 1', option1: 'Buy 1', price: 3995, compare_at_price: 5990 },
        { id: 102, title: 'Buy 2', option1: 'Buy 2', price: 6990, compare_at_price: 11980 },
        { id: 103, title: 'Buy 3', option1: 'Buy 3', price: 8985, compare_at_price: 17970 },
      ], images: [],
    };
  }
  const imgs = (p.images || []).map((im) => {
    const src = typeof im === 'string' ? im : im.src;
    return { src, url: src, alt: p.title, width: im.width || 1200, height: im.height || 1200, aspect_ratio: 1, toString() { return src; } };
  });
  const variants = (p.variants || []).map((v, i) => ({
    id: v.id || 100 + i, title: v.title || v.option1 || `Variant ${i + 1}`,
    option1: v.option1 || v.title, option2: v.option2 || null, option3: v.option3 || null,
    options: [v.option1, v.option2, v.option3].filter(Boolean),
    price: toCents(v.price) || 0, compare_at_price: toCents(v.compare_at_price),
    available: v.available !== false, featured_image: null, sku: v.sku || '', url: `/products/${p.handle}?variant=${v.id}`,
  }));
  const prices = variants.map((v) => v.price);
  const prod = {
    id: p.id, title: args.title || p.title, handle: p.handle || 'product', url: `/products/${p.handle || 'product'}`,
    vendor: p.vendor || '', description: p.body_html || p.description || '', content: p.body_html || '',
    featured_image: imgs[0] || null, images: imgs, media: imgs,
    options: (p.options || []).map((o) => (typeof o === 'string' ? o : o.name)),
    variants, available: true, selected_variant: null,
    selected_or_first_available_variant: variants[0], first_available_variant: variants[0],
    has_only_default_variant: variants.length <= 1 && /default/i.test((variants[0] || {}).title || 'Default Title'),
    price: Math.min(...prices), price_min: Math.min(...prices), price_max: Math.max(...prices),
    compare_at_price: variants[0] ? variants[0].compare_at_price : null,
  };
  return prod;
}
const product = buildProduct();

// ───────────────────────────── Liquid engine ─────────────────────────────
const shop = { name: args.shop || themeInfo.theme_name || 'Shop', currency: CURRENCY, url: 'https://example.myshopify.com', policies: [], locale: args.locale || 'en' };
const globals = {
  settings, shop, product, closest: { product },
  request: { design_mode: false, visual_preview_mode: false, page_type: 'product', locale: { iso_code: args.locale || 'en' }, path: product.url },
  routes: { root_url: '/', cart_url: '/cart', cart_add_url: '/cart/add', search_url: '/search', all_products_collection_url: '/collections/all', account_url: '/account' },
  collections: { all: { products: Object.assign([product], { first: product }) } },
  cart: { item_count: 0, items: [], total_price: 0 }, localization: { available_countries: [], available_languages: [] },
  template: { name: 'product', suffix: null }, canonical_url: '#', page_title: product.title,
};
const engine = new Liquid({
  root: [path.join(THEME, 'snippets'), path.join(THEME, 'sections'), path.join(THEME, 'blocks')],
  partials: path.join(THEME, 'snippets'),
  extname: '.liquid', strictFilters: false, strictVariables: false, dynamicPartials: true,
  globals, // snippets rendered with {% render %} get an isolated scope: settings/shop must be globals
});

const cssChunks = new Set();
const jsChunks = new Set();
function rawCollector(name, sink) {
  engine.registerTag(name, class extends Tag {
    constructor(token, remain, liquid) {
      super(token, remain, liquid);
      this.raw = '';
      while (remain.length) {
        const t = remain.shift();
        if (t.name === 'end' + name) return;
        this.raw += t.getText();
      }
    }
    render() { if (sink && this.raw.trim()) sink.add(this.raw); return ''; }
  });
}
rawCollector('stylesheet', cssChunks);
rawCollector('javascript', jsChunks);
rawCollector('schema', null);
rawCollector('doc', null);

// {% form %}, {% style %}, {% paginate %}: render inner content inside a wrapper.
function passthrough(name, open, close) {
  engine.registerTag(name, class extends Tag {
    constructor(token, remain, liquid, parser) {
      super(token, remain, liquid);
      this.tpls = [];
      const stream = (parser || liquid.parser).parseStream(remain)
        .on('tag:end' + name, () => stream.stop())
        .on('template', (tpl) => this.tpls.push(tpl))
        .on('end', () => { throw new Error(`tag ${name} not closed`); });
      stream.start();
    }
    * render(ctx, emitter) {
      emitter.write(open);
      yield this.liquid.renderer.renderTemplates(this.tpls, ctx, emitter);
      emitter.write(close);
    }
  });
}
passthrough('form', '<form method="post" action="/cart/add" onsubmit="return false">', '</form>');
passthrough('style', '<style>', '</style>');
passthrough('paginate', '', '');
for (const t of ['section', 'sections', 'layout']) engine.registerTag(t, class extends Tag { render() { return ''; } });

// {% content_for 'blocks' %} / {% content_for 'block', type: 'x', id: 'y' %} - theme blocks from blocks/*.liquid.
const tplCache = new Map();
const parseFile = (file) => { if (!tplCache.has(file)) tplCache.set(file, engine.parse(fs.readFileSync(file, 'utf8'))); return tplCache.get(file); };
const schemaCache = new Map();
function readSchema(file) {
  if (!schemaCache.has(file)) {
    let sch = {};
    try {
      const m = fs.readFileSync(file, 'utf8').match(/\{%-?\s*schema\s*-?%\}([\s\S]*?)\{%-?\s*endschema\s*-?%\}/);
      if (m) sch = JSON.parse(m[1]);
    } catch (e) { warnings.add(`schema JSON unreadable in ${path.relative(THEME, file)}: ${e.message}`); }
    schemaCache.set(file, sch);
  }
  return schemaCache.get(file);
}
const defaultsOf = (settingDefs) => Object.fromEntries((settingDefs || []).filter((s) => s.id && s.default !== undefined).map((s) => [s.id, s.default]));
const withRefs = (obj) => Object.fromEntries(Object.entries(obj || {}).map(([k, v]) => [k, convertRefs(v)]));

function makeBlock(id, node, defs) {
  return {
    id, type: node.type, settings: withRefs({ ...defaultsOf(defs), ...(node.settings || {}) }),
    shopify_attributes: `data-block-id="${esc(id)}" data-block-type="${esc(node.type)}"`, __node: node,
  };
}
const childIds = (node) => (node.block_order || Object.keys(node.blocks || {})).filter((id) => node.blocks && node.blocks[id] && !node.blocks[id].disabled);

function* renderThemeBlock(id, node, ctx, emitter, liquid) {
  const file = path.join(THEME, 'blocks', node.type + '.liquid');
  if (!exists(file)) { warnings.add(`block file missing locally: blocks/${node.type}.liquid`); emitter.write(`<!-- missing block ${esc(node.type)} -->`); return; }
  ctx.push({ block: makeBlock(id, node, readSchema(file).settings), __owner: node });
  try { yield liquid.renderer.renderTemplates(parseFile(file), ctx, emitter); } finally { ctx.pop(); }
}
engine.registerTag('content_for', class extends Tag {
  constructor(token, remain, liquid) { super(token, remain, liquid); this.argstr = token.args; }
  * render(ctx, emitter) {
    const kind = (this.argstr.match(/^\s*['"](\w+)['"]/) || [])[1];
    const owner = ctx.getSync(['__owner']);
    if (!owner || !owner.blocks) return;
    if (kind === 'blocks') {
      for (const id of childIds(owner)) if (!owner.blocks[id].static) yield* renderThemeBlock(id, owner.blocks[id], ctx, emitter, this.liquid);
    } else if (kind === 'block') {
      const id = (this.argstr.match(/\bid:\s*['"]([^'"]+)['"]/) || [])[1];
      if (id && owner.blocks[id]) yield* renderThemeBlock(id, owner.blocks[id], ctx, emitter, this.liquid);
    }
  }
});

// ── Filters (Shopify stubs) ──
const kw = (argv) => Object.fromEntries(argv.filter(Array.isArray));
const missingAssets = new Set();
const assetUrl = (n) => { const p = path.join(THEME, 'assets', String(n)); if (!exists(p)) missingAssets.add(String(n)); return fileUrl(p); };
const imgSrc = (img) => (img == null ? '' : typeof img === 'string' ? img : img.src || img.url || '');
const F = {
  asset_url: assetUrl, asset_img_url: assetUrl, file_url: (n) => placeholderSvg(n), file_img_url: (n) => placeholderSvg(n),
  inline_asset_content: (n) => { const p = path.join(THEME, 'assets', String(n)); return exists(p) ? fs.readFileSync(p, 'utf8') : ''; },
  image_url: imgSrc, img_url: imgSrc, product_img_url: imgSrc,
  image_tag: (src, ...argv) => {
    const o = kw(argv);
    const attrs = Object.entries(o).filter(([k]) => !['widths', 'sizes', 'preload'].includes(k)).map(([k, v]) => `${k}="${esc(v)}"`).join(' ');
    return `<img src="${esc(imgSrc(src))}"${attrs.includes('alt=') ? '' : ' alt=""'} ${attrs}>`;
  },
  img_tag: (src, alt) => `<img src="${esc(imgSrc(src))}" alt="${esc(alt || '')}">`,
  placeholder_svg_tag: (name, cls) => `<svg class="${esc(cls || '')}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="#e4e4e4"/></svg>`,
  money: (c) => money(c), money_with_currency: (c) => money(c, 'code'), money_without_currency: (c) => money(c, 'plain'), money_without_trailing_zeros: (c) => money(c, 'trim'),
  preload_tag: () => '', stylesheet_tag: (u) => `<link rel="stylesheet" href="${esc(u)}">`, script_tag: (u) => `<script src="${esc(u)}"></script>`,
  font_face: () => '', font_url: () => '', font_modify: (f) => f, structured_data: () => '', payment_type_svg_tag: () => '', metafield_tag: () => '', default_pagination: () => '',
  t: (key, ...argv) => {
    const o = kw(argv); let v = lookup(locale, String(key));
    if (v && typeof v === 'object') v = o.count === 1 ? v.one : v.other;
    if (typeof v !== 'string') return String(key).split('.').pop().replace(/_/g, ' ');
    return v.replace(/\{\{\s*(\w+)\s*\}\}/g, (m, k) => (o[k] !== undefined ? o[k] : m));
  },
  handle: (s) => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''),
  link_to: (text, url) => `<a href="${esc(url)}">${text}</a>`, within: (u) => u, url_param_escape: (s) => encodeURIComponent(s),
  pluralize: (n, one, many) => (Number(n) === 1 ? one : many), camelize: (s) => String(s).replace(/[-_\s]+(.)?/g, (m, c) => (c ? c.toUpperCase() : '')),
  color_to_rgb: (c) => { const x = parseColor(String(c)); return x.a < 1 ? `rgba(${x.r}, ${x.g}, ${x.b}, ${x.a})` : `rgb(${x.r}, ${x.g}, ${x.b})`; },
  color_to_hex: (c) => { const x = parseColor(String(c)); return '#' + [x.r, x.g, x.b].map((n) => n.toString(16).padStart(2, '0')).join(''); },
  color_modify: (c, prop, val) => { const x = parseColor(String(c)); return prop === 'alpha' ? `rgba(${x.r}, ${x.g}, ${x.b}, ${val})` : String(c); },
  color_brightness: (c) => { const x = parseColor(String(c)); return (x.r * 299 + x.g * 587 + x.b * 114) / 1000; },
  color_mix: (c) => String(c), color_lighten: (c) => String(c), color_darken: (c) => String(c), color_saturate: (c) => String(c), color_desaturate: (c) => String(c),
};
F.translate = F.t; F.handleize = F.handle;
for (const [name, fn] of Object.entries(F)) engine.registerFilter(name, fn);

// ───────────────────────────── Template → sections ─────────────────────────────
const tpl = readJson(TPL_PATH);
const order = (tpl.order || Object.keys(tpl.sections || {})).filter((k) => tpl.sections[k] && !tpl.sections[k].disabled);
const isMain = (k, t) => k === 'main' || /^main-/.test(t) || ['product-information', 'main-product', 'featured-product'].includes(t);
const wanted = !args.sections || args.sections === true || String(args.sections).toUpperCase() === 'ALL'
  ? order.filter((k) => !isMain(k, tpl.sections[k].type))
  : String(args.sections).split(',').map((s) => s.trim()).filter(Boolean);

// Custom block prefix for the buy-box mock: --prefix, else the most common first token of rendered section types.
const prefixes = (() => {
  if (args.prefix && args.prefix !== true) return String(args.prefix).split(',').map((s) => s.trim()).filter(Boolean);
  const counts = {};
  for (const k of wanted) { const t = (tpl.sections[k] || {}).type || ''; const p = t.split('-')[0]; if (p && t.includes('-')) counts[p] = (counts[p] || 0) + 1; }
  const best = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
  return best ? [best[0]] : [];
})();
const isCustomType = (t) => prefixes.some((p) => new RegExp(`^_?${p.replace(/[^\w-]/g, '')}-`).test(t));

async function renderSection(key) {
  const node = tpl.sections[key];
  if (!node) { warnings.add(`section key not in template: ${key}`); return ''; }
  const file = path.join(THEME, 'sections', node.type + '.liquid');
  if (!exists(file)) { warnings.add(`skipped ${key}: sections/${node.type}.liquid not found`); return ''; }
  const sch = readSchema(file);
  const localBlockDefs = Object.fromEntries((sch.blocks || []).filter((b) => b.type && b.settings).map((b) => [b.type, b.settings]));
  const blocks = childIds(node).filter((id) => !node.blocks[id].static).map((id) => {
    const bn = node.blocks[id];
    const defs = localBlockDefs[bn.type] || (exists(path.join(THEME, 'blocks', bn.type + '.liquid')) ? readSchema(path.join(THEME, 'blocks', bn.type + '.liquid')).settings : []);
    return makeBlock(id, bn, defs);
  });
  const sid = `template--local__${key}`;
  const section = { id: sid, settings: withRefs({ ...defaultsOf(sch.settings), ...(node.settings || {}) }), blocks, block_order: blocks.map((b) => b.id), index: order.indexOf(key) + 1, location: 'template', __node: node };
  const tag = sch.tag || 'div';
  try {
    const html = await engine.render(parseFile(file), { section, __owner: node });
    return `<${tag} id="shopify-section-${sid}" class="shopify-section${sch.class ? ' ' + esc(sch.class) : ''}" data-qa-section="${esc(key)}">${html}</${tag}>\n`;
  } catch (e) {
    errors.push(`${key} (${node.type}): ${e.message}`);
    return `<pre class="qa-error">Liquid error in ${esc(key)} (${esc(node.type)}): ${esc(e.message)}</pre>`;
  }
}

// ───────────────────────────── Buy-box static mock (--buybox) ─────────────────────────────
function findDetailsNode(main) {
  const kids = main.blocks || {};
  const details = Object.values(kids).find((b) => /details/.test(b.type) && b.blocks && Object.keys(b.blocks).length);
  return details || main; // Horizon: _product-details static block; Dawn: section-level blocks
}
const presetSize = (preset) => {
  const m = String(preset || '').match(/^h([1-6])$/);
  const px = m ? Number(rawSettings[`type_size_h${m[1]}`]) : Number(rawSettings.type_size_paragraph);
  return px ? `${m ? Math.min(px, 40) : px}px` : (m ? '28px' : '16px');
};
async function renderBuybox() {
  const key = order.find((k) => isMain(k, tpl.sections[k].type));
  if (!key) { warnings.add('--buybox: no main product section in template'); return ''; }
  const main = tpl.sections[key];
  const det = findDetailsNode(main);
  const sid = `template--local__${key}`;
  const section = { id: sid, settings: main.settings || {}, blocks: [], __node: main };
  const variantsJson = JSON.stringify(product.variants.map((v) => ({ id: v.id, price: money(v.price), compare: v.compare_at_price > v.price ? money(v.compare_at_price) : '' })));

  async function blockHtml(id, node) {
    const t = node.type;
    const file = path.join(THEME, 'blocks', t + '.liquid');
    if (isCustomType(t) && exists(file)) {
      try {
        return await engine.render(engine.parse(`{% content_for 'block', type: '${t}', id: '${id}' %}`), { section, __owner: det });
      } catch (e) { errors.push(`buybox ${id} (${t}): ${e.message}`); return `<pre class="qa-error">${esc(t)}: ${esc(e.message)}</pre>`; }
    }
    const st = node.settings || {};
    const kids = async () => (await Promise.all(childIds(node).map((cid) => blockHtml(cid, node.blocks[cid])))).join('');
    switch (t) {
      case 'text': {
        const html = await engine.parseAndRender(String(st.text || ''), { section });
        return `<div class="bbm-text" style="font-size:${presetSize(st.type_preset)};${/^h/.test(st.type_preset || '') ? 'font-family:var(--font-heading--family);font-weight:' + headingFont.weight + ';line-height:1.15' : ''}">${html}</div>`;
      }
      case 'title': return `<h1 class="bbm-text" style="font-size:${presetSize('h3')};font-family:var(--font-heading--family)">${esc(product.title)}</h1>`;
      case 'price': return `<div class="bbm-price"><b data-bbm-price>${money(product.variants[0].price)}</b> <s data-bbm-compare>${product.variants[0].compare_at_price ? money(product.variants[0].compare_at_price) : ''}</s></div>`;
      case 'variant-picker': case 'variant_picker':
        return `<variant-picker class="bbm-variants"><fieldset><legend>${esc(product.options[0] || 'Option')}</legend>${product.variants.map((v, i) =>
          `<label><input type="radio" name="bbm-opt" value="${esc(v.option1)}" data-variant-id="${v.id}"${i === 0 ? ' checked' : ''}><span>${esc(v.title)}</span></label>`).join('')}</fieldset></variant-picker>`;
      case 'buy-buttons': case 'buy_buttons':
        return `<div class="buy-buttons-block bbm-buy"><button type="button" name="add" class="bbm-atc">${esc(lookup(locale, 'products.product.add_to_cart') || lookup(locale, 'actions.add_to_cart') || 'Add to cart')}</button></div>`;
      case 'accordion': case 'collapsible_tab': case '_accordion-row': {
        if (t === 'collapsible_tab') return `<details class="bbm-acc"><summary>${esc(st.heading || 'Tab')}</summary><div>${st.content || ''}</div></details>`;
        if (t === '_accordion-row') return `<details class="bbm-acc"${st.open_by_default ? ' open' : ''}><summary>${esc(st.heading || 'Row')}</summary><div>${await kids()}</div></details>`;
        return `<div class="bbm-accs">${await kids()}</div>`;
      }
      case 'product-description': case 'description': return `<div class="bbm-text">${product.description}</div>`;
      case 'group': return `<div class="bbm-group">${await kids()}</div>`;
      default: return `<div class="bbm-native">native block: ${esc(t)}</div>`;
    }
  }
  const parts = [];
  for (const id of childIds(det)) parts.push(await blockHtml(id, det.blocks[id]));
  const img = product.featured_image ? `<img src="${esc(product.featured_image.src)}" alt="">` : '<div class="bbm-ph">Product media gallery<br><small>images come from the Shopify product</small></div>';
  return `<div class="shopify-section bbm-section" id="shopify-section-${sid}" data-qa-section="${esc(key)} (buy-box mock)">
<div class="bbm"><div class="bbm__media"><div class="bbm__frame">${img}</div><div class="bbm__thumbs">${'<span></span>'.repeat(4)}</div></div>
<div class="bbm__details product-details">${parts.join('\n')}</div></div>
<script>window.__bbmVariants=${variantsJson};</script></div>\n`;
}

// ───────────────────────────── Page assembly ─────────────────────────────
function fontsLink() {
  if (args.fonts === 'none') return '';
  const fam = (f, w) => `family=${encodeURIComponent(f.family).replace(/%20/g, '+')}:wght@${[...new Set([400, 600, 700, w])].sort().join(';')}`;
  const pair = headingFont.family === bodyFont.family ? fam(headingFont, headingFont.weight) : `${fam(headingFont, headingFont.weight)}&${fam(bodyFont, bodyFont.weight)}`;
  // QA render only: the theme itself must self-host fonts (no third-party font requests in production).
  return `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?${pair}&display=swap">`;
}
function buyboxCss() {
  const r = (k, d) => String(resolveRefs(rawSettings[k]) || d);
  const btnBg = r('palette_primary_button_background', (settings.color_schemes && settings.color_schemes[0] && settings.color_schemes[0].settings.button) || palette.fg);
  const btnFg = r('palette_primary_button_text', (settings.color_schemes && settings.color_schemes[0] && settings.color_schemes[0].settings.button_label) || palette.bg);
  const radius = rawSettings.button_border_radius_primary ?? rawSettings.buttons_radius ?? 0;
  return `.bbm{display:grid;grid-template-columns:1fr 1fr;gap:48px;max-width:1200px;margin:0 auto;padding:24px 16px 48px;align-items:start}
.bbm__frame{aspect-ratio:1;border-radius:12px;overflow:hidden;background:#f2f2f2}.bbm__frame img{width:100%;height:100%;object-fit:contain}
.bbm-ph{height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;text-align:center;color:#777;font-size:14px}
.bbm__thumbs{display:flex;gap:8px;margin-top:8px}.bbm__thumbs span{width:64px;height:64px;border-radius:8px;background:#ececec}
.bbm__details{display:flex;flex-direction:column;gap:18px;min-width:0}.bbm-text>*{margin:0;font-size:inherit;font-weight:inherit;line-height:inherit}.bbm-text p+p{margin-top:.6em}
.bbm-variants fieldset{border:0;padding:0;margin:0;display:flex;gap:8px;flex-wrap:wrap}.bbm-variants legend{font-weight:600;margin-bottom:6px}
.bbm-variants label{border:1px solid #ccc;border-radius:14px;padding:8px 14px;cursor:pointer}.bbm-variants input{margin-right:6px}
.bbm-atc{width:100%;min-height:52px;border:0;border-radius:${radius}px;background:${btnBg};color:${btnFg};font:600 16px var(--font-body--family);cursor:pointer}
.bbm-acc{border-bottom:1px solid #e5e5e5;padding:14px 0}.bbm-acc summary{font-weight:600;cursor:pointer}.bbm-acc>div{padding-top:10px}
.bbm-native{border:1.5px dashed #bbb;border-radius:8px;padding:10px;color:#777;font-size:12px;text-align:center}
@media (max-width:749px){.bbm{grid-template-columns:1fr;gap:20px}}`;
}
const MOCK_JS = `if(!customElements.get('variant-picker')){customElements.define('variant-picker',class extends HTMLElement{});}
document.addEventListener('change',function(e){var i=e.target;if(!i.closest||!i.closest('variant-picker'))return;var v=(window.__bbmVariants||[]).find(function(x){return String(x.id)===i.dataset.variantId});if(!v)return;
document.querySelectorAll('[data-bbm-price]').forEach(function(n){n.textContent=v.price});document.querySelectorAll('[data-bbm-compare]').forEach(function(n){n.textContent=v.compare});});`;
const MEASURE_JS = `addEventListener('load',function(){setTimeout(function(){document.documentElement.setAttribute('data-qa-height',Math.ceil(document.documentElement.scrollHeight))},300)});`;

(async () => {
  let body = '';
  if (args.buybox) body += await renderBuybox();
  for (const key of wanted) body += await renderSection(key);
  const cssLinks = (args.css && args.css !== true ? String(args.css).split(',') : []).map((n) => `<link rel="stylesheet" href="${assetUrl(n.trim())}">`).join('\n');
  const html = `<!doctype html><html lang="${esc(args.locale || 'en')}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>QA render - ${esc(path.basename(TPL_PATH))}</title>
${fontsLink()}
${cssLinks}
<style>
:root{--font-heading--family:'${headingFont.family}',${headingFont.fallback_families};--font-body--family:'${bodyFont.family}',${bodyFont.fallback_families};--font-heading-family:var(--font-heading--family);--font-body-family:var(--font-body--family);--font-heading--weight:${headingFont.weight};--font-body--weight:${bodyFont.weight};--font-heading-weight:${headingFont.weight};--font-body-weight:${bodyFont.weight};--color-background:${palette.bg};--color-foreground:${palette.fg};--header-height:64px}
*,*::before,*::after{box-sizing:border-box}html,body{margin:0}body{background:${palette.bg};color:${palette.fg};font-family:var(--font-body--family);font-size:${Number(rawSettings.type_size_paragraph) || 16}px;line-height:1.5}
h1,h2,h3,h4,h5,h6{font-family:var(--font-heading--family)}img{max-width:100%;display:block;height:auto}
.visually-hidden{position:absolute!important;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0 0 0 0);border:0;white-space:nowrap}
.page-width{max-width:1200px;margin:0 auto;padding:0 16px}.qa-error{background:#fee;color:#900;padding:12px;margin:12px;white-space:pre-wrap}
${schemeCss()}
${args.buybox ? buyboxCss() : ''}
</style>
<style data-qa="collected {% stylesheet %} blocks">
${[...cssChunks].join('\n')}
</style></head><body>
${body}
${[...jsChunks].map((j) => `<script>try{${j}}catch(e){console.error('collected javascript failed',e)}</script>`).join('\n')}
${args.buybox ? `<script>${MOCK_JS}</script>` : ''}
<script>${MEASURE_JS}</script>
</body></html>`;
  // Headless browsers don't scroll, so lazy images never load: force eager.
  fs.writeFileSync(OUT, html.replace(/loading="lazy"/g, 'loading="eager"'));

  console.log(`theme: ${themeInfo.theme_name || '?'} ${themeInfo.theme_version || ''} | palette (${palette.source}): ${Object.entries(palette.all).map(([k, v]) => `${k} ${v}`).join(', ')}`);
  console.log(`fonts: heading ${headingFont.family} ${headingFont.weight}, body ${bodyFont.family} ${bodyFont.weight} | buy-box prefix: ${prefixes.join(',') || '-'}`);
  console.log(`rendered ${args.buybox ? 'buy-box mock + ' : ''}${wanted.length} section(s): ${wanted.join(', ')} -> ${OUT} (${cssChunks.size} stylesheets, ${jsChunks.size} scripts)`);
  for (const a of missingAssets) warnings.add(`asset missing in theme assets/: ${a}`);
  for (const w of warnings) console.log('warn:', w);
  for (const e of errors) console.error('ERROR:', e);
  if (args.shot) shoot();
  process.exit(errors.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });

// ───────────────────────────── Screenshots (--shot) ─────────────────────────────
function findBrowser() {
  if (args.browser && args.browser !== true) return args.browser;
  const c = process.platform === 'win32'
    ? ['C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', 'C:/Program Files/Microsoft/Edge/Application/msedge.exe', 'C:/Program Files/Google/Chrome/Application/chrome.exe', path.join(process.env.LOCALAPPDATA || '', 'Google/Chrome/Application/chrome.exe')]
    : process.platform === 'darwin'
      ? ['/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
      : ['/usr/bin/microsoft-edge', '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'];
  return c.find(exists);
}
function shoot() {
  const exe = findBrowser();
  if (!exe) { console.error('no Edge/Chrome found for --shot (pass --browser PATH)'); return; }
  const profile = path.join(os.tmpdir(), 'render-sections-profile'); // own profile: avoids locks with the operator's open browser
  const base = ['--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--allow-file-access-from-files',
    '--disable-web-security', `--user-data-dir=${profile}`, '--force-device-scale-factor=1', '--virtual-time-budget=8000'];
  const run = (extra, url) => spawnSync(exe, [...base, ...extra, url], { encoding: 'utf8', timeout: 120000, maxBuffer: 64 * 1024 * 1024 });
  const measure = (url, width) => {
    const r = run([`--window-size=${width},1000`, '--dump-dom'], url);
    const m = (r.stdout || '').match(/data-qa-height="(\d+)"/);
    return m ? Math.min(Number(m[1]) + 20, 16000) : 9000;
  };
  const stem = OUT.replace(/\.html?$/i, '');
  const W = Number(args.width) || 1280;
  const hD = measure(fileUrl(OUT), W);
  run([`--window-size=${W},${hD}`, `--screenshot=${stem}-desktop.png`], fileUrl(OUT));
  // Mobile: 390px iframe (headless windows have a ~500px minimum width); measured from inside the iframe.
  const wrap = `${stem}-mobile-wrap.html`;
  const wrapHtml = (h) => `<!doctype html><html data-qa-height="0"><body style="margin:0;background:#fff"><iframe id="f" src="${fileUrl(OUT)}" style="width:390px;height:${h}px;border:0;display:block"></iframe>
<script>addEventListener('load',function(){setTimeout(function(){try{var d=document.getElementById('f').contentDocument;document.documentElement.setAttribute('data-qa-height',Math.ceil(d.documentElement.scrollHeight))}catch(e){}},400)});</script></body></html>`;
  fs.writeFileSync(wrap, wrapHtml(1200));
  const hM = measure(fileUrl(wrap), 500);
  fs.writeFileSync(wrap, wrapHtml(hM));
  run([`--window-size=500,${hM}`, `--screenshot=${stem}-mobile.png`], fileUrl(wrap));
  console.log(`screenshots: ${stem}-desktop.png (${W}x${hD}), ${stem}-mobile.png (390 wide in a 500px window, height ${hM})`);
}
