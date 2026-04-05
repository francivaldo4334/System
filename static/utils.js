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
        const child = buildChild?.(it)
        if (child) frag.appendChild(child)
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

function toastError(message) {
  const newToastId = id_app_toast.childElementCount + 1
  const div = document.createElement("div")
  div.classList.add("alert")
  div.classList.add("alert-error")
  div.setAttribute("rule", "alert")
  div.textContent = message
  div.id = `id_toast_error_${newToastId}`
  setTimeout(() => {
    document.getElementById(`id_toast_error_${newToastId}`).remove()
  }, 3000)
  id_app_toast.appendChild(div)
}
