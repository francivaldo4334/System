const queryCacheFactory = () => {
  // Armazena os dados codificados como string para evitar problemas de referência
  const cache = new Map();
  const inFlightRequests = new Map();

  // O registry agora guarda a chave original (array) para permitir a busca por prefixo
  const registry = new Map();
  // Cache  Desabilitado
  const hoCache = new Map();

  // Função utilitária para serializar arrays de forma consistente
  const serializeKey = (key) => JSON.stringify(Array.isArray(key) ? key : [key]);

  const refetch = async (_queryKey) => {
    const queryKey = Array.isArray(_queryKey) ? _queryKey : [_queryKey];

    const promises = [];

    // Varre o registro para encontrar todas as chaves que iniciam com o prefixo fornecido
    for (const [serializedKey, registered] of registry.entries()) {
      const registeredKey = registered.originalKey;

      // Verifica se a chave registrada possui o prefixo da query informada
      const isMatch = queryKey.every((part, index) => registeredKey[index] === part);

      if (isMatch) {
        promises.push(
          executeQuery(serializedKey, registered.queryFn, registered.callbacks)
        );
      }
    }

    if (promises.length === 0) {
      console.warn(`Nenhuma query encontrada para o prefixo: ${JSON.stringify(queryKey)}`);
      return [];
    }

    // Executa todos os refetches do grupo em paralelo
    return Promise.all(promises);
  };

  const executeQuery = async (serializedKey, queryFn, callbacks = {}) => {
    const { onSuccess, onError, onFinally } = callbacks;

    if (inFlightRequests.has(serializedKey)) {
      return inFlightRequests.get(serializedKey);
    }

    const promise = (async () => {
      try {
        const data = await queryFn();
        if (!hoCache.get(serializedKey)) {
          const entry = cache.get(serializedKey) || {};
          cache.set(serializedKey, {
            ...entry,
            data,
            updatedAt: Date.now(),
          });
        }

        if (typeof onSuccess === 'function') onSuccess(data);
        return data;
      } catch (error) {
        if (typeof onError === 'function') onError(error);
        throw error;
      } finally {
        inFlightRequests.delete(serializedKey);
        if (typeof onFinally === 'function') onFinally();
      }
    })();

    inFlightRequests.set(serializedKey, promise);
    return promise;
  };

  async function useQueryCache(_queryKey, queryFn, callbacks = {}, options = {}) {
    const queryKey = Array.isArray(_queryKey) ? _queryKey : [_queryKey];
    const {
      enableRefetch: enabled = true,
      ttl: staleTime = 0,
      disableCache = False,
    } = options;

    if (!enabled) {
      return null;
    }
    const serializedKey = serializeKey(queryKey);

    // Registra guardando a chave original em formato de array para a lógica do prefixo
    registry.set(serializedKey, { originalKey: queryKey, queryFn, callbacks });
    // Deabilita o cache
    hoCache.set(serializedKey, false)
    if (disableCache) {
      hoCache.set(serializedKey, true)
    }


    const cachedEntry = cache.get(serializedKey);
    const now = Date.now();

    if (cachedEntry && (now - cachedEntry.updatedAt < staleTime)) {
      return cachedEntry.data;
    }

    return executeQuery(serializedKey, queryFn, callbacks);
  }

  return {
    use: useQueryCache,
    refetch,
    _internal: { cache, registry, inFlightRequests }
  };
};

const $q = queryCacheFactory();
