document.addEventListener("DOMContentLoaded", () => {
	const renderChart = (canvasId, labels, data) => {
		const ctx = document.getElementById(canvasId);

		new Chart(ctx, {
			type: "doughnut",
			data: {
				labels: labels,
				datasets: [
					{
						label: "Distribution per source (last 3 months)",
						data: data,
						backgroundColor: [
							"rgb(255, 99, 132)",
							"rgb(54, 162, 235)",
							"rgb(255, 205, 86)",
						],
						hoverOffset: 4,
					},
				],
			},
			options: {
				plugins: {
					title: {
						display: true,
						text: "Distribution per source (last 3 months)",
					},
				},
			},
		});
	};

	const getChartData = () => {
		fetch("income_source_summary")
			.then((res) => res.json())
			.then((results) => {
				const source_data = results.income_source_data;
				const [labels, data] = [
					Object.keys(source_data),
					Object.values(source_data),
				];

				renderChart("myChart1", labels, data);
			});
	};

	const renderLineChart = (labels, datasets) => {
		const ctx = document.getElementById("myChart2");

		new Chart(ctx, {
			type: "polarArea",
			data: {
				labels: labels,
				datasets: datasets
			},
			options: {
				plugins: {
					title: {
						display: true,
						text: "Source Cumulative Comparison (Last 3 Months)",
					},
				},
			},
		});
	};

	const getLineChartData = () => {
		fetch("income_source_trend")
			.then((res) => res.json())
			.then((results) => {
				const source_trend = results.source_trend;

				const labels = Object.keys(source_trend).map((monthString) =>{
					const date = new Date(monthString);
					return date.toLocaleString("default", { month: "long" });
				});
				const categories = Object.keys(source_trend[Object.keys(source_trend)[0]]);
				const datasets = categories.map((source) => {
					return {
						label: source,
						data: Object.keys(source_trend).map((month) => source_trend[month][source]),
						backgroundColor: [
							'rgb(255, 99, 132)',
							'rgb(75, 192, 192)',
							'rgb(255, 205, 86)',
							'rgb(201, 203, 207)',
							'rgb(54, 162, 235)'
						],
					}
				});

				renderLineChart(labels, datasets);
			});
	};

	window.onload = () => {
		getChartData();
		getLineChartData();
	};
});
