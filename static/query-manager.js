const queryCacheFactory = () => {
  const _internalCache = new Map();
  return async function useQueryCache(queryKey, url, onSuccess, onError, onFinally, ttl = 0,selection = (r) => r.json() ) {
    const now = Date.now();
    try {
      if (_internalCache.has(queryKey)) {
        const { data, status, timestamp } = _internalCache.get(queryKey);
        if (now - timestamp <= ttl) {
          onSuccess?.(data, status);
          return response;
        }
        _internalCache.delete(queryKey);
      }
      const response = await fetch(url);
      const isSuccess = response.status >= 200 && response.status < 300;

      if (isSuccess) {
        let data;
          data = await selection(response)
        _internalCache.set(queryKey, { data, status: response.status, timestamp: now });
        onSuccess?.(data, response.status);
      } else {
        const errorContext = { 
          status: response.status,
          data: response.data 
        };
        throw errorContext;
      }
      return response;
    } catch (error) {
      if (onError) {
        onError(error.status ? error : { message: error.message, status: 500 });
      }
      throw error;
    } finally {
      onFinally?.();
    }
  };
};

const $q = queryCacheFactory();
