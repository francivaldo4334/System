// const loadSheet = () => {
//   const sides = {
//     f: '',
//     x: '-inline',
//     y: '-block',
//     t: '-top',
//     b: '-bottom',
//     l: '-left',
//     r: '-right',
//   };

//   const genUtility = (prefix, prop, unitVar) => {
//     const scales = [1, 2, 3, 4].map(n => {
//       const val = unitVar === '--s' ? `var(--s${n})` : `calc(var(--b-unit) * ${n})`;
//       return `[class^="${prefix}-"][class$="-${n}"] { --v-${prefix}: ${val}; }`;
//     }).join('\n');

//     const rules = Object.entries(sides).map(([s, dir]) => {
//       const value = prefix === 'border'
//         ? `var(--v-border, var(--b-unit)) solid var(--bc, var(--c-100))`
//         : `var(--v-${prefix}, var(--s4))`;

//       return `[class*="${prefix}-${s}"] { ${prop}${dir}: ${value}; }`;
//     }).join('\n');

//     return `${scales}\n${rules}`;
//   };

//   return`
//     .flex { display: flex; }
//     .flex-wrap { flex-wrap: wrap; }
//     .flex-col { flex-direction: column; }
//     .items-center { align-items: center; }
//     .justify-between { justify-content: space-between; }
//     ${genUtility('p', 'padding', '--s')}
//     ${genUtility('m', 'margin', '--s')}
//     ${genUtility('border', 'border', '--b-unit')}
//     [class^="gap-"][class$="-1"] { --g: var(--s1); }
//     [class^="gap-"][class$="-2"] { --g: var(--s2); }
//     [class^="gap-"][class$="-3"] { --g: var(--s3); }
//     [class^="gap-"][class$="-4"] { --g: var(--s4); }
//     .gap-f { gap: var(--g, var(--s4)); }
//     .gap-x { column-gap: var(--g, var(--s4)); }
//     .gap-y { row-gap: var(--g, var(--s4)); }
//   `;
// };


class CustomAppLayout extends HTMLElement {
  constructor() {
    super();
    const shadow = this.attachShadow({ mode: 'open' })
    // font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    shadow.innerHTML = `
    <style>
        :host {
          display: grid;
          grid-template-columns: minmax(0, 240px) 1fr;
          width: 100dvw;
          height: 100dvh;
          margin: 0;
          padding: 0;
          overflow: hidden;
          font-weight: 400;
          font-style: normal;
        }
      </style>
      <slot name="sidebar"></slot>
      <slot name="content"></slot>
    `
  }
}
class CustomAppNavItem extends HTMLElement {
  connectedCallback() {
    const endpoint = this.getAttribute('endpoint')
    const store = this.getAttribute('store')
    this.innerHTML = `
      <form is="ajax-form" endpoint="${endpoint}" store="${store}">
          <button
            type="submit"
            style="
              padding: 0.375rem 0.75rem;
              min-height: 2.25rem;
              width: 100%;
            "
          >
            ${this.innerHTML}
          </button>
      </form>
    `
  }
}

window.customElements.define('app-layout', CustomAppLayout)
window.customElements.define('app-nav-item', CustomAppNavItem)
