// const states = new WeakMap();

// const getState = (key) => states.get(key);

// const setState = (key, newValue) => {
//   if (!states.has(key)) {
//     throw new Error(`Estado '${key}' não foi definido. Utilize <app-state name="${key}"> primeiro.`);
//   }
//   const oldValue = states.get(key);
//   if (oldValue !== newValue) {
//     states.set(key, newValue);
//     window.dispatchEvent(new CustomEvent('state:update', {
//       detail: {
//         key,
//         oldValue,
//         newValue,
//       },
//       composed: true,
//       bubbles: true,
//     }));
//   }
// };
// const getStateSet = (prefix) => {
//   const store = `${prefix}.`
//   const entries = Array.from(states.entries())
//     .filter(([key]) => key.startsWith(store))
//     .map(([key, value]) => [key.replace(store, ''), value])
//   return Object.fromEntries(entries)
// }
// class StateDef extends HTMLElement {
//   static observedAttributes = ['value'];
//   constructor() {
//     super();
//     this.attachShadow({ mode: 'open' })
//     this.style.display = 'none'
//     this.name = this.getAttribute('name');
//     states.set(this.name, undefined);
//   }
//   disconnectedCallback() {
//     states.delete(this.name);
//   }
//   attributeChangedCallback(name, oldValue, newValue) {
//     setState(this.name, newValue);
//   }
// }
// const updateElement = (el, key, value) => {
//   const target = el.dataset.at || 'textContent';
//   if (target in el) {
//     el[target] = value;
//   } else {
//     el.setAttribute(target, String(value));
//   }
// };

// window.addEventListener('state:update', ({ detail }) => {
//   const { key, newValue } = detail;
//   const targets = document.querySelectorAll(`[data-state="${key}"], [data-state*=",${key},"], [data-state^="${key},"], [data-state$=",${key}"]`);
//   targets.forEach(el => updateElement(el, key, newValue));
// });
// window.customElements.define('app-state', StateDef)
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
