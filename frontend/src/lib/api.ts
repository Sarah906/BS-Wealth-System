import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
});

// Attach Bearer token from localStorage on each request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("wealthos_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Redirect to login on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("wealthos_token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;

// ─── Auth ─────────────────────────────────────────────────────────────────
export const authApi = {
  login: (username: string, password: string) =>
    api.post("/auth/login", { username, password }),
  register: (email: string, username: string, password: string, full_name?: string) =>
    api.post("/auth/register", { email, username, password, full_name }),
  me: () => api.get("/auth/me"),
};

// ─── Platforms ────────────────────────────────────────────────────────────
export const platformsApi = {
  list: () => api.get("/platforms"),
};

// ─── Accounts ─────────────────────────────────────────────────────────────
export const accountsApi = {
  list: () => api.get("/accounts"),
  create: (data: object) => api.post("/accounts", data),
};

// ─── Assets ───────────────────────────────────────────────────────────────
export const assetsApi = {
  list: (search?: string) => api.get("/assets", { params: { search } }),
  create: (data: object) => api.post("/assets", data),
};

// ─── Deals ────────────────────────────────────────────────────────────────
export const dealsApi = {
  list: (params?: object) => api.get("/deals", { params }),
  get: (id: number) => api.get(`/deals/${id}`),
  create: (data: object) => api.post("/deals", data),
};

// ─── Transactions ─────────────────────────────────────────────────────────
export const transactionsApi = {
  list: (params?: object) => api.get("/transactions", { params }),
  create: (data: object) => api.post("/transactions", data),
};

// ─── Cashflows ────────────────────────────────────────────────────────────
export const cashflowsApi = {
  list: (deal_id?: number) => api.get("/cashflows", { params: { deal_id } }),
  create: (data: object) => api.post("/cashflows", data),
};

// ─── Analytics ────────────────────────────────────────────────────────────
export const analyticsApi = {
  summary: () => api.get("/analytics/summary"),
  brokerage: (account_id?: number) => api.get("/analytics/brokerage", { params: { account_id } }),
  deals: (params?: object) => api.get("/analytics/deals", { params }),
  monthlyCashflow: () => api.get("/analytics/monthly-cashflow"),
  alerts: () => api.get("/analytics/insights/alerts"),
};

// ─── Imports ──────────────────────────────────────────────────────────────
export const importsApi = {
  list: () => api.get("/imports"),
  upload: (formData: FormData) =>
    api.post("/imports/upload", formData, { headers: { "Content-Type": "multipart/form-data" } }),
  preview: (id: number) => api.get(`/imports/${id}/preview`),
  run: (id: number) => api.post(`/imports/${id}/run`),
};
