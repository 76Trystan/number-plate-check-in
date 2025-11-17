function CurrentVehiclesTable({ vehicles }) {
  return (
    <section>
      <h3>Currently Checked In Vehicles</h3>
      <div className="current-vehicles-table">
        <table>
          <thead>
            <tr>
              <th>License Plate</th>
              <th>Booked Check-In</th>
              <th>Actual Check-In</th>
              <th>Scheduled Checkout</th>
              <th>Duration</th>
            </tr>
          </thead>
          <tbody>
            {vehicles.map((v, i) => (
              <tr key={i}>
                <td>{v["License Plate"]}</td>
                <td>{v["Booked Checkin Time"] || "-"}</td>
                <td>{v["Actual Checkin Time"] || "-"}</td>
                <td>{v["Scheduled Checkout Time"] || "-"}</td>
                <td>{v.duration}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default CurrentVehiclesTable;
