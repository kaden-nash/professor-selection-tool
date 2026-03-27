import PageTitle from "../components/PageTitle";
import Login from "../components/Login";

function LoginPage({ onGoToRegister }: { onGoToRegister: () => void }) {
  return (
    <div>
      <PageTitle />
      <Login onGoToRegister={onGoToRegister} />
    </div>
  );
}

export default LoginPage;
