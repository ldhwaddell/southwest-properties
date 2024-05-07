import { getApplications } from "@/db/utils";
import { ApplicationsDataTable } from "@/components/applications-table/data-table";
import { columns } from "@/components/applications-table/columns";

export const revalidate = 3600;

export default async function Page() {
  const applications = await getApplications();

  return (
    <main className="w-full h-full min-h-screen space-y-2 p-2">
      <ApplicationsDataTable columns={columns} data={applications} />
    </main>
  );
}

// flex-col items-center flex
