// nav
// footer
// section
// main
class AppLayout extends HTMLDivElement {
  constructor() {
    super();
    this.style.display = 'grid'
    this.style.gridTemplateColumns = 'minmax(0, 15rem) 1fr'
    this.style.width = '100dvw'
    this.style.height = '100dvh'
    this.style.margin = '0'
    this.style.overflow = 'hidden'
  }
}

window.customElements.define('app-layout', AppLayout, { extends: 'div' })
