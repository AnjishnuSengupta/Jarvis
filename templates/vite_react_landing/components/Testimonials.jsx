import React from 'react';

export default function Testimonials() {
  return (
    <section className="testimonials" style={{ padding: '40px 0', borderBottom: '1px solid #eaeaea' }}>
      <h2>What our customers say</h2>
      <blockquote style={{ fontStyle: 'italic', borderLeft: '4px solid #0070f3', margin: '0', paddingLeft: '20px' }}>
        <p>"Jarvis generated this site in 5 seconds. Incredible."</p>
        <cite style={{ fontWeight: 'bold' }}>- A Happy User</cite>
      </blockquote>
    </section>
  );
}
