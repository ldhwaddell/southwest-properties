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
  defaultExportFileName: string;
  filterInputPlaceholder: string;
  filterColumn: string;
  facetedFilterColumm: string;
  facetedFilterTitle: string;
}

export function DataTableToolbar<TData>({
  table,
  statuses,
  defaultExportFileName,
  filterInputPlaceholder,
  filterColumn,
  facetedFilterColumm,
  facetedFilterTitle,
}: DataTableToolbarProps<TData>) {
  const isFiltered = table.getState().columnFilters.length > 0;

  return (
    <div className="flex items-center justify-between h-8">
      <div className="flex flex-1 items-center space-x-2">
        <Input
          placeholder={filterInputPlaceholder}
          value={
            (table.getColumn(filterColumn)?.getFilterValue() as string) ?? ""
          }
          onChange={(event) =>
            table.getColumn(filterColumn)?.setFilterValue(event.target.value)
          }
          className="h-8 w-[150px] lg:w-[250px]"
        />
        {table.getColumn(facetedFilterColumm) && (
          <DataTableFacetedFilter
            column={table.getColumn(facetedFilterColumm)}
            title={facetedFilterTitle}
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
