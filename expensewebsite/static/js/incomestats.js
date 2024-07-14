const renderChart = (labels, data) => {
    const ctx = document.getElementById('myChart');

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'last six months expenses',
        data: data,
        backgroundColor: [
          'rgba(255, 99, 132, 0.2)',
          'rgba(255, 159, 64, 0.2)',
          'rgba(255, 205, 86, 0.2)',
          'rgba(75, 192, 192, 0.2)', 
          'rgba(54, 162, 235, 0.2)' ,
          'rgba(153, 102, 255, 0.2)',
          'rgba(201, 203, 207, 0.2)'
        ],
        borderColor: [
            'rgb(255, 99, 132)',
            'rgb(255, 159, 64)',
            'rgb(255, 205, 86)',
            'rgb(75, 192, 192)',
            'rgb(54, 162, 235)',
            'rgb(153, 102, 255)',
            'rgb(201, 203, 207)'
          ],
          borderWidth: 1
        }]
    },
    options: {
        plugins: {
            title: {
                display: true,
                text: 'Income per source'
            }
        }
    }
  });
}

const getChartData = () => {
    fetch('income_source_summary')
    .then((res) => res.json())
    .then((results) => {
        console.log("results", results);
        source_data = results.income_source_data;
        const [labels, data] = [Object.keys(source_data), Object.values(source_data)]

        renderChart(labels, data);
    })
}

document.onload = getChartData();