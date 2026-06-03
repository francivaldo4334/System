const queryCacheFactory = () => {
  // Armazena os dados, timestamps e os timers de expiração
  const cache = new Map();
  // Armazena promessas em voo para evitar Race Conditions (Request Collapsing)
  const inFlightRequests = new Map();
  // Armazena as funções de busca (queryFn) originais para permitir o refetch manual
  const registry = new Map();

  const refetch = async (queryKey) => {
    const registered = registry.get(queryKey);
    if (!registered) {
      console.warn(`Nenhuma query registrada para a chave: ${queryKey}`);
      return null;
    }

    // Força a execução ignorando o cache existente
    return executeQuery(queryKey, registered.queryFn, registered.callbacks);
  };

  // Função auxiliar centralizada para gerenciar a execução e callbacks
  const executeQuery = async (queryKey, queryFn, callbacks = {}) => {
    const { onSuccess, onError, onFinally } = callbacks;

    // Se já existe uma requisição idêntica em andamento, reaproveita a mesma promessa
    if (inFlightRequests.has(queryKey)) {
      return inFlightRequests.get(queryKey);
    }

    const promise = (async () => {
      try {
        const data = await queryFn();
        
        // Atualiza o cache com o timestamp atual
        const entry = cache.get(queryKey) || {};
        cache.set(queryKey, {
          ...entry,
          data,
          updatedAt: Date.now(),
        });

        if (typeof onSuccess === 'function') onSuccess(data);
        return data;
      } catch (error) {
        if (typeof onError === 'function') onError(error);
        throw error;
      } finally {
        // Limpa a requisição em voo assim que terminar
        inFlightRequests.delete(queryKey);
        if (typeof onFinally === 'function') onFinally();
      }
    })();

    inFlightRequests.set(queryKey, promise);
    return promise;
  };

  async function useQueryCache(
    queryKey,
    queryFn,
    callbacks = {},
    options = {},
  ) {
    const { enableRefetch:enabled = true, ttl:staleTime = 0 } = options;

    // Se a query estiver desativada, não busca e não retorna dados
    if (!enabled) {
      return null;
    }

    // Registra/atualiza a função e callbacks para uso posterior no refetch
    registry.set(queryKey, { queryFn, callbacks });

    const cachedEntry = cache.get(queryKey);
    const now = Date.now();

    // Verifica se o cache existe e ainda é válido com base no staleTime
    if (cachedEntry && (now - cachedEntry.updatedAt < staleTime)) {
      return cachedEntry.data;
    }

    // Se o cache expirou ou não existe, executa a query
    return executeQuery(queryKey, queryFn, callbacks);
  }

  return {
    use: useQueryCache,
    refetch,
    // Exposto apenas para fins de debug/testes se necessário
    _internal: { cache, registry }
  };
};

const $q = queryCacheFactory();
