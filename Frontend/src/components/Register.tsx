import React, { useState } from "react";

export default function Register({ onGoToLogin }: { onGoToLogin: () => void })
{
  const [form, setForm] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [message, setMessage] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) =>
  {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) =>
  {
    e.preventDefault();

    if (form.password !== form.confirmPassword)
    {
      setMessage("Passwords do not match");
      return;
    }

    try
    {
      const res = await fetch('/api/auth/register',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: form.firstName + " " + form.lastName,
          email: form.email,
          password: form.password,
        }),
      });
      const data = await res.json();
      if (res.ok)
      {
        setMessage("Registration successful! You can now log in.");
      }
      else
      {
        setMessage(data.msg || "Registration failed");
      }
    }
    catch (err)
    {
      setMessage("Server error");
    }
  };

  return (
    <div id="registerDiv">
      <span id="inner-title">PLEASE REGISTER</span><br />

      <form onSubmit={handleSubmit}>

        <input
          type="text"
          name="firstName"
          placeholder="First Name"
          value={form.firstName}
          onChange={handleChange}
        /><br />

        <input
          type="text"
          name="lastName"
          placeholder="Last Name"
          value={form.lastName}
          onChange={handleChange}
        /><br />

        <input
          type="email"
          name="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
        /><br />

        <input
          type="password"
          name="password"
          placeholder="Password"
          value={form.password}
          onChange={handleChange}
        /><br />

        <input
          type="password"
          name="confirmPassword"
          placeholder="Confirm Password"
          value={form.confirmPassword}
          onChange={handleChange}
        /><br />

        <button type="submit">Register</button>
      </form>

      <span>{message}</span><br />

      <button onClick={onGoToLogin}>
        Back to Login
      </button>
    </div>
  );
}
