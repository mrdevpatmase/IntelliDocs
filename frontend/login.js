const API_URL = "http://127.0.0.1:5000";

document
.getElementById("loginBtn")
.addEventListener(
    "click",
    login
);

async function login() {

    const username =
        document.getElementById(
            "username"
        ).value;

    const password =
        document.getElementById(
            "password"
        ).value;

    const response =
        await fetch(
            `${API_URL}/login`,
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

        localStorage.setItem(
            "token",
            data.token
        );

        localStorage.setItem(
            "username",
            data.username
        );

        window.location.href =
            "index.html";

    }

    else{

        alert(
            data.error
        );

    }

}