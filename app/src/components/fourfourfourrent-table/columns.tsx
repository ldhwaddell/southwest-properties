"use client";

import { Checkbox } from "../ui/checkbox";
import { DataTableColumnHeader } from "../data-table-components/column-header";
import { ColumnDef } from "@tanstack/react-table";
import type { fourfourfourrent_listings } from "@prisma/client";
import { cn } from "@/lib/utils";

export const columns: ColumnDef<fourfourfourrent_listings>[] = [
  {
    accessorKey: "id",
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && "indeterminate")
        }
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        aria-label="Select all"
      />
    ),
    cell: ({ row }) => {
      return (
        <Checkbox
          checked={row.getIsSelected()}
          onCheckedChange={(value) => row.toggleSelected(!!value)}
          aria-label="Select row"
          onClick={(event) => {
            event.stopPropagation();
          }}
        />
      );
    },
    enableHiding: false,
  },
  { accessorKey: "building", header: "Building", enableHiding: false },
  {
    accessorKey: "available",
    header: "Available",
    cell: ({ row }) => {
      const isAvailable = row.getValue("available");

      return (
        <div
          className={cn(
            "inline-flex justify-center items-center rounded-full px-2 text-white",
            {
              "bg-green-500": isAvailable,
              "bg-red-500": !isAvailable,
            }
          )}
        >
          {isAvailable ? "True" : "False"}
        </div>
      );
    },
    filterFn: (row, id, value) => {
      const rowValue = row.getValue(id) ? "True" : "False";
      return value.includes(rowValue);
    },
    enableHiding: false,
  },
  {
    accessorKey: "url",
    header: "URL",
    cell: ({ row }) => {
      const url: string = row.getValue("url");

      return url ? (
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:text-blue-800"
          title={url}
          onClick={(event) => {
            event.stopPropagation();
          }}
        >
          Link
        </a>
      ) : (
        <div>No URL</div>
      );
    },
  },
  { accessorKey: "address", header: "Address" },
  {
    accessorKey: "price",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Monthly Rent" />
    ),
  },
  { accessorKey: "rooms", header: "Rooms" },
  {
    accessorKey: "square_feet",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Square Feet" />
    ),
  },
];
