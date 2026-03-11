class CustomAppLayout extends HTMLElement {
  constructor() {
    super();
    const shadow = this.attachShadow({ mode: 'open' })
    // font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    shadow.innerHTML = `
    <style>
        :host {
          display: grid;
          grid-template-columns: minmax(0, 240px) 1fr;
          width: 100dvw;
          height: 100dvh;
          margin: 0;
          padding: 0;
          overflow: hidden;
          font-weight: 400;
          font-style: normal;
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
    this.innerHTML = `
      <form is="ajax-form" endpoint="${endpoint}" store="${store}">
          <button
            type="submit"
            style="
              padding: 0.375rem 0.75rem;
              min-height: 2.25rem;
              width: 100%;
            "
          >
            ${this.innerHTML}
          </button>
      </form>
    `
  }
}
class CustomButton extends HTMLButtonElement {
  baseStyle = {};
  hoverStyle = {};
  clickStyle = {};

  constructor() {
    super();
    this._onPres = this._onPres.bind(this);
    this._onRelease = this._onRelease.bind(this);
    this._onHoverIn = this._onHoverIn.bind(this);
    this._onHoverOut = this._onHoverOut.bind(this);
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
    this._applyStyles(this.clickStyle);
  }

  _onRelease() {
    this._clearStyles(this.clickStyle);
  }

  _onHoverIn() {
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
    'bg-base-50': '',
    'text-md': '',
    'font-semibold': '',
    'border-f': '--bfc:var(--c-300)',
    'elevation': '',
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
}

window.customElements.define('app-layout', CustomAppLayout)
window.customElements.define('app-nav-item', CustomAppNavItem)
window.customElements.define('app-btn', BaseButtton, { extends: 'button' })
