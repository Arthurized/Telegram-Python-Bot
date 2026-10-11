/* all.about.python — progressive enhancement only.
   Every page works with this file blocked: the nav is a plain list, the FAQ
   is a stack of native <details>, and code blocks are selectable text. */

(function () {
  "use strict";

  /* ---- Mobile navigation ------------------------------------------- */

  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("nav");

  if (toggle && nav) {
    toggle.hidden = false;
    toggle.addEventListener("click", function () {
      var open = nav.getAttribute("data-open") === "true";
      nav.setAttribute("data-open", String(!open));
      toggle.setAttribute("aria-expanded", String(!open));
    });

    // Close on escape, and when a link is followed.
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.getAttribute("data-open") === "true") {
        nav.setAttribute("data-open", "false");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A") {
        nav.setAttribute("data-open", "false");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* ---- Copy buttons on code samples -------------------------------- */

  document.querySelectorAll(".snippet").forEach(function (snippet) {
    var pre = snippet.querySelector("pre");
    var bar = snippet.querySelector(".snippet__bar");
    if (!pre || !bar || !navigator.clipboard) return;

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "copy";
    btn.textContent = "Copy";
    btn.setAttribute("aria-label", "Copy code to clipboard");

    btn.addEventListener("click", function () {
      // Strip REPL prompts and output so the paste is runnable.
      var clone = pre.cloneNode(true);
      clone.querySelectorAll(".pr, .ou").forEach(function (n) { n.remove(); });
      var text = clone.textContent.replace(/\n{3,}/g, "\n\n").trim();

      navigator.clipboard.writeText(text).then(function () {
        btn.textContent = "Copied";
        btn.setAttribute("data-done", "true");
        setTimeout(function () {
          btn.textContent = "Copy";
          btn.removeAttribute("data-done");
        }, 1600);
      }).catch(function () {
        btn.textContent = "Press Ctrl+C";
        var range = document.createRange();
        range.selectNodeContents(pre);
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
      });
    });

    bar.appendChild(btn);
  });

  /* ---- FAQ: expand all, collapse all, and deep links --------------- */

  // Page-wide: the questions are split across several .faq groups, so the
  // controls have to reach all of them, not just the first.
  var items = Array.prototype.slice.call(document.querySelectorAll(".qa"));

  if (items.length) {
    var controls = document.querySelector(".faq-controls");

    if (controls) {
      controls.hidden = false;

      controls.querySelectorAll("[data-action]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var open = btn.getAttribute("data-action") === "expand";
          items.forEach(function (d) { d.open = open; });
        });
      });
    }

    // Open the question named in the URL hash and scroll to it.
    var openFromHash = function () {
      var id = window.location.hash.slice(1);
      if (!id) return;
      var target = document.getElementById(id);
      if (target && target.classList.contains("qa")) {
        target.open = true;
        target.scrollIntoView({ block: "start" });
      }
    };
    openFromHash();
    window.addEventListener("hashchange", openFromHash);

    // Keep the address bar in step so a question can be linked directly.
    items.forEach(function (d) {
      d.addEventListener("toggle", function () {
        if (d.open && d.id) {
          history.replaceState(null, "", "#" + d.id);
        }
      });
    });
  }
})();
