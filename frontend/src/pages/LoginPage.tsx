import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { LoginForm } from "../components/LoginForm";

export function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <LoginForm
      onSubmit={async (email) => {
        await login(email);
        navigate("/dashboard", { replace: true });
      }}
    />
  );
}
