const queryCacheFactory = () => {
  const _internalCache = new Map();
  const _watchedQueries = new Map();
  const refetch = async (queryKey) => {
    const config = _watchedQueries.get(queryKey);
    if (!config) return;
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
    const {
      onSuccess,
      onError,
      onFinally,
    } = callbacks;
    const {
      ttl = 5000,
      refetchOnFocus = false
    } = options;
    if (refetchOnFocus) {
      _watchedQueries.set(queryKey, { queryFn, callbacks, options });
    }

    const now = Date.now();

    try {
      if (_internalCache.has(queryKey)) {
        const entry = _internalCache.get(queryKey);
        if (now - entry.timestamp <= ttl) {
          onSuccess?.(entry.data);
          return entry.data;
        }
      }
      const data = await queryFn();
      _internalCache.set(queryKey, { data, timestamp: Date.now() });
      onSuccess?.(data);
      return data;
    } catch (error) {
      onError?.(error);
      throw error;
    } finally {
      onFinally?.();
    }
  }

  return { use: useQueryCache, refetch };
};
const $q = queryCacheFactory();
