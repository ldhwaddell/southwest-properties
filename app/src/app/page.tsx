import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import { ModeToggle } from "@/components/mode-toggle";
import { Header } from "@/components/header";

import { getApplications } from "@/db/utils";

export const revalidate = 3600;

export default async function Home() {
  const applications = await getApplications();

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
              <CardDescription>{`${applications}`}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="space-y-1">ociencioen</div>
            </CardContent>
            <CardFooter>
              <Button>Save changes</Button>
            </CardFooter>
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
