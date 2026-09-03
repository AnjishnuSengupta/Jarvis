import React from 'react';

export default function Gallery() {
  return (
    <section className="gallery" style={{ padding: '40px 0', borderBottom: '1px solid #eaeaea' }}>
      <h2>Our Work</h2>
      <div className="gallery-grid" style={{ display: 'flex', gap: '20px' }}>
        <div className="gallery-item" style={{ flex: 1, background: "#f0f0f0", height: "150px", display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '8px' }}>Project 1</div>
        <div className="gallery-item" style={{ flex: 1, background: "#e0e0e0", height: "150px", display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '8px' }}>Project 2</div>
      </div>
    </section>
  );
}
