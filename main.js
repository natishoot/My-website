(() => {
  const PAGE = 12;
  const photos = window.PHOTOS || [];
  const series = window.SERIES || [];

  // Nav : fond au scroll + menu mobile
  const nav = document.querySelector(".nav");
  const menu = document.getElementById("menu");
  const burger = document.querySelector(".burger");
  const onScroll = () => nav.classList.toggle("scrolled", scrollY > 40);
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  burger.addEventListener("click", () => {
    const open = burger.getAttribute("aria-expanded") !== "true";
    burger.setAttribute("aria-expanded", open);
    menu.classList.toggle("open", open);
  });
  menu.addEventListener("click", e => {
    if (e.target.tagName === "A") { burger.setAttribute("aria-expanded", "false"); menu.classList.remove("open"); }
  });

  // Séries
  document.getElementById("series-list").innerHTML = series.map(s =>
    `<a class="serie" href="${s.url}" target="_blank" rel="noopener"><strong>${s.name}</strong><span>${s.year} ↗</span></a>`
  ).join("");
  document.getElementById("stat-series").textContent = series.length;

  // Filtres + galerie
  const cats = ["Tout", ...new Set(photos.map(p => p.cat))];
  const filters = document.getElementById("filters");
  const gallery = document.getElementById("gallery");
  const more = document.getElementById("more");
  let current = "Tout", shown = PAGE, list = photos;

  filters.innerHTML = cats.map(c =>
    `<button role="tab" aria-selected="${c === "Tout"}" data-cat="${c}">${c}</button>`).join("");
  if (cats.length <= 2) filters.hidden = true;
  filters.addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    current = b.dataset.cat; shown = PAGE;
    filters.querySelectorAll("button").forEach(x => x.setAttribute("aria-selected", x === b));
    render();
  });
  more.addEventListener("click", () => { shown += PAGE; render(); });

  function render() {
    list = current === "Tout" ? photos : photos.filter(p => p.cat === current);
    if (!list.length) {
      gallery.innerHTML = `<p class="empty">Les photos arrivent bientôt. En attendant, découvrez les séries ci-dessus.</p>`;
      more.hidden = true; return;
    }
    gallery.innerHTML = list.slice(0, shown).map((p, i) =>
      `<button class="tile" data-i="${i}" aria-label="Agrandir : ${p.alt || p.cat}">
         <img src="${p.thumb || p.src}" alt="${p.alt || ""}" loading="${i < 4 ? "eager" : "lazy"}" decoding="async">
         <span class="label">${p.cat}</span>
       </button>`).join("");
    gallery.querySelectorAll("img").forEach(img => {
      if (img.complete) img.classList.add("loaded");
      else img.addEventListener("load", () => img.classList.add("loaded"), { once: true });
    });
    more.hidden = shown >= list.length;
  }
  render();

  // Visionneuse
  const lb = document.getElementById("lightbox");
  const lbImg = lb.querySelector("img");
  let idx = 0;
  const pad = n => String(n).padStart(2, "0");
  function show(i) {
    idx = (i + list.length) % list.length;
    const p = list[idx];
    lbImg.src = p.src; lbImg.alt = p.alt || "";
    lb.querySelector(".lb-cat").textContent = p.cat;
    lb.querySelector(".lb-count").textContent = `${pad(idx + 1)} / ${pad(list.length)}`;
  }
  gallery.addEventListener("click", e => {
    const t = e.target.closest(".tile"); if (!t) return;
    show(+t.dataset.i); lb.showModal();
  });
  lb.querySelector(".lb-close").onclick = () => lb.close();
  lb.querySelector(".lb-prev").onclick = () => show(idx - 1);
  lb.querySelector(".lb-next").onclick = () => show(idx + 1);
  lb.addEventListener("keydown", e => {
    if (e.key === "ArrowLeft") show(idx - 1);
    if (e.key === "ArrowRight") show(idx + 1);
  });
  lb.addEventListener("click", e => { if (e.target === lb) lb.close(); });
  // Swipe mobile
  let x0 = null;
  lb.addEventListener("touchstart", e => { x0 = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener("touchend", e => {
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 50) show(idx + (dx < 0 ? 1 : -1));
    x0 = null;
  });

  // Pré-sélection du type de séance depuis les cartes prestations
  document.querySelectorAll("[data-service]").forEach(a => a.addEventListener("click", () => {
    const r = document.querySelector(`input[name="service"][value="${a.dataset.service}"]`);
    if (r) r.checked = true;
  }));

  document.getElementById("year").textContent = new Date().getFullYear();
})();
