import { SignIn } from "@clerk/nextjs";

export default function Page() {
  return (
    // subtract height of nav + footer
    <section className="w-full h-[calc(100vh-100px)] flex flex-col items-center justify-center py-5">
      <SignIn path="/sign-in" />
    </section>
  );

}
