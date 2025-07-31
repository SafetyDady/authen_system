
// Basic HTML + CSS Login Page (no Tailwind, no React dependencies)
import { useState } from 'react';

const LoginPage = () => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const email = e.target.email.value;
    const password = e.target.password.value;

    // Demo credentials
    if (email === 'admin@example.com' && password === 'admin123456') {
      setMessage('เข้าสู่ระบบสำเร็จ! (Login successful)');
    } else {
      setMessage('อีเมลหรือรหัสผ่านไม่ถูกต้อง (Invalid email or password)');
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f5f6fa' }}>
      <form onSubmit={handleSubmit} style={{ background: '#fff', padding: '2rem', borderRadius: '1rem', boxShadow: '0 2px 16px rgba(0,0,0,0.08)', minWidth: '320px', width: '100%', maxWidth: '400px' }} autoComplete="off">
        <h2 style={{ textAlign: 'center', marginBottom: '1.5rem', color: '#222' }}>Login</h2>
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="email" style={{ display: 'block', marginBottom: '0.5rem', color: '#333' }}>Email</label>
          <input type="email" id="email" name="email" placeholder="Enter your email" style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #ddd', fontSize: '1rem' }} required defaultValue="admin@example.com" />
        </div>
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="password" style={{ display: 'block', marginBottom: '0.5rem', color: '#333' }}>Password</label>
          <input type="password" id="password" name="password" placeholder="Enter your password" style={{ width: '100%', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #ddd', fontSize: '1rem' }} required defaultValue="admin123456" />
        </div>
        <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center' }}>
          <input type="checkbox" id="remember_me" name="remember_me" style={{ marginRight: '0.5rem' }} />
          <label htmlFor="remember_me" style={{ color: '#555', fontSize: '0.95rem' }}>Remember me</label>
        </div>
        <button type="submit" style={{ width: '100%', background: '#2d8cf0', color: '#fff', padding: '0.75rem', borderRadius: '0.5rem', border: 'none', fontWeight: 'bold', fontSize: '1rem', cursor: 'pointer' }}>Sign In</button>
        {message && (
          <div style={{ marginTop: '1rem', textAlign: 'center', color: message.includes('สำเร็จ') ? '#2d8cf0' : '#d93025', fontSize: '1rem', fontWeight: 'bold' }}>
            {message}
          </div>
        )}
        <div style={{ marginTop: '1.5rem', textAlign: 'center', color: '#888', fontSize: '0.95rem' }}>
          <strong>Demo:</strong> admin@example.com / admin123456
        </div>
      </form>
    </div>
  );
};

export default LoginPage;

