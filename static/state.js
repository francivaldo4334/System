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
  constructor(){
    super();
    const name = this.getAttribute('name')
    const at = this.getAttribute("at")
    if (at) stateAt.set(name, at)
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

class StateIf extends HTMLElement {
  constructor() {
    super();
    this.trigger = this.trigger.bind(this);
    this.template = "";
    this.state = "";
  }

  connectedCallback() {
    debugger
    this.state = this.getAttribute("state");

    const elseElement = this.querySelector(`s-else`);

    this.templateDefault = elseElement ? elseElement.innerHTML : "";

    if (elseElement) elseElement.remove();

    this.template = this.innerHTML;
    this.innerHTML = ""

    const when = this.getAttribute('when');

    try {
      this.check = new Function('it', `return ${when};`);
    } catch (e) {
      console.error("Invalid condition expression:", when);
      this.check = (v) => false;
    }

    window.addEventListener('state-update', this.trigger);

    const initialState = getState(this.state);
    this.render(initialState);
  }

  disconnectedCallback() {
    window.removeEventListener('state-update', this.trigger);
  }

  render(value) {
    try {
      if (this.check(value) && this.innerHTML !== this.template) {
        this.innerHTML = this.template;
      } else {
        this.innerHTML = this.templateDefault || "";
      }
    } catch (e) {
      console.warn("Error evaluating condition with value:", value, e);
    }
  }

  trigger(event) {
    const { key, value } = event.detail
    if (key === this.state) {
      this.render(value)
    }
  }
}

window.customElements.define('app-state', StateDef)
window.customElements.define('app-if', StateIf)
