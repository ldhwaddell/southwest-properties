import { Row } from "@tanstack/react-table";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogClose,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ScrollArea } from "./ui/scroll-area";
import { Separator } from "./ui/separator";

import type { applications } from "@prisma/client";

import { formatSnakeCaseToTitle } from "@/utils";

interface RowDialogProps<TData> {
  isOpen: boolean;
  onClose: () => void;
  row: Row<TData>;
}

export function RowDialog<TData>({
  isOpen,
  onClose,
  row,
}: RowDialogProps<TData>) {
  // Cast the object to an applications type
  const rowData = row?.original as applications;

  return (
    <Dialog
      open={isOpen}
      onOpenChange={(isOpen) => (isOpen ? null : onClose())}
    >
      <DialogContent className="h-[90vh] sm:max-w-[800px]">
        <>
          <DialogHeader>
            <DialogTitle>{rowData?.title}</DialogTitle>
          </DialogHeader>

          <ScrollArea className="grid gap-4 py-4 h-full">
            {Object.entries(rowData).map(([key, value]) => (
              <div key={key} className="mb-4">
                <h3 className="text-lg font-semibold">
                  {formatSnakeCaseToTitle(key)}
                </h3>
                <p>
                  {value !== null && value !== undefined
                    ? value.toString()
                    : "Does not exist"}
                </p>
                <Separator className="mt-1" />
              </div>
            ))}
          </ScrollArea>
          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="secondary">
                Close
              </Button>
            </DialogClose>
          </DialogFooter>
        </>
      </DialogContent>
    </Dialog>
  );
}
