import { SignUp } from "@clerk/nextjs";

export default function Page() {
  return (
    <section className="w-full h-[calc(100vh-100px)] flex flex-col items-center justify-center py-5">
      <SignUp path="/sign-up" />
    </section>
  );
}
