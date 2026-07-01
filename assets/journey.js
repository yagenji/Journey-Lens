/* JOURNEY LENS — 物語ページ用 共有JS（ライトボックス／遅延表示／動画） */
(function () {
  function el(t, c, h) { var e = document.createElement(t); if (c) e.className = c; if (h != null) e.innerHTML = h; return e; }
  function ytId(u) { var m = (u || "").match(/(?:youtube\.com\/(?:watch\?v=|shorts\/|embed\/)|youtu\.be\/)([\w-]{11})/); return m ? m[1] : ""; }
  function parseVideo(u) {
    if (!u) return null;
    var id = ytId(u);
    if (id) return { kind: "embed", embed: "https://www.youtube.com/embed/" + id + "?autoplay=1&rel=0&playsinline=1" };
    return { kind: "file", src: u };
  }
  var lb = document.getElementById("lightbox");
  var lbSlot = document.getElementById("lbSlot");
  var lbCap = document.getElementById("lbCap");

  function openLb(fig) {
    if (!lb) return;
    lbSlot.innerHTML = "";
    var v = fig.getAttribute("data-video");
    if (v) {
      var info = parseVideo(v);
      if (info && info.kind === "embed") {
        var f = el("iframe"); f.src = info.embed; f.allow = "autoplay; fullscreen; encrypted-media"; f.allowFullscreen = true; lbSlot.appendChild(f);
      } else {
        var vid = el("video"); vid.controls = true; vid.loop = true; vid.autoplay = true; vid.playsInline = true; vid.setAttribute("playsinline", "");
        var poster = fig.getAttribute("data-poster"); if (poster) vid.poster = poster;
        var s = el("source"); s.src = info ? info.src : v; vid.appendChild(s); lbSlot.appendChild(vid);
      }
    } else {
      var im = fig.querySelector("img");
      if (im) { var i = el("img"); i.src = im.src; i.alt = im.alt || ""; lbSlot.appendChild(i); }
    }
    lbCap.textContent = fig.getAttribute("data-cap") || "";
    lb.classList.add("open");
  }
  function closeLb() { if (!lb) return; lb.classList.remove("open"); lbSlot.innerHTML = ""; }

  var closeBtn = document.getElementById("lbClose");
  if (closeBtn) closeBtn.addEventListener("click", closeLb);
  if (lb) lb.addEventListener("click", function (e) { if (e.target === lb) closeLb(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeLb(); });

  // プレート: クリック/Enterで拡大
  document.querySelectorAll(".plate").forEach(function (f) {
    f.addEventListener("click", function () { openLb(f); });
    f.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openLb(f); } });
  });

  // 画像の遅延フェードイン
  document.querySelectorAll("img.ph").forEach(function (img) {
    if (img.complete && img.naturalWidth) img.classList.add("on");
    else {
      img.addEventListener("load", function () { img.classList.add("on"); }, { once: true });
      img.addEventListener("error", function () { img.classList.add("on"); }, { once: true });
    }
  });
  setTimeout(function () { document.querySelectorAll("img.ph:not(.on)").forEach(function (i) { i.classList.add("on"); }); }, 2500);

  // 埋め込みでない動画(ファイル)の自動再生（画面内のとき）
  if ("IntersectionObserver" in window) {
    var vio = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        var v = en.target;
        if (en.isIntersecting) { var p = v.play && v.play(); if (p && p.catch) p.catch(function () {}); }
        else { v.pause && v.pause(); }
      });
    }, { threshold: .25 });
    document.querySelectorAll(".plate video").forEach(function (v) { vio.observe(v); });
  }
  // モバイル: メニュー開閉
  var tgl = document.getElementById("navToggle"), links = document.getElementById("navLinks");
  if (tgl && links) {
    tgl.addEventListener("click", function () {
      var o = links.classList.toggle("open");
      tgl.setAttribute("aria-expanded", o);
      tgl.textContent = o ? "閉じる ×" : "メニュー ＋";
    });
    links.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () { links.classList.remove("open"); tgl.textContent = "メニュー ＋"; });
    });
  }
})();
