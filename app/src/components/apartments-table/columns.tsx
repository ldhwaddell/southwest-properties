"use client";

import { Checkbox } from "../ui/checkbox";
import { DataTableColumnHeader } from "../data-table-components/column-header";
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
    <div className="w-full md:w-80 break-words">
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
  { accessorKey: "monthly_rent", header: "Monthly Rent" },
  { accessorKey: "bedrooms", header: "Bedrooms" },
  { accessorKey: "bathrooms", header: "Bathrooms" },
  { accessorKey: "square_feet", header: "Square Feet" },

  //   {
  //     accessorKey: "title",
  //     header: "Title",
  //     cell: ({ row }) => {
  //       const title: string = row.getValue("title");

  //       return title ? <div className="w-80">{title}</div> : <div>No Title</div>;
  //     },
  //     enableHiding: false,
  //   },
  //   {
  //     accessorKey: "active",
  //     header: "Active",
  //     cell: ({ row }) => {
  //       const isActive = row.getValue("active");

  //       return (
  //         <div
  //           className={cn(
  //             "inline-flex justify-center items-center rounded-full px-2 text-white",
  //             {
  //               "bg-green-500": isActive,
  //               "bg-red-500": !isActive,
  //             }
  //           )}
  //         >
  //           {" "}
  //           {isActive ? "True" : "False"}
  //         </div>
  //       );
  //     },

  //     filterFn: (row, id, value) => {
  //       const rowValue = row.getValue(id) ? "True" : "False";
  //       return value.includes(rowValue);
  //     },
  //     enableHiding: false,
  //   },
  //   {
  //     accessorKey: "url",
  //     header: "URL",
  //     cell: ({ row }) => {
  //       const url: string = row.getValue("url");

  //       return url ? (
  //         <a
  //           href={url}
  //           target="_blank"
  //           rel="noopener noreferrer"
  //           className="text-blue-600 hover:text-blue-800"
  //           title={url}
  //           onClick={(event) => {
  //             event.stopPropagation();
  //           }}
  //         >
  //           Link
  //         </a>
  //       ) : (
  //         <div>No URL</div>
  //       );
  //     },
  //   },
  //   {
  //     accessorKey: "last_updated",
  //     header: ({ column }) => (
  //       <DataTableColumnHeader column={column} title="Last Updated" />
  //     ),
  //     sortingFn: "datetime",
  //     cell: ({ row }) => {
  //       const lastUpdated: Date = row.getValue("last_updated");

  //       if (!lastUpdated) return <div>No Last Updated Time</div>;

  //       // Convert the ISO string to a Date object
  //       const dateObject = new Date(lastUpdated);

  //       // Format the date using toLocaleString
  //       const formattedDate = dateObject.toLocaleString("en-US", {
  //         month: "2-digit",
  //         day: "2-digit",
  //         year: "numeric",
  //       });
  //       // Suppress hydration warning because dates are weird
  //       return <div suppressHydrationWarning>{formattedDate}</div>;
  //     },
  //   },
  //   {
  //     accessorKey: "summary",
  //     header: "Summary",
  //     cell: ({ row }) =>
  //       truncateText(row, (row) => row.getValue("summary"), 100, "No Summary"),
  //   },
  //   {
  //     accessorKey: "contact_info",
  //     header: "Contact Info",
  //     cell: ({ row }) => {
  //       const contactInfoStr: string = row.getValue("contact_info");

  //       try {
  //         const parsedContactInfo = JSON.parse(contactInfoStr || "{}");

  //         if (parsedContactInfo && parsedContactInfo.name) {
  //           return <div>{parsedContactInfo.name}</div>;
  //         } else {
  //           return <div>No contact</div>;
  //         }
  //       } catch (e) {
  //         return <div>No contact</div>;
  //       }
  //     },
  //   },
];