// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDwSJiD3soaz1xac7wg3ejguWtmM3eKMUM",
  authDomain: "talk2me-417cf.firebaseapp.com",
  projectId: "talk2me-417cf",
  storageBucket: "talk2me-417cf.firebasestorage.app",
  messagingSenderId: "80333990638",
  appId: "1:80333990638:web:18c4020a3ebbc39d74e1ff",
  measurementId: "G-ZLVQ0V4W7Y"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);