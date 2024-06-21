import MaxWidthWrapper from "./MaxWidthWrapper";

import Link from "next/link";
import { buttonVariants } from "./ui/button";
import { ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
// import { getKindeServerSession as getServerSession }  from "@kinde-oss/kinde-auth-nextjs/server";
const Navbar =  async () => {
        // // const { getUser} = getServerSession();
        // // const user = await getUser();
        // const isAdmin = user?.email===process.env.ADMIN_EMAIL;
        return (
           <nav className="sticky z-[100] h-14 inset-x-0 top-0 w-full border-b
           border-gray-200 bg-white/75 backdrop-blur-lg transition-all">
            <MaxWidthWrapper >
                <div className="flex h-14 items-center justify-between border-b border-zinc-200">
                    <Link href="/" className="flex flex:display  font-bold text-lg text-black-200"
                   >
                    <span  className="text-2xl font-bold mt-3">chaiWith</span>
                    <span className="text-red-600  box-content box-shadow">
                        <img src="data:image/png;base64,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"
                            alt="homePageLogo"  className="md:box md:cover h-12 mx-1 my-1 rounded-2xl"/>
                     </span>
                   </Link>

                <div className="h-full flex items-center space-x-4">
                                            
                    <Link href='/home' className={buttonVariants({
                        variant: "ghost",
                        size: "sm"
                    })}>  Home    </Link>
                
                
                    <Link href='#' className={buttonVariants({
                        variant: "ghost",
                        size: "sm"
                    })}>  About ✨   </Link>

                    <Link href='/pdf/upload' className={buttonVariants({
                        variant: "ghost",
                        size: "sm",
                        className:"hidden sm:flex  bg-slate-400 items-center gap-1"
                    })}>  Chat with PDF 📄 </Link>

                    <Link href='#' className={buttonVariants({
                        variant: "ghost",
                        size: "sm",
                        className:"hidden sm:flex items-center bg-slate-200 gap-1"
                    })}>  Chat with <img src="https://em-content.zobj.net/content/2020/04/05/yt.png"  className="h-5"alt="yt" /> 
                            YouTube </Link>


                     <Link href='#' className={buttonVariants({
                        className:"hidden sm:flex items-center gap-1",
                        size: "sm"
                    })}>  Sign IN</Link>


                    <Link href='#' className={buttonVariants({
                        className:"hidden sm:flex items-center gap-1",
                        size: "sm"
                    })}>  Sign UP
                    <ArrowRight className="ml-1.5 h-5 w-5" /></Link>
                </div>
                </div>
            </MaxWidthWrapper>
           </nav>
                
        )
    };

    export default Navbar;

