import React from 'react';

export default function Pricing() {
  return (
    <section className="pricing" style={{ padding: '40px 0', borderBottom: '1px solid #eaeaea', textAlign: 'center' }}>
      <h2>Simple, transparent pricing</h2>
      <div className="pricing-tier" style={{ border: '1px solid #ccc', borderRadius: '8px', padding: '20px', display: 'inline-block', marginTop: '20px' }}>
        <h3 style={{ margin: '0' }}>Pro Plan</h3>
        <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '10px 0' }}>$29<span style={{ fontSize: '1rem', fontWeight: 'normal', color: '#666' }}>/mo</span></p>
        <button style={{ padding: '10px 20px', background: 'black', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Subscribe</button>
      </div>
    </section>
  );
}
