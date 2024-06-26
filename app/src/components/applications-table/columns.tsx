"use client";

import { Checkbox } from "../ui/checkbox";
import { DataTableColumnHeader } from "../data-table-components/column-header";
import { ColumnDef } from "@tanstack/react-table";
import type { Application } from "@/db/utils";
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

export const columns: ColumnDef<Application>[] = [
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
    accessorKey: "title",
    header: "Title",
    cell: ({ row }) => {
      const title: string = row.getValue("title");

      return title ? <div className="w-80">{title}</div> : <div>No Title</div>;
    },
    enableHiding: false,
  },
  {
    accessorKey: "active",
    header: "Active",
    cell: ({ row }) => {
      const isActive = row.getValue("active");

      return (
        <div
          className={cn(
            "inline-flex justify-center items-center rounded-full px-2 text-white",
            {
              "bg-green-500": isActive,
              "bg-red-500": !isActive,
            }
          )}
        >
          {" "}
          {isActive ? "True" : "False"}
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
    accessorKey: "last_updated",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Last Updated" />
    ),
    sortingFn: "datetime",
    cell: ({ row }) => {
      const lastUpdated: Date = row.getValue("last_updated");

      if (!lastUpdated) return <div>No Last Updated Time</div>;

      // Convert the ISO string to a Date object
      const dateObject = new Date(lastUpdated);

      // Format the date using toLocaleString
      const formattedDate = dateObject.toLocaleString("en-US", {
        month: "2-digit",
        day: "2-digit",
        year: "numeric",
      });
      // Suppress hydration warning because dates are weird
      return <div suppressHydrationWarning>{formattedDate}</div>;
    },
  },
  {
    accessorKey: "summary",
    header: "Summary",
    cell: ({ row }) =>
      truncateText(row, (row) => row.getValue("summary"), 100, "No Summary"),
  },
  {
    accessorKey: "update_notice",
    header: "Update Notice",
    cell: ({ row }) =>
      truncateText(
        row,
        (row) => row.getValue("update_notice"),
        100,
        "No Update Notice"
      ),
  },
  {
    accessorKey: "request",
    header: "Request",
    cell: ({ row }) =>
      truncateText(row, (row) => row.getValue("request"), 100, "No Request"),
  },
  {
    accessorKey: "proposal",
    header: "Proposal",
    cell: ({ row }) =>
      truncateText(row, (row) => row.getValue("proposal"), 100, "No Proposal"),
  },
  {
    accessorKey: "process",
    header: "Process",
    cell: ({ row }) =>
      truncateText(row, (row) => row.getValue("process"), 100, "No Process"),
  },
  {
    accessorKey: "documents_submitted_for_evaluation",
    header: "Documents",
    cell: ({ row }) =>
      truncateText(
        row,
        (row) => row.getValue("documents_submitted_for_evaluation"),
        100,
        "No documents"
      ),
  },
  {
    accessorKey: "contact_info",
    header: "Contact Info",
    cell: ({ row }) => {
      const contactInfoStr: string = row.getValue("contact_info");

      try {
        const parsedContactInfo = JSON.parse(contactInfoStr || "{}");

        if (parsedContactInfo && parsedContactInfo.name) {
          return <div>{parsedContactInfo.name}</div>;
        } else {
          return <div>No contact</div>;
        }
      } catch (e) {
        return <div>No contact</div>;
      }
    },
  },
];
