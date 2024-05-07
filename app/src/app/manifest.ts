import { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Landlords and Listings NS",
    short_name: "LLNS",
    description: "Data and insights on rental listings and landlords in Nova Scotia",
    start_url: "/",
    display: "standalone",
  };
}