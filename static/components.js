class FieldControl extends HTMLElement {
  static observedAttributes = ['invalid', 'success', 'error', 'label', 'help'];
  constructor() {
    super();
    this._initialContent = this.innerHTML;
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (this.isConnected && oldValue !== newValue) {
      this.render();
    }
  }

  connectedCallback() {
    if (!this._initialContent) this._initialContent = this.innerHTML;
    this.render();
  }

  render() {
    const label = this.getAttribute('label') || '';
    const error = this.getAttribute('error') || '';
    const help = this.getAttribute('help') || '';
    const isInvalid = this.hasAttribute('invalid');
    const isSuccess = this.hasAttribute('success');
    const id = this.getAttribute('for');
    this.innerHTML = `
      <div class="flex flex-col">
          <label${id ? ' for="' + id + '"' : ''}><strong>${label}</strong></label>
          ${this._initialContent}
          <div class="border-t m-x" style="--mx:var(--b2);${isInvalid ? '--btc:var(--c-error)' : isSuccess ? '--btc:var(--c-success)' : 'display:none'}"></div>
          <small role="alert"
                 class="text-color"
                 style="--tc:var(--c-error); --text-sm-lh:var(--s4);display: ${error && isInvalid ? 'block' : 'none'}">
            ${error}
          </small>
          <small style="display: ${error ? 'block' : 'none'}">
            ${help}
          </small>
      </div>
    `;
  }
}
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
// class CustomAjaxForm extends HTMLFormElement {
//   constructor() {
//     super();
//     this._onSubmit = this._onSubmit.bind(this);
//   }

//   connectedCallback() {
//     const store = this.getAttribute('store');
//     if (!store) throw TypeError("'store' is required.");

//     this.store = Object.freeze({
//       data: `${store}.data`,
//       loading: `${store}.loading`,
//       status: `${store}.status`,
//       error: `${store}.error`,
//     });

//     setState(this.store.data, '');
//     setState(this.store.loading, '');
//     setState(this.store.error, '');
//     setState(this.store.status, '');

//     this.endpoint = this.getAttribute('endpoint');
//     this.method = (this.getAttribute('method') || 'GET').toUpperCase();

//     this.addEventListener('submit', this._onSubmit);
//   }

//   disconnectedCallback() {
//     Object.values(this.store).forEach(k => typeof states !== 'undefined' && states.delete(k));
//     this.removeEventListener('submit', this._onSubmit);
//   }
//   _onSubmit(event) {
//     event.preventDefault();
//     setState(this.store.loading, 'true')
//     fetch(this.endpoint, { method: this.method })
//       .then(response => {
//         const status = response.status;
//         response.text().then(data => {
//           if (response.ok) {
//             setState(this.store.data, data)
//           }
//           else {
//             setState(this.store.error, data)
//           }
//         }).finally(()=>{
//           setState(this.store.status, status)
//         })
//       })
//       .finally(() => setState(this.store.loading, 'false'))
//   }
// }
// class AppIf extends HTMLElement {
//   static observedAttributes = ['value'];

//   constructor() {
//     super();
//     this.attachShadow({ mode: 'open' });
//     this.shadowRoot.innerHTML = `
//       <style>
//         :host([result="false"]) slot:not([name="else"]) { display: none; }
//         :host([result="true"]) slot[name="else"] { display: none; }
//         :host(:not([result])) slot { display: none; }
//       </style>
//       <slot></slot> <slot name="else"></slot>
//     `;
//   }

//   attributeChangedCallback() {
//     this.update();
//   }
//   update() {
//     const value = this.getAttribute('value');
//     const isTrue = value === 'true';
//     this.setAttribute('result', isTrue ? 'true' : 'false');
//   }
// }
class CustomAjaxForm extends HTMLFormElement {
  connectedCallback(){
    this.store = this.getAttribute('store');
    if (!this.store) throw "'store' required."
    this.addEventListener('submit', this);
  }
  clean(){
    states.set(`${this.store}.loading`, false);
    states.set(`${this.store}.status`, undefined);
    states.set(`${this.store}.data`, undefined);
  }
  async handleEvent(e){
    e.preventDefault();
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
}
window.customElements.define('app-field', FieldControl)
window.customElements.define('app-input-currency', CurrencyField, { extends: 'input' })
window.customElements.define('app-input-ean', EanCodeField, { extends: 'input' })
window.customElements.define('app-ajax-form', CustomAjaxForm, { extends: 'form' })
// window.customElements.define('app-if', AppIf);
