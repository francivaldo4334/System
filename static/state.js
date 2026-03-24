function createStateManager() {
  const states = new Map();
  return {
    remove: (name) => states.delete(name),
    create: (name, initialValue = null) => {
      if (!states.has(name)) {
        states.set(name, { value: initialValue, observers: [] });
      }
    },
    subscribe: (name, selector, attribute = 'textContent', transform = (v) => v) => {
      const state = states.get(name);
      if (!state) return;
      const elements = document.querySelectorAll(selector);
      elements.forEach(el => {
        state.observers.push({ el, at: attribute, transform });
      });
    },

    set: (name, newValue) => {
      const state = states.get(name);
      if (!state) return;
      state.value = newValue;
      state.observers.forEach(obs => {
        const content = obs.transform(newValue, obs.el);
        if (obs.at !== null) obs.el[obs.at] = content;
      });
    },
    get: (name) => {
      const searchKey = String(name);
      const matches = Array.from(states.entries()).filter(([key]) => 
        key.startsWith(searchKey)
      );
      if (matches.length === 0) return null;
      if (matches.length === 1 && matches[0][0] === searchKey) {
        return matches[0][1].value;
      }
      return Object.fromEntries(
        matches.map(([key, data]) => [key.replace(`${name}.`, ''), data.value])
      );
    },
  };
}
const $s = createStateManager()
