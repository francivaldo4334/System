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
class AppQuery extends HTMLFormElement {
  constructor() {
    super();
    this.queryKey = this.getAttribute("querykey")
    if (!this.queryKey) throw Error("Insira uma 'querykey'")
    this._fetch = this._fetch.bind(this)
  }
  async _fetch(event) {
    event.preventDefault();

    const action = this.getAttribute('action');
    const method = (this.getAttribute('method') || 'GET').toUpperCase();

    let endpoint = action;
    let options = { method };

    const formData = new FormData(this);

    if (method === 'GET') {
      const params = new URLSearchParams(formData).toString();
      endpoint = params ? `${action}?${params}` : action;
    } else {
      options.body = formData;
    }

    try {
      const response = await fetch(endpoint, options);
      const data = await response.text();
      if (!response.ok) throw { status: response.status, data };
      this.dispatchEvent(new CustomEvent('query:success', {
        bubbles: true,
        composed: true,
        detail: { queryKey: this.queryKey, status: response.status, data }
      }));
    } catch (error) {
      this.dispatchEvent(new CustomEvent('query:error', {
        bubbles: true,
        composed: true,
        detail: { querykey: this.queryKey, error }
      }));
    }
  }
  connectedCallback() {
    this.addEventListener('submit', this._fetch)
    if (this.hasAttribute('autofetch')) {
      this.requestSubmit()
    }
  }
  disconnectedCallback() {
    this.removeEventListener('submit', this._fetch)
  }
}
//@deprecated
class CustomAjaxForm extends HTMLFormElement {
  connectedCallback() {
    this.queryKey = this.getAttribute('querykey');
    this.addEventListener('submit', this);
    if (this.hasAttribute('autofetch')) {
      this._fetch();
    }
  }

  async _fetch() {
    const action = this.getAttribute('action');
    const method = (this.getAttribute('method') || 'GET').toUpperCase();

    const options = { method };
    if (method !== 'GET') {
      options.body = new FormData(this);
    }

    try {
      const response = await fetch(action, options);
      const data = await response.text();

      if (!response.ok) throw { status: response.status, data };

      this._dispatch('app-ajax:success', {
        queryKey: this.queryKey,
        status: response.status,
        data
      });

    } catch (error) {
      this._dispatch('app-ajax:error', {
        queryKey: this.queryKey,
        error
      });
    }
  }

  _dispatch(type, detail) {
    this.dispatchEvent(new CustomEvent(type, {
      bubbles: true,
      composed: true,
      detail: detail
    }));
  }

  handleEvent(e) {
    e.preventDefault();
    this._fetch();
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
    }
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
customElements.define('app-query', AppQuery, { extends: 'form' })
