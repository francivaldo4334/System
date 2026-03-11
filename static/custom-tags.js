// const applyStyles = (el, styleMap) => {
//   Object.entries(styleMap).forEach(([className, styleString]) => {
//     if (className) el.classList.add(className);
//     if (styleString) {
//       styleString.split(';').forEach(prop => {
//         const [name, value] = prop.split(':').map(s => s?.trim());
//         if (name && value) el.style.setProperty(name, value);
//       });
//     }
//   });
// };
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
  hoverStyle = {};
  clickStyle = {};
  disabledStyle = {};

  static observedAttributes = ['disabled'];

  constructor() {
    super();
    this._onPres = this._onPres.bind(this);
    this._onRelease = this._onRelease.bind(this);
    this._onHoverIn = this._onHoverIn.bind(this);
    this._onHoverOut = this._onHoverOut.bind(this);
  }
  attributeChangedCallback(name, oldValue, newValue) {
    if (name === 'disabled') {
      if (this.disabled) {
        this._applyStyles(this.disabledStyle);
        this._clearStyles(this.hoverStyle);
        this._clearStyles(this.clickStyle);
      } else {
        this._clearStyles(this.disabledStyle);
      }
    }
  }

  _getStyleProps(props) {
    if (!props || typeof props !== 'string') return [];
    return props.split(';').filter(Boolean).map(it => it.split(':').map(s => s.trim()));
  }

  _applyStyles(styleObj) {
    Object.entries(styleObj).forEach(([className, styleString]) => {
      if (className) this.classList.add(className);
      this._getStyleProps(styleString).forEach(([name, value]) => {
        if (name && value) this.style.setProperty(name, value);
      });
    });
  }

  _clearStyles(styleObj) {
    Object.entries(styleObj).forEach(([className, styleString]) => {
      if (className) this.classList.remove(className);
      this._getStyleProps(styleString).forEach(([name]) => {
        this.style.removeProperty(name);
      });
    });
  }

  _onPres() {
    if (this.disabled) return;
    this._applyStyles(this.clickStyle);
  }

  _onRelease() {
    this._clearStyles(this.clickStyle);
  }

  _onHoverIn() {
    if (this.disabled) return;
    this._applyStyles(this.hoverStyle);
  }

  _onHoverOut() {
    this._clearStyles(this.hoverStyle);
  }

  connectedCallback() {
    this._applyStyles(this.baseStyle);
    this.addEventListener('mouseenter', this._onHoverIn);
    this.addEventListener('mouseleave', this._onHoverOut);
    this.addEventListener('mousedown', this._onPres);
    this.addEventListener('mouseup', this._onRelease);
    this.addEventListener('mouseleave', this._onRelease);
  }

  disconnectedCallback() {
    this.removeEventListener('mouseenter', this._onHoverIn);
    this.removeEventListener('mouseleave', this._onHoverOut);
    this.removeEventListener('mousedown', this._onPres);
    this.removeEventListener('mouseup', this._onRelease);
    this.removeEventListener('mouseleave', this._onRelease);
  }
}

class BaseButtton extends CustomButton {
  baseStyle = {
    'min-w': '--minw:var(--sm)',
    'min-h': '--minh:var(--xs)',
    'm-f': '--mf:0',
    'rounded-xs': '',
    'bg-base-100': '',
    'text-md': '',
    'font-semibold': '',
    'border-f': '--bfc:var(--c-300)',
    'text-black': '',
    'shadow-inset':'--si:0.2;--sic:var(--c-blac);--siy:-8px',
  }
  hoverStyle = {
    'elevation': '',
    'bg-base-100': '',
    'shadow': '--s:1',
  }
  clickStyle = {
    'bg-base-800': '',
    'elevation-base': '--ebs:0s',
    'elevation-active': '--eay:0.5px',
    'text-white': '',
  }
  disabledStyle = {
    'bg-pattern-diagonal': '--pattern-bg:var(--c-200);--pattern-accent:var(--c-300)',
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
  hoverStyle = {
    'bg-base-100': '',
  }
  clickStyle = {
    'bg-base-800': '',
    'elevation-base': '--ebs:0s',
    'elevation-active': '--eay:0.5px',
    'text-white': '',
  }
  disabledStyle = {
    'bg-pattern-diagonal': '--pattern-bg:var(--c-200);--pattern-accent:var(--c-300)'
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
  hoverStyle = {
    'bg-base-100': '',
  }
  clickStyle = {
    'bg-base-800': '',
    'elevation-base': '--ebs:0s',
    'elevation-active': '--eay:0.5px',
    'text-white': '',
  }
  disabledStyle = {
    'text-color': '--tc:var(--c-400)'
  }
}
window.customElements.define('app-layout', CustomAppLayout)
window.customElements.define('app-nav-item', CustomAppNavItem)
window.customElements.define('app-btn', BaseButtton, { extends: 'button' })
window.customElements.define('app-btn-outlined', BaseButttonOutlined, { extends: 'button' })
window.customElements.define('app-btn-ghost', BaseButttonGhost, { extends: 'button' })
