const states = new Map();

const getState = (key) => states.get(key)
const setState = (key, newValue) => {
  if (!states.has(key)) states.set(key, newValue)
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
  connectedCallback() {
    this.key = this.getAttribute('key')
    setState(this.key, this.getAttribute('value'))
  }
  disconnectedCallback() {
    states.delete(this.key)
  }
}
window.addEventListener('state-update', (event) => {
  const { key, value } = event.detail
  document.querySelectorAll(`[data-state="${key}"]`).forEach(el => {
    const target = el.dataset.at || 'textContent'
    if (el[target] != value)
      el[target] = value;
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

    const elseElement = this.querySelector(`[slot="else"]`);

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

window.customElements.define('s-def', StateDef)
window.customElements.define('s-if', StateIf)
