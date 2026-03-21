const states = new Map();
const stateAt = new Map();

const ensureStateExists = (key) => {
  if (!states.has(key)) {
    throw new Error(`Estado '${key}' não foi definido. Utilize <app-state name="${key}"> primeiro.`);
  }
};

const getState = (key) => states.get(key);

const setState = (key, newValue) => {
  ensureStateExists(key);
  const oldValue = states.get(key);
  if (oldValue !== newValue) {
    states.set(key, newValue);
    window.dispatchEvent(new CustomEvent('state-update', {
      detail: { key, value: newValue },
      composed: true,
      bubbles: true,
    }));
  }
};
class StateDef extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' })
    this.style.display = 'none'
  }

  connectedCallback() {
    this.name = this.getAttribute('name');
    const at = this.getAttribute("at");
    if (!this.name) return;
    if (at) stateAt.set(this.name, at);
    if (!states.has(this.name)) {
      states.set(this.name, undefined);
    }
    if (this.hasAttribute('value')) {
      const initialValue = this.getAttribute('value');
      setState(this.name, initialValue);
    }
  }

  disconnectedCallback() {
    states.delete(this.name);
    stateAt.delete(this.name);
  }

  static observedAttributes = ['value'];

  attributeChangedCallback(name, oldValue, newValue) {
    if (this.name && oldValue !== newValue) {
      setState(this.name, newValue);
    }
  }
}
const updateElement = (el, key, value) => {
  let displayValue = value;

  if (el.dataset.then) {
    try {
      const transformFn = new Function('it', `return (${el.dataset.then})(it)`);
      displayValue = transformFn.call(el, value);
    } catch (e) {
      return console.error(`Erro no data-then [${key}]:`, e);
    }
  }
  const target = el.dataset.at || stateAt.get(key) || 'textContent';
  if (target in el) {
    if (el[target] !== displayValue) el[target] = displayValue;
  } else {
    const strValue = String(displayValue);
    if (el.getAttribute(target) !== strValue) el.setAttribute(target, strValue);
  }
};

window.addEventListener('state-update', ({ detail }) => {
  const { key, value } = detail;
  if (!key) return;

  const targets = document.querySelectorAll(`[data-state*="${key}"]`);
  targets.forEach(el => updateElement(el, key, value));
});
window.customElements.define('app-state', StateDef)

