import axios from "axios";
const API = axios.create({ baseURL: "", timeout: 180000 });
API.interceptors.response.use(r => r, err => { console.error("API:", err.response?.data || err.message); return Promise.reject(err); });
export default API;
