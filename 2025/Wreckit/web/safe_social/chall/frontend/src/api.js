const JSON_HEADERS = { 'Content-Type': 'application/json' }

async function request(path, opts = {}) {
  const res = await fetch(path, {
    credentials: 'include',
    ...opts,
    headers: { ...(opts.headers || {}), ...(opts.body && JSON_HEADERS) }
  })
  let data = null
  try { data = await res.json() } catch {}
  if (!res.ok) {
    const msg = data?.error || `HTTP ${res.status}`
    const err = new Error(msg); err.status = res.status; err.data = data
    throw err
  }
  return data
}

export const api = {
  session: () => request('/api/session'),
  login: (username, password) => request('/api/login', { method: 'POST', body: JSON.stringify({ username, password }) }),
  register: (username, password) => request('/api/register', { method: 'POST', body: JSON.stringify({ username, password }) }),
  logout: () => request('/api/logout', { method: 'POST' }),

  listPosts: () => request('/api/posts'),
  getPost: (id) => request(`/api/posts/${id}`),
  createPost: (title, content) => request('/api/posts', { method: 'POST', body: JSON.stringify({ title, content }) }),
  updatePost: (id, payload) => request(`/api/posts/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deletePost: (id) => request(`/api/posts/${id}`, { method: 'DELETE' })
}
