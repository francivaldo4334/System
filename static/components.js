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
createComponent('feedback-response', {
  scoped: false,
  props: [
    'text',
    'date',
  ],
  html: `
    <div class="bg-primary/5 border-l-4 border-primary p-3 rounded-r-lg space-y-1">
        <div class="flex justify-between items-center">
            <span class="text-xs font-bold text-primary">
                {%trans "Response"%}
            </span>
            <span class="text-[10px] text-base-content/40" id="id_feedback_response_created_at">
            </span>
        </div>
        <p class="text-xs text-base-content/90 leading-relaxed" id="id_feedback_response_text"></p>
    </div>
  `,
  onUpdate(name, value) {
    if (name === 'text') {
      const content = this.$('#id_feedback_response_text');
      content.innerText = value
    }
    if (name === 'date') {
      const content = this.$('#id_feedback_response_created_at');
      content.innerText = value
    }
  }
})
createComponent('app-fb', {
  scoped: false,
  html: `
<div class="collapse collapse-arrow bg-base-100 border border-base-200 rounded-xl shadow-sm">
      <input type="radio" name="feedback-accordion" checked="checked" />
      <div class="collapse-title p-4 pr-10">
          <div class="flex flex-wrap items-center gap-1.5 mb-2">
              <span class="badge badge-sm badge-info font-medium" id="id_feedback_category"></span>
              <span class=" badge badge-sm badge-outline font-semibold" id="id_feedback_status"></span>
          </div>
          <div class="text-[10px] text-base-content/50 mt-1 flex gap-2">
              <span>
                  <span id="id_feedback_create_label">
                  </span>
                  <span id="id_feedback_created_at"></span>
              </span>
              <span>•</span>
              <span class="text-warning-content/80 font-medium">
                  <span id="id_feedback_update_label">
                  </span>
                  <span id="id_feedback_updated_at"></span>
              </span>
          </div>
      </div>
      <div class="collapse-content px-4 pb-4 text-sm space-y-3">
          <div class="p-3 bg-base-200/60 rounded-lg text-xs text-base-content/80 italic">
              "
                <span id="id_feedback_text"></span>
              "
          </div>
          <!-- Linha do tempo interna da resposta -->
          <div id="id_response_content">
          </div>
      </div>
  </div>
`,
  props: [
    "create_label",
    "update_label",
    "create_at",
    "update_at",
    "category",
    "status",
    "text",
  ],
  onUpdate(name, value) {
    let el = null;
    if (name === "create_label")
      el = this.$("#id_feedback_create_label")
    if (name === "update_label")
      el = this.$("#id_feedback_update_label")
    if (name === "category")
      el = this.$("#id_feedback_category")
    if (name === "status")
      el = this.$("#id_feedback_status")
    if (name === "text")
      el = this.$("#id_feedback_text")
    if (name === "create_at")
      el = this.$("#id_feedback_created_at")
    if (name === "update_at")
      el = this.$("#id_feedback_updated_at")
    if (el) el.innerText = value

  },
  addResponse(response) {
    const { text, date } = response;
    const content = this.$('#id_response_content');

    // Cria o elemento corretamente
    const resp = document.createElement('feedback-response');

    // ✅ Define os atributos na variável CORRETA (resp)
    resp.setAttribute('text', text || '');
    resp.setAttribute('date', date || '');

    content.appendChild(resp);
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
  setStatusCentent() {

  }
})
