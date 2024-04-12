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

type ListingSource = "444rent" | "apartments";

export function RentalListings() {
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
      {listingSource === "apartments" && <div>yurrrr</div>}
    </>
  );
}
