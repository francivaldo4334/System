const queryCacheFactory = () => {
  const _internalCache = new Map();
  return async function useQueryCache(queryKey, fn, onSuccess, onError, onFinally, ttl = 0) {
    const now = Date.now();
    try {
      if (_internalCache.has(queryKey)) {
        const { data, timestamp } = _internalCache.get(queryKey);
        const isExpired = now - timestamp > ttl;
        if (!isExpired) {
          if (onSuccess) onSuccess(data);
          return data;
        }
        _internalCache.delete(queryKey);
      }
      const data = await fn();
      _internalCache.set(queryKey, {
        data,
        timestamp: now
      });

      if (onSuccess) onSuccess(data);
      return data;
    } catch (error) {
      if (onError) onError(error);
      throw error;
    } finally {
      onFinally?.()
    }
  };
};

const $q = queryCacheFactory();
