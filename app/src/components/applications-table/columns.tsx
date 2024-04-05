"use client";

import { Checkbox } from "../ui/checkbox";
import { ColumnDef } from "@tanstack/react-table";
import type { applications } from "@prisma/client";

export const columns: ColumnDef<applications>[] = [
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
      return <div>{isActive ? "True" : "False"}</div>;
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
      const MAX_LENGTH = 30;

      const truncatedURL =
        url && url.length > MAX_LENGTH
          ? url.substring(0, MAX_LENGTH) + "..."
          : url;

      return url ? (
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:text-blue-800"
          title={url}
        >
          {truncatedURL}
        </a>
      ) : (
        <div>No URL</div>
      );
    },
  },
  {
    accessorKey: "last_updated",
    header: "Last Updated",
    cell: ({ row }) => {
      const lastUpdated: Date = row.getValue("last_updated");

      if (!lastUpdated) return <div>No Last Updated Time</div>;

      // Convert the ISO string to a Date object
      const dateObject = new Date(lastUpdated);

      // Format the date using toLocaleString
      const formattedDate = dateObject.toLocaleString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
      // Suppress hydration warning because dates are weird
      return <div suppressHydrationWarning>{formattedDate}</div>;
    },
  },
  {
    accessorKey: "summary",
    header: "Summary",
  },
  {
    accessorKey: "proposal",
    header: "Proposal",
    cell: ({ row }) => {
      const proposalText: string = row.getValue("proposal");
      const MAX_LENGTH = 100;

      const truncatedText =
        proposalText && proposalText.length > MAX_LENGTH
          ? proposalText.substring(0, MAX_LENGTH) + "..."
          : proposalText;

      return proposalText ? <div>{truncatedText}</div> : <div>No Proposal</div>;
    },
  },
];
