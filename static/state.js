const states = new Map();

const getState = (key) => states.get(key);

const setState = (key, newValue) => {
  if (!states.has(key)) {
    throw new Error(`Estado '${key}' não foi definido. Utilize <app-state name="${key}"> primeiro.`);
  }
  const oldValue = states.get(key);
  if (oldValue !== newValue) {
    states.set(key, newValue);
    window.dispatchEvent(new CustomEvent('state:update', {
      detail: {
        key,
        oldValue,
        newValue,
      },
      composed: true,
      bubbles: true,
    }));
  }
};
class StateDef extends HTMLElement {
  static observedAttributes = ['value'];
  constructor() {
    super();
    this.attachShadow({ mode: 'open' })
    this.style.display = 'none'
    this.name = this.getAttribute('name');
    states.set(this.name, undefined);
  }
  disconnectedCallback() {
    states.delete(this.name);
  }
  attributeChangedCallback(name, oldValue, newValue) {
    setState(this.name, newValue);
  }
}
const updateElement = (el, key, value) => {
  const target = el.dataset.at || 'textContent';
  if (target in el) {
    el[target] = value;
  } else {
    el.setAttribute(target, String(value));
  }
};

window.addEventListener('state:update', ({ detail }) => {
  const { key, newValue } = detail;
  const targets = document.querySelectorAll(`[data-state="${key}"], [data-state*=",${key},"], [data-state^="${key},"], [data-state$=",${key}"]`);
  targets.forEach(el => updateElement(el, key, newValue));
});
window.customElements.define('app-state', StateDef)
