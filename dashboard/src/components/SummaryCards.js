function SummaryCards({ totalCurrent, totalCheckins, totalCheckouts }) {
  return (
    <section className="summary">
      <div className="card">
        <p>Total Vehicles Currently Checked In</p>
        <h2>{totalCurrent}</h2>
      </div>
      <div className="card">
        <p>Total Check-Ins</p>
        <h2>{totalCheckins}</h2>
      </div>
      <div className="card">
        <p>Total Check-Outs</p>
        <h2>{totalCheckouts}</h2>
      </div>
    </section>
  );
}

export default SummaryCards;
