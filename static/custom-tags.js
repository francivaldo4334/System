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
  baseStyle = {}
  hoverStyle = {}
  clickStyle = {}
  addStyle(style) {
    Object.entries(style).forEach(([className, styleValue]) => {
      this.classList.add(className);
      this.style.setProperty(...styleValue.split(':'))
    })
  }
  removeStyle(style) {
    Object.entries(style).forEach(([className, styleValue]) => {
      this.classList.remove(className);
      this.style.removeProperty(styleValue.split(':')[0])
    })
  }
  connectedCallback() {
    Object.entries(this.baseStyle).forEach(([className, styleValue]) => {
      this.classList.add(className);
      const [name, value] = styleValue.split(':')
      this.style.setProperty(name, value)
    })

    this.classList.add(
      'min-w',
      'min-h',
      'm-f',
      'bg-base-200',
      'border-f',
      'rounded-xs',

    )
    this.style.setProperty('--minw', 'var(--sm)')
    this.style.setProperty('--minh', 'var(--xs)')
    this.style.setProperty('--mf', '0')

    //HOVER
    this.addEventListener('mouseenter', () => {
      Object.entries(this.hoverStyle).forEach(([className, styleValue]) => {
        this.classList.add(className);
        const [name, value] = styleValue.split(':')
        this.style.setProperty(name, value)
      })
    })
    this.addEventListener('mouseleave', () => {

    })
  }
}
window.customElements.define('app-layout', CustomAppLayout)
window.customElements.define('app-nav-item', CustomAppNavItem)
window.customElements.define('app-btn', CustomButton, { extends: 'button' })
