"use client";
import React, { useState } from "react";

import {
  ColumnDef,
  SortingState,
  ColumnFiltersState,
  flexRender,
  getCoreRowModel,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
  Row,
} from "@tanstack/react-table";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { DataTablePagination } from "../data-table-components/pagination";
import { DataTableToolbar } from "../data-table-components/toolbar";
import { RowDialog } from "./row-dialog";
import { statuses } from "./statuses";

interface ApplicationsDataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
}

export function ApplicationsDataTable<TData, TValue>({
  columns,
  data,
}: ApplicationsDataTableProps<TData, TValue>) {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  // State to hold the selected row data
  const [selectedRowData, setSelectedRowData] = useState<Row<TData> | null>(
    null
  );

  // Increase default page size
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 20,
  });

  // Allow sorting
  const [sorting, setSorting] = useState<SortingState>([]);

  // Event handler for opening the dialog with the clicked row's data
  const handleRowClick = (row: Row<TData>) => {
    setSelectedRowData(row);
    setIsDialogOpen(true);
  };

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onColumnFiltersChange: setColumnFilters,
    getFilteredRowModel: getFilteredRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
    getFacetedRowModel: getFacetedRowModel(),
    onPaginationChange: setPagination,
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    state: {
      columnFilters,
      pagination,
      sorting,
    },
  });

  return (
    <>
      <DataTableToolbar
        table={table}
        statuses={statuses}
        defaultExportFileName="applications"
        filterInputPlaceholder="Filter Applications..."
        filterColumn="title"
        facetedFilterColumm="active"
        facetedFilterTitle="Active"
      />
      <div className="rounded-md border">
        {/* Modify h-full to make table take up entire screen but not more */}
        <div className="h-[55vh] relative overflow-auto">
          <Table>
            <TableHeader className="sticky top-0 bg-secondary">
              {table.getHeaderGroups().map((headerGroup) => (
                <TableRow key={headerGroup.id}>
                  {headerGroup.headers.map((header) => {
                    return (
                      <TableHead key={header.id}>
                        {header.isPlaceholder
                          ? null
                          : flexRender(
                              header.column.columnDef.header,
                              header.getContext()
                            )}
                      </TableHead>
                    );
                  })}
                </TableRow>
              ))}
            </TableHeader>
            <TableBody>
              {table.getRowModel().rows?.length ? (
                table.getRowModel().rows.map((row) => (
                  <TableRow
                    key={row.id}
                    data-state={row.getIsSelected() && "selected"}
                    onClick={() => handleRowClick(row)}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id}>
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell
                    colSpan={columns.length}
                    className="h-24 text-center"
                  >
                    No results.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
          {selectedRowData && (
            <RowDialog
              isOpen={isDialogOpen}
              onClose={() => setIsDialogOpen(false)}
              row={selectedRowData}
            />
          )}
        </div>
      </div>

      <DataTablePagination table={table} />
    </>
  );
}
