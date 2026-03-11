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
    'hover:bg-color': '--bgch:var(--c-600)',
    'hover:text-color': '--tch:var(--c-white)',
    'hover-shadow': '--s:0.3',
    'hover-elevation': '',
    'active:bg-color': '--bgca:var(--c-900)',
    'disabled:bg-pattern-diagonal': '',
  }
}

class BaseButttonOutlined extends CustomButton {
  baseStyle = {
    'min-w': '--minw:var(--sm)',
    'min-h': '--minh:var(--xs)',
    'm-f': '--mf:0',
    'rounded-xs': '',
    'bg-white': '',
    'text-md': '',
    'font-semibold': '',
    'border-f': '--bfc:var(--c-300);--bf:1px;',
    'text-black': '',
  }
}

class BaseButttonGhost extends CustomButton {
  baseStyle = {
    'min-w': '--minw:var(--sm)',
    'min-h': '--minh:var(--xs)',
    'm-f': '--mf:0',
    'rounded-xs': '',
    'bg-white': '',
    'text-md': '',
    'font-semibold': '',
    'border-f': '--bf:0;',
    'text-black': '',
  }
}
window.customElements.define('app-layout', CustomAppLayout)
window.customElements.define('app-nav-item', CustomAppNavItem)
window.customElements.define('app-btn', BaseButtton, { extends: 'button' })
window.customElements.define('app-btn-outlined', BaseButttonOutlined, { extends: 'button' })
window.customElements.define('app-btn-ghost', BaseButttonGhost, { extends: 'button' })
