import prisma from "../db/prisma";
import { cache } from "react";
import type { applications } from "@prisma/client";

export const getApplications = cache(async (): Promise<applications[]> => {
  const applications: applications[] = await prisma.applications.findMany();
  return applications;
});
