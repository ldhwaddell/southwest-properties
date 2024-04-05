import { Header } from "@/components/header";
import { ModeToggle } from "@/components/mode-toggle";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { columns } from "@/components/applications-table/columns";
import { DataTable } from "@/components/applications-table/data-table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import { getApplications } from "@/db/utils";
import type { applications } from "@prisma/client";

export const revalidate = 3600;

export default async function Home() {
  const applications: applications[] = await getApplications();

  return (
    <div className="p-2.5 m-2.5 min-h-screen">
      <Header />
      <Tabs defaultValue="applications">
        <TabsList className="grid grid-cols-2">
          <TabsTrigger value="applications">Applications</TabsTrigger>
          <TabsTrigger value="rentals">Rentals</TabsTrigger>
        </TabsList>
        <TabsContent value="applications">
          <Card>
            <CardHeader>
              <CardTitle>Account</CardTitle>
              <CardDescription>This shows all applications that have been found since the </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
            <DataTable columns={columns} data={applications} />


            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="rentals">
          <Card>
            <CardHeader>
              <CardTitle>Account</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="space-y-1">ociencioen</div>
            </CardContent>
            <CardFooter>
              <Button>Save changes</Button>
            </CardFooter>{" "}
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
