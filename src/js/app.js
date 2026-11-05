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
  if (player) {
    var btn = player.querySelector(".player__play");
    if (btn) {
      btn.addEventListener("click", function () {
        var src = btn.getAttribute("data-src");
        if (!src) return;
        var title = btn.getAttribute("data-title") || "game";
        var frame = document.createElement("iframe");
        frame.src = src;
        frame.title = "Play " + title + " free online";
        frame.setAttribute("allow", "autoplay; fullscreen; gamepad; pointer-lock");
        frame.setAttribute("allowfullscreen", "");
        player.innerHTML = "";
        player.appendChild(frame);
        frame.focus();
      });
    }
  }

  /* ---------- Search ---------- */
  var box = document.querySelector("[data-results]");
  if (!box) return;

  var hint = document.querySelector("[data-hint]");
  var input = document.getElementById("q");
  // A ?q= from the nav search or a shared link must render on load, not only
  // after the visitor types another character.
  var initial = new URLSearchParams(window.location.search).get("q") || "";
  if (input && initial) input.value = initial;
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
