import PageTitle from "../components/PageTitle";
import Register from "../components/Register";

function RegisterPage({ onGoToLogin }: { onGoToLogin: () => void })
{
  return (
    <div>
      <PageTitle />
      <Register onGoToLogin={onGoToLogin} />
    </div>
  );
}

export default RegisterPage;
