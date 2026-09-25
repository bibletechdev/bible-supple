/* みことばカード ─ 描画と3D演出（トレーディングカード風）
   MC.render(card)            … カード要素を作る（verses.js / icons.js が先に読み込まれている前提）
   MC.fit(cardEl)             … 本文がはみ出さないよう文字サイズを詰める
   MC.live(cardEl, opts)      … 傾き・光沢・裏返しを有効にする。戻り値 {flip(), setFlipped(b), destroy()}
      opts.hover / drag / tapFlip / gyro / idle
   ばねの定数は参考記事（ポケポケUI再現）の値 mass 1 / tension 170 / friction 26 を使う。 */
(function (global) {
  const RARITY = {
    d1: { label: "◆", name: "コモン" },
    d2: { label: "◆◆", name: "アンコモン" },
    d3: { label: "◆◆◆", name: "レア" },
    d4: { label: "◆◆◆◆", name: "ダブルレア" },
    s1: { label: "☆", name: "スペシャル", full: true },
    s2: { label: "☆☆", name: "スーパースペシャル", full: true },
    cr: { label: "👑", name: "クラウン", full: true },
    hr: { label: "SSSSSSSSSSSSSSS", name: "ハイパーレア", full: true },
  };
  const HR = "SSSSSSSSSSSSSSS";
  const TOTAL = () => VERSES.length;
  const pad = (n) => String(n).padStart(3, "0");
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const svg = (inner, vb = "0 0 24 24") => `<svg viewBox="${vb}" aria-hidden="true">${inner}</svg>`;

  // エネルギーの玉
  const orb = (t, cls = "") => {
    const T = TYPES[t] || TYPES.C;
    return `<i class="orb t-${t} ${cls}" style="--o1:${T.c1};--o2:${T.c2}" title="${T.name}">${svg(ICONS[T.icon] || "")}</i>`;
  };

  const EMBLEM = svg(
    '<g fill="none" stroke="currentColor" stroke-linecap="round">' +
      '<circle cx="50" cy="50" r="44" stroke-width="1.5"/><circle cx="50" cy="50" r="38" stroke-width=".8" stroke-dasharray="1 3"/>' +
      '<path d="M50 18v64M34 38h32" stroke-width="5"/>' +
      Array.from({ length: 16 }, (_, i) => {
        const a = (i / 16) * Math.PI * 2, r1 = 46.5, r2 = i % 2 ? 49 : 52;
        return `<path d="M${50 + Math.cos(a) * r1} ${50 + Math.sin(a) * r1}L${50 + Math.cos(a) * r2} ${50 + Math.sin(a) * r2}" stroke-width="1.2"/>`;
      }).join("") + "</g>",
    "-4 -4 108 108"
  );

  // 同じカードはいつも同じ位置に光の粒が出るよう、番号から疑似乱数を作る
  function rand(seed) { let s = seed * 9301 + 49297; return () => ((s = (s * 9301 + 49297) % 233280) / 233280); }

  function rarityHTML(r) {
    if (r === "hr") return `<span class="hr">${HR}</span>`;
    if (r === "cr") return "<span>👑</span>";
    if (r[0] === "s") return '<span class="star">☆</span>'.repeat(+r[1]);
    return "<span>◆</span>".repeat(+r[1]);
  }

  // 絵文字を「主役」と「添え」に分ける（ZWJ や異体字セレクタを含む絵文字も1つとして扱う）
  function splitEmoji(s) {
    if (global.Intl && Intl.Segmenter) return [...new Intl.Segmenter("ja", { granularity: "grapheme" }).segment(s)].map((x) => x.segment);
    return [...s];
  }

  // 十字架は絵文字だと環境によって紫の四角になるので、金色の十字架を描く
  const CROSS = '<svg viewBox="-2 -2 28 28" class="mc-crossart" aria-hidden="true"><defs><linearGradient id="mcg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fffbe6"/><stop offset=".45" stop-color="#ffd35a"/><stop offset="1" stop-color="#c8871a"/></linearGradient></defs><path d="M10.2 2h3.6v5.6h5.4v3.6h-5.4V22h-3.6V11.2H4.8V7.6h5.4z" fill="url(#mcg)" stroke="#fff8d8" stroke-width=".6" stroke-linejoin="round"/></svg>';
  const glyph = (e) => (e === "✝️" || e === "✝" ? CROSS : e);

  function artHTML(v) {
    if (v.img) return `<img src="${esc(v.img)}" alt="" loading="lazy" decoding="async">`;
    const rnd = rand(v.no);
    const [a, b] = splitEmoji(v.emoji || "✨");
    const motes = Array.from({ length: RARITY[v.rarity].full ? 18 : 8 }, () =>
      `<i style="left:${(rnd() * 92 + 4).toFixed(1)}%;top:${(rnd() * 80 + 6).toFixed(1)}%;animation-delay:${(rnd() * 3).toFixed(2)}s;transform:scale(${(0.5 + rnd()).toFixed(2)})"></i>`).join("");
    const emo = b ? `<div class="mc-emoji main">${glyph(a)}</div><div class="mc-emoji sub">${glyph(b)}</div>` : `<div class="mc-emoji solo">${glyph(a)}</div>`;
    return `<div class="mc-rays"></div><div class="mc-ground"></div>${emo}<div class="mc-motes">${motes}</div>`;
  }

  function nameClass(n) { return n.length > 8 ? " l3" : n.length > 5 ? " l2" : ""; }

  function personHTML(v) {
    const T = TYPES[v.type];
    const attacks = v.attacks.map((a) => `
      <div class="mc-atk">
        <span class="cost">${[...a.cost].map((c) => orb(c)).join("")}</span>
        <b>${esc(a.name)}</b>
        <span class="pw">${a.power ? esc(a.power) : ""}</span>
        ${a.text ? `<p>${esc(a.text)}</p>` : ""}
      </div>`).join("");
    const ab = v.ability ? `<div class="mc-ability"><span class="lb">特性</span><b>${esc(v.ability.name)}</b><p>${esc(v.ability.text)}</p></div>` : "";
    const weak = v.weak ? `${orb(v.weak)}<em>×2</em>` : "<em>なし</em>";
    const resist = v.resist ? `${orb(v.resist)}<em>−30</em>` : "<em>なし</em>";
    const retreat = v.retreat ? Array.from({ length: v.retreat }, () => orb("C")).join("") : "<em>0</em>";
    return `
      <div class="mc-head">
        <span class="mc-stage">${v.era}</span>
        <h3 class="mc-name${nameClass(v.name)}">${esc(v.name)}</h3>
        <span class="mc-hp"><small>HP</small><b>${esc(v.hp)}</b></span>
        ${orb(v.type, "big")}
      </div>
      <div class="mc-art">${artHTML(v)}<div class="mc-fx mc-holo"></div></div>
      <div class="mc-hrmark"><b>${HR}</b><span>HYPER RARE</span></div>
      <div class="mc-info">${esc(T.name)}タイプ ・ ${esc(v.ref)}</div>
      <div class="mc-lower">
        <div class="mc-body">${ab}${attacks}</div>
        <div class="mc-stats"><div>弱点 ${weak}</div><div>抵抗力 ${resist}</div><div>にげる ${retreat}</div></div>
        <p class="mc-flavor">${esc(v.text.replace(/ +/g, ""))}<cite>${esc(v.ref)}（口語訳）</cite></p>
        <div class="mc-foot"><span>みことばカード</span><span class="rr"><span class="mc-rar" title="${RARITY[v.rarity].name}">${rarityHTML(v.rarity)}</span><b>${pad(v.no)}/${TOTAL()}</b></span></div>
      </div>`;
  }

  function itemHTML(v) {
    return `
      <div class="mc-itemband"><span>アイテム</span><span>グッズ</span></div>
      <div class="mc-head"><h3 class="mc-name${nameClass(v.name)}">${esc(v.name)}</h3></div>
      <div class="mc-art">${artHTML(v)}<div class="mc-fx mc-holo"></div></div>
      <div class="mc-info">${esc(v.ref)}</div>
      <div class="mc-lower">
        <div class="mc-body">
          <div class="mc-effect"><p>${esc(v.effect)}</p></div>
          <p class="mc-rule">アイテムは、自分の番に何枚でも使える。</p>
        </div>
        <p class="mc-flavor">${esc(v.text.replace(/ +/g, ""))}<cite>${esc(v.ref)}（口語訳）</cite></p>
        <div class="mc-foot"><span>みことばカード</span><span class="rr"><span class="mc-rar" title="${RARITY[v.rarity].name}">${rarityHTML(v.rarity)}</span><b>${pad(v.no)}/${TOTAL()}</b></span></div>
      </div>`;
  }

  function render(v) {
    const r = RARITY[v.rarity];
    const T = TYPES[v.type] || TYPES.C;
    const el = document.createElement("div");
    el.className = "mc" + (r.full ? " is-full" : "");
    el.dataset.rarity = v.rarity;
    el.dataset.kind = v.kind;
    el.dataset.type = v.type || "";
    el.dataset.id = v.id;
    el.style.setProperty("--t1", T.c1);
    el.style.setProperty("--t2", T.c2);
    el.setAttribute("role", "img");
    el.setAttribute("aria-label", `${v.name}（${r.name}）　${v.text}　${v.ref}`);
    el.innerHTML = `
      <div class="mc-rot">
        <div class="mc-face mc-front">
          <div class="mc-frame">${v.kind === "item" ? itemHTML(v) : personHTML(v)}</div>
          <div class="mc-fx mc-holo"></div>
          <div class="mc-fx mc-sparkle"></div>
          <div class="mc-fx mc-glare"></div>
        </div>
        <div class="mc-face mc-back">
          <div class="mc-emblem">${EMBLEM}</div>
          <h4>${esc(v.name)}</h4>
          <p class="mc-one">${esc(v.desc)}</p>
          <span class="mc-bref">${esc(v.ref)}</span>
          <span class="mc-brand">MIKOTOBA CARD</span>
        </div>
      </div>`;
    return el;
  }

  // 本文がはみ出していたら、本文まわりの文字を少しずつ小さくする（--k を下げる）
  function fit(el) {
    const body = el.querySelector(".mc-body");
    const lower = el.classList.contains("is-full") ? el.querySelector(".mc-lower") : el.querySelector(".mc-frame");
    if (!body || !lower || !lower.clientHeight) return;
    const over = () => body.scrollHeight > body.clientHeight + 1 || lower.scrollHeight > lower.clientHeight + 1;
    let k = 1;
    el.style.setProperty("--k", "1");
    for (let i = 0; i < 20 && over() && k > 0.66; i++) { k -= 0.03; el.style.setProperty("--k", k.toFixed(2)); }
  }

  // ── ばね ──
  const K = { mass: 1, tension: 170, friction: 26 };
  function spring(x) { return { x, v: 0, t: x }; }
  function step(s, dt) {
    const f = -K.tension * (s.x - s.t) - K.friction * s.v;
    s.v += (f / K.mass) * dt;
    s.x += s.v * dt;
    return Math.abs(s.v) > 0.01 || Math.abs(s.x - s.t) > 0.01;
  }

  function live(el, opts = {}) {
    const S = { rx: spring(0), ry: spring(0), mx: spring(50), my: spring(50), act: spring(0), flip: spring(0) };
    let raf = 0, last = 0, flipped = false, pointer = null, gyro = null, g0 = null, dead = false;
    const MAX = 16; // 最大の傾き（度）

    el.classList.add("is-live");
    const apply = () => {
      el.style.setProperty("--rx", S.rx.x.toFixed(2) + "deg");
      el.style.setProperty("--ry", (S.ry.x + S.flip.x).toFixed(2) + "deg");
      el.style.setProperty("--mx", S.mx.x.toFixed(1) + "%");
      el.style.setProperty("--my", S.my.x.toFixed(1) + "%");
      el.style.setProperty("--act", Math.max(0, Math.min(1, S.act.x)).toFixed(3));
    };
    const loop = (now) => {
      const dt = Math.min(0.032, (now - (last || now)) / 1000) || 0.016;
      last = now;
      if (!pointer && !gyro && opts.idle) {
        const t = now / 1000;
        S.rx.t = Math.sin(t * 0.7) * 4;
        S.ry.t = Math.cos(t * 0.5) * 7;
        S.mx.t = 50 + Math.cos(t * 0.5) * 35;
        S.my.t = 50 + Math.sin(t * 0.7) * 30;
        S.act.t = 0.4;
      }
      let moving = false;
      for (const k in S) moving = step(S[k], dt) || moving;
      apply();
      raf = moving || opts.idle ? requestAnimationFrame(loop) : 0;
      if (!raf) last = 0;
    };
    const kick = () => { if (!raf && !dead) raf = requestAnimationFrame(loop); };

    const aim = (px, py, act = 1) => { // px,py: 0..1
      S.ry.t = (px - 0.5) * 2 * MAX;
      S.rx.t = -(py - 0.5) * 2 * MAX;
      S.mx.t = px * 100;
      S.my.t = py * 100;
      S.act.t = act;
      kick();
    };
    const rest = () => { S.rx.t = 0; S.ry.t = 0; S.mx.t = 50; S.my.t = 50; S.act.t = 0; kick(); };
    const rel = (e) => {
      const b = el.getBoundingClientRect();
      let px = (e.clientX - b.left) / b.width, py = (e.clientY - b.top) / b.height;
      if (flipped) px = 1 - px; // 裏返し中は左右が逆
      return [Math.max(0, Math.min(1, px)), Math.max(0, Math.min(1, py))];
    };

    const on = [];
    const listen = (t, ev, fn, o) => { t.addEventListener(ev, fn, o); on.push([t, ev, fn, o]); };

    if (opts.hover) {
      listen(el, "pointermove", (e) => { if (e.pointerType === "mouse") { pointer = e.pointerId; aim(...rel(e)); } });
      listen(el, "pointerleave", (e) => { if (e.pointerType === "mouse") { pointer = null; rest(); } });
    }
    if (opts.drag) {
      el.style.touchAction = "none";
      let down = null;
      listen(el, "pointerdown", (e) => { down = { x: e.clientX, y: e.clientY, t: performance.now() }; pointer = e.pointerId; el.setPointerCapture(e.pointerId); aim(...rel(e)); });
      listen(el, "pointermove", (e) => { if (pointer === e.pointerId || e.pointerType === "mouse") { aim(...rel(e)); } });
      const up = (e) => {
        if (down && opts.tapFlip && Math.hypot(e.clientX - down.x, e.clientY - down.y) < 8 && performance.now() - down.t < 350) api.flip();
        down = null;
        if (e.pointerType !== "mouse") { pointer = null; rest(); }
      };
      listen(el, "pointerup", up);
      listen(el, "pointercancel", up);
      listen(el, "pointerleave", (e) => { if (e.pointerType === "mouse") { pointer = null; rest(); } });
    }
    if (opts.gyro && "DeviceOrientationEvent" in global) {
      listen(global, "deviceorientation", (e) => {
        if (e.beta == null || pointer) return;
        if (!g0) g0 = { b: e.beta, g: e.gamma };
        const px = 0.5 + Math.max(-0.5, Math.min(0.5, (e.gamma - g0.g) / 40));
        const py = 0.5 + Math.max(-0.5, Math.min(0.5, (e.beta - g0.b) / 40));
        gyro = true;
        aim(flipped ? 1 - px : px, py, 0.75);
      });
    }

    const api = {
      flip() { api.setFlipped(!flipped); },
      setFlipped(b) { flipped = b; S.flip.t = b ? 180 : 0; kick(); el.classList.toggle("is-flipped", b); },
      get flipped() { return flipped; },
      destroy() { dead = true; cancelAnimationFrame(raf); on.forEach(([t, ev, fn, o]) => t.removeEventListener(ev, fn, o)); el.classList.remove("is-live"); },
    };
    apply();
    if (opts.idle) kick();
    return api;
  }

  // iPhone は傾きセンサーの利用に許可が必要（タップの中で呼ぶ）
  async function askGyro() {
    const D = global.DeviceOrientationEvent;
    if (D && typeof D.requestPermission === "function") {
      try { return (await D.requestPermission()) === "granted"; } catch { return false; }
    }
    return !!D;
  }

  global.MC = { render, fit, live, askGyro, RARITY, pad };
})(window);
