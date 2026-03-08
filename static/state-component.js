//@props
// key: string
// type: 'str' | 'num' | 'bol'
class Signal {
  constructor(
    { key, type, value }
  ) {
    if (typeof key !== 'string') {
      throw TypeError("'key' must be of the 'string' type")
    }
    if (typeof type !== 'string') {
      throw TypeError("'type' must be of the 'string' type")
    }
    if (!['str', 'num', 'bol', 'list'].includes(type)) {
      throw TypeError("'type' must be one of the options 'str', 'num', 'bol' or 'list'")
    }
    this.key = key;
    this.type = type;
    this._value = value;
  }
  get value() {
    return this._value
  }
  setStr(value) {
    if (typeof value !== 'string') {
      throw TypeError('invalid signal type')
    }
    this._value = value;
  }
  setNum(value) {
    if (typeof value === 'number') {
      this._value = value;
      return;
    }
    if (typeof value !== 'string') {
      throw TypeError('invalid signal type')
    }
    if (!/^\d+$/.test(value)) {
      throw TypeError('invalid signal type')
    }
    this._value = Number(value)
  }
  setBol(value) {
    this._value = Boolean(value)
  }
  set value(value) {
    if (this.type === 'str') {
      this.setStr(value)
    }
    else if (this.type === 'num') {
      this.setNum(value)
    }
    else if (ths.type === 'bol') {
      this.setBol(value)
    } else {
      throw Error()
    }
    const signalEvent = new CustomEvent('signal-update', {
      detail: { key: this.key, value },
      composed: true,
      bubbles: true,
    })
    window.dispatchEvent(signalEvent);
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
    const value = this.getAttribute('default');
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
