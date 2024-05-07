import { Nav } from "./nav";
import { MobileNav } from "./mobile-nav";
import { ModeToggle } from "@/components/mode-toggle";

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full px-2 border-b border-border bg-background">
      <div className="mx-auto h-14 flex items-center justify-between">
        <div className="flex grow-0">
          <Nav />
          <MobileNav />
        </div>
        <div className="flex grow-0 items-center space-x-2">
          <nav className="flex items-center">
            <ModeToggle />
          </nav>
        </div>
      </div>
    </header>
  );
}

export default Header;
