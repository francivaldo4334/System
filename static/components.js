class AppNavItem extends HTMLElement {
  connectedCallback() {
    const store = this.getAttribute('store')
    const endpoint = this.getAttribute('endpoint')
    const content = this.innerHTML;
    const active = this.hasAttribute('default')
    this.innerHTML = `
      <form is="app-ajax-form"
            store="${store}"
            endpoint="${endpoint}">
          <button class="btn btn-ghost w-full text-start flex items-center gap-x ${active ? 'active' : ''} "
            type = "submit"
            style = "--gx:var(--s2)" > ${content}</button >
      </form >
  `
    this.querySelector('button').addEventListener('click', (e) => {
      if (e.target.classList.contains('active'))
        return e.preventDefault();
      const btns = document.querySelectorAll('form[is="app-ajax-form"] button')
      btns.forEach(btn => {
        btn.classList.remove('active')
      })
      e.target.classList.add('active')
    })
  }
}

customElements.define('app-nav-option', AppNavItem)
