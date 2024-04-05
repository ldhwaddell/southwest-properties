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
import { Table, Row } from "@tanstack/react-table";
import { Workbook } from "exceljs";
import * as FileSaver from "file-saver";

interface ExportExcelProps<TData> {
  table: Table<TData>;
  defaultFileName: string;
}

type UserModel = {
  id: number;
  name: string;
  phone: string;
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

  // if (allColumnsChecked) {
  //   console.log(table.getAllColumns());
  // } else {
  //   console.log(table.getVisibleFlatColumns());
  // }

  const generateExcelFile = async () => {
    const fileType =
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8";
    const fileExtension = ".xlsx";
    const workbook = new Workbook();
    const worksheet = workbook.addWorksheet(defaultFileName);

    // Define column based on switch
    if (allColumnsChecked) {
      console.log(table.getAllFlatColumns());
    } else {
      console.log(table.getVisibleFlatColumns());
    }

    // 3. Define columns and bind data fields to columns.
    worksheet.columns = [
      {
        header: "ID", // Label of column's header.
        key: "id", // The key to bind data field to column, see it in the {UserModel} above.
        width: 10, // Optional, column width
      },
      { header: "Name", key: "name", width: 32 },
      { header: "Phone", key: "phone", width: 32 },
    ];
    // 4. Add the data array to the worksheet
    // worksheet.addRows(data);
    // // you may also add an array of data as a row to while not using the header binding.
    // // worksheet.addRow([1, 'John Doe', '0123456789']);
    // const buffer = await workbook.xlsx.writeBuffer();

    // const excelBlob = new Blob([buffer], { type: fileType });

    // FileSaver.saveAs(excelBlob, fileName + fileExtension);
  };

  const users: UserModel[] = [
    { id: 1, name: "John", phone: "123456789" },
    { id: 2, name: "Anne", phone: "987654321" },
    { id: 3, name: "Zack", phone: "123987456" },
    { id: 4, name: "Jill", phone: "456123789" },
    { id: 5, name: "Judy", phone: "789456123" },
    { id: 6, name: "Jenny", phone: "123789456" },
    { id: 7, name: "David", phone: "456789123" },
  ];

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
