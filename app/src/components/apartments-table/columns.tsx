"use client";

import { Checkbox } from "../ui/checkbox";
import { ColumnDef } from "@tanstack/react-table";
import type { apartments_dot_com_listings } from "@prisma/client";
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

export const columns: ColumnDef<apartments_dot_com_listings>[] = [
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

      return <div className="w-40">{rowData || "No Address"}</div>;
    },
  },
  {
    accessorKey: "monthly_rent",
    header: "Monthly Rent",
    cell: ({ row }) => {
      const rowData: string = row.getValue("monthly_rent");

      return <div className="w-24">{rowData || "No Monthly Rent"}</div>;
    },
  },
  {
    accessorKey: "bedrooms",
    header: "Bedrooms",
  },
  {
    accessorKey: "bathrooms",
    header: "Bathrooms",
  },
  {
    accessorKey: "square_feet",
    header: "Square Feet",
    cell: ({ row }) => {
      const rowData: string = row.getValue("square_feet");

      return <div className="w-28">{rowData || "No Square Feet"}</div>;
    },
  },
  {
    accessorKey: "about",
    header: "About",
    cell: ({ row }) =>
      truncateText(row, (row) => row.getValue("about"), 100, "No About"),
  },
  {
    accessorKey: "description",
    header: "Description",
    cell: ({ row }) =>
      truncateText(
        row,
        (row) => row.getValue("description"),
        100,
        "No Description"
      ),
  },
  {
    accessorKey: "amenities",
    header: "Amenities",
    cell: ({ row }) =>
      truncateText(
        row,
        (row) => row.getValue("amenities"),
        100,
        "No Amenities"
      ),
  },
  {
    accessorKey: "fees",
    header: "Fees",
    cell: ({ row }) =>
      truncateText(row, (row) => row.getValue("fees"), 100, "No Fees"),
  },
];
