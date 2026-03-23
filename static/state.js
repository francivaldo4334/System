function createStateManager() {
  const states = new Map();
  return {
    create: (name, initialValue = null) => {
      states.set(name, {
        value: initialValue,
        observers: []
      });
    },

    observer: (name, selector, attribute = 'textContent', then = (v, el) => v) => {
      const state = states.get(name);
      if (!state) return console.warn(`Estado "${name}" não existe.`);
      const elements = document.querySelectorAll(selector);
      elements.forEach(el => {
        if (!state.observers.some(obs => obs.el === el && obs.at === attribute)) {
          state.observers.push({ el, at: attribute, then });
          el[attribute] = state.value;
        }
      });
    },
    set: (name, newValue) => {
      const state = states.get(name);
      if (!state) return;
      state.value = newValue;
      state.observers.forEach(obs => {
        if (obs.el) {
          const content = obs.then(newValue, obs.el);
          if (content !== null) {
            obs.el[obs.at] = content
          }
        }
      });
    },
    remove: (name) => states.delete(name)
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
