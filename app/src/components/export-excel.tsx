import { Button } from "./ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "./ui/switch";

import React, { useState } from "react";

import { File } from "lucide-react";
import { Table } from "@tanstack/react-table";
import { Workbook } from "exceljs";
import * as FileSaver from "file-saver";

interface ExportExcelProps<TData> {
  table: Table<TData>;
  defaultFileName: string;
}

const formatSnakeCaseToTitle = (text: string): string => {
  const words = text.split("_");

  // Capitalize the first letter of each word and join them with a space
  const formattedText = words
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");

  return formattedText;
};

export function ExportExcel<TData>({
  table,
  defaultFileName,
}: ExportExcelProps<TData>) {
  const [fileName, setFileName] = useState<string>(defaultFileName);
  const [allColumnsChecked, setAllColumnsChecked] = useState<boolean>(false);

  const handleFileNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFileName(event.target.value);
  };

  const generateExcelFile = async () => {
    const fileType =
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8";
    const fileExtension = ".xlsx";

    const workbook = new Workbook();
    const worksheet = workbook.addWorksheet(defaultFileName);
    let columns;

    // Define column based on switch position
    if (allColumnsChecked) {
      columns = table.getAllFlatColumns();
    } else {
      columns = table.getVisibleFlatColumns();
    }

    const sheetColumns = columns.map((column) => {
      return {
        header: formatSnakeCaseToTitle(column.id),
        key: column.id,
      };
    });

    worksheet.columns = sheetColumns;

    const selectedRows = table.getSelectedRowModel();

    // Match the desired columns with the fields from the rows
    const dataForExport = selectedRows.rows.map((row) => {
      const rowData: TData = row.original;
      // Construct an object for the current row with keys and values matching the sheet columns
      const rowObjectForSheet: Partial<TData> = {};

      sheetColumns.forEach((column) => {
        rowObjectForSheet[column.key as keyof TData] =
          rowData[column.key as keyof TData];
      });

      return rowObjectForSheet;
    });

    worksheet.addRows(dataForExport);

    const buffer = await workbook.xlsx.writeBuffer();

    const excelBlob = new Blob([buffer], { type: fileType });

    FileSaver.saveAs(excelBlob, fileName + fileExtension);
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        {/* Disable button is no rows are selected */}
        <Button
          variant="outline"
          size="sm"
          className="h-8 lg:flex ml-2"
          disabled={!table.getIsSomeRowsSelected()}
        >
          <File className="h-3.5 w-3.5" />
          <span className="sr-only sm:not-sr-only">Export</span>
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Export Excel File</DialogTitle>
          <DialogDescription>
            Name your file here and choose what columns you want. Click download
            to save the file
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-9">
            <Label htmlFor="fileName" className="text-right col-span-1">
              File Name
            </Label>
            <Input
              id="fileName"
              className="col-span-3"
              value={fileName}
              onChange={handleFileNameChange}
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-5">
            <div className="text-right col-span-1">
              <Label htmlFor="allColumns">All Columns</Label>
            </div>
            <Switch
              id="allColumns"
              checked={allColumnsChecked}
              onClick={() => setAllColumnsChecked((prev) => !prev)}
            />
          </div>
        </div>
        <DialogFooter>
          <Button type="submit" onClick={() => generateExcelFile()}>
            Download
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
