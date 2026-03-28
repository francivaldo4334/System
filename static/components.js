import { createComponent } from './web-component-factory.js'
createComponent('app-timeline', {
  scoped: true,
  css: `:host {
    display: grid;
    grid-auto-columns: var(--tab-space) 1fr;
    gap: 0 0.2rem;
    grid-auto-rows: var(--slotunit);
    position: relative; 
  }`,
  html: `<slot></slot>`,
  props: ['slotunit'],
  onUpdate(prop, value) {
    this.style.setProperty('--slotunit', value)
  }
})
createComponent('app-slot', {
  scoped: true,
  html: "<span><slot></slot></span>",
  props: ['start', 'duration'],
  css: ` :host { display: block; } `,
  onUpdate(prop, value) {
    const val = parseInt(value) || 1;
    if (prop === 'start')
      this.style.gridRowStart = val;
    if (prop === 'duration')
      this.style.gridRowEnd = `span ${val}`;
  }
})

createComponent('c-days', {
  html: '<div class="calendar-grid"></div>',
  props: ['date', 'range', 'onchange'],
  onUpdate(prop, value) {
    this.setAttribute(prop, value)
    const dateIso = this.getAttribute('date')
    const rangeIso = this.getAttribute('range')
    const onchange = this.getAttribute('onchange')
    if (!dateIso || !rangeIso) return;
    const date = new Date(dateIso)
    const [init, end] = rangeIso.split(',').map(iso => new Date(iso))
    this.render(date, init, end, onchange)
  },
  _check(date, other, type, start, end) {
    const d = new Date(date).setHours(0, 0, 0, 0);
    const o = new Date(other).setHours(0, 0, 0, 0);
    if (type === 'same') return d === o;
    if (type === 'range') {
      return start && end && d >= start && d <= end;
    }
  },
  render(date, startR, endR, onchange) {
    const grid = this.$('.calendar-grid');
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1).getDay();
    const totalDays = new Date(year, month + 1, 0).getDate();
    const today = new Date();
    const frag = document.createDocumentFragment();
    for (let i = 0; i < firstDay; i++) {
      frag.appendChild(document.createElement('div'));
    }
    for (let day = 1; day <= totalDays; day++) {
      const iterDate = new Date(year, month, day);
      const btn = document.createElement('button');
      btn.type = "button"
      btn.textContent = day;
      if (this._check(iterDate, null, 'range', startR, endR)) btn.dataset.type = 'range';
      if (this._check(iterDate, today, 'same')) btn.dataset.type = 'today';
      if (day === date.getDate()) btn.dataset.type = 'selected';
      btn.onclick = () => {
        new Function('it', onchange)(iterDate.toISOString())
      };
      frag.appendChild(btn);
    }

    grid.innerHTML = '';
    grid.appendChild(frag);
  },
})
createComponent('exec-mount', {
  base: HTMLScriptElement,
  baseName: 'script',
  onMount() {
    if (!this.innerText.trim()) return;
    const runner = document.createElement('script');
    runner.textContent = this.innerText;
    document.head.appendChild(runner);
    document.head.removeChild(runner);
  }
})
createComponent('exec-umount', {
  base: HTMLScriptElement,
  baseName: 'script',
  onUmount() {
    if (!this.innerText.trim()) return;
    const runner = document.createElement('script');
    runner.textContent = this.innerText;
    document.head.appendChild(runner);
    document.head.removeChild(runner);
  }
})
