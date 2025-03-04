import MaxWidthWrapper from "@/components/MaxWidthWrapper";
import { ReactNode } from "react";

const Layout = ({ children}:{ children:ReactNode})=>{
    return (
        <MaxWidthWrapper className="flex-1 flex flex-col w-full">
            {children}
        </MaxWidthWrapper>
    )

}
export default Layout;