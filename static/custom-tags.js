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
class AppSelect extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {

    this.shadowRoot.innerHTML = `
      <style>
        .container { 
          anchor-name: --select-anchor; 
          position: relative;
        }
        [popover] {
          margin: 0;
          padding: 0;
          border: none;
          background: transparent;
          overflow: visible;
          position-anchor: --select-anchor;
          top: anchor(bottom);
          left: anchor(left);
          min-width: anchor-size(width);
          position-try-options: flip-block;
        }
        button {
          all: unset;
          display: block;
          width: 100%;
          cursor: pointer;
        }
        [popover]:-internal-popover-in-top-layer::backdrop {
          display: none;
        }
        ::slotted([slot="trigger"])::after {
          content: "---";
          width: var(--s4);
          height: var(--s4);
          margin: auto;
          flex-shrink: 0;
          background-color: currentColor;
          -webkit-mask: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNoZXZyb25zLXVwLWRvd24taWNvbiBsdWNpZGUtY2hldnJvbnMtdXAtZG93biI+PHBhdGggZD0ibTcgMTUgNSA1IDUtNSIvPjxwYXRoIGQ9Im03IDkgNS01IDUgNSIvPjwvc3ZnPg==") no-repeat center;
          mask: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNoZXZyb25zLXVwLWRvd24taWNvbiBsdWNpZGUtY2hldnJvbnMtdXAtZG93biI+PHBhdGggZD0ibTcgMTUgNSA1IDUtNSIvPjxwYXRoIGQ9Im03IDkgNS01IDUgNSIvPjwvc3ZnPg==") no-repeat center;
          mask-size: contain;
          transition: transform 0.2s ease;
        }
      </style>
      <div class="container">
        <button popovertarget="options-menu" popovertargetaction="toggle">
          <slot name="trigger"></slot>
        </button>
        <div id="options-menu" popover>
          <slot name="content"></slot>
        </div>
      </div>
    `;
    this.setupLogic();
  }

  setupLogic() {
    const popover = this.shadowRoot.querySelector('[popover]');
    const optionsSlot = this.shadowRoot.querySelector('slot[name="content"]');
    optionsSlot.addEventListener('click', (e) => {
      const item = e.target.closest('[data-value]');
      const allItems = optionsSlot.assignedElements({ flatten: true });
      allItems.forEach(el => el.removeAttribute('aria-selected'));
      item.setAttribute('aria-selected', 'true');
      if (item) {
        const trigger = this.querySelector('[slot="trigger"]');
        const label = trigger?.querySelector('[data-label]')
        if (label) label.innerText = item.innerText;
        popover.hidePopover();
        this.dispatchEvent(new CustomEvent('change', {
          detail: {
            value: item.dataset.value,
            label: item.innerText
          },
          bubbles: true,
          composed: true
        }));
      }
    });
  }
}
class SelectTrigerField extends HTMLElement {
  connectedCallback() {
    applyStyles(this, {
      'input-field': '',
      'icon-chevron': '',
      'grid-cols': '--gc: 1fr auto',
      'hover-bg-color': '--bgc:var(--c-200)',
    })
  }
}
class SelectContentField extends HTMLElement {
  connectedCallback() {
    applyStyles(this, {
      'shadow': '',
      'container': 'display: block;',
    })
  }
}
class SelectOptionField extends HTMLElement {
  connectedCallback() {
    if (!this.hasAttribute('role')) this.setAttribute('role', 'option');
    applyStyles(this, {
      'rounded-xs': 'display:block;',
      'p-x': '--px:12px;',
      'p-y': '--py:6px;',
      'hover-bg-color': '--bgc:var(--c-300)',
      'active-bg-color': '--bgca:var(--c-900)',
      'active-text-color': '--tca:var(--c-white)',
    })
  }
}

window.customElements.define('app-field', FieldControl)
window.customElements.define('app-input-currency', CurrencyField, { extends: 'input' })
window.customElements.define('app-input-ean', EanCodeField, { extends: 'input' })
window.customElements.define('app-select-trigger', SelectTrigerField)
window.customElements.define('app-select-content', SelectContentField)
window.customElements.define('app-select-option', SelectOptionField)
window.customElements.define('app-select', AppSelect);
