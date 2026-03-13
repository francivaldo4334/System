const applyStyles = (el, styleMap) => {
  Object.entries(styleMap).forEach(([className, styleString]) => {
    if (className) el.classList.add(className);
    if (styleString) {
      styleString.split(';').forEach(prop => {
        const [name, value] = prop.split(':').map(s => s?.trim());
        if (name && value) el.style.setProperty(name, value);
      });
    }
  });
};
class CustomAppLayout extends HTMLElement {
  constructor() {
    super();
    shadow.innerHTML = `
    <style>
        ::slotted([slot="sidebar"]) {
        }
        ::slotted([slot="content"]) {
        }
      </style>
      <slot name="sidebar"></slot>
      <slot name="content"></slot>
    `
  }
}
class CustomAppNavItem extends HTMLElement {
  connectedCallback() {
    const endpoint = this.getAttribute('endpoint')
    const store = this.getAttribute('store')
    const content = this.innerHTML;
    this.innerHTML = `
      <form is="ajax-form" endpoint="${endpoint}" store="${store}">
          <button type="submit">
            ${content}
          </button>
      </form>
    `
  }
}
class CustomButton extends HTMLButtonElement {
  baseStyle = {};

  connectedCallback() {
    applyStyles(this, this.baseStyle);
  }
}

class BaseButtton extends CustomButton {
  baseStyle = {
    'min-w': '--minw:var(--sm)',
    'min-h': '--minh:var(--xs)',
    'm-f': '--mf:0',
    'rounded-xs': '',
    'font': '--f:600',
    'border-f': '--bfc:var(--c-300)',
    'shadow-inset': '--si:0.2;--sic:var(--c-blac);--siy:-8px',
    'bg-color': '--bgc:var(--c-100)',
    'text-color': '--tc:var(--c-black)',
    'hover-bg-color': '--bgch:var(--c-200)',
    'hover-shadow': '--s:0.3',
    'hover-elevation': '',
    'active-bg-color': '--bgca:var(--c-900)',
    'active-text-color': '--tca:var(--c-white)',
    'disabled-text-color': '--tcd:var(--c-black)',
    'disabled-bg-pattern-diagonal': '',
  }
}
class BaseButttonOutlined extends BaseButtton {
  baseStyle = {
    ...this.baseStyle,
    'bg-color': '--bgc:transparent',
    'border-f': '--bf:1px;--bfc:var(--c-300)',
    'text-color': '--tc:var(--c-black)',
    'hover-bg-color': '--bgch:var(--c-50)',
    'hover-shadow': '--s:0.1',
    'shadow-inset': '--si:0',
  }
}
class BaseButttonGhost extends BaseButtton {
  baseStyle = {
    ...this.baseStyle,
    'bg-color': '--bgc:transparent',
    'border-f': '--bf:0',
    'shadow-inset': '--si:0',
    'text-color': '--tc:var(--c-black)',
    'hover-bg-color': '--bgch:var(--c-100)',
    'active-bg-color': '--bgca:var(--c-200)',
    'active-text-color': '--tca:var(--c-black)',
  }
}

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

    let statusColor = 'var(--c-600)'; // Padrão
    if (isInvalid) statusColor = 'var(--c-error)';
    if (isSuccess) statusColor = 'var(--c-success)';

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

class TextField extends HTMLInputElement {
  constructor() {
    super();
  }
  connectedCallback() {
    this.classList.add('input-field')
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
    this.classList.add('input-field')
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
  connectedCallback() {
    this.classList.add('input-field')
  }
}
window.customElements.define('app-layout', CustomAppLayout)
window.customElements.define('app-nav-item', CustomAppNavItem)
window.customElements.define('app-btn', BaseButtton, { extends: 'button' })
window.customElements.define('app-btn-outlined', BaseButttonOutlined, { extends: 'button' })
window.customElements.define('app-btn-ghost', BaseButttonGhost, { extends: 'button' })
window.customElements.define('app-field', FieldControl)
window.customElements.define('app-input-text', TextField, { extends: 'input' })
window.customElements.define('app-input-currency', CurrencyField, { extends: 'input' })
window.customElements.define('app-input-ean', EanCodeField, { extends: 'input' })
