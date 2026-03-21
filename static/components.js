class CurrencyField extends HTMLInputElement {
  get valueAsDecimal() {
    const cleanValue = this.value.replace(/\D/g, '');
    const digits = cleanValue.slice(0, -2).replace(/^0+(?=\d)/, '') || '0'
    const decimals = cleanValue.slice(-2).padStart(2, '0')
    return `${digits}.${decimals}`
  }
  constructor() {
    super();
  }
  connectedCallback() {
    this.inputMode = 'decimal';
    this.maxLength = 29;
    if (!this.value || this.value === "") this.formatCurrency();
    this.addEventListener('input', () => this.formatCurrency())
  }
  formatCurrency() {
    let floatValue = this.valueAsDecimal;
    this.value = floatValue.toLocaleString('pt-BR', {
      maximumFractionDigits: 2,
      minimumFractionDigits: 2,
    })
    this.setSelectionRange(this.value.length, this.value.length)
  }
}
class EanCodeField extends HTMLInputElement {
  constructor() {
    super();
  }
  checkValidity() {
    const code = this.value;
    const calcCheckDigit = (baseCode = "") => {
      const sum = baseCode
        .split('')
        .reverse()
        .reduce((acc, n, i) => {
          const weight = i % 2 === 0 ? 3 : 1;
          return acc + weight * parseInt(n, 10);
        }, 0);

      return ((10 - (sum % 10)) % 10).toString();
    }

    const cleanCode = code.replace(/\D/g, '')

    if (![14, 13, 12, 8].includes(cleanCode.length))
      return false;
    const base = cleanCode.slice(0, -1);
    const actualDigit = cleanCode.slice(-1);
    const expectedDigit = calcCheckDigit(base);

    return actualDigit === expectedDigit;
  }
}
class CustomAjaxForm extends HTMLFormElement {
  connectedCallback() {
    this.store = this.getAttribute('store');
    if (!this.store) throw "'store' required."
    this.clean()
    this.addEventListener('submit', this);
    const autofetch = this.hasAttribute('autofetch')
    if (autofetch) {
      this._fetch()
    }
  }
  clean() {
    states.set(`${this.store}.loading`, false);
    states.set(`${this.store}.status`, undefined);
    states.set(`${this.store}.data`, undefined);
  }
  async _fetch() {
    setState(`${this.store}.loading`, true);
    try {
      const r = await fetch(this.getAttribute('action'), {
        method: (this.getAttribute('method') || 'GET').toUpperCase()
      })
      const data = await r.text();
      setState(`${this.store}.data`, data);
      setState(`${this.store}.status`, r.status);
    } finally {
      setState(`${this.store}.loading`, false);
    }
  }
  handleEvent(e) {
    e.preventDefault();
    this._fetch()
  }
}
class AppScope extends HTMLScriptElement {
  constructor() {
    super();
    this._cleanUpFn = null;
  }

  connectedCallback() {
    if (!this.textContent.trim() || this._cleanUpFn) return;
    const code = this.getAttribute('cleanup');

    try {
      this._cleanUpFn = new Function(`${code}`);;

    } catch (e) {
      console.error("Erro na execução do escopo AppScope:", e);
    }
  }

  disconnectedCallback() {
    if (this._cleanUpFn) {
      this._cleanUpFn();
      this._cleanUpFn = null;
      console.log("AppScope: Recursos limpos com sucesso.");
    }
    this.textContent = "";
  }
}
class AppUseJson extends HTMLElement {
  constructor() {
    super();
    this._proxy = null;
  }

  static get observedAttributes() {
    return ['value'];
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue !== newValue) {
      this.render();
    }
  }

  connectedCallback() {
    this.render();
  }
  setContent(el, value) {
    const at = this.getAttribute('at') || 'textContent';
    const safeAt = ['textContent', 'value', 'innerText'].includes(at) ? at : 'textContent';
    el[safeAt] = value;
  }

  render() {
    const valueAttr = this.getAttribute('value');
    const thenAttr = this.getAttribute('then');
    const targetAttr = this.getAttribute('target');
    const isList = this.hasAttribute('list');

    if (!valueAttr || !thenAttr) return;

    try {
      const obj = JSON.parse(valueAttr);
      if (!this._proxy) this._proxy = new Function('it', `return (${thenAttr})(it)`);

      if (isList && Array.isArray(obj)) {
        const template = this.querySelector(targetAttr);
        if (!template) return;
        this.querySelectorAll('[data-is-clone]').forEach(el => el.remove());
        template.style.display = 'none';
        const fragment = document.createDocumentFragment();
        obj.forEach((itemData) => {
          const clone = template.cloneNode(true);
          clone.style.display = '';
          clone.setAttribute('data-is-clone', 'true');
          const result = this._proxy(itemData);
          this.setContent(clone, result);
          fragment.appendChild(clone);
        });
        this.appendChild(fragment);

      } else {
        // Lógica para valor único
        const targetEl = targetAttr ? this.querySelector(targetAttr) : this;
        const result = this._proxy(obj);
        this.setContent(targetEl, result);
      }
    } catch (e) {
      console.error('AppUseJson Error:', e);
    }
  }
}

customElements.define('app-input-currency', CurrencyField, { extends: 'input' })
customElements.define('app-input-ean', EanCodeField, { extends: 'input' })
customElements.define('app-ajax', CustomAjaxForm, { extends: 'form' })
customElements.define('app-scope', AppScope, { extends: 'script' })
customElements.define('app-json', AppUseJson);
