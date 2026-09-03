import React from 'react';

export default function ContactForm() {
  return (
    <section className="contact-form" style={{ padding: '40px 0', borderBottom: '1px solid #eaeaea' }}>
      <h2>Contact Us</h2>
      <form 
        onSubmit={(e) => { e.preventDefault(); alert("Form submitted!"); }}
        style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '400px' }}
      >
        <input type="text" placeholder="Your Name" required style={{ padding: '10px' }} />
        <input type="email" placeholder="Your Email" required style={{ padding: '10px' }} />
        <button type="submit" style={{ padding: '10px', background: '#0070f3', color: 'white', border: 'none', cursor: 'pointer' }}>Send Message</button>
      </form>
    </section>
  );
}
