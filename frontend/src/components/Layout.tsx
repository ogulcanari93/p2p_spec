import { Link, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="layout">
      <header className="layout__header">
        <div>
          <strong>P2P Payment Requests</strong>
          {user && (
            <div style={{ display: "block", fontSize: "0.875rem", color: "var(--muted)" }}>
              {user.email}
            </div>
          )}
        </div>
        {user && (
          <nav className="layout__nav">
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/requests/new">New request</Link>
            <button type="button" className="btn btn--secondary" onClick={logout}>
              Log out
            </button>
          </nav>
        )}
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
