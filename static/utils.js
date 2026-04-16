function utilsManager() {
  function renderList(
    key,
    el,
    items,
    buildChild,
    onFinished,
  ) {
    const rafId = `_${key}_raf_id`
    if (!window[rafId]) cancelAnimationFrame(window[rafId]);
    const render = () => {
      if (items.length === 0) {
        window[rafId] = null;
        onFinished?.()
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

  function getDataByForm(formElement){
    const formData = new FormData(formElement);
    const data = Object.fromEntries(Array.from(formData.keys()).map(key => {
        let value = formData.getAll(key);
        const field = formElement.elements[key];
        if (field.tagName !== 'SELECT' && !field.multiple && value.length === 1) value = value[0];
        return [key, value || undefined];
    }));
    return data
  }
  return {
    renderList,
    getDataByForm,
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
