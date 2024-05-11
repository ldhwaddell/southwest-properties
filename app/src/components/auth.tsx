import { Button } from "./ui/button";
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/nextjs";

export function Auth() {
  return (
    <>
      <SignedOut>
        <SignInButton>
          <Button variant="secondary">Sign In</Button>
        </SignInButton>
      </SignedOut>
      <SignedIn>
        <UserButton afterSignOutUrl="/" />
      </SignedIn>
    </>
  );
}

export default Auth;
