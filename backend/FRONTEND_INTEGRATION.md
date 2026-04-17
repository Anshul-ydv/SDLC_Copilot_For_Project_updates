# Frontend Integration Guide for JWT Authentication

## Overview
This guide shows how to integrate JWT authentication with your Next.js frontend.

---

## 1. Update Frontend to Handle JWT Tokens

### Create Auth Service (`frontend/src/services/authService.ts`)

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: string;
  user_id: string;
  email: string;
  expires_in: number;
}

export interface UserInfo {
  user_id: string;
  email: string;
  role: string;
}

class AuthService {
  private tokenKey = 'jwt_token';
  private userKey = 'user_info';

  // Login and store token
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data: LoginResponse = await response.json();
    
    // Store token and user info
    this.setToken(data.access_token);
    this.setUserInfo({
      user_id: data.user_id,
      email: data.email,
      role: data.role,
    });

    return data;
  }

  // Logout and clear storage
  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
  }

  // Get stored token
  getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(this.tokenKey);
  }

  // Set token
  setToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
  }

  // Get user info
  getUserInfo(): UserInfo | null {
    if (typeof window === 'undefined') return null;
    const userStr = localStorage.getItem(this.userKey);
    return userStr ? JSON.parse(userStr) : null;
  }

  // Set user info
  setUserInfo(user: UserInfo): void {
    localStorage.setItem(this.userKey, JSON.stringify(user));
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  // Get authorization header
  getAuthHeader(): { Authorization: string } | {} {
    const token = this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  // Verify token is still valid
  async verifyToken(): Promise<boolean> {
    const token = this.getToken();
    if (!token) return false;

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/verify-token`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  // Get current user from API
  async getCurrentUser(): Promise<UserInfo> {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: this.getAuthHeader() as HeadersInit,
    });

    if (!response.ok) {
      throw new Error('Failed to get user info');
    }

    return response.json();
  }
}

export const authService = new AuthService();
```

---

## 2. Create Login Page (`frontend/src/app/login/page.tsx`)

```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/services/authService';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await authService.login({ email, password });
      router.push('/chat'); // Redirect to chat after successful login
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <div>
          <h2 className="text-center text-3xl font-bold">Sign in</h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            SDLC Automation Copilot
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="ba@hsbc.com"
              />
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="password123"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <div className="mt-4 text-sm text-gray-600">
          <p className="font-semibold">Test Accounts:</p>
          <ul className="mt-2 space-y-1">
            <li>• ba@hsbc.com / password123 (BA)</li>
            <li>• fba@hsbc.com / password123 (FBA)</li>
            <li>• qa@hsbc.com / password123 (QA)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
```

---

## 3. Create Auth Context (`frontend/src/contexts/AuthContext.tsx`)

```typescript
'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { authService, UserInfo } from '@/services/authService';
import { useRouter } from 'next/navigation';

interface AuthContextType {
  user: UserInfo | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in on mount
    const initAuth = async () => {
      const userInfo = authService.getUserInfo();
      if (userInfo) {
        const isValid = await authService.verifyToken();
        if (isValid) {
          setUser(userInfo);
        } else {
          authService.logout();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authService.login({ email, password });
    setUser({
      user_id: response.user_id,
      email: response.email,
      role: response.role,
    });
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

---

## 4. Protect Routes with Middleware (`frontend/src/middleware.ts`)

```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('jwt_token')?.value;
  const isAuthPage = request.nextUrl.pathname.startsWith('/login');
  const isProtectedPage = request.nextUrl.pathname.startsWith('/chat');

  // Redirect to login if accessing protected page without token
  if (isProtectedPage && !token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Redirect to chat if accessing login page with valid token
  if (isAuthPage && token) {
    return NextResponse.redirect(new URL('/chat', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/chat/:path*', '/login'],
};
```

---

## 5. Update API Calls to Include Auth Token

### Example: Chat API Call

```typescript
import { authService } from '@/services/authService';

async function sendChatMessage(message: string) {
  const response = await fetch('http://localhost:8000/api/chat/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...authService.getAuthHeader(),
    },
    body: JSON.stringify({
      user_id: authService.getUserInfo()?.user_id,
      session_id: currentSessionId,
      role: authService.getUserInfo()?.role,
      query: message,
    }),
  });

  if (response.status === 401) {
    // Token expired, redirect to login
    authService.logout();
    window.location.href = '/login';
    return;
  }

  return response.json();
}
```

---

## 6. Add Logout Button to UI

```typescript
'use client';

import { useAuth } from '@/contexts/AuthContext';

export function UserMenu() {
  const { user, logout } = useAuth();

  return (
    <div className="flex items-center gap-4">
      <span className="text-sm">
        {user?.email} ({user?.role})
      </span>
      <button
        onClick={logout}
        className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
      >
        Logout
      </button>
    </div>
  );
}
```

---

## 7. Environment Variables

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 8. Update Root Layout

```typescript
// frontend/src/app/layout.tsx
import { AuthProvider } from '@/contexts/AuthContext';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

---

## Testing the Integration

1. Start backend: `cd backend && python -m uvicorn main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to `http://localhost:3000/login`
4. Login with test credentials
5. Verify token is stored in localStorage
6. Access protected routes
7. Test logout functionality

---

## Security Considerations

1. **Use httpOnly cookies** in production instead of localStorage
2. **Implement token refresh** for better UX
3. **Add CSRF protection** for state-changing operations
4. **Use HTTPS** in production
5. **Implement rate limiting** on login endpoint
6. **Add session timeout warnings** to notify users before token expires

---

## Common Issues

### CORS Errors
- Ensure backend CORS is configured for your frontend origin
- Check that credentials are included in requests

### Token Not Persisting
- Check localStorage is accessible
- Verify token is being stored after login

### 401 Errors on Protected Routes
- Token may have expired (30 min default)
- Token may be malformed
- Check Authorization header format: `Bearer <token>`
