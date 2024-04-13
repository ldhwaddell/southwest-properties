import { Header } from "@/components/header";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";

import { columns } from "@/components/applications-table/columns";
import { ApplicationsDataTable } from "@/components/applications-table/data-table";
import { RentalListings } from "@/components/rental-listings";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import {
  getApplications,
  getApartmentsDotComListings,
  get444RentListings,
} from "@/db/utils";

import type {
  applications,
  apartments_dot_com_listings,
  fourfourfourrent_listings,
} from "@prisma/client";

export const revalidate = 3600;

export default async function Page() {
  // Get data for tables
  const applications: applications[] = await getApplications();
  const apartments_dot_com_listings: apartments_dot_com_listings[] =
    await getApartmentsDotComListings();
  const fourfourfourrent_listings: fourfourfourrent_listings[] =
    await get444RentListings();

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
              <CardDescription>
                This shows all applications that have been found since
                collections began. Click a row to see more detailed information. 
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <ApplicationsDataTable columns={columns} data={applications} />
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="rentals">
          <Card>
            <CardHeader>
              <CardDescription>
                This shows all rentals currently listed on the currently
                targeted posting websites. Click a row to see more detailed information. 
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
                <RentalListings
                  apartments_dot_com_listings={apartments_dot_com_listings}
                  fourfourfourrent_listings={fourfourfourrent_listings}
                />
            </CardContent>
            <CardFooter></CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
