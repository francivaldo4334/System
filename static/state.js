function createStateManager() {
  const states = new Map();

  // --- Helpers Privados (Encapsulamento e Reuso) ---

  const _getState = (name) => states.get(name);

  const _notify = (state, value, name, oldValue) => {
    state.observers.forEach(obs => {
      const content = obs.transform(value, obs.el, name, oldValue);
      // Atribuição segura: só altera se houver atributo e conteúdo
      if (obs.at !== null && content !== undefined) {
        obs.el[obs.at] = content;
      }
    });
  };

  const _findEntries = (name) => {
    const searchKey = String(name);
    return Array.from(states.entries()).filter(([key]) =>
      key === searchKey || key.startsWith(`${searchKey}.`)
    );
  };

  const _subscribe = (name, element, attribute = 'textContent', transform = (v) => v) => {
      // if (!element) throw new Error(`Subscription failed: Element for "${name}" is null.`);

      const state = _getState(name);
      if (!state) return () => { };

      const observer = { el: element, at: attribute, transform };
      state.observers.push(observer);

      // Execução imediata (Sync inicial)
      const initialContent = transform(state.value, element, name);
      if (attribute !== null && !!initialContent) {
        element[attribute] = initialContent;
      }

      // Retorna função de limpeza (Unsubscribe)
      return () => {
        state.observers = state.observers.filter(obs => obs !== observer);
      };
  }

  // --- API Pública ---

  return {
    create: (name, initialValue = null) => {
      if (!states.has(name)) {
        states.set(name, { value: initialValue, observers: [] });
      }
    },

    createStore: (name, store = {}) => {
      Object.entries(store).forEach(([key, value]) => {
        const fullPath = name ? `${name}.${key}` : key;
        states.set(fullPath, { value, observers: [] });
      });
    },

    set: (name, newValue) => {
      const state = _getState(name);
      if (!state) return;
      state.value = newValue;
      state.oldValue = state.value;
      _notify(state, state.value, name, state.oldValue);
    },

    get: (name) => {
      const matches = _findEntries(name);
      if (matches.length === 0) return null;
      if (matches.length === 1 && matches[0][0] === name) {
        return matches[0][1].value;
      }
      return Object.fromEntries(
        matches.map(([key, data]) => [key.replace(`${name}.`, ''), data.value])
      );
    },

    subscribe: (name, element, attribute = 'textContent', transform = (v) => v) => {
      if (name.endsWith(".*")) {
        const key = name.split(".")[0]
        const states = _findEntries(key)
        return states.map(([name]) => {
          return _subscribe(name, element, attribute, transform)
        })
      }
      return _subscribe(name, element, attribute, transform)
    },

    compute: (name, dependencies, formula) => {
      // O estado computado é um estado comum que nasce via fórmula
      const update = () => {
        const values = dependencies.map(dep => {
          const state = _getState(dep);
          return state ? state.value : null;
        });
        const newValue = formula(...values);

        // Se o estado computado ainda não existe, cria-o
        if (!states.has(name)) {
          states.set(name, { value: newValue, observers: [] });
        } else {
          const state = _getState(name);
          state.oldValue = state.value;
          state.value = newValue;
          _notify(state, newValue, name, state.oldValue);
        }
      };

      // Se inscreve nas dependências
      dependencies.forEach(dep => {
        const depState = _getState(dep);
        if (depState) {
          // Usa um observer "fantasma" (sem elemento) para disparar o update
          depState.observers.push({ el: null, at: null, transform: update });
        }
      });

      update(); // Cálculo inicial
    },

    remove: (name) => {
      _findEntries(name).forEach(([key]) => states.delete(key));
    }
  };
}

const $s = createStateManager();
