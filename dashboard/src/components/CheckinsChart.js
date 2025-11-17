import { Bar } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function CheckinsChart({ labels, data }) {
  const chartData = {
    labels,
    datasets: [
      {
        label: "Check-Ins",
        data,
        backgroundColor: "#007bff88",
        borderColor: "#007bff",
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    scales: {
      y: { beginAtZero: true, title: { display: true, text: "Number of Check-Ins" } },
      x: { title: { display: true, text: "Date" } },
    },
  };

  return (
    <section className="chart-container">
      <h3>Check-Ins Over Last 7 Days</h3>
      <Bar data={chartData} options={options} />
    </section>
  );
}

export default CheckinsChart;
