/* Pages détail : apparition des photos au défilement + visionneuse */
(() => {
  const tiles = [...document.querySelectorAll(".tile")];
  const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!calm && "IntersectionObserver" in window) {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
    }), { rootMargin: "0px 0px -6% 0px" });
    tiles.forEach((t, i) => { t.style.transitionDelay = `${(i % 3) * 0.08}s`; io.observe(t); });
  } else tiles.forEach(t => t.classList.add("in"));

  const lb = document.getElementById("lb"), img = document.getElementById("lbi");
  let i = 0;
  const pad = n => String(n).padStart(2, "0");
  const show = n => {
    i = (n + tiles.length) % tiles.length;
    img.style.opacity = 0;
    img.onload = () => { img.style.opacity = 1; };
    img.src = tiles[i].href; img.alt = tiles[i].dataset.alt || "";
    document.getElementById("lbc").textContent = `${pad(i + 1)} / ${pad(tiles.length)}`;
    document.getElementById("lbt").textContent = tiles[i].dataset.alt || "";
  };
  const close = () => { lb.classList.remove("open"); document.body.style.overflow = ""; };
  tiles.forEach((t, n) => t.addEventListener("click", e => {
    e.preventDefault(); show(n); lb.classList.add("open"); document.body.style.overflow = "hidden";
  }));
  document.getElementById("lbx").onclick = close;
  document.getElementById("lbp").onclick = () => show(i - 1);
  document.getElementById("lbn").onclick = () => show(i + 1);
  addEventListener("keydown", e => {
    if (!lb.classList.contains("open")) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowLeft") show(i - 1);
    if (e.key === "ArrowRight") show(i + 1);
  });
  let x0 = null;
  lb.addEventListener("touchstart", e => { x0 = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener("touchend", e => {
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 50) show(i + (dx < 0 ? 1 : -1));
    x0 = null;
  });
})();
