import PageTitle from "../components/PageTitle";
import Login from "../components/Login";
import HeaderBox from "../components/HeaderBox";

function LoginPage({ onGoToRegister }: { onGoToRegister: () => void }) {
  return (
    <div className="page">
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
