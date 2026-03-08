class CustomForm extends HTMLFormElement {
  constructor() {
    super();
    this._onSubmit = this._onSubmit.bind(this)
  }
  connectedCallback() {
    const key = this.getAttribute('key')
    if (!key) {
      throw TypeError("'key' is required.")
    }
    this.queryKeys = Object.freeze({
      data: `${key}.data`,
      isLoading: `${key}.isLoading`,
      status: `${key}.status`,
      error: `${key}.error`,
    })
    setState(this.queryKeys.data, '{}')
    setState(this.queryKeys.isLoading, 'false')
    setState(this.queryKeys.error, '')
    setState(this.queryKeys.status, '')


    this.url = this.getAttribute('url')
    this.method = (this.getAttribute('method') || 'GET').toLowerCase()
    window.addEventListener('submit', this._onSubmit)
  }
  disconnectedCallback() {
    Object.values(this.queryKeys).forEach(k => states.delete(k))
    window.removeEventListener('submit', this._onSubmit)
  }
  _onSubmit(event) {
    event.preventDefault();
    setState(this.queryKeys.isLoading, 'true')
    fetch(this.url, { method: this.method })
      .then(response => {
        const status = response.status;
        setState(this.queryKeys.status, status)
        if (response.ok) {
          response.text().then(data => setState(this.queryKeys.data, data))
          return
        }
        response.text().then(data => setState(this.queryKeys.error, data))
      })
      .finally(() => setState(this.queryKeys.isLoading, 'false'))
  }
}

window.customElements.define('c-form', CustomForm, { extends: 'form' })
