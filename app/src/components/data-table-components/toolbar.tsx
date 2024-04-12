"use client";

import { Cross2Icon } from "@radix-ui/react-icons";
import { Table } from "@tanstack/react-table";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import type { Status } from "../applications-table/statuses";
import { DataTableFacetedFilter } from "./faceted-filter";

import { DataTableViewOptions } from "./view-options";
import { ExportExcel } from "./export-excel";

interface DataTableToolbarProps<TData> {
  table: Table<TData>;
  statuses: Status[];
  defaultExportFileName: string
}

export function DataTableToolbar<TData>({
  table,
  statuses,
  defaultExportFileName
}: DataTableToolbarProps<TData>) {
  const isFiltered = table.getState().columnFilters.length > 0;

  return (
    <div className="flex items-center justify-between">
      <div className="flex flex-1 items-center space-x-2">
        <Input
          placeholder="Filter applications..."
          value={(table.getColumn("title")?.getFilterValue() as string) ?? ""}
          onChange={(event) =>
            table.getColumn("title")?.setFilterValue(event.target.value)
          }
          className="h-8 w-[150px] lg:w-[250px]"
        />
        {table.getColumn("active") && (
          <DataTableFacetedFilter
            column={table.getColumn("active")}
            title="Active"
            options={statuses}
          />
        )}

        {isFiltered && (
          <Button
            variant="ghost"
            onClick={() => table.resetColumnFilters()}
            className="h-8 px-2 lg:px-3"
          >
            Reset
            <Cross2Icon className="ml-2 h-4 w-4" />
          </Button>
        )}
      </div>
      <DataTableViewOptions table={table} />
      <ExportExcel table={table} defaultFileName={defaultExportFileName} />
    </div>
  );
}
