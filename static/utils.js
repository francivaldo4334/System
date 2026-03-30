function utilsManager() {
  function renderList(
    key,
    el,
    items,
    buildChild,
  ) {
    const rafId = `_${key}_raf_id`
    if (!window[rafId]) cancelAnimationFrame(window[rafId]);
    const render = () => {
      if (items.length === 0) {
        window[rafId] = null;
        return;
      }
      const chunk = items.splice(0, 10);
      const frag = document.createDocumentFragment();
      chunk.forEach(it => {
        const child = buildChild(it)
        frag.appendChild(child)
      })
      if (el) {
        el.appendChild(frag)
        window[rafId] = requestAnimationFrame(render)
      }
    }
    el.innerHTML = "";
    window[rafId] = requestAnimationFrame(render)
  }
  return {
    renderList,
  }
}
const $u = utilsManager()
