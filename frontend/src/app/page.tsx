"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<{email?: string; password?: string}>({});
  const [loading, setLoading] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const validateForm = () => {
    const errors: {email?: string; password?: string} = {};
    if (!email.trim()) {
      errors.email = "Email is required";
    } else if (!email.includes("@")) {
      errors.email = "Please enter a valid email address";
    }
    if (!password.trim()) {
      errors.password = "Password is required";
    } else if (password.length < 3) {
      errors.password = "Password must be at least 3 characters";
    }
    return errors;
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      setError("");
      return;
    }
    
    setFieldErrors({});
    setLoading(true);
    setError("");

    try {
      const response = await axios.post("http://127.0.0.1:8000/api/auth/login", {
        email,
        password,
      });

      // Save token and role to local storage
      localStorage.setItem("token", response.data.token);
      localStorage.setItem("role", response.data.role);
      localStorage.setItem("user_id", response.data.user_id);

      // Redirect to chat dashboard
      router.push("/chat");
    } catch (err) {
      if (err && typeof err === 'object' && 'response' in err) {
        const error = err as { response?: { status?: number; data?: { detail?: string } }; request?: unknown };
        if (error.response) {
          if (error.response.status === 401) {
            setError("Invalid email or password. Please try again.");
          } else {
            setError(`Server Error (${error.response.status}): ${error.response.data?.detail || "Unknown error"}`);
          }
        } else if (error.request) {
          setError("Connection Error: Cannot reach the backend server. Please ensure the backend is running at http://127.0.0.1:8000");
        } else {
          setError("An unexpected error occurred. Please try again.");
        }
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  if (!mounted) return null;

  return (
    <div className="flex items-center justify-center min-h-screen bg-neutral-900 text-white font-sans">
      <div className="w-full max-w-md p-8 bg-neutral-800 rounded-xl shadow-2xl border border-neutral-700">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-blue-400 mb-2">SDLC Copilot</h1>
          <p className="text-neutral-400">Login to access your workspace</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-900/50 border border-red-500 rounded text-red-200 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-neutral-300 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => {setEmail(e.target.value); setFieldErrors({...fieldErrors, email: undefined});}}
              className={`w-full px-4 py-2 bg-neutral-900 border rounded focus:outline-none text-white transition-colors ${
                fieldErrors.email ? 'border-red-500 focus:border-red-500' : 'border-neutral-700 focus:border-blue-500'
              }`}
              required
            />
            {fieldErrors.email && <p className="text-sm text-red-400 mt-1">{fieldErrors.email}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-300 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => {setPassword(e.target.value); setFieldErrors({...fieldErrors, password: undefined});}}
              className={`w-full px-4 py-2 bg-neutral-900 border rounded focus:outline-none text-white transition-colors ${
                fieldErrors.password ? 'border-red-500 focus:border-red-500' : 'border-neutral-700 focus:border-blue-500'
              }`}
              required
            />
            {fieldErrors.password && <p className="text-sm text-red-400 mt-1">{fieldErrors.password}</p>}
          </div>
          <button
            type="submit"
            disabled={loading || !email.trim() || !password.trim()}
            className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-600/50 disabled:cursor-not-allowed text-white font-semibold rounded-lg shadow transition-colors"
          >
            {loading ? "Authenticating..." : "Login"}
          </button>
        </form>

        <div className="mt-6 p-4 bg-neutral-900 rounded border border-neutral-700 text-xs text-neutral-400">
          <p><strong>Demo Accounts:</strong></p>
          <ul className="list-disc pl-4 mt-2 space-y-1">
            <li>ba@hsbc.com (Business Analyst)</li>
            <li>fba@hsbc.com (Functional BA)</li>
            <li>qa@hsbc.com (QA / Tester)</li>
          </ul>
          <p className="mt-2">Password for all: <strong>password123</strong></p>
        </div>
      </div>
    </div>
  );
}
