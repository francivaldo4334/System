class ParserJson extends HTMLElement {
  getStringValue(value) {
    if (typeof value !== 'object')
      return value
    return JSON.stringify(value)
  }
  setValue(value) {
    try {
      this.data = JSON.parse(value);
      this.render();
    } catch (e) {
      console.error("Erro ao parsear JSON no p-json:", e);
    }
  }
  connectedCallback() {
    const rawValue = this.getAttribute('value');
    const bind = this.dataset.bind;
    if (bind) return
    this.setValue(rawValue)
  }
  static get observedAttributes() {
    return ['value']
  }
  attributeChangedCallback(name, oldValue, newValue) {
    if (name === 'value' && oldValue !== newValue) {
      this.setValue(newValue)
    }
  }
  render() {
    const targets = Array.from(this.querySelectorAll('[data-bind]'))
      .filter(el => el.parentElement.closest('p-json') === this);
    targets.forEach(el => {
      const bind = el.dataset.bind;
      const value = bind ? this.data[bind] : this.data;
      if (el.tagName === "P-JSON") {
        el.setAttribute('value', this.getStringValue(value))
        return
      }

      const at = el?.dataset.at || "textContent";
      if (!Array.isArray(value)) {
        el[at] = this.getStringValue(value)
        return
      }

      const template = el.cloneNode(true);
      const container = el.parentElement;

      el.remove();

      value.forEach(item => {
        const clone = template.cloneNode(true);
        clone[at] = this.getStringValue(item);
        container.appendChild(clone);
      });

    });
  }
}

window.customElements.define('p-json', ParserJson);
