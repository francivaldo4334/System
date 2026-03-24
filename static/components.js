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
    const headers = [];
    if (this.hasAttribute('headers')) {
      this.getAttribute('headers').split(',').forEach(h => {
        const [key, value] = h.split(':')
        headers.push([key.trim(), value.trim()])
      })
    }
    let endpoint = action;
    let options = { method, headers };

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

class AppScope extends HTMLScriptElement {
  disconnectedCallback() {
    const cleanupCode = this.getAttribute('onclearup');
    if (cleanupCode) {
      try {
        new Function(cleanupCode).call(globalThis);
      } catch (e) {
        console.error("Erro ao executar cleanup do AppScope:", e);
      }
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

class AppState extends HTMLElement {
  constructor() {
    super();
    this.style.display = 'none'
  }
  connectedCallback() {
    this.stateName = this.getAttribute('name');
    const selector = this.getAttribute('selector');
    const value = this.getAttribute('value');
    const attr = this.getAttribute('attribute');
    if (!this.stateName) return console.error("AppState: Atributo 'name' é obrigatório.");
    $s.create(this.stateName);
    if (selector) $s.subscribe(this.stateName, selector, attr);
    if (value) $s.set(this.name, value)
  }
  disconnectedCallback() {
    $s.remove(this.stateName);
  }
}

customElements.define('app-state', AppState);
customElements.define('app-timeline', AppTimeline)
customElements.define('app-slot', AppSlot)
customElements.define('app-input-currency', CurrencyField, { extends: 'input' })
customElements.define('app-input-ean', EanCodeField, { extends: 'input' })
customElements.define('app-scope', AppScope, { extends: 'script' })
customElements.define('app-query', AppQuery, { extends: 'form' })
