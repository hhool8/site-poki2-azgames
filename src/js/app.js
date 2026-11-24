/* AZ Games — client behaviour: nav toggle, click-to-play player, search. */
(function () {
  "use strict";

  /* ---------- Mobile navigation ---------- */
  var toggle = document.getElementById("nav-toggle");
  var links = document.getElementById("nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      toggle.classList.toggle("open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      document.body.classList.toggle("nav-open", open);
    });
  }

  /* ---------- Click-to-play ----------
     The iframe is only created on click: 291 game pages each pulling a third
     party embed on load would mean a third-party ad stack running before the
     visitor asked for the game. */
  var player = document.getElementById("player");
  var frame = null;
  if (player) {
    var btn = player.querySelector(".player__play");
    if (btn) {
      btn.addEventListener("click", function () {
        var src = btn.getAttribute("data-src");
        if (!src) return;
        var title = btn.getAttribute("data-title") || "game";
        var stage = player.querySelector(".player__stage");
        var fallback = player.querySelector(".player__fallback");
        frame = document.createElement("iframe");
        frame.src = src;
        frame.title = "Play " + title + " free online";
        frame.setAttribute("allow", "autoplay; fullscreen; gamepad; pointer-lock");
        frame.setAttribute("allowfullscreen", "");
        if (fallback && fallback.parentNode) fallback.parentNode.removeChild(fallback);
        btn.parentNode.removeChild(btn);
        stage.appendChild(frame);
        frame.focus();
      });
    }
  }

  /* ---------- Game toolbar (same behaviour set as poki2.online) ----------
     Bound inside this handler on purpose: top-level DOM lookups run before
     DOMContentLoaded and silently return null for nodes defined later. */
  (function () {
    var likeBtn = document.getElementById("tb-like");
    if (!likeBtn) return;
    var favBtn = document.getElementById("tb-fav");
    var shareBtn = document.getElementById("tb-share");
    var xBtn = document.getElementById("tb-x");
    var fbBtn = document.getElementById("tb-facebook");
    var reportBtn = document.getElementById("tb-report");
    var resetBtn = document.getElementById("tb-reset");
    var expandBtn = document.getElementById("tb-expand");
    var fsBtn = document.getElementById("tb-fullscreen");
    var countEl = document.getElementById("tb-like-count");
    var slug = likeBtn.getAttribute("data-slug") || "";
    var EXPAND_PATH = '<path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/>';
    var COLLAPSE_PATH = '<path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3"/>';
    var FS_PATH = '<polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/>';
    var FS_EXIT_PATH = '<polyline points="4 14 10 14 10 20"/><polyline points="20 10 14 10 14 4"/><line x1="10" y1="14" x2="21" y2="3"/><line x1="3" y1="21" x2="14" y2="10"/>';

    /* Deterministic base count so the number is stable without a backend. */
    function hashSlug(s) {
      var h = 5381;
      for (var i = 0; i < s.length; i++) h = ((h * 33) ^ s.charCodeAt(i)) >>> 0;
      return h;
    }
    var BASE_LIKES = 100 + hashSlug(slug) % 800;

    function refocus() { if (frame) frame.focus(); }

    /* ----- Like ----- */
    var liked = localStorage.getItem("like_" + slug) === "1";
    function refreshLike() {
      countEl.textContent = BASE_LIKES + (liked ? 1 : 0);
      likeBtn.classList.toggle("tb-liked", liked);
      likeBtn.setAttribute("aria-pressed", liked ? "true" : "false");
    }
    refreshLike();
    likeBtn.addEventListener("click", function () {
      liked = !liked;
      localStorage.setItem("like_" + slug, liked ? "1" : "0");
      refreshLike();
      refocus();
    });

    /* ----- Favorite ----- */
    var favd = localStorage.getItem("fav_" + slug) === "1";
    function refreshFav() {
      favBtn.classList.toggle("tb-favorited", favd);
      favBtn.setAttribute("aria-pressed", favd ? "true" : "false");
    }
    refreshFav();
    favBtn.addEventListener("click", function () {
      favd = !favd;
      localStorage.setItem("fav_" + slug, favd ? "1" : "0");
      refreshFav();
    });

    /* ----- Share ----- */
    shareBtn.addEventListener("click", function () {
      var url = window.location.href;
      if (navigator.share) {
        navigator.share({ title: document.title, text: "Play " + document.title + " free online", url: url })
          .catch(function (e) { if (e && e.name !== "AbortError") window.prompt("Copy this game link:", url); })
          .then(refocus);
        return;
      }
      if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(function () {
          shareBtn.setAttribute("title", "Link copied");
          setTimeout(function () { shareBtn.setAttribute("title", "Share"); }, 1600);
          refocus();
        }).catch(function () { window.prompt("Copy this game link:", url); });
      } else {
        window.prompt("Copy this game link:", url);
      }
    });

    function openShare(url) {
      window.open(url, "_blank", "noopener,noreferrer,width=640,height=520");
      refocus();
    }
    if (xBtn) xBtn.addEventListener("click", function () {
      openShare("https://x.com/intent/post?text=" + encodeURIComponent("Play " + document.title + " free online") +
                "&url=" + encodeURIComponent(window.location.href));
    });
    if (fbBtn) fbBtn.addEventListener("click", function () {
      openShare("https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(window.location.href));
    });

    /* ----- Report ----- */
    reportBtn.addEventListener("click", function () {
      window.open("/contact?game=" + encodeURIComponent(slug) + "&issue=unavailable", "_blank", "noopener");
    });

    /* ----- Reset: recreate the iframe rather than reload the page ----- */
    resetBtn.addEventListener("click", function () {
      if (!frame) return;
      var src = frame.getAttribute("src");
      var parent = frame.parentNode;
      parent.removeChild(frame);
      frame = document.createElement("iframe");
      frame.src = src;
      frame.title = "Play " + (likeBtn.getAttribute("data-slug") || "game") + " free online";
      frame.setAttribute("allow", "autoplay; fullscreen; gamepad; pointer-lock");
      frame.setAttribute("allowfullscreen", "");
      parent.appendChild(frame);
      setTimeout(refocus, 300);
    });

    /* ----- In-page expand (theater) ----- */
    var theater = false;
    function setTheater(on) {
      theater = on;
      player.classList.toggle("theater-mode", on);
      document.body.style.overflow = on ? "hidden" : "";
      expandBtn.querySelector("svg").innerHTML = on ? COLLAPSE_PATH : EXPAND_PATH;
      expandBtn.setAttribute("aria-label", on ? "Exit expand" : "Expand in page");
      setTimeout(refocus, 200);
    }
    expandBtn.addEventListener("click", function () { setTheater(!theater); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && theater) setTheater(false);
    });

    /* ----- Fullscreen: request on the iframe so the game is not resized ----- */
    function reqFS() {
      var el = frame || player.querySelector(".player__stage");
      (el.requestFullscreen || el.webkitRequestFullscreen || function () {}).call(el);
    }
    fsBtn.addEventListener("click", function () {
      if (document.fullscreenElement) document.exitFullscreen();
      else reqFS();
    });
    document.addEventListener("fullscreenchange", function () {
      var full = !!document.fullscreenElement;
      fsBtn.querySelector("svg").innerHTML = full ? FS_EXIT_PATH : FS_PATH;
      fsBtn.setAttribute("aria-label", full ? "Exit fullscreen" : "Fullscreen");
      if (!full) setTimeout(refocus, 200);
    });
  })();

  /* ---------- Search ---------- */
  var box = document.querySelector("[data-results]");
  if (!box) return;

  var hint = document.querySelector("[data-hint]");
  var input = document.getElementById("q");
  // A ?q= from the nav search or a shared link must render on load, not only
  // after the visitor types another character.
  var initial = new URLSearchParams(window.location.search).get("q") || "";
  if (input && initial) input.value = initial;
  var index = null;

  function card(g) {
    return (
      '<a class="featured-card" href="/play/' + g.s + '/">' +
      '<img src="/img/game/' + g.s + '.webp" alt="' + g.t.replace(/"/g, "&quot;") + '" width="400" height="400" loading="lazy">' +
      '<span class="featured-card-label">' + g.t + "</span>" +
      '<span class="featured-card-src">' + g.c + "</span></a>"
    );
  }

  function render(q) {
    q = (q || "").trim().toLowerCase();
    if (!index) return;
    if (!q) {
      box.innerHTML = index.slice(0, 24).map(card).join("");
      if (hint) hint.textContent = "Showing 24 of " + index.length + " games. Start typing to narrow it down.";
      return;
    }
    var terms = q.split(/\s+/);
    var hits = index.filter(function (g) {
      var hay = g.n;
      return terms.every(function (t) { return hay.indexOf(t) !== -1; });
    });
    box.innerHTML = hits.slice(0, 60).map(card).join("");
    if (hint) {
      hint.textContent = hits.length
        ? hits.length + (hits.length === 1 ? " game matches “" : " games match “") + q + "”"
        : "No game matches “" + q + "”. Try a shorter word.";
    }
  }

  fetch("/search-index.json")
    .then(function (r) { return r.json(); })
    .then(function (data) {
      index = data;
      render(input ? (input.value || initial) : initial);
      if (input) {
        var timer;
        input.addEventListener("input", function () {
          clearTimeout(timer);
          timer = setTimeout(function () { render(input.value); }, 90);
        });
      }
    })
    .catch(function () {
      if (hint) hint.textContent = "Search is unavailable right now — browse /games/ instead.";
    });
})();
