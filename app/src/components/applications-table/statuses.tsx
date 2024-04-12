import { ForwardRefExoticComponent, RefAttributes } from "react";
import { CheckCircledIcon, CrossCircledIcon } from "@radix-ui/react-icons";
import { IconProps } from "@radix-ui/react-icons/dist/types";

export type Status = {
  value: string;
  label: string;
  icon: ForwardRefExoticComponent<IconProps & RefAttributes<SVGSVGElement>>;
};

export const statuses: Status[] = [
  {
    value: "True",
    label: "Active",
    icon: CheckCircledIcon,
  },
  {
    value: "False",
    label: "Inactive",
    icon: CrossCircledIcon,
  },
];
