// const queryCacheFactory = () => {
//   const _internalCache = new Map();
//   const _fetchingQueries = new Map();
//   const _watchedQueries = new Map();
//   const refetch = async (queryKey) => {
//     const config = _watchedQueries.get(queryKey);
//     if (!config) return;
//     _internalCache.delete(queryKey)
//     return await useQueryCache(queryKey, config.queryFn, config.callbacks, config.options);
//   };
//   window.addEventListener('focus', () => {
//     _watchedQueries.forEach(async (config, queryKey) => {
//       if (config.options.refetchOnFocus) {
//         await useQueryCache(queryKey, config.queryFn, config.callbacks, config.options);
//       }
//     });
//   });
//   async function useQueryCache(queryKey, queryFn, callbacks = {}, options = {}) {
//     const {
//       onSuccess,
//       onError,
//       onFinally,
//     } = callbacks;
//     const {
//       ttl = 0,
//       refetchOnFocus = false,
//       enableRefetch = false,
//     } = options;
//     if (refetchOnFocus || enableRefetch) {
//       _watchedQueries.set(queryKey, { queryFn, callbacks, options });
//     }

//     const now = Date.now();

//     try {
//       if (_internalCache.has(queryKey)) {
//         const entry = _internalCache.get(queryKey);
//         if (now - entry.timestamp <= ttl) {
//           onSuccess?.(entry.data);
//           return entry.data;
//         }
//       }
//       const data = await queryFn();
//       _internalCache.set(queryKey, { data, timestamp: Date.now() });
//       onSuccess?.(data);
//       return data;
//     } catch (error) {
//       onError?.(error);
//       throw error;
//     } finally {
//       onFinally?.();
//     }
//   }

//   return { use: useQueryCache, refetch };
// };
const queryCacheFactory = () => {
  const _internalCache = new Map();
  // _fetchingQueries armazenará as Promises em andamento
  const _fetchingQueries = new Map();
  const _watchedQueries = new Map();

  const refetch = async (queryKey) => {
    const config = _watchedQueries.get(queryKey);
    if (!config) return;

    // Limpamos o cache físico para forçar a nova busca
    _internalCache.delete(queryKey);
    return await useQueryCache(queryKey, config.queryFn, config.callbacks, config.options);
  };

  window.addEventListener('focus', () => {
    _watchedQueries.forEach(async (config, queryKey) => {
      if (config.options.refetchOnFocus) {
        await useQueryCache(queryKey, config.queryFn, config.callbacks, config.options);
      }
    });
  });

  async function useQueryCache(queryKey, queryFn, callbacks = {}, options = {}) {
    const { onSuccess, onError, onFinally } = callbacks;
    const { ttl = 0, refetchOnFocus = false, enableRefetch = false } = options;

    if (refetchOnFocus || enableRefetch) {
      _watchedQueries.set(queryKey, { queryFn, callbacks, options });
    }

    const now = Date.now();

    // 1. Verificação de Cache Válido (Dados prontos)
    if (_internalCache.has(queryKey)) {
      const entry = _internalCache.get(queryKey);
      if (now - entry.timestamp <= ttl) {
        onSuccess?.(entry.data);
        return entry.data;
      }
    }

    // 2. Verificação de Deduping (Query já em vôo)
    if (_fetchingQueries.has(queryKey)) {
      // Retorna a promessa existente em vez de criar uma nova
      const result = await _fetchingQueries.get(queryKey);
      onSuccess?.(result); // Garante que toda chamada 'use' execute seu callback
      return result;
    }

    // 3. Execução da Query
    const fetchPromise = (async () => {
      try {
        const data = await queryFn();
        _internalCache.set(queryKey, { data, timestamp: Date.now() });
        onSuccess?.(data);
        return data;
      } catch (error) {
        onError?.(error);
        throw error;
      } finally {
        // Limpa a marcação de 'fetching' independente do resultado
        _fetchingQueries.delete(queryKey);
        onFinally?.();
      }
    })();

    // Registra a promessa no mapa de execuções ativas
    _fetchingQueries.set(queryKey, fetchPromise);

    return fetchPromise;
  }

  return {
    use: useQueryCache,
    refetch,
    // Exposto para monitoramento/debugging externo se necessário
    isFetching: (queryKey) => _fetchingQueries.has(queryKey)
  };
};
const $q = queryCacheFactory();
