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
    const code = this.getAttribute('oncleanup');

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

class AppTimeline extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    const unit = this.getAttribute('slotunit') || '10px';
    this.shadowRoot.innerHTML = `
          <style>
          :host {
              display: grid;
              grid-auto-rows: ${unit};
              position: relative;
          }
          </style>
          <slot></slot>
        `;
  }
}
class AppSlot extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    const start = parseInt(this.getAttribute('start')) || 1;
    const duration = parseInt(this.getAttribute('duration')) || 1;
    this.style.gridRowStart = start;
    this.style.gridRowEnd = start + duration;
    this.shadowRoot.innerHTML = `<slot></slot>`;
  }
}
customElements.define('app-timeline', AppTimeline)
customElements.define('app-slot', AppSlot)
customElements.define('app-input-currency', CurrencyField, { extends: 'input' })
customElements.define('app-input-ean', EanCodeField, { extends: 'input' })
customElements.define('app-ajax', CustomAjaxForm, { extends: 'form' })
customElements.define('app-scope', AppScope, { extends: 'script' })
