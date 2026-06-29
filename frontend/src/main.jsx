import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { ArrowRight, Bot, CalendarDays, CheckCircle, Clock, LayoutDashboard, LogOut, RefreshCw, Search, Send, ShieldCheck, Sparkles, Trash2, Users, XCircle } from 'lucide-react';
import './style.css';

const API = 'http://127.0.0.1:8001';
const statuses = ['Pending', 'Confirmed', 'Cancelled', 'Rescheduled'];
const leadStatuses = ['New', 'Contacted', 'Qualified', 'Won', 'Lost'];

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function api(path, options = {}, token) {
  const response = await fetch(API + path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(token),
      ...(options.headers || {}),
    },
  });
  if (!response.ok) throw new Error(await response.text());
  return response.status === 204 ? null : response.json();
}

function App() {
  const [page, setPage] = useState('home');
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [stats, setStats] = useState({});
  const [leads, setLeads] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [notice, setNotice] = useState('');

  const refresh = async () => {
    if (!token) return;
    try {
      const [nextStats, nextLeads, nextAppointments] = await Promise.all([
        api('/dashboard/stats', {}, token),
        api('/leads', {}, token),
        api('/appointments', {}, token),
      ]);
      setStats(nextStats);
      setLeads(nextLeads);
      setAppointments(nextAppointments);
      setNotice('');
    } catch {
      localStorage.removeItem('token');
      setToken(null);
      setNotice('Admin session expired. Please log in again.');
    }
  };

  useEffect(() => { refresh(); }, [token]);

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setPage('home');
  };

  return <>
    <Nav page={page} setPage={setPage} token={token} logout={logout} />
    <main>
      {notice && <div className="notice">{notice}</div>}
      {page === 'home' && <Home setPage={setPage} />}
      {page === 'chat' && <Chat />}
      {page === 'book' && <Booking />}
      {page === 'login' && <Login setToken={setToken} setPage={setPage} />}
      {page === 'admin' && token && <Admin stats={stats} leads={leads} appointments={appointments} refresh={refresh} token={token} />}
      {page === 'admin' && !token && <Login setToken={setToken} setPage={setPage} />}
    </main>
  </>;
}

function Nav({ page, setPage, token, logout }) {
  return <nav>
    <button className="brand" onClick={() => setPage('home')}><Bot /> AptlyAI</button>
    <button className={page === 'chat' ? 'active' : ''} onClick={() => setPage('chat')}>Chat</button>
    <button className={page === 'book' ? 'active' : ''} onClick={() => setPage('book')}>Book</button>
    {token ? <>
      <button className={page === 'admin' ? 'active' : ''} onClick={() => setPage('admin')}><ShieldCheck size={16} /> Admin</button>
      <button onClick={logout}><LogOut size={16} /> Logout</button>
    </> : <button className={page === 'login' ? 'active' : ''} onClick={() => setPage('login')}>Admin Login</button>}
  </nav>;
}

function Home({ setPage }) {
  return <section className="hero">
    <div>
      <p className="badge"><Sparkles size={15} /> AI Booking Workspace</p>
      <h1>Turn every chat into a booked appointment.</h1>
      <p>A polished SaaS-style workflow for client conversations, public booking, CRM follow-up, email confirmation, and Google Calendar event creation.</p>
      <div className="actions">
        <button className="primary" onClick={() => setPage('chat')}>Start Chat <ArrowRight size={16} /></button>
        <button onClick={() => setPage('book')}>Book Appointment</button>
      </div>
    </div>
    <div className="hero-panel">
      <div className="panel-top">
        <span>Pipeline</span>
        <b>Live Demo</b>
      </div>
      <div className="flow-row"><CheckCircle size={18} /> Capture lead details</div>
      <div className="flow-row"><CalendarDays size={18} /> Create appointment records</div>
      <div className="flow-row"><Send size={18} /> Send confirmation updates</div>
      <div className="flow-row"><ShieldCheck size={18} /> Manage CRM in admin</div>
    </div>
  </section>;
}

function Chat() {
  const [messages, setMessages] = useState([{ sender: 'bot', text: 'Hello! I can help you book an appointment. May I have your full name?' }]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);

  const send = async () => {
    if (!input.trim() || busy) return;
    const text = input.trim();
    setInput('');
    setBusy(true);
    setMessages(items => [...items, { sender: 'user', text }]);
    try {
      const data = await api('/chat', { method: 'POST', body: JSON.stringify({ message: text }) });
      setMessages(items => [...items, { sender: 'bot', text: data.reply }]);
    } catch {
      setMessages(items => [...items, { sender: 'bot', text: 'Backend is not connected. Please start the FastAPI server.' }]);
    } finally {
      setBusy(false);
    }
  };

  return <section>
    <PageTitle icon={<Bot />} title="AI Booking Chat" subtitle="Guide visitors through the first step of scheduling a service call." />
    <div className="chatbox">{messages.map((m, i) => <div key={i} className={'msg ' + m.sender}>{m.text}</div>)}</div>
    <div className="chatinput">
      <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && send()} placeholder="Ask about booking, pricing, or availability..." />
      <button className="primary" onClick={send} disabled={busy}><Send size={16} /> Send</button>
    </div>
  </section>;
}

function Booking() {
  const initial = { name: '', email: '', phone: '', service: 'AI chatbot demo', appointment_date: '', appointment_time: '', message: '' };
  const [form, setForm] = useState(initial);
  const [message, setMessage] = useState('');

  const submit = async (event) => {
    event.preventDefault();
    setMessage('Saving appointment request...');
    try {
      const data = await api('/appointments', { method: 'POST', body: JSON.stringify(form) });
      setForm(initial);
      const emailStatus = data.email_sent ? 'confirmation email sent' : 'confirmation email not sent';
      const calendarStatus = data.calendar_event_created ? 'calendar event created' : 'calendar event not created';
      setMessage(`Appointment saved, ${emailStatus}, ${calendarStatus}.`);
    } catch {
      setMessage('Could not save booking. Check that the backend server is running.');
    }
  };

  const fields = [
    ['name', 'Full name'],
    ['email', 'Email address'],
    ['phone', 'Phone number'],
    ['service', 'Service'],
    ['appointment_date', 'Preferred date'],
    ['appointment_time', 'Preferred time'],
  ];

  return <section>
    <PageTitle icon={<CalendarDays />} title="Book Appointment" subtitle="Create a lead, appointment record, email confirmation, and calendar event in one flow." />
    <form className="grid card" onSubmit={submit}>
      {fields.map(([key, label]) =>
        <label key={key}>{label}
          <input type={key.includes('date') ? 'date' : key.includes('time') ? 'time' : key === 'email' ? 'email' : 'text'} required value={form[key]} onChange={e => setForm({ ...form, [key]: e.target.value })} />
        </label>
      )}
      <label className="full">Project notes<textarea value={form.message} onChange={e => setForm({ ...form, message: e.target.value })} placeholder="Share goals, budget, or any context for the call." /></label>
      <button className="primary">Submit Booking</button>
      <p className="form-message">{message}</p>
    </form>
  </section>;
}

function Login({ setToken, setPage }) {
  const [email, setEmail] = useState('admin@aptlyai.com');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');

  const submit = async (event) => {
    event.preventDefault();
    setError('');
    try {
      const data = await api('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
      localStorage.setItem('token', data.access_token);
      setToken(data.access_token);
      setPage('admin');
    } catch {
      setError('Invalid login or backend not running.');
    }
  };

  return <section className="login">
    <form className="card" onSubmit={submit}>
      <h2><ShieldCheck /> Admin Login</h2>
      <p className="muted">Access lead records, appointment statuses, and dashboard metrics.</p>
      <input value={email} onChange={e => setEmail(e.target.value)} aria-label="Email address" />
      <input type="password" value={password} onChange={e => setPassword(e.target.value)} aria-label="Password" />
      <button className="primary">Login</button>
      <p className="error">{error}</p>
    </form>
  </section>;
}

function Admin({ stats, leads, appointments, refresh, token }) {
  const [appointmentQuery, setAppointmentQuery] = useState('');
  const [appointmentStatus, setAppointmentStatus] = useState('All');
  const [leadQuery, setLeadQuery] = useState('');
  const [leadStatus, setLeadStatus] = useState('All');
  const [tab, setTab] = useState('appointments');
  const leadById = useMemo(() => new Map(leads.map(lead => [lead.id, lead])), [leads]);

  const filteredAppointments = useMemo(() => appointments.filter(item => {
    const lead = leadById.get(item.lead_id) || {};
    const haystack = `${lead.name || ''} ${lead.email || ''} ${lead.phone || ''} ${item.service} ${item.status}`.toLowerCase();
    return haystack.includes(appointmentQuery.toLowerCase()) && (appointmentStatus === 'All' || item.status === appointmentStatus);
  }), [appointments, appointmentQuery, appointmentStatus, leadById]);

  const filteredLeads = useMemo(() => leads.filter(item => {
    const haystack = `${item.name} ${item.email} ${item.phone} ${item.status}`.toLowerCase();
    return haystack.includes(leadQuery.toLowerCase()) && (leadStatus === 'All' || item.status === leadStatus);
  }), [leads, leadQuery, leadStatus]);

  const updateAppointment = async (id, nextStatus) => {
    await api(`/appointments/${id}/status`, { method: 'PUT', body: JSON.stringify({ status: nextStatus }) }, token);
    refresh();
  };

  const updateLead = async (id, nextStatus) => {
    await api(`/leads/${id}`, { method: 'PUT', body: JSON.stringify({ status: nextStatus }) }, token);
    refresh();
  };

  const remove = async (kind, id) => {
    await api(`/${kind}/${id}`, { method: 'DELETE' }, token);
    refresh();
  };

  return <section>
    <div className="section-title">
      <PageTitle icon={<LayoutDashboard />} title="Admin Dashboard" subtitle="Track booking demand, qualify leads, and manage appointment status." compact />
      <button onClick={refresh}><RefreshCw size={16} /> Refresh</button>
    </div>
    <div className="stats">
      <Stat icon={<Users />} title="Leads" val={stats.leads || 0} />
      <Stat icon={<CalendarDays />} title="Bookings" val={stats.appointments || 0} />
      <Stat icon={<Clock />} title="Pending" val={stats.pending || 0} />
      <Stat icon={<CheckCircle />} title="Conversion" val={`${stats.conversion_rate || 0}%`} />
    </div>
    <div className="tabs mb-3">
      <button className={tab === 'appointments' ? 'active' : ''} onClick={() => setTab('appointments')}>Appointments</button>
      <button className={tab === 'leads' ? 'active' : ''} onClick={() => setTab('leads')}>Leads</button>
    </div>
    {tab === 'appointments' ? <>
      <FilterPanel
        title="Appointment Filters"
        searchValue={appointmentQuery}
        statusValue={appointmentStatus}
        statusOptions={statuses}
        placeholder="Search by name, email, phone, service, or status"
        resultCount={filteredAppointments.length}
        totalCount={appointments.length}
        onSearch={setAppointmentQuery}
        onStatus={setAppointmentStatus}
        onClear={() => { setAppointmentQuery(''); setAppointmentStatus('All'); }}
      />
      <AppointmentsTable rows={filteredAppointments} leads={leadById} update={updateAppointment} remove={remove} />
    </> : <>
      <FilterPanel
        title="Lead Filters"
        searchValue={leadQuery}
        statusValue={leadStatus}
        statusOptions={leadStatuses}
        placeholder="Search by name, email, phone, or status"
        resultCount={filteredLeads.length}
        totalCount={leads.length}
        onSearch={setLeadQuery}
        onStatus={setLeadStatus}
        onClear={() => { setLeadQuery(''); setLeadStatus('All'); }}
      />
      <LeadsTable rows={filteredLeads} update={updateLead} remove={remove} />
    </>}
  </section>;
}

function FilterPanel({ title, searchValue, statusValue, statusOptions, placeholder, resultCount, totalCount, onSearch, onStatus, onClear }) {
  return <div className="card filter-panel mb-3">
    <div className="d-flex flex-column flex-lg-row align-items-lg-center justify-content-between gap-2 mb-3">
      <h3 className="h6 mb-0">{title}</h3>
      <span className="badge text-bg-secondary">{resultCount} of {totalCount}</span>
    </div>
    <div className="row g-3 align-items-end">
      <div className="col-12 col-lg-7">
        <label className="form-label">Search</label>
        <div className="input-group">
          <span className="input-group-text"><Search size={16} /></span>
          <input className="form-control" value={searchValue} onChange={event => onSearch(event.target.value)} placeholder={placeholder} />
        </div>
      </div>
      <div className="col-12 col-sm-6 col-lg-3">
        <label className="form-label">Status</label>
        <select className="form-select" value={statusValue} onChange={event => onStatus(event.target.value)}>
          {['All', ...statusOptions].map(item => <option key={item}>{item}</option>)}
        </select>
      </div>
      <div className="col-12 col-sm-6 col-lg-2">
        <button className="btn btn-outline-light w-100" onClick={onClear}>Clear</button>
      </div>
    </div>
  </div>;
}

function AppointmentsTable({ rows, leads, update, remove }) {
  return <table>
    <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Service</th><th>Date</th><th>Time</th><th>Status</th><th>Actions</th></tr></thead>
    <tbody>{rows.length === 0 && <EmptyRow columns={9} message="No appointments match the current filters." />}{rows.map(item => <tr key={item.id}>
      <td>{item.id}</td>
      <td>{leads.get(item.lead_id)?.name || 'Unassigned'}</td>
      <td>{leads.get(item.lead_id)?.email || '-'}</td>
      <td>{leads.get(item.lead_id)?.phone || '-'}</td>
      <td>{item.service}</td><td>{item.appointment_date}</td><td>{item.appointment_time}</td>
      <td><select className="form-select form-select-sm" value={item.status} onChange={e => update(item.id, e.target.value)}>{statuses.map(s => <option key={s}>{s}</option>)}</select></td>
      <td><button className="danger" onClick={() => remove('appointments', item.id)}><Trash2 size={16} /> Delete</button></td>
    </tr>)}</tbody>
  </table>;
}

function LeadsTable({ rows, update, remove }) {
  return <table>
    <thead><tr><th>Name</th><th>Email</th><th>Phone</th><th>Status</th><th>Actions</th></tr></thead>
    <tbody>{rows.length === 0 && <EmptyRow columns={5} message="No leads match the current filters." />}{rows.map(item => <tr key={item.id}>
      <td>{item.name}</td><td>{item.email}</td><td>{item.phone}</td>
      <td><select className="form-select form-select-sm" value={item.status} onChange={e => update(item.id, e.target.value)}>{leadStatuses.map(s => <option key={s}>{s}</option>)}</select></td>
      <td><button className="danger" onClick={() => remove('leads', item.id)}><XCircle size={16} /> Remove</button></td>
    </tr>)}</tbody>
  </table>;
}

function Stat({ icon, title, val }) {
  return <div className="stat">{icon}<span>{title}</span><b>{val}</b></div>;
}

function PageTitle({ icon, title, subtitle, compact = false }) {
  return <div className={compact ? 'page-title compact' : 'page-title'}>
    <h2>{icon} {title}</h2>
    <p>{subtitle}</p>
  </div>;
}

function EmptyRow({ columns, message }) {
  return <tr><td className="table-empty" colSpan={columns}>{message}</td></tr>;
}

createRoot(document.getElementById('root')).render(<App />);
