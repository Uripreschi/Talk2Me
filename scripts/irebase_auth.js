import { auth } from "./firebase_setup.js";
import { signInWithEmailAndPassword, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/9.15.0/firebase-auth.js";

// Handle Signup
document.addEventListener("DOMContentLoaded", function() {
    const signupForm = document.getElementById("signup-form");
    if (signupForm) {
        signupForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const email = document.getElementById("signup-email").value;
            const password = document.getElementById("signup-password").value;

            createUserWithEmailAndPassword(auth, email, password)
                .then((userCredential) => {
                    alert("Signup successful! Please log in.");
                    window.location.href = "login.html";
                })
                .catch((error) => {
                    alert(error.message);
                });
        });
    }
});

// Handle Login
document.addEventListener("DOMContentLoaded", function() {
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const email = document.getElementById("login-email").value;
            const password = document.getElementById("login-password").value;

            signInWithEmailAndPassword(auth, email, password)
                .then((userCredential) => {
                    alert("Login successful!");
                    window.location.href = "teacher.html"; // Redirect based on user type
                })
                .catch((error) => {
                    alert(error.message);
                });
        });
    }
});
