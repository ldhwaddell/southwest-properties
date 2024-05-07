import prisma from "./prisma";
import { cache } from "react";
import type { applications, application_histories } from "@prisma/client";

export type Application = applications & {
  application_histories: application_histories[];
};

export const getApplications = cache(async (): Promise<Application[]> => {
  const applications = await prisma.applications.findMany({
    include: {
      application_histories: {
        orderBy: {
          created_at: "desc",
        },
      },
    },
  });

  return applications;
});
