import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import Register from '../components/Register';

const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return { ...actual, useNavigate: () => mockNavigate };
});

vi.mock('../services/api', () => ({
  register: vi.fn(),
}));

import { register } from '../services/api';
const mockRegister = register as ReturnType<typeof vi.fn>;

function renderRegister() {
  return render(
    <MemoryRouter>
      <Register />
    </MemoryRouter>
  );
}

describe('Register Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders full name input', () => {
    renderRegister();
    expect(screen.getByPlaceholderText('John Doe')).toBeInTheDocument();
  });

  it('renders email input', () => {
    renderRegister();
    expect(screen.getByPlaceholderText('john@example.com')).toBeInTheDocument();
  });

  it('renders password input', () => {
    renderRegister();
    expect(screen.getByPlaceholderText('Create a password')).toBeInTheDocument();
  });

  it('renders Register button', () => {
    renderRegister();
    expect(screen.getByRole('button', { name: /^register$/i })).toBeInTheDocument();
  });

  it('renders Log in link', () => {
    renderRegister();
    expect(screen.getByRole('button', { name: /log in/i })).toBeInTheDocument();
  });

  it('clicking Log in navigates to /login', () => {
    renderRegister();
    fireEvent.click(screen.getByRole('button', { name: /log in/i }));
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  it('calls register api with name, email, password on submit', async () => {
    mockRegister.mockResolvedValueOnce({ msg: 'Registration successful! Please check your email to verify your account.' });
    renderRegister();

    fireEvent.change(screen.getByPlaceholderText('John Doe'), {
      target: { name: 'name', value: 'Jane Smith' },
    });
    fireEvent.change(screen.getByPlaceholderText('john@example.com'), {
      target: { name: 'email', value: 'jane@test.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Create a password'), {
      target: { name: 'password', value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /^register$/i }));

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith('Jane Smith', 'jane@test.com', 'password123');
    });
  });

  it('shows success message on successful registration', async () => {
    mockRegister.mockResolvedValueOnce({ msg: 'Registration successful! Please check your email to verify your account.' });
    renderRegister();

    fireEvent.change(screen.getByPlaceholderText('John Doe'), {
      target: { name: 'name', value: 'Jane Smith' },
    });
    fireEvent.change(screen.getByPlaceholderText('john@example.com'), {
      target: { name: 'email', value: 'jane@test.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Create a password'), {
      target: { name: 'password', value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /^register$/i }));

    await waitFor(() => {
      expect(screen.getByText('Registration successful! Please check your email to verify your account.')).toBeInTheDocument();
    });
  });

  it('clears form fields after successful registration', async () => {
    mockRegister.mockResolvedValueOnce({ msg: 'Registration successful! Please check your email to verify your account.' });
    renderRegister();

    const nameInput = screen.getByPlaceholderText('John Doe') as HTMLInputElement;
    fireEvent.change(nameInput, { target: { name: 'name', value: 'Jane Smith' } });
    fireEvent.change(screen.getByPlaceholderText('john@example.com'), {
      target: { name: 'email', value: 'jane@test.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Create a password'), {
      target: { name: 'password', value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /^register$/i }));

    await waitFor(() => {
      expect(nameInput.value).toBe('');
    });
  });

  it('shows error message on failed registration', async () => {
    mockRegister.mockRejectedValueOnce({
      response: { data: { msg: 'User already exists' } },
    });
    renderRegister();

    fireEvent.change(screen.getByPlaceholderText('John Doe'), {
      target: { name: 'name', value: 'Jane Smith' },
    });
    fireEvent.change(screen.getByPlaceholderText('john@example.com'), {
      target: { name: 'email', value: 'existing@test.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Create a password'), {
      target: { name: 'password', value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /^register$/i }));

    await waitFor(() => {
      expect(screen.getByText('User already exists')).toBeInTheDocument();
    });
  });

  it('shows fallback error when no response msg', async () => {
    mockRegister.mockRejectedValueOnce(new Error('Network Error'));
    renderRegister();

    fireEvent.change(screen.getByPlaceholderText('John Doe'), {
      target: { name: 'name', value: 'Jane Smith' },
    });
    fireEvent.change(screen.getByPlaceholderText('john@example.com'), {
      target: { name: 'email', value: 'jane@test.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Create a password'), {
      target: { name: 'password', value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /^register$/i }));

    await waitFor(() => {
      expect(screen.getByText('An error occurred')).toBeInTheDocument();
    });
  });

  it('shows loading state while submitting', async () => {
    let resolve: (v: any) => void;
    mockRegister.mockReturnValueOnce(new Promise(r => { resolve = r; }));
    renderRegister();

    fireEvent.change(screen.getByPlaceholderText('John Doe'), {
      target: { name: 'name', value: 'Jane Smith' },
    });
    fireEvent.change(screen.getByPlaceholderText('john@example.com'), {
      target: { name: 'email', value: 'jane@test.com' },
    });
    fireEvent.change(screen.getByPlaceholderText('Create a password'), {
      target: { name: 'password', value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /^register$/i }));

    expect(screen.getByRole('button', { name: /please wait/i })).toBeInTheDocument();
    resolve!({ msg: 'ok' });
  });
});
