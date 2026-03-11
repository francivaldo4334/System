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

window.customElements.define('app-layout', CustomAppLayout)
window.customElements.define('app-nav-item', CustomAppNavItem)
window.customElements.define('app-btn', BaseButtton, { extends: 'button' })
window.customElements.define('app-btn-outlined', BaseButttonOutlined, { extends: 'button' })
window.customElements.define('app-btn-ghost', BaseButttonGhost, { extends: 'button' })
