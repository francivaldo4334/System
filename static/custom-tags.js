class CustomLayout extends HTMLElement {
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
class CustomSidebarItem extends HTMLElement {
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

window.customElements.define('c-layout', CustomLayout)
window.customElements.define('c-sidebar-item', CustomSidebarItem)
