const ctx = document.getElementById('line').getContext('2d');

// Ensure resultProbabilities is defined and parsed
const data = {
  labels: Array.from({ length: resultProbabilities.length }, (_, i) => `Result ${i + 1}`),
  datasets: [{
    label: 'Prediction Accuracy',
    data: resultProbabilities,
    fill: false,
    borderColor: 'rgb(75, 192, 192)',
    tension: 0.1
  }]
};

new Chart(ctx, {
  type: 'line',
  data: data,
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});
