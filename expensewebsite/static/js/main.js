// Function to delete user's expense
function showDeleteModal(event, expenseId) {
    event.preventDefault();
    const url =  `expense_delete/${expenseId}/`;

    Swal.fire({
        title: "Are you sure you want to delete this expense?.",
        text: "You won't be able to revert this!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Yes, delete it!",
    })
    .then((result) => {
        if (result.isConfirmed) {
            fetch(url, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                }
            })
            .then(res => res.json())
            .then((data) => {
                if (data.success) {
                    Swal.fire({
                        title: "Deleted!",
                        text: "Your expense has been deleted.",
                        icon: "success"
                    }).then(() => {
                        location.reload();
                    });
                } else {
                    Swal.fire({
                        title: "Error!",
                        text: "There was an error deleting the expense.",
                        icon: "error"
                    });
                }
            })
            .catch((error) => {
                Swal.fire({
                    title: "Error!",
                    text: "There was an error deleting the expense.",
                    icon: "error"
                });
            });
        }
    });
}

// Function to delete user's income
function showIncomeDeleteModal(event, incomeId) {
    event.preventDefault();
    let url = `/income/income_delete/${incomeId}`;
	console.log(url);

    Swal.fire({
        title: "Are you sure you want to delete this income?.",
        text: "You won't be able to revert this!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Yes, delete it!",
    })
    .then((result) => {
        if (result.isConfirmed) {
            fetch(url, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                }
            })
            .then(res => res.json())
            .then((data) => {
                if (data.success) {
                    Swal.fire({
                        title: "Deleted!",
                        text: "Your income has been deleted.",
                        icon: "success"
                    }).then(() => {
                        location.reload();
                    });
                } else {
                    Swal.fire({
                        title: "Error!",
                        text: "There was an error deleting the income.",
                        icon: "error"
                    });
                }
            })
            .catch((error) => {
                Swal.fire({
                    title: "Error!",
                    text: "There was an error deleting the income.",
                    icon: "error"
                });
            });
        }
    });
}

// Function to delete user's account
function showUserDeleteModal(event, userId) {
    event.preventDefault();
    let url = `/preferences/delete_account/${userId}`;
    console.log(url);

    Swal.fire({
        title: "Are you sure you want to delete your account?",
        text: "You won't be able to revert this!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Yes, delete it!",
    })
    .then((result) => {
        if (result.isConfirmed) {
            fetch(url, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                }
            })
            .then(res => {
                if (res.status === 204) {
                    Swal.fire({
                        title: "Deleted!",
                        text: "Your account has been deleted.",
                        icon: "success"
                    }).then(() => {
                        window.location.href = "/authentication/login";
                    });
                } else {
                    return res.json().then(data => {
                        Swal.fire({
                            title: "Error!",
                            text: data.error || "There was an error deleting the account.",
                            icon: "error"
                        });
                    });
                }
            })
            .catch((error) => {
                Swal.fire({
                    title: "Error!",
                    text: "There was an error deleting the account.",
                    icon: "error"
                });
            });
        }
    });
}


// Function to notify user at the registeration that an email has ben sent to them
 document.addEventListener('DOMContentLoaded', (event) => {
            const register = document.getElementById('register');
            const form = document.getElementById('formId');

            if (register && form) {
                console.log("Register button and form found");
                register.addEventListener('click', (event) => {
                    if (form.checkValidity()) {
                        event.preventDefault();
                        Swal.fire({
                            title: 'Email Sent!',
                            text: 'An email has been sent to you. Please use the link sent to your mail to verify your account.',
                            icon: 'success',
                            confirmButtonText: 'OK'
                        }).then((result) => {
                            if (result.isConfirmed) {
                                form.submit();
                            }
                        });
                    } else {
                        console.log("Form is not valid");
                        form.reportValidity();
                    }
                });
            } else {
                console.log("Register button or form not found");
            }
        });