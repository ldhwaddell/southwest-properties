import prisma from "../db/prisma";
import { cache } from "react";

export const getApplications = cache(async () => {
  const applications = await prisma.applications.findMany();
  return applications;
});

