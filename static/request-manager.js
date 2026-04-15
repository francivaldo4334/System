const requestFactory = () => {
  const handleResponse = async (response) => {
    const isJson = response.headers.get('content-type')?.includes('application/json');
    const data = isJson ? await response.json() : await response.text();
    if (!response.ok) {
      const error = new Error(data.message || `Erro ${response.status}: ${response.statusText}`);
      error.status = response.status;
      error.data = data;
      throw error;
    }
    return data;
  };
  const send = async (url, options = {}) => {
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });
      return await handleResponse(response);
    } catch (error) {
      console.error(`[Fetch Error] ${options.method || 'GET'} ${url}:`, error);
      throw error;
    }
  };
  return {
    get: (url, headers = {}) => 
      send(url, { method: 'GET', headers }),
      
    post: (url, body, headers = {}) => 
      send(url, { method: 'POST', body: JSON.stringify(body), headers }),
      
    patch: (url, body, headers = {}) => 
      send(url, { method: 'PATCH', body: JSON.stringify(body), headers }),

    put: (url, body, headers = {}) => 
      send(url, { method: 'PUT', body: JSON.stringify(body), headers }),
      
    delete: (url, headers = {}) => 
      send(url, { method: 'DELETE', headers }),
  };
};
const $r = requestFactory()
