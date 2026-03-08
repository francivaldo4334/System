const TYPE_HANDLERS = {
  str: (v) => String(v),
  num: (v) => {
    const n = Number(v)
    if (isNaN(n)) throw TypeError('Value is not a valid number')
    return n;
  },
  bol: (v) => {
    if (typeof v === 'string') return v.toLowerCase() === 'true';
    return Boolean(v);
  },
  obj: (v) => {
    if (typeof v !== 'object') throw TypeError('Value is not a valid object')
    return v
  },
  list: (v) => {
    if (!Array.isArray(v)) throw TypeError("Value is not a valid Array")
    return v
  }
}
class Signal {
  constructor(
    { key, type, value }
  ) {
    if (typeof key !== 'string') throw TypeError("'key' must be a string");
    if (!TYPE_HANDLERS[type]) throw TypeError(`Invalid type: ${type}`)
    this.key = key;
    this.type = type;
    this._value = TYPE_HANDLERS[type](value);
  }
  get value() {
    return this._value
  }
  set value(newValue) {
    try {
      const parseValue = TYPE_HANDLERS[this.type](newValue)
      this._value = parseValue;
      window.dispatchEvent(new CustomEvent('signal-update', {
        detail: { key: this.key, value: newValue },
        composed: true,
        bubbles: true,
      }));
    } catch (e) {
      console.error(`[Signal ${this.key}] Update failed: ${e.message}`)
    }
  }
}
class SignalManager {
  static #instance;
  #signals = new Map();

  constructor() {
    if (SignalManager.#instance) {
      return SignalManager.#instance;
    }
    SignalManager.#instance = this;
  }

  static get instance() {
    if (!this.#instance) {
      this.#instance = new SignalManager();
    }
    return this.#instance;
  }

  add(key, config) {
    if (this.#signals.has(key)) {
      console.warn(`Signal com chave "${key}" já existe.`);
      return;
    }
    this.#signals.set(key, new Signal({ ...config, key }));
  }

  remove(key) {
    return this.#signals.delete(key);
  }

  get values() {
    return Array.from(this.#signals.values());
  }
  get(key) {
    return this.#signals.get(key)
  }
}
const signalManager = new SignalManager();
Object.freeze(signalManager)
function updateSignal(key, value) {
  signalManager.get(key).value = value
}

class UseSignal extends HTMLElement {
  constructor() {
    super();
    const key = this.getAttribute('key');
    const type = this.getAttribute('type');
    const defaultValue = this.getAttribute('default');
    let value;
    try {
      const parseJson = JSON.parse(defaultValue)
      value = parseJson;
    } catch (e) {
      value = defaultValue
    }
    signalManager.add(key, { type, value });
  }
}
class UseObserver extends HTMLElement {
  constructor() {
    super();
    this._handleUpdate = this._handleUpdate.bind(this);
  }

  connectedCallback() {
    this.keys = this.getAttribute('keys')?.split(',').map(k => k.trim()) || [];
    window.addEventListener('signal-update', this._handleUpdate);
    this.render();
  }

  disconnectedCallback() {
    window.removeEventListener('signal-update', this._handleUpdate);
  }

  _handleUpdate(event) {
    const { key } = event.detail;
    if (this.keys.includes(key)) {
      this.render();
    }
  }

  render() {
    const keysToUpdate = this.keys;
    keysToUpdate.forEach(key => {
      const value = signalManager.get(key).value;
      const targets = this.querySelectorAll(`[use-key="${key}"]`);
      targets.forEach(el => {
        if (el.textContent !== String(value)) {
          el.textContent = value;
        }
      });
    });
  }
}
window.customElements.define('use-signal', UseSignal)
window.customElements.define('use-observer', UseObserver)
