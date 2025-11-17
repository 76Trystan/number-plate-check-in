import { useEffect, useState } from "react";
import Papa from "papaparse";

import "./App.css";
import Header from "./components/Header";
import SummaryCards from "./components/SummaryCards";
import CurrentVehiclesTable from "./components/CurrentVehiclesTable";
import CheckinsChart from "./components/CheckinsChart";

function App() {
  const [vehicles, setVehicles] = useState([]);
  const [totals, setTotals] = useState({ current: 0, checkins: 0, checkouts: 0 });
  const [chartData, setChartData] = useState({ labels: [], data: [] });

  useEffect(() => {
    const csvPath = "/data/data.csv"; // adjust if needed

    function calculateDuration(checkinTime) {
      if (!checkinTime) return "-";
      const start = new Date(checkinTime);
      const now = new Date();
      const diff = now - start;
      const minutes = Math.floor(diff / 60000);
      const hours = Math.floor(minutes / 60);
      const days = Math.floor(hours / 24);
      const weeks = Math.floor(days / 7);
      const months = Math.floor(days / 30);
      return `${minutes}:${hours}:${days}:${weeks}:${months}`;
    }

    Papa.parse(csvPath, {
      download: true,
      header: true,
      complete: function (results) {
        const data = results.data.filter(d => d["License Plate"]);

        const currentVehicles = data.filter(d => !d["Actual Checkout Time"])
          .map(v => ({ ...v, duration: calculateDuration(v["Actual Checkin Time"]) }));

        setVehicles(currentVehicles);
        setTotals({
          current: currentVehicles.length,
          checkins: data.length,
          checkouts: data.filter(d => d["Actual Checkout Time"]).length,
        });

        const last7Days = [];
        const today = new Date();
        for (let i = 6; i >= 0; i--) {
          const d = new Date(today);
          d.setDate(today.getDate() - i);
          last7Days.push(d.toISOString().split("T")[0]);
        }

        const counts = last7Days.map(date =>
          data.filter(d => d["Actual Checkin Time"]?.startsWith(date)).length
        );

        setChartData({ labels: last7Days, data: counts });
      },
      error: function (err) {
        console.error("Error loading CSV:", err);
      },
    });
  }, []);

  return (
    <>
      <Header />
      <main>
        <CurrentVehiclesTable vehicles={vehicles} />
        <SummaryCards
          totalCurrent={totals.current}
          totalCheckins={totals.checkins}
          totalCheckouts={totals.checkouts}
        />
        <CheckinsChart labels={chartData.labels} data={chartData.data} />
      </main>
    </>
  );
}

export default App;
