import LoginForm from "./login-form";

export default function LoginPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-sm flex-col justify-center px-6">
      <h1 className="text-3xl font-bold">TruRate</h1>
      <p className="mt-2 text-muted">Fair reel prices for WLDD&apos;s campaign team.</p>
      <LoginForm />
    </main>
  );
}
