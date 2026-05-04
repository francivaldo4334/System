import { createComponent } from './web-component-factory.js'
createComponent('app-timeline', {
  scoped: true,
  css: `:host {
    display: grid;
    grid-auto-columns: 1fr;
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
    const val = (parseInt(value) || 0);
    if (prop === 'start')
      this.style.gridRowStart = val;
    if (prop === 'duration')
      this.style.gridRowEnd = `span ${val}`;
  }
})

createComponent('c-days', {
  html: '<div class="calendar-grid"></div>',
  props: ['date', 'range', 'onchange'],
  onMount() {
    this._renderId = null;
  },
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
    if (this._renderId) cancelAnimationFrame(this._renderId);
    const year = date.getFullYear();
    const month = date.getMonth();
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const firstDay = new Date(year, month, 1).getDay();
    const totalDays = new Date(year, month + 1, 0).getDate();
    grid.replaceChildren();
    const fragInit = document.createDocumentFragment();
    for (let i = 0; i < firstDay; i++) {
      fragInit.appendChild(document.createElement('div'));
    }
    grid.appendChild(fragInit);
    const btns = [];
    const iterDate = new Date(year, month, 1);
    for (let day = 1; day <= totalDays; day++) {
      iterDate.setDate(day);
      let type = '';
      if (this._check(iterDate, null, 'range', startR, endR)) type = 'range';
      if (this._check(iterDate, today, 'same')) type = 'today';
      if (day === date.getDate()) type = 'selected';
      btns.push({
        day,
        type,
        dateIso: iterDate.toISOString()
      });
    }
    const renderFrame = () => {
      if (btns.length === 0) {
        this._renderId = null;
        return;
      }
      const fragment = document.createDocumentFragment();
      const chunk = btns.splice(0, 7);
      chunk.forEach(({ day, type, dateIso }) => {
        const btn = document.createElement('button');
        btn.type = "button";
        btn.textContent = day;
        if (type) btn.dataset.type = type;
        btn.onclick = () => {
          if (typeof onchange === 'function') onchange(dateIso);
          else new Function('it', onchange)(dateIso);
        };

        fragment.appendChild(btn);
      });

      grid.appendChild(fragment);
      this._renderId = requestAnimationFrame(renderFrame);
    };

    this._renderId = requestAnimationFrame(renderFrame);
  }
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
createComponent('app-assignment', {
  props: [
    'date',
    'servicename',
    'resourcenames',
    'status',
  ],
  scoped: true,
  css: `
    .content {
      display: flex;
      flex-direction: column;
      color: currentColor;
      padding-inline: 1rem;
      padding-block: 0.5rem;
    }
    .date, .service {
      font-weight: bold;
    }
    .status {
      position: absolute;
      display: flex;
      gap: 0.25rem;
      align-items: center;
    }
    .resource {
      padding: 0;
      margin: 0;
    }
  `,
  html: `
   <div class="content">
     <div>
       <span class="date" id="date"></span> /
       <span class="service" id="service_name"></span>
     </div>
     <p id="resource_names" class="resource"></p>
     <div class="status">
       <slot></slot>
     </div>
   </div> 
  `,
  onMount() {
    const {
      date,
      servicename,
      resourcenames,
      //status,
    } = this.getProps();
    this.$('#date').innerText = date;
    this.$('#service_name').innerText = servicename;
    this.$('#resource_names').innerText = resourcenames;
    //this.$('#status-target').innerHTML = status;
  },
  setStatusCentent(){
    
  }
})
