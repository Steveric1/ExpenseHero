document.addEventListener("DOMContentLoaded", () => {
	const renderChart = (canvasId, labels, data) => {
		const ctx = document.getElementById(canvasId);

		new Chart(ctx, {
			type: "doughnut",
			data: {
				labels: labels,
				datasets: [
					{
						label: labels,
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
						text: "Distribution per category (last 3 months)"
					},
				},
			},
		});
	};

	const getChartData = () => {
		fetch("expense_category_summary")
			.then((res) => res.json())
			.then((results) => {
				const category_data = results.expense_category_data;
				const [labels, data] = [
					Object.keys(category_data),
					Object.values(category_data),
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
						text: "Category Cumulative Comparison (Last 3 Months)"
					},
				},
			},
		});
	};

	const getLineChartData = () => {
		fetch("expense_category_trend")
			.then((res) => res.json())
			.then((results) => {
				const category_trend = results.category_trend;

				const labels = Object.keys(category_trend).map((monthString) =>{
					const date = new Date(monthString);
					return date.toLocaleString("default", { month: "long" });
				});
				const categories = Object.keys(category_trend[Object.keys(category_trend)[0]]);
				const datasets = categories.map((category) => {
					return {
						label: category,
						data: Object.keys(category_trend).map((month) => category_trend[month][category]),
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
