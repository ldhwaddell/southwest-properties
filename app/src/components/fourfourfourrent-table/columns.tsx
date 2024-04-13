"use client";

import { Checkbox } from "../ui/checkbox";
import { DataTableColumnHeader } from "../data-table-components/column-header";
import { ColumnDef } from "@tanstack/react-table";
import type { fourfourfourrent_listings } from "@prisma/client";
import { cn } from "@/lib/utils";

type GetValueFunction<T> = (row: T) => string | null | undefined;

function truncateText<T>(
  row: T,
  getValue: GetValueFunction<T>,
  maxLength: number,
  noValueMessage: string
): JSX.Element {
  const text = getValue(row);
  const truncatedText =
    text && text.length > maxLength
      ? `${text.substring(0, maxLength)}...`
      : text;

  return (
    <div className={`w-full md:w-80 break-words`}>
      {text ? truncatedText : noValueMessage}
    </div>
  );
}

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
  {
    accessorKey: "building",
    header: "Building",
    cell: ({ row }) => {
      const rowData: string = row.getValue("building");

      return <div className="w-40">{rowData || "No Building"}</div>;
    },
    enableHiding: false,
  },
  {
    accessorKey: "unit",
    header: "Unit",
    cell: ({ row }) => {
      const rowData: string = row.getValue("unit");

      return <div className="w-20">{rowData || "No Unit"}</div>;
    },
  },
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
  {
    accessorKey: "address",
    header: "Address",
    cell: ({ row }) => {
      const rowData: string = row.getValue("address");

      return <div className="w-44">{rowData || "No Address"}</div>;
    },
  },
  { accessorKey: "management", header: "Management" },
  {
    accessorKey: "available_date",
    header: "Available Date",
    cell: ({ row }) => {
      const rowData: string = row.getValue("available_date");

      return <div className="w-24">{rowData || "No Available Date"}</div>;
    },
  },
  {
    accessorKey: "price",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Monthly Rent" />
    ),
    cell: ({ row }) => {
      const rowData: string = row.getValue("price");

      return <div className="w-20">{rowData || "No Monthly Rent"}</div>;
    },
  },
  {
    accessorKey: "rooms",
    header: "Rooms",
    cell: ({ row }) => {
      const rowData: string = row.getValue("rooms");

      return <div className="w-32">{rowData || "No Rooms"}</div>;
    },
  },
  {
    accessorKey: "square_feet",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Square Feet" />
    ),
    cell: ({ row }) => {
      const rowData: string = row.getValue("square_feet");

      return <div className="w-28">{rowData || "No Square Feet"}</div>;
    },
  },
  {
    accessorKey: "leasing_info",
    header: "Leasing Info",
    cell: ({ row }) =>
      truncateText(
        row,
        (row) => row.getValue("leasing_info"),
        100,
        "No Leasing Info"
      ),
  },
  {
    accessorKey: "description_info",
    header: "Description Info",
    cell: ({ row }) =>
      truncateText(
        row,
        (row) => row.getValue("description_info"),
        100,
        "No Description"
      ),
  },
  {
    accessorKey: "building_info",
    header: "Building Info",
    cell: ({ row }) =>
      truncateText(
        row,
        (row) => row.getValue("building_info"),
        100,
        "No Building Info"
      ),
  },
  {
    accessorKey: "suite_info",
    header: "Suite Info",
    cell: ({ row }) =>
      truncateText(
        row,
        (row) => row.getValue("suite_info"),
        100,
        "No Suite Info"
      ),
  },
];
