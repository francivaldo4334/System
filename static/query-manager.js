const queryCacheFactory = () => {
  const _internalCache = new Map();
  const _watchedQueries = new Map();
  const refetch = async (queryKey) => {
      const config = _watchedQueries.get(queryKey)
      await useQueryCache(queryKey, config.url, config.callbacks, config.options);
  }
  window.addEventListener('focus', () => {
    _watchedQueries.forEach(async (config, queryKey) => {
      await useQueryCache(queryKey, config.url, config.callbacks, config.options);
    });
  });
  async function useQueryCache(queryKey, url, callbacks = {}, options = {}) {
    const { onSuccess, onError, onFinally } = callbacks;
    const { ttl = 0, selection = (r) => r.json(), refetchOnFocus = false } = options;
    if (refetchOnFocus) {
      _watchedQueries.set(queryKey, { url, callbacks, options });
    }
    const now = Date.now();
    try {
      if (_internalCache.has(queryKey)) {
        const entry = _internalCache.get(queryKey);
        if (now - entry.timestamp <= ttl) {
          onSuccess?.(entry.data, entry.status);
          return entry.data; 
        }
      }
      const response = await fetch(url);
      if (!response.ok) throw { status: response.status };
      const data = await selection(response);
      _internalCache.set(queryKey, { data, status: response.status, timestamp: now });
      onSuccess?.(data, response.status);
      return data;
    } catch (error) {
      onError?.(error.status ? error : { message: error.message, status: 500 });
      throw error;
    } finally {
      onFinally?.();
    }
  }

  return {
    use: useQueryCache,
    refetch,
  };
};

const $q = queryCacheFactory();
