"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await axios.post("http://localhost:8000/api/auth/login", {
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
      setError("Invalid credentials. Try ba@hsbc.com, fba@hsbc.com, or qa@hsbc.com with password 'password123'.");
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
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 bg-neutral-900 border border-neutral-700 rounded focus:outline-none focus:border-blue-500 text-white"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-300 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 bg-neutral-900 border border-neutral-700 rounded focus:outline-none focus:border-blue-500 text-white"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow transition-colors"
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
