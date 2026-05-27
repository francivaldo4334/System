const requestFactory = () => {
  const handleResponse = async (response) => {
    const isJson = response.headers.get('content-type')?.includes('application/json');
    const data = isJson ? await response.json() : await response.text();
    
    if (!response.ok) {
      const error = new Error(data?.message || `Erro ${response.status}: ${response.statusText}`);
      error.status = response.status;
      error.data = data;
      throw error;
    }
    return data;
  };

  const send = async (url, options = {}) => {
    // 1. Detecta se o corpo da requisição é um FormData
    const isFormData = options.body instanceof FormData;

    // 2. Constrói os cabeçalhos padrão inteligentemente
    const defaultHeaders = isFormData 
      ? {} // Se for FormData, deixa o navegador definir o Content-Type + boundary
      : { 'Content-Type': 'application/json' };

    try {
      const response = await fetch(url, {
        ...options,
        // Garante que o JSON.stringify só ocorra se NÃO for FormData e se houver um corpo
        body: isFormData ? options.body : (options.body ? JSON.stringify(options.body) : undefined),
        headers: {
          ...defaultHeaders,
          ...options.headers,
        },
      });
      return await handleResponse(response);
    } catch (error) {
      console.error(`[Fetch Error] ${options.method || 'GET'} ${url}:`, error);
      throw error;
    }
  };

  // Os métodos POST, PATCH e PUT agora aceitam o objeto puro ou FormData diretamente
  return {
    get: (url, headers = {}) => 
      send(url, { method: 'GET', headers }),
      
    post: (url, body, headers = {}) => 
      send(url, { method: 'POST', body, headers }),
      
    patch: (url, body, headers = {}) => 
      send(url, { method: 'PATCH', body, headers }),

    put: (url, body, headers = {}) => 
      send(url, { method: 'PUT', body, headers }),
      
    delete: (url, headers = {}) => 
      send(url, { method: 'DELETE', headers }),
  };
};

const $r = requestFactory();
