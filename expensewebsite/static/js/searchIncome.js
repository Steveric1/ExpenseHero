document.addEventListener("DOMContentLoaded", () => {
	const searchField = document.getElementById("searchField");
	const tableOutput = document.querySelector(".table-output");
	const appTable = document.querySelector(".app-table");
	const pagination = document.querySelector(".pagination-container");
	const tableBody = document.querySelector(".table-body");
	const noResult = document.querySelector(".no-results");

	tableOutput.style.display = "none";

	searchField.addEventListener("keyup", (event) => {
		const searchVal = event.target.value;

		if (searchVal.trim().length > 0) {
			pagination.style.display = "none";
			tableBody.innerHTML = " ";
			fetch("/income/search-income", {
				body: JSON.stringify({ searchText: searchVal }),
				method: "POST",
			})
				.then((res) => {
					return res.json();
				})
				.then((data) => {
					appTable.style.display = "none";
					tableOutput.style.display = "block";

					if (data.length === 0) {
						noResult.style.display = "block";
						tableOutput.style.display = "none";
					} else {
						noResult.style.display = "none";
						tableBody.innerHTML = "";
						data.forEach((item) => {
							tableBody.innerHTML += `
                    <tr>
                       <td>${item.amount}</td>
                       <td>${item.source}</td>
                       <td>${item.description}</td>
                       <td>${item.date}</td>
                    </tr>
                    `;
						});
					}
				});
		} else {
			tableOutput.style.display = "none";
			appTable.style.display = "block";
			pagination.style.display = "block";
		}
	});
});
