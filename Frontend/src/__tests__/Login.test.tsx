import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import Login from '../components/Login';

const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return { ...actual, useNavigate: () => mockNavigate };
});

vi.mock('../services/api', () => ({
  login: vi.fn(),
}));

import { login } from '../services/api';
const mockLogin = login as ReturnType<typeof vi.fn>;

function renderLogin() {
  return render(
    <MemoryRouter>
      <Login />
    </MemoryRouter>
  );
}

describe('Login Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders email input', () => {
    renderLogin();
    expect(screen.getByPlaceholderText('john@example.com')).toBeInTheDocument();
  });

  it('renders password input', () => {
    renderLogin();
    expect(screen.getByPlaceholderText('Enter your password')).toBeInTheDocument();
  });

  it('renders Sign in button', () => {
    renderLogin();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('renders Sign up link', () => {
    renderLogin();
    expect(screen.getByRole('button', { name: /sign up/i })).toBeInTheDocument();
  });

  it('renders Forgot password link', () => {
    renderLogin();
    expect(screen.getByRole('button', { name: /forgot password/i })).toBeInTheDocument();
  });

  it('calls login api with email and password on submit', async () => {
    mockLogin.mockResolvedValueOnce({ token: 'test-token-123' });
    renderLogin();

    fireEvent.change(screen.getByPlaceholderText('john@example.com'), {
      target: { name: 'email', value: 'user@test.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Enter your password'), {
      target: { name: 'password', value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('user@test.com', 'password123');
    });
  });

  it('stores token in localStorage on successful login', async () => {
    mockLogin.mockResolvedValueOnce({ token: 'test-token-abc' });
    renderLogin();

    fireEvent.change(screen.getByPlaceholderText('john@example.com'), {
      target: { name: 'email', value: 'user@test.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Enter your password'), {
      target: { name: 'password', value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(localStorage.getItem('token')).toBe('test-token-abc');
    });
  });

  it('navigates to /search on successful login', async () => {
    mockLogin.mockResolvedValueOnce({ token: 'test-token-xyz' });
    renderLogin();

    fireEvent.change(screen.getByPlaceholderText('john@example.com'), {
      target: { name: 'email', value: 'user@test.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Enter your password'), {
      target: { name: 'password', value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/search');
    });
  });

  it('shows error message on failed login', async () => {
    mockLogin.mockRejectedValueOnce({
      response: { data: { msg: 'Invalid credentials' } },
    });
    renderLogin();

    fireEvent.change(screen.getByPlaceholderText('john@example.com'), {
      target: { name: 'email', value: 'bad@test.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Enter your password'), {
      target: { name: 'password', value: 'wrongpass' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
    });
  });

  it('shows fallback error message when no response msg', async () => {
    mockLogin.mockRejectedValueOnce(new Error('Network Error'));
    renderLogin();

    fireEvent.change(screen.getByPlaceholderText('john@example.com'), {
      target: { name: 'email', value: 'bad@test.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Enter your password'), {
      target: { name: 'password', value: 'wrongpass' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText('An error occurred')).toBeInTheDocument();
    });
  });

  it('shows loading state while submitting', async () => {
    let resolve: (v: any) => void;
    mockLogin.mockReturnValueOnce(new Promise(r => { resolve = r; }));
    renderLogin();

    fireEvent.change(screen.getByPlaceholderText('john@example.com'), {
      target: { name: 'email', value: 'user@test.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Enter your password'), {
      target: { name: 'password', value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    expect(screen.getByRole('button', { name: /please wait/i })).toBeInTheDocument();
    resolve!({ token: 'tok' });
  });
});
