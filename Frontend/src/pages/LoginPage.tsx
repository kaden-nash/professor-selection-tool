import PageTitle from "../components/PageTitle";
import Login from "../components/Login";

function LoginPage({ onGoToRegister }: { onGoToRegister: () => void }) {
  return (
    <div className="loginPage">
      <div className="header">
        <PageTitle />
      </div>

      <div className="content">
        <Login onGoToRegister={onGoToRegister} />
      </div>
    </div>
  );
}

export default LoginPage;
