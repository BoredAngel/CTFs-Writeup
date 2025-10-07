import React, { useEffect, useState } from 'react'
import { Routes, Route, Link, useNavigate, useLocation, useParams } from 'react-router-dom'
import { api } from './api'

function Navbar({ user, onLogout }) {
  return (
    <header className="flex items-center justify-between p-4">
      <Link to="/" className="text-2xl font-bold">Social Media</Link>
      <nav className="flex items-center gap-3">
        {user ? (
          <>
            <span className="opacity-70">Hi, {user.username}</span>
            <button onClick={onLogout} className="px-3 py-1 rounded-lg bg-black text-white text-sm">Logout</button>
          </>
        ) : (
          <>
            <Link className="underline" to="/login">Login</Link>
            <Link className="underline" to="/register">Register</Link>
          </>
        )}
      </nav>
    </header>
  )
}

function PostCard({ post }) {
  const ts = post.timestamp ? new Date(parseInt(post.timestamp, 10) * 1000) : null
  return (
    <Link to={`/post/${post.id}`} className="block rounded-2xl shadow p-4 bg-white">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-lg">{post.title}</h3>
        {ts && <span className="text-sm opacity-60">{ts.toLocaleString()}</span>}
      </div>
      <p className="text-sm opacity-80 mt-1">by {post.author}</p>
      <p className="mt-2 line-clamp-2 opacity-80">{post.content}</p>
    </Link>
  )
}

function Home({ user }) {
  const [posts, setPosts] = useState([])
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [err, setErr] = useState('')

  const load = async () => {
    try {
      setErr('')
      const data = await api.listPosts()
      setPosts(Array.isArray(data) ? data : [])
    } catch (e) {
      setPosts([])
      setErr(e.message)
    }
  }

  useEffect(() => {
    if (user) load()
    else setPosts([])
  }, [user])

  const create = async (e) => {
    e.preventDefault()
    setErr('')
    try {
      await api.createPost(title, content)
      setTitle(''); setContent('')
      await load()
    } catch (e) {
      setErr(e.message)
    }
  }

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-6">
      {user ? (
        <section className="bg-white rounded-2xl shadow p-4">
          <h2 className="font-semibold mb-2">Create a Post</h2>
          {err && <div className="text-red-600 text-sm mb-2">{err}</div>}
          <form onSubmit={create} className="space-y-2">
            <input className="w-full border rounded-xl p-2" placeholder="Title" value={title} onChange={e=>setTitle(e.target.value)} required />
            <textarea className="w-full border rounded-xl p-2" placeholder="Write something..." rows={4} value={content} onChange={e=>setContent(e.target.value)} required />
            <button className="px-4 py-2 rounded-xl bg-black text-white" type="submit">Post</button>
          </form>
        </section>
      ) : (
        <div className="rounded-xl border border-amber-300 bg-amber-50 p-3 text-amber-900">
          Login to create posts. <Link className="underline" to="/login">Login</Link>
        </div>
      )}

      <section className="space-y-3">
        <h2 className="font-semibold">{user ? 'Your Posts' : 'Latest Posts'}</h2>
        {posts.map(p => <PostCard key={p.id} post={p} />)}
      </section>
    </div>
  )
}

function Login({ setUser }) {
  const [u, setU] = useState('')
  const [p, setP] = useState('')
  const [err, setErr] = useState('')
  const nav = useNavigate()
  const loc = useLocation()
  const next = new URLSearchParams(loc.search).get('next') || '/'

  const submit = async (e) => {
    e.preventDefault(); setErr('')
    try {
      const r = await api.login(u, p)
      setUser({ username: r.username })
      nav(next)
    } catch (e) { setErr(e.message) }
  }

  return (
    <div className="max-w-sm mx-auto p-4 space-y-4">
      <h2 className="text-xl font-semibold">Login</h2>
      {err && <div className="text-red-600 text-sm">{err}</div>}
      <form onSubmit={submit} className="space-y-2">
        <input className="w-full border rounded-xl p-2" placeholder="Username" value={u} onChange={e=>setU(e.target.value)} required />
        <input type="password" className="w-full border rounded-xl p-2" placeholder="Password" value={p} onChange={e=>setP(e.target.value)} required />
        <button className="px-4 py-2 rounded-xl bg-black text-white w-full" type="submit">Login</button>
      </form>
      <div className="text-sm">No account? <Link className="underline" to="/register">Register</Link></div>
    </div>
  )
}

function Register({ setUser }) {
  const [u, setU] = useState('')
  const [p, setP] = useState('')
  const [err, setErr] = useState('')
  const nav = useNavigate()

  const submit = async (e) => {
    e.preventDefault(); setErr('')
    try {
      const r = await api.register(u, p)
      setUser({ username: r.username })
      nav('/')
    } catch (e) { setErr(e.message) }
  }

  return (
    <div className="max-w-sm mx-auto p-4 space-y-4">
      <h2 className="text-xl font-semibold">Register</h2>
      {err && <div className="text-red-600 text-sm">{err}</div>}
      <form onSubmit={submit} className="space-y-2">
        <input className="w-full border rounded-xl p-2" placeholder="Username" value={u} onChange={e=>setU(e.target.value)} required />
        <input type="password" className="w-full border rounded-xl p-2" placeholder="Password" value={p} onChange={e=>setP(e.target.value)} required />
        <button className="px-4 py-2 rounded-xl bg-black text-white w-full" type="submit">Create Account</button>
      </form>
      <div className="text-sm">Have an account? <Link className="underline" to="/login">Login</Link></div>
    </div>
  )
}

function PostDetail({ user }) {
  const [post, setPost] = useState(null)
  const [err, setErr] = useState('')
  const nav = useNavigate()
  const { id } = useParams()                

  const load = async () => {
    try { setPost(await api.getPost(id)) } catch (e) { setErr(e.message) }
  }
  useEffect(() => { load() }, [id])         

  const del = async () => {
    try {
      await api.deletePost(id)
      nav('/')
    } catch (e) { setErr(e.message) }
  }

  if (!post) return <div className="max-w-3xl mx-auto p-4">Loading… {err && <span className="text-red-600">{err}</span>}</div>

  const owner = user && post.user_id && user.username === post.author

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-4">
      <div className="rounded-2xl shadow p-4 bg-white">
        <h2 className="text-2xl font-bold">{post.title}</h2>
        <div className="opacity-70">by {post.author}</div>
        <div className="mt-2 line-clamp-2 opacity-80" dangerouslySetInnerHTML={{ __html: post.content }} />
      </div>
      {owner && (
        <div className="flex gap-2">
          <Link to={`/post/${post.id}/edit`} className="px-3 py-1 rounded-lg bg-black text-white">Edit</Link>
          <button onClick={del} className="px-3 py-1 rounded-lg border">Delete</button>
        </div>
      )}
      {err && <div className="text-red-600 text-sm">{err}</div>}
    </div>
  )
}

function PostEdit({ user }) {
  const nav = useNavigate()
  const { id } = useParams()                
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [err, setErr] = useState('')

  useEffect(() => {
    (async () => {
      try {
        const p = await api.getPost(id)
        setTitle(p.title); setContent(p.content)
      } catch (e) { setErr(e.message) }
    })()
  }, [id])

  const save = async (e) => {
    e.preventDefault(); setErr('')
    try {
      const r = await api.updatePost(id, { title, content })
      const nextId = r?.id || id
      nav(`/post/${nextId}`)
    } catch (e) { setErr(e.message) }
  }

  if (!user) return <div className="max-w-3xl mx-auto p-4">Login required.</div>

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-4">
      <h2 className="text-xl font-semibold">Edit Post</h2>
      {err && <div className="text-red-600 text-sm">{err}</div>}
      <form onSubmit={save} className="space-y-2">
        <input className="w-full border rounded-xl p-2" value={title} onChange={e=>setTitle(e.target.value)} required />
        <textarea className="w-full border rounded-xl p-2" rows={6} value={content} onChange={e=>setContent(e.target.value)} required />
        <div className="flex gap-2">
          <button className="px-4 py-2 rounded-xl bg-black text-white">Save</button>
          <Link to={`/post/${id}`} className="px-4 py-2 rounded-xl border">Cancel</Link>
        </div>
      </form>
    </div>
  )
}

export default function App() {
  const [user, setUser] = useState(null)

  useEffect(() => {
    (async () => {
      try {
        const s = await api.session()
        setUser(s.authenticated ? { username: s.username, user_id: s.user_id } : null)
      } catch {
        setUser(null)
      }
    })()
  }, [])

  const logout = async () => {
    await api.logout()
    setUser(null)
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <Navbar user={user} onLogout={logout} />
      <Routes>
        <Route path="/" element={<Home user={user} />} />
        <Route path="/login" element={<Login setUser={setUser} />} />
        <Route path="/register" element={<Register setUser={setUser} />} />
        <Route path="/post/:id" element={<PostDetail user={user} />} />
        <Route path="/post/:id/edit" element={<PostEdit user={user} />} />
      </Routes>
    </div>
  )
}
