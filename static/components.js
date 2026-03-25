import { createComponent } from './web-component-factory.js'
// class CurrencyField extends HTMLInputElement {
//   get valueAsDecimal() {
//     const cleanValue = this.value.replace(/\D/g, '');
//     const digits = cleanValue.slice(0, -2).replace(/^0+(?=\d)/, '') || '0'
//     const decimals = cleanValue.slice(-2).padStart(2, '0')
//     return `${digits}.${decimals}`
//   }
//   constructor() {
//     super();
//   }
//   connectedCallback() {
//     this.inputMode = 'decimal';
//     this.maxLength = 29;
//     if (!this.value || this.value === "") this.formatCurrency();
//     this.addEventListener('input', () => this.formatCurrency())
//   }
//   formatCurrency() {
//     let floatValue = this.valueAsDecimal;
//     this.value = floatValue.toLocaleString('pt-BR', {
//       maximumFractionDigits: 2,
//       minimumFractionDigits: 2,
//     })
//     this.setSelectionRange(this.value.length, this.value.length)
//   }
// }
// class EanCodeField extends HTMLInputElement {
//   constructor() {
//     super();
//   }
//   checkValidity() {
//     const code = this.value;
//     const calcCheckDigit = (baseCode = "") => {
//       const sum = baseCode
//         .split('')
//         .reverse()
//         .reduce((acc, n, i) => {
//           const weight = i % 2 === 0 ? 3 : 1;
//           return acc + weight * parseInt(n, 10);
//         }, 0);

//       return ((10 - (sum % 10)) % 10).toString();
//     }

//     const cleanCode = code.replace(/\D/g, '')

//     if (![14, 13, 12, 8].includes(cleanCode.length))
//       return false;
//     const base = cleanCode.slice(0, -1);
//     const actualDigit = cleanCode.slice(-1);
//     const expectedDigit = calcCheckDigit(base);

//     return actualDigit === expectedDigit;
//   }
// }
// class AppQuery extends HTMLFormElement {
//   constructor() {
//     super();
//     this.queryKey = this.getAttribute("querykey")
//     if (!this.queryKey) throw Error("Insira uma 'querykey'")
//     this._fetch = this._fetch.bind(this)
//   }
//   async _fetch(event) {
//     event.preventDefault();

//     const action = this.getAttribute('action');
//     const method = (this.getAttribute('method') || 'GET').toUpperCase();
//     const headers = [];
//     if (this.hasAttribute('headers')) {
//       this.getAttribute('headers').split(',').forEach(h => {
//         const [key, value] = h.split(':')
//         headers.push([key.trim(), value.trim()])
//       })
//     }
//     let endpoint = action;
//     let options = { method, headers };

//     const formData = new FormData(this);

//     if (method === 'GET') {
//       const params = new URLSearchParams(formData).toString();
//       endpoint = params ? `${action}?${params}` : action;
//     } else {
//       options.body = formData;
//     }

//     try {
//       const response = await fetch(endpoint, options);
//       const data = await response.text();
//       if (!response.ok) throw { status: response.status, data };
//       this.dispatchEvent(new CustomEvent('query:success', {
//         bubbles: true,
//         composed: true,
//         detail: { queryKey: this.queryKey, status: response.status, data }
//       }));
//     } catch (error) {
//       this.dispatchEvent(new CustomEvent('query:error', {
//         bubbles: true,
//         composed: true,
//         detail: { querykey: this.queryKey, error }
//       }));
//     }
//   }
//   connectedCallback() {
//     this.addEventListener('submit', this._fetch)
//     if (this.hasAttribute('autofetch')) {
//       this.requestSubmit()
//     }
//   }
//   disconnectedCallback() {
//     this.removeEventListener('submit', this._fetch)
//   }
// }

// class AppScope extends HTMLScriptElement {
//   disconnectedCallback() {
//     const cleanupCode = this.getAttribute('onclearup');
//     if (cleanupCode) {
//       try {
//         new Function(cleanupCode).call(globalThis);
//       } catch (e) {
//         console.error("Erro ao executar cleanup do AppScope:", e);
//       }
//     }
//   }
// }
// class AppState extends HTMLElement {
//   constructor() {
//     super();
//     this.style.display = 'none'
//   }
//   connectedCallback() {
//     this.stateName = this.getAttribute('name');
//     const selector = this.getAttribute('selector');
//     const value = this.getAttribute('value');
//     const attr = this.getAttribute('attribute');
//     if (!this.stateName) return console.error("AppState: Atributo 'name' é obrigatório.");
//     $s.create(this.stateName);
//     if (selector) $s.subscribe(this.stateName, selector, attr);
//     if (value) $s.set(this.name, value)
//   }
//   disconnectedCallback() {
//     $s.remove(this.stateName);
//   }
// }
createComponent('app-timeline', {
  scoped: true,
  css: `:host { display: grid; grid-auto-rows: var(--slotunit); position: relative; }`,
  html: `<slot></slot>`,
  props: ['slotunit'],
  onUpdate(prop, value) {
    this.style.setProperty('--slotunit', value)
  }
})
createComponent('app-slot', {
  scoped: true,
  html: "<slot></slot>",
  props: ['start', 'duration'],
  css: ` :host { display: block; } `,
  onUpdate(prop, value) {
    const val = parseInt(value) || 1;
    if (prop === 'start')
      this.style.gridRowStart = val;
    if (prop === 'duration')
      this.style.gridRowEnd = `span ${val}`;
  }
})

createComponent('c-days', {
  html: '<div class="calendar-grid"></div>',
  props: ['date', 'range', 'onchange'],
  onUpdate(prop, value){
    this.setAttribute(prop, value)
    const dateIso = this.getAttribute('date')
    const rangeIso = this.getAttribute('range')
    const onchange = this.getAttribute('onchange')
    if (!dateIso || !rangeIso) return;
    const date = new Date(dateIso)
    const [init, end] = rangeIso.split(',').map(iso => new Date(iso))
    this.render(date, init, end, onchange)
  },
  _check(date, other, type, start, end) {
    const d = new Date(date).setHours(0, 0, 0, 0);
    const o = new Date(other).setHours(0, 0, 0, 0);
    if (type === 'same') return d === o;
    if (type === 'range') {
      return start && end && d >= start && d <= end;
    }
  },
  render(date, startR, endR,onchange) {
    const grid = this.$('.calendar-grid');
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1).getDay();
    const totalDays = new Date(year, month + 1, 0).getDate();
    const today = new Date();
    const frag = document.createDocumentFragment();
    for (let i = 0; i < firstDay; i++) {
      frag.appendChild(document.createElement('div'));
    }
    for (let day = 1; day <= totalDays; day++) {
      const iterDate = new Date(year, month, day);
      const btn = document.createElement('button');
      btn.textContent = day;
      if (this._check(iterDate, null, 'range', startR, endR)) btn.dataset.type = 'range';
      if (this._check(iterDate, today, 'same')) btn.dataset.type = 'today';
      if (day === date.getDate()) btn.dataset.type = 'selected';
      btn.onclick = ()=>{
        new Function('it',onchange)(iterDate.toISOString())
      };
      frag.appendChild(btn);
    }

    grid.innerHTML = '';
    grid.appendChild(frag);
  },
})
// customElements.define('app-state', AppState);
// customElements.define('app-timeline', AppTimeline)
// customElements.define('', AppSlot)
// customElements.define('app-input-currency', CurrencyField, { extends: 'input' })
// customElements.define('app-input-ean', EanCodeField, { extends: 'input' })
// customElements.define('app-scope', AppScope, { extends: 'script' })
// customElements.define('app-query', AppQuery, { extends: 'form' })
