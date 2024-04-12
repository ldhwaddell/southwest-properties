import prisma from "./prisma";
import { cache } from "react";
import type {
  applications,
  apartments_dot_com_listings,
  fourfourfourrent_listings,
} from "@prisma/client";

export const getApplications = cache(async (): Promise<applications[]> => {
  const applications: applications[] = await prisma.applications.findMany();
  return applications;
});

export const getApartmentsDotComListings = cache(
  async (): Promise<apartments_dot_com_listings[]> => {
    const apartments_dot_com_listings: apartments_dot_com_listings[] =
      await prisma.apartments_dot_com_listings.findMany();
    return apartments_dot_com_listings;
  }
);

export const get444RentListings = cache(
  async (): Promise<fourfourfourrent_listings[]> => {
    const fourfourfourrent_listings: fourfourfourrent_listings[] =
      await prisma.fourfourfourrent_listings.findMany();

    return fourfourfourrent_listings;
  }
);
