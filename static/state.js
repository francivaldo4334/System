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

class StateView extends HTMLElement {
  constructor() {
    super();
    this.update = this.update.bind(this);
  }
  connectedCallback() {
    this.keys = this.getAttribute('keys')?.split(',').map(k => k.trim()) || [];
    window.addEventListener('state-update', this.update)
    this.keys.forEach(k => this.render(k))
  }
  disconnectedCallback() {
    window.removeEventListener('state-update', this.update)
  }
  update(event) {
    const { key } = event.detail;
    if (this.keys.includes(key)) {
      this.render(key);
    }
  }
  render(key) {
    const value = getState(key)
    this.querySelectorAll(`[data-bind="${key}"]`).forEach(el => {
      const target = el.dataset.at || 'textContent'
      if (el[target] != value)
        el[target] = value;
      else
        el.setAttribute(target, value)
    })
  }
}

class StateIf extends HTMLElement {
  constructor() {
    super();
    this.trigger = this.trigger.bind(this);
    this.template = "";
    this.key = "";
  }

  connectedCallback() {
    this.key = this.getAttribute("key");
    this.template = this.innerHTML;
    this.innerHTML = "";

    const condition = this.getAttribute('check');

    try {
      this.check = new Function('v', `return ${condition};`);
    } catch (e) {
      console.error("Invalid condition expression:", condition);
      this.check = (v) => false;
    }

    window.addEventListener('state-update', this.trigger);
  }

  disconnectedCallback() {
    window.removeEventListener('state-update', this.trigger);
  }

  trigger(event) {
    if (event.detail && event.detail.key === this.key) {
      const value = event.detail.value;
      try {
        if (this.check(value)) {
          if (this.innerHTML !== this.template) {
            this.innerHTML = this.template;
          }
        } else {
          this.innerHTML = ""; // Esconde o conteúdo se a condição falhar
        }
      } catch (e) {
        console.warn("Error evaluating condition with value:", value, e);
      }
    }
  }
}
window.customElements.define('s-def', StateDef)
window.customElements.define('s-view', StateView)
window.customElements.define('s-if', StateIf)
