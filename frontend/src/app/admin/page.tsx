'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { Plus, Edit2, Trash2, LogOut, Eye, EyeOff } from 'lucide-react';

interface User {
  id: string;
  email: string;
  username: string;
  roles: string[];
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

interface AdminState {
  isAuthenticated: boolean;
  adminEmail: string | null;
  token: string | null;
}

const AVAILABLE_ROLES = [
  'Business Analyst (BA)',
  'Functional BA (FBA)',
  'QA / Tester'
];

export default function AdminPage() {
  const router = useRouter();
  const [adminState, setAdminState] = useState<AdminState>({
    isAuthenticated: false,
    adminEmail: null,
    token: null
  });
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Login form state
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [showLoginPassword, setShowLoginPassword] = useState(false);

  // Create user form state
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createForm, setCreateForm] = useState({
    email: '',
    username: '',
    password: '',
    roles: ['Business Analyst (BA)']
  });
  const [showCreatePassword, setShowCreatePassword] = useState(false);

  // Edit user form state
  const [editingUserId, setEditingUserId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({
    email: '',
    username: '',
    password: '',
    roles: [] as string[]
  });
  const [showEditPassword, setShowEditPassword] = useState(false);

  // Admin login
  const handleAdminLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post('/api/admin/login', {
        email: loginEmail,
        password: loginPassword
      });

      setAdminState({
        isAuthenticated: true,
        adminEmail: response.data.email,
        token: response.data.access_token
      });

      setLoginEmail('');
      setLoginPassword('');
      fetchUsers(response.data.access_token);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  // Fetch users
  const fetchUsers = async (token: string) => {
    try {
      const response = await axios.get('/api/admin/users', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUsers(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch users');
    }
  };

  // Create user
  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await axios.post('/api/admin/users', createForm, {
        headers: { Authorization: `Bearer ${adminState.token}` }
      });

      setSuccess('User created successfully!');
      setCreateForm({
        email: '',
        username: '',
        password: '',
        roles: ['Business Analyst (BA)']
      });
      setShowCreateForm(false);
      fetchUsers(adminState.token!);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create user');
    } finally {
      setLoading(false);
    }
  };

  // Start editing user
  const startEditUser = (user: User) => {
    setEditingUserId(user.id);
    setEditForm({
      email: user.email,
      username: user.username,
      password: '',
      roles: user.roles
    });
  };

  // Update user
  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const updateData: any = {
        email: editForm.email,
        username: editForm.username,
        roles: editForm.roles
      };

      if (editForm.password) {
        updateData.password = editForm.password;
      }

      await axios.put(`/api/admin/users/${editingUserId}`, updateData, {
        headers: { Authorization: `Bearer ${adminState.token}` }
      });

      setSuccess('User updated successfully!');
      setEditingUserId(null);
      fetchUsers(adminState.token!);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update user');
    } finally {
      setLoading(false);
    }
  };

  // Delete user
  const handleDeleteUser = async (userId: string) => {
    if (!confirm('Are you sure you want to delete this user?')) return;

    setLoading(true);
    setError('');

    try {
      await axios.delete(`/api/admin/users/${userId}`, {
        headers: { Authorization: `Bearer ${adminState.token}` }
      });

      setSuccess('User deleted successfully!');
      fetchUsers(adminState.token!);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete user');
    } finally {
      setLoading(false);
    }
  };

  // Logout
  const handleLogout = () => {
    setAdminState({
      isAuthenticated: false,
      adminEmail: null,
      token: null
    });
    setUsers([]);
  };

  // Toggle role selection
  const toggleRole = (role: string, isCreate: boolean = true) => {
    if (isCreate) {
      setCreateForm(prev => ({
        ...prev,
        roles: prev.roles.includes(role)
          ? prev.roles.filter(r => r !== role)
          : [...prev.roles, role]
      }));
    } else {
      setEditForm(prev => ({
        ...prev,
        roles: prev.roles.includes(role)
          ? prev.roles.filter(r => r !== role)
          : [...prev.roles, role]
      }));
    }
  };

  // Clear messages
  useEffect(() => {
    const timer = setTimeout(() => {
      setSuccess('');
      setError('');
    }, 5000);
    return () => clearTimeout(timer);
  }, [success, error]);

  if (!adminState.isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Admin Portal</h1>
          <p className="text-gray-600 mb-6">User Management System</p>

          <form onSubmit={handleAdminLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                placeholder="admin1@hsbc.com"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <div className="relative">
                <input
                  type={showLoginPassword ? 'text' : 'password'}
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowLoginPassword(!showLoginPassword)}
                  className="absolute right-3 top-2.5 text-gray-500"
                >
                  {showLoginPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg transition disabled:opacity-50"
            >
              {loading ? 'Logging in...' : 'Login as Admin'}
            </button>
          </form>

          <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-sm text-blue-800">
              <strong>Demo Credentials:</strong><br />
              Email: admin1@hsbc.com<br />
              Password: admin123
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
            <p className="text-gray-600">Logged in as: {adminState.adminEmail}</p>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition"
          >
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Messages */}
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
            {success}
          </div>
        )}

        {/* Create User Section */}
        <div className="mb-8">
          {!showCreateForm ? (
            <button
              onClick={() => setShowCreateForm(true)}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition font-semibold"
            >
              <Plus size={20} />
              Create New User
            </button>
          ) : (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Create New User</h2>
              <form onSubmit={handleCreateUser} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email
                    </label>
                    <input
                      type="email"
                      value={createForm.email}
                      onChange={(e) => setCreateForm({ ...createForm, email: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Username
                    </label>
                    <input
                      type="text"
                      value={createForm.username}
                      onChange={(e) => setCreateForm({ ...createForm, username: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Password
                  </label>
                  <div className="relative">
                    <input
                      type={showCreatePassword ? 'text' : 'password'}
                      value={createForm.password}
                      onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowCreatePassword(!showCreatePassword)}
                      className="absolute right-3 top-2.5 text-gray-500"
                    >
                      {showCreatePassword ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Assign Roles (Select multiple)
                  </label>
                  <div className="space-y-2">
                    {AVAILABLE_ROLES.map(role => (
                      <label key={role} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={createForm.roles.includes(role)}
                          onChange={() => toggleRole(role, true)}
                          className="w-4 h-4 text-blue-600 rounded"
                        />
                        <span className="ml-2 text-gray-700">{role}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="flex gap-4">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg transition disabled:opacity-50"
                  >
                    {loading ? 'Creating...' : 'Create User'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowCreateForm(false)}
                    className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-2 rounded-lg transition"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>

        {/* Users Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900">Users ({users.length})</h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Email</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Username</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Roles</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Created</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {users.map(user => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-900">{user.email}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{user.username}</td>
                    <td className="px-6 py-4 text-sm">
                      <div className="flex flex-wrap gap-1">
                        {user.roles.map(role => (
                          <span key={role} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-semibold">
                            {role}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      {editingUserId === user.id ? (
                        <form onSubmit={handleUpdateUser} className="space-y-3 bg-gray-50 p-4 rounded">
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Email</label>
                            <input
                              type="email"
                              value={editForm.email}
                              onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                              className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Username</label>
                            <input
                              type="text"
                              value={editForm.username}
                              onChange={(e) => setEditForm({ ...editForm, username: e.target.value })}
                              className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">New Password (optional)</label>
                            <div className="relative">
                              <input
                                type={showEditPassword ? 'text' : 'password'}
                                value={editForm.password}
                                onChange={(e) => setEditForm({ ...editForm, password: e.target.value })}
                                placeholder="Leave blank to keep current"
                                className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                              />
                              <button
                                type="button"
                                onClick={() => setShowEditPassword(!showEditPassword)}
                                className="absolute right-2 top-1.5 text-gray-500"
                              >
                                {showEditPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                              </button>
                            </div>
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Roles</label>
                            <div className="space-y-1">
                              {AVAILABLE_ROLES.map(role => (
                                <label key={role} className="flex items-center text-sm">
                                  <input
                                    type="checkbox"
                                    checked={editForm.roles.includes(role)}
                                    onChange={() => toggleRole(role, false)}
                                    className="w-3 h-3 text-blue-600 rounded"
                                  />
                                  <span className="ml-2 text-gray-700">{role}</span>
                                </label>
                              ))}
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <button
                              type="submit"
                              disabled={loading}
                              className="flex-1 bg-green-600 hover:bg-green-700 text-white text-sm font-semibold py-1 rounded transition disabled:opacity-50"
                            >
                              Save
                            </button>
                            <button
                              type="button"
                              onClick={() => setEditingUserId(null)}
                              className="flex-1 bg-gray-400 hover:bg-gray-500 text-white text-sm font-semibold py-1 rounded transition"
                            >
                              Cancel
                            </button>
                          </div>
                        </form>
                      ) : (
                        <div className="flex gap-2">
                          <button
                            onClick={() => startEditUser(user)}
                            className="flex items-center gap-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm transition"
                          >
                            <Edit2 size={16} />
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteUser(user.id)}
                            disabled={user.is_admin}
                            className="flex items-center gap-1 bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm transition disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <Trash2 size={16} />
                            Delete
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
