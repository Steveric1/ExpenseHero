
document.addEventListener("DOMContentLoaded", () => {
  const today = new Date();
  const todayNumber = today.getDate();
  const weekNumber = getWeekNumber(today);
  const monthNumber = today.getMonth() + 1;
  const yearNumber = today.getFullYear().toString().slice(-2);

  document.getElementById("today-number").textContent = todayNumber;
  document.getElementById("week-number").textContent = weekNumber;
  document.getElementById("month-number").textContent = monthNumber;
  document.getElementById("year-number").textContent = yearNumber;


  const totalTodayIncome = document.getElementById("todays-total-income");
  const totalWeekIncome = document.getElementById("totalWeekIncome");
  const totalMonthIncome = document.getElementById("totalMonthIncome");
  const totalYearIncome = document.getElementById("totalYearIncome");

  if (totalTodayIncome) {
    fetch("total_income_of_the_day").then((res) => res.json())
      .then((results) => {
        if (results && results.today_total_income !== undefined) {
          totalTodayIncome.textContent = results.today_total_income;
        }else {
          console.error('Unexpected response format:', results);
        }
      });
  }
  
  if(totalWeekIncome) {
    fetch("total_income_of_the_week").then((res) => res.json())
      .then((results) => {
        if (results && results.total_week_income !== undefined) {
          totalWeekIncome.textContent = results.total_week_income;
        } else {
          console.error('Unexpected response format:', results);
        }
      });
  }

  if (totalMonthIncome) {
    fetch("total_income_of_the_month").then((res) => res.json())
      .then((results) => {
        console.log(results);
        if (results && results.total_month_income !== undefined) {
          totalMonthIncome.textContent = results.total_month_income;
        } else {
          console.log('Unexpected response format:', results);
        }
      });
  }

  if (totalYearIncome) {
    fetch("total_income_of_the_year").then((res) => res.json())
      .then((results) => {
        if (results && results.total_year_income !== undefined) {
          totalYearIncome.textContent = results.total_year_income;
        } else {
          console.error('Unexpected response format:', results);
        }
      });
  }
});

function getWeekNumber(date) {
  const startOfYear = new Date(date.getFullYear(), 0, 1);
  const pastDaysOfYear = (date - startOfYear) / 86400000;
  return Math.ceil((pastDaysOfYear + startOfYear.getDay() + 1) / 7);
}


const renderChart = (labels, data) => {
	const ctx = document.getElementById("myChart").getContext("2d");
	new Chart(ctx, {
		type: "line",
		data: {
			labels: labels,
			datasets: [
				{
					label: "This Year",
					data: data,
					backgroundColor: "rgba(255, 99, 132)",
					borderColor: "rgb(255, 99, 132 )",
					pointRadius: 2.5,
				},
			],
		},
		options: {
			plugins: {
				title: {
					display: true,
					text: "Yearly Data",
				},
			},
			scales: {
				y: {
					beginAtZero: true,
				},
			},
		},
	});
};

const getChartData = () => {
	fetch("income_by_month")
		.then((res) => res.json())
		.then((results) => {
			console.log("results", results);
			const monthly_totals = results.monthly_totals;
      const data = Object.values(monthly_totals);
			const labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];


			renderChart(labels, data);
		});
};


const renderChart2 = (labels, data) => {
	const ctx = document.getElementById("myChart2").getContext("2d");
	new Chart(ctx, {
		type: "line",
		data: {
			labels: labels,
			datasets: [
				{
					label: "This Week",
					data: data,
					backgroundColor: "rgba(26, 163, 102)",
					borderColor: "rgb(26, 163, 102)",
					pointRadius: 2,
				},
			],
		},
		options: {
			plugins: {
				title: {
					display: true,
					text: "Yearly Data",
				},
			},
			scales: {
				y: {
					beginAtZero: true,
				},
			},
		},
	});
};

const getChartData2 = () => {
	fetch("income_by_week")
		.then((res) => res.json())
		.then((results) => {
			console.log("results", results);
			const weekly_totals = results.weekly_totals;
      const data = Object.values(weekly_totals);
			const labels = ["Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun"];


			renderChart2(labels, data);
		});
};


window.onload = () => {
  getChartData();
  getChartData2();
}
