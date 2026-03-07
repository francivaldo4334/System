//@props
// key: string
// type: 'str' | 'num' | 'bol'
class Signal {
  constructor(
    { type, value }
  ) {
    if (typeof type !== 'string') {
      throw TypeError("'type' must be of the 'string' type")
    }
    if (!['str', 'num', 'bol', 'list'].includes(type)) {
      throw TypeError("'type' must be one of the options 'str', 'num', 'bol' or 'list'")
    }
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
    const signalEvent = new CustomEvent('signal-update', { key: ths.key, value })
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
    this.#signals.set(key, new Signal(config));
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
    const keys = this.getAttribute('keys')
    window.addEventListener('signal-update', (event) => {
      console.log("ok")
      event.detail.key
      event.detail.value
    })
  }
}
window.customElements.define('use-signal', UseObserver)
window.customElements.define('use-observer', UseObserver)
