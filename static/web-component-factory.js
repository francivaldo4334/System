const createComponent = (tagName,{
  html, css,
  scoped = false,
  props = [],
  methods = {},
}) => {
  const template = document.createElement('template')
  template.innerHTML = `
    <style>${css}</style>
    ${html}
  `
  class CustomElement extends HTMLElement {
    constructor(){
      super();
      if (scoped){
        this.attachShadow({mode: 'open'})
        this.shadowRoot.appendChild(template.content.cloneNode(true))
      }
      else {
        this.appendChild(template.content.cloneNode(true))
      }
      Object.assign(this, methods)
    }
    getProps(){
      return Object.fromEntries(props.map(prop => [
        prop,
        this.getAttribute(prop)
      ]))
    }
    static get observedAttributes(){
      return props
    }
    attributeChangedCallback(name, oldValue, newValue){
      if (oldValue === newValue || !this.onUpdate)
        return
      this.onUpdate(name, newValue);
    }
    connectedCallback(){
      if (!this.onMount) return;
      this.onMount();
    }
    disconnectedCallback(){
      if (!this.onUmount) return;
      this.onUmount();
    }
    $(selector){
      return this.shadowRoot.querySelector(selector)
    }
  }
  if (!customElements.get(tagName)) {
    customElements.define(tagName, CustomElement)
  }
}
