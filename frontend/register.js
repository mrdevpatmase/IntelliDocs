const API_URL = "http://127.0.0.1:5000";

document
.getElementById("registerBtn")
.addEventListener(
    "click",
    register
);

async function register() {

    const username =
        document.getElementById(
            "username"
        ).value;

    const password =
        document.getElementById(
            "password"
        ).value;

    const confirmPassword =
        document.getElementById(
            "confirmPassword"
        ).value;

    if(
        password !==
        confirmPassword
    ){

        alert(
            "Passwords do not match"
        );

        return;
    }

    const response =
        await fetch(
            `${API_URL}/register`,
            {
                method:"POST",

                headers:{
                    "Content-Type":
                    "application/json"
                },

                body:JSON.stringify({
                    username,
                    password
                })
            }
        );

    const data =
        await response.json();

    if(response.ok){

        alert(
            "Registration Successful"
        );

        window.location.href =
            "login.html";

    }

    else{

        alert(
            data.error
        );

    }

}