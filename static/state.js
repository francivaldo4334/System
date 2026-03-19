const states = new Map();
const stateAt = new Map();

const getState = (key) => states.get(key)
const setState = (key, newValue) => {
  const state = states.get(key);
  if (state !== newValue) {
    states.set(key, newValue)
    window.dispatchEvent(new CustomEvent('state-update', {
      detail: { key, value: newValue },
      composed: true,
      bubbles: true,
    }))
  }
}
class StateDef extends HTMLElement {
  constructor() {
    super();
    const name = this.getAttribute('name')
    const at = this.getAttribute("at")
    if (at) stateAt.set(name, at)
    if (states.has(name)) console.error(`Override state '${name}'.`)
  }
  connectedCallback() {
    this.name = this.getAttribute('name')
    setState(this.name, this.getAttribute('value'))
  }
  disconnectedCallback() {
    states.delete(this.name)
    stateAt.delete(this.name)
  }
  static observedAttributes = ['value']
  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue != newValue) {
      const name = this.getAttribute('name')
      setState(name, newValue)
    }
  }
}
window.addEventListener('state-update', (event) => {
  const { key, value } = event.detail
  if (!key) return;
  document.querySelectorAll(`[data-state*="${key}"]`).forEach(el => {
    const target = el.dataset.at || stateAt.get(key) || 'textContent'
    if (target in el && el[target] !== value) {
      el[target] = value;
    } else if (el.getAttribute(target) !== String(value)) {
      el.setAttribute(target, value);
    }
  })

})

window.customElements.define('app-state', StateDef)
