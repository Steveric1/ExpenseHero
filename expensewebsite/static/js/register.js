// This file is used to validate the username and emailfield in the register form

const usernameField = document.getElementById('usernamefield');
const feedBackArea = document.querySelector(".invalid-feedback");
const emailField = document.getElementById('emailField')
const emailFeedBackArea = document.querySelector(".invalid-email-feedback");
const usernameSuccessOutput = document.querySelector(".usernameSuccessOutput");
const emailSuccessOutput = document.querySelector(".emailSuccessOutput");
const showPasswordToggle = document.querySelector(".showPasswordToggle");
const passwordField = document.getElementById('passwordField');
const submitBtn = document.querySelector('.submit-btn input[type="submit"]');
const passwordFeedBackArea = document.querySelector('.invalid-password-feedback');
// const passwordInput = document.querySelector('.password');


if (usernameField) {
    usernameField.addEventListener('keyup', (event) => {
        const usernameVal = event.target.value;
        usernameSuccessOutput.textContent = 'Checking...';
    
        // make an api call if usernameVal is not empty
        if (usernameVal !== "") {
            fetch('/authentication/validate-username', {
                body: JSON.stringify({ username: usernameVal }),
                method: 'POST',
            }).then(res => {
                return res.json();
            }) .then(data => {
                usernameSuccessOutput.style.display = "none";
                if (data.username_error) {
                    usernameField.classList.add('is-invalid');
                    feedBackArea.style.display = "block"
                    feedBackArea.innerHTML = `<p>${data.username_error}</p>`;
                    submitBtn.setAttribute('disabled', 'disabled');
                } else {
                    usernameField.classList.remove("is-invalid");
                    feedBackArea.style.display = "none";
                    submitBtn.removeAttribute('disabled');
                }
            });
        }
    });
}

// Handle email validation
if (emailField) {
    emailField.addEventListener('keyup', (event) => {
        const emailVal = event.target.value;
        emailSuccessOutput.textContent = 'Checking...';
    
        if (emailVal.length > 0) {
            fetch('/authentication/validate-email', {
                body: JSON.stringify({ email: emailVal }),
                method: 'POST',
            }).then(res => res.json())
            .then(data => {
                emailSuccessOutput.style.display = "none";
                if (data.email_error) {
                    submitBtn.disabled = true;
                    emailField.classList.add('is-invalid');
                    emailFeedBackArea.style.display = "block"
                    emailFeedBackArea.innerHTML = `<p>${data.email_error}</p>`;
                } else {
                    emailField.classList.remove('is-invalid');
                    emailFeedBackArea.style.display = "none";
                    submitBtn.removeAttribute('disabled');
                }
            })
        } else {
            emailField.classList.remove('is-invalid');
            emailFeedBackArea.style.display = "none";
        }
    }) 
}


if (passwordField) {
    passwordField.addEventListener('keyup', (event) => {
        const passwordVal = event.target.value;

        if (passwordVal.length > 0) {
            fetch('/authentication/validate-password', {
                body: JSON.stringify({ password: passwordVal }),
                method: 'POST'
            }).then((res) => res.json())
            .then(data =>{
                if (data.password_error) {
                    submitBtn.disabled = true;
                    passwordField.classList.add('is-invalid');
                    passwordFeedBackArea.style.display = "block"
                    passwordFeedBackArea.innerHTML = `<p>${data.password_error}</p>`;
                } else {
                    passwordField.classList.remove('is-invalid');
                    passwordFeedBackArea.style.display = "none";
                    submitBtn.removeAttribute('disabled');
                }
            })
        } else {
            passwordField.classList.remove('is-invalid');
            passwordFeedBackArea.style.display = "none";
        }
    });
}


// Implement show password toggle
const handlePasswordToggle = (event) => {
    if (showPasswordToggle.textContent === "SHOW") {
        showPasswordToggle.textContent = "HIDE";
        passwordField.setAttribute("type", "text");
    } else {
        showPasswordToggle.textContent = "SHOW";
        passwordField.setAttribute("type", "password");
    }
}
showPasswordToggle.addEventListener('click', handlePasswordToggle);

