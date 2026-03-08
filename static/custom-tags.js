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

window.customElements.define('c-layout', CustomLayout)
