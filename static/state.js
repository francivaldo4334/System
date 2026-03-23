function createStateManager() {
  const states = new Map();
  return {
    remove: (name) => states.delete(name),
    create: (name, initialValue = null) => {
      if (!states.has(name)) {
        states.set(name, { value: initialValue, observers: [] });
      }
    },
    subscribe: (name, selector, attribute = 'textContent', transform = (v) => v) => {
      const state = states.get(name);
      if (!state) return;
      const elements = document.querySelectorAll(selector);
      elements.forEach(el => {
        state.observers.push({ el, at: attribute, transform });
        el[attribute] = transform(state.value, el);
      });
    },

    set: (name, newValue) => {
      const state = states.get(name);
      if (!state) return;
      state.value = newValue;
      state.observers = state.observers.forEach(obs => {
        const content = obs.transform(newValue, obs.el);
        if (obs.at !== null) obs.el[obs.at] = content;
      });
    }
  };
}
const $s = createStateManager()

class AppState extends HTMLElement {
  constructor() {
    super();
    this.style.display = 'none'
  }
  connectedCallback() {
    this.stateName = this.getAttribute('name');
    const selector = this.getAttribute('selector');
    const attr = this.getAttribute('attribute');
    if (!this.stateName) return console.error("AppState: Atributo 'name' é obrigatório.");
    $s.create(this.stateName);
    if (selector) $s.addObserver(this.stateName, selector, attr);
  }
  disconnectedCallback() {
    $s.remove(this.stateName);
  }
}

customElements.define('app-state', AppState);
