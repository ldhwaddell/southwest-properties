"use client";

import { Separator } from "@/components/ui/separator";
import { ModeToggle } from "@/components/mode-toggle";

export function Header() {
  return (
    <>
      <div className="flex justify-between items-center mb-2">
        <h1 className="text-3xl font-bold">Southwest Data Viewer</h1>
        <ModeToggle />
      </div>
      <Separator className="mb-2" />
    </>
  );
}
