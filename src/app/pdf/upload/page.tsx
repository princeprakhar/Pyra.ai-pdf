'use client'

import { Progress } from "@/components/ui/progress";
import { useToast } from "@/components/ui/use-toast";
import { cn } from "@/lib/utils";
import { Image, Loader, MousePointerSquareDashed } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";
import Dropzone, { FileRejection } from "react-dropzone";
 const Page = () => {

    const { toast } = useToast()
    const [isDragOver, setIsDragOver] = useState<boolean>(false);
    const onDropRejected = (rejectedFiles: FileRejection[]) => {
        const [file]  = rejectedFiles;
        setIsDragOver(false);
        toast({
            title: "File Rejected",
            description: `File ${file.file.name} was rejected because it is not a valid supported file`,
            variant: "destructive",
        });
    }

    const onDropAccepted = (acceptedFiles:File[]) => {
        console.log("acceptedFiles");
        toast({
          title: "PDF uploaded successfully",
          description: `File ${acceptedFiles[0].name} was uploaded successfully`,
          variant: "default",
      });
        setIsDragOver(false);
    }
    const [isPending , startTransition]= useTransition();
    const [uploadProgress, setUploadProgress] = useState<number>(0);
    const router = useRouter();
    const isUploading = false;

    return (
      <div
        className={cn(
          "relative h-full  flex-1 my-16 w-full rounded-xl bg-gray-900/5 p-2 ring-1 ring-inset ring-gray-900/10 lg:2xl flex justifiy-center flex-col items-senter",
          {
            "ring-blue-900/25 bg-blue-900/10": isDragOver,
          }
        )}
      >
        {/*  Add the Dropzone component */}
        <div className="relative flex flex-1 flex-col items-center justify-center w-full ">
          <Dropzone
            onDropRejected={onDropRejected}
            onDropAccepted={onDropAccepted}
            accept={{
              "pdf": [".pdf"],
            }}
            onDragEnter={() => setIsDragOver(true)}
            onDragLeave={() => setIsDragOver(false)}
          >
            {({ getRootProps, getInputProps }) => (
              <div
                {...getRootProps()}
                className="flex flex-1
                            flex-col items-center justify-center w-full h-full"
              >
                <input {...getInputProps()} />
                {isDragOver ? (
                  <MousePointerSquareDashed className="text-blue-900/50 w-16 h-16 mb-2" />
                ) : isUploading || isPending ? (
                  <Loader className="animate-spin h-6 w-6 text-zinc-500 mb-2" />
                ) : (
                  <Image className="w-16 h-16 mb-2" />
                )}
                <div className="flex flex-col justify-center mb-2 text-sm">
                  {isUploading ? (
                    <div className="flex flex-col items-center">
                      <p>Uploading...</p>

                      <Progress
                        value={uploadProgress}
                        className="mt-2 w-40 h-2 bg-gray-300"
                      />
                    </div>
                  ) : isPending ? (
                    <div className="flex flex-col items-center">
                      <p>Processing...</p>
                    </div>
                  ) : isDragOver ? (
                    <span className="font-semibold">
                      Drop file <span>to upload</span>
                    </span>
                  ) : (
                    <p>
                      <span className="font-semibold">Click here Upload</span>{" "}
                      or Drag and drop your files here
                    </p>
                  )}
                </div>
                {isPending ? null : (
                  <p className="text-xs text-zinc-500">only PDF</p>
                )}
              </div>
            )}
          </Dropzone>
        </div>
      </div>
    );
 }
 export default Page;


