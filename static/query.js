class CustomAjaxForm extends HTMLFormElement {
  constructor() {
    super();
    this._onSubmit = this._onSubmit.bind(this)
  }
  connectedCallback() {
    const store = this.getAttribute('store')
    if (!store) {
      throw TypeError("'store' is required.")
    }
    this.store = Object.freeze({
      data: `${store}.data`,
      isLoading: `${store}.isLoading`,
      status: `${store}.status`,
      error: `${store}.error`,
    })
    setState(this.store.data, '{}')
    setState(this.store.isLoading, 'false')
    setState(this.store.error, '')
    setState(this.store.status, '')


    this.endpoint = this.getAttribute('endpoint')
    this.method = (this.getAttribute('method') || 'GET').toLowerCase()
    window.addEventListener('submit', this._onSubmit)
  }
  disconnectedCallback() {
    Object.values(this.store).forEach(k => states.delete(k))
    window.removeEventListener('submit', this._onSubmit)
  }
  _onSubmit(event) {
    event.preventDefault();
    setState(this.store.isLoading, 'true')
    fetch(this.endpoint, { method: this.method })
      .then(response => {
        const status = response.status;
        setState(this.store.status, status)
        if (response.ok) {
          response.text().then(data => setState(this.store.data, data))
          return
        }
        response.text().then(data => setState(this.store.error, data))
      })
      .finally(() => setState(this.store.isLoading, 'false'))
  }
}

window.customElements.define('ajax-form', CustomAjaxForm, { extends: 'form' })
