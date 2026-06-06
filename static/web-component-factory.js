export function createComponent(tagName, {
  html, css,
  scoped = false,
  props = [],
  base = HTMLElement,
  baseName = null,
  ...methods
}) {
  const template = document.createElement('template')
  template.innerHTML = `
    ${css ? '<style>' + css + '</style>' : ''}
    ${html ?? ''}
  `
  class CustomElement extends base {
    constructor() {
      super();
      // Inicializa o Shadow DOM imediatamente (permitido por lei)
      if (scoped) {
        this.attachShadow({ mode: 'open' })
        this.shadowRoot.appendChild(template.content.cloneNode(true))
      }

      Object.assign(this, methods)
      this.onInit?.()
    }

    getProps() {
      return Object.fromEntries(props.map(prop => [
        prop,
        this.getAttribute(prop)
      ]))
    }

    static get observedAttributes() {
      return props
    }

    attributeChangedCallback(name, oldValue, newValue) {
      if (oldValue === newValue || !this.onUpdate)
        return
      // Pequena proteção: só atualiza se o DOM já estiver pronto (ou se for scoped)
      this.onUpdate(name, newValue);
    }

    connectedCallback() {
      // ✅ CORREÇÃO: Injeta o HTML comum apenas quando o elemento é anexado à página
      if (!scoped && !this.hasChildNodes()) {
        this.appendChild(template.content.cloneNode(true));

        // Força uma atualização inicial das propriedades que já vieram no elemento
        props.forEach(prop => {
          if (this.hasAttribute(prop)) {
            this.onUpdate(prop, this.getAttribute(prop));
          }
        });
      }

      if (!this.onMount) return;
      this.onMount();
    }

    disconnectedCallback() {
      if (!this.onUmount) return;
      this.onUmount();
    }

    $(selector) {
      if (!scoped) return this.querySelector(selector)
      return this.shadowRoot.querySelector(selector)
    }
  }

  if (!customElements.get(tagName)) {
    if (typeof baseName === 'string') {
      customElements.define(tagName, CustomElement, { extends: baseName })
      return;
    }
    customElements.define(tagName, CustomElement)
  }
}
