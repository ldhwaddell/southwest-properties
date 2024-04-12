"use client";

import React, { useState } from "react";

import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { ApartmentsDataTable } from "./apartments-table/data-table";
import { columns as apartmentsColumns } from "./apartments-table/columns";
import type {
  apartments_dot_com_listings,
  fourfourfourrent_listings,
} from "@prisma/client";

type ListingSource = "444rent" | "apartments";

interface RentalListingsProps {
  apartments_dot_com_listings: apartments_dot_com_listings[];
  fourfourfourrent_listings: fourfourfourrent_listings[];
}

export function RentalListings({
  apartments_dot_com_listings,
  fourfourfourrent_listings,
}: RentalListingsProps) {
  const [listingSource, setListingSource] = useState<ListingSource>("444rent");

  const handleListingSourceChange = (newValue: ListingSource) => {
    setListingSource(newValue);
  };

  return (
    <>
      <Select
        defaultValue={listingSource}
        value={listingSource}
        onValueChange={handleListingSourceChange}
      >
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Select a listing source" />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectLabel>Sources</SelectLabel>
            <SelectItem value="444rent">444rent.com</SelectItem>
            <SelectItem value="apartments">apartments.com</SelectItem>
          </SelectGroup>
        </SelectContent>
      </Select>
        {listingSource === "444rent" && <div>wooo</div>}
        {listingSource === "apartments" && (
          <ApartmentsDataTable
            columns={apartmentsColumns}
            data={apartments_dot_com_listings}
          />
        )}
    </>
  );
}
