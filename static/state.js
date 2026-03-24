function createStateManager() {
  const states = new Map();
  const registerState = (name, initialValue) => {
    if (!states.has(name)) {
      states.set(name, { value: initialValue, observers: [] });
    }
  }
  const getSet = (name) => {
    const searchKey = String(name);
    return Array.from(states.entries()).filter(([key]) =>
      key.startsWith(searchKey)
    );
  }
  return {
    remove: (name) => {
      const matches = getSet(name)
      matches.forEach(([n]) => {
        states.delete(n)
      })
    },
    create: (name, initialValue = null) => {
      registerState(name, initialValue)
    },
    createStore: (name, store = {}) => {
      Object.entries(store).forEach(([key, value]) => {
        registerState(`${name}.${key}`, value)
      })
    },
    subscribe: (name, element, attribute = 'textContent', transform = (v) => v) => {
      const state = states.get(name);
      if (!state) return;
      state.observers.push({ el: element, at: attribute, transform });
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
      const matches = getSet(name)
      if (matches.length === 0) return null;
      if (matches.length === 1) {
        return matches[0][1].value;
      }
      return Object.fromEntries(
        matches.map(([key, data]) => [key.replace(`${name}.`, ''), data.value])
      );
    },
  };
}
const $s = createStateManager()
