// 'use client'

// import { Progress } from "@/components/ui/progress";
// import { useToast } from "@/components/ui/use-toast";
// import { cn } from "@/lib/utils";
// import { Image, Loader, MousePointerSquareDashed } from "lucide-react";
// import { useRouter } from "next/navigation";
// import { useEffect, useState, useTransition } from "react";
// import Dropzone, { FileRejection } from "react-dropzone";
// import axios from "axios";
// import { BACKEND_URL } from "@/utils/constant";
// import { useAuth } from "@/contexts/AuthContext";

// const Page = () => {
//   const { toast } = useToast();
//   const [isDragOver, setIsDragOver] = useState<boolean>(false);
//   const [isUploading, setIsUploading] = useState<boolean>(false);
//   const [uploadProgress, setUploadProgress] = useState<number>(0);
//   const [isPending, startTransition] = useTransition();
//   const router = useRouter();
//   const { isLoggedIn } = useAuth();

//   useEffect(() => {
//     if (typeof window !== "undefined" && !isLoggedIn) {
//       toast({
//         title: "SignIn Required",
//         description: "Signin required to chat with the PDF.",
//         variant: "destructive",
//         className: "text-white",
//       });
//       router.push("/auth/signin");
//     }
//   }, [isLoggedIn, router, toast]);

//   const onDropRejected = (rejectedFiles: FileRejection[]) => {
//     const [file] = rejectedFiles;
//     setIsDragOver(false);
//     toast({
//       title: "File Rejected",
//       description: `File ${file.file.name} was rejected because it is not a valid supported file`,
//       variant: "destructive",
//     });
//   };

//   const onDropAccepted = async (acceptedFiles: File[]) => {
//     setIsUploading(true);
//     setUploadProgress(0);
//     setIsDragOver(false);

//     try {
//       // Create a blob URL for the PDF to display in the chat page
//       const pdfBlobUrl = URL.createObjectURL(acceptedFiles[0]);
//       localStorage.setItem("pdfBlobUrl", pdfBlobUrl);
//       localStorage.setItem("pdfFileName", acceptedFiles[0].name);

//       const formData = new FormData();
//       formData.append("file", acceptedFiles[0]);

//       const response = await axios.post(`${BACKEND_URL}/upload-doc`, formData, {
//         headers: {
//           Authorization: `Bearer ${localStorage.getItem("Token")}`,
//           "Content-Type": "multipart/form-data",
//         },
//         onUploadProgress: (progressEvent) => {
//           if (progressEvent.total) {
//             const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
//             setUploadProgress(percentCompleted);
//           }
//         },
//       });

//       setIsUploading(false);
//       toast({
//         title: "PDF uploaded successfully",
//         description: `File ${acceptedFiles[0].name} was uploaded successfully`,
//         variant: "default",
//       });

//       // Save document ID from response if available
//       if (response.data && response.data.document_id) {
//         localStorage.setItem("documentId", response.data.document_id);
//       }

//       // Navigate to chat page after successful upload
//       startTransition(() => {
//         router.push("/chat");
//       });
//     } catch (error) {
//       console.error("Upload error:", error);
//       setIsUploading(false);
//       toast({
//         title: "Upload error",
//         description: "An error occurred during upload",
//         className: "text-white",
//         variant: "destructive",
//       });
//     }
//   };

//   return (
//     <div
//       className={cn(
//         "relative h-full flex-1 my-16 w-full dark:border-2 rounded-xl bg-gray-900/5 p-2 ring-1 ring-inset ring-gray-900/10 flex justify-center flex-col items-center",
//         {
//           "ring-blue-900/25 bg-blue-900/10": isDragOver,
//         }
//       )}
//     >
//       <div className="relative flex flex-1 flex-col items-center justify-center w-full">
//         <Dropzone
//           onDropRejected={onDropRejected}
//           onDropAccepted={onDropAccepted}
//           accept={{
//             "application/pdf": [".pdf"],
//           }}
//           onDragEnter={() => setIsDragOver(true)}
//           onDragLeave={() => setIsDragOver(false)}
//         >
//           {({ getRootProps, getInputProps }) => (
//             <div {...getRootProps()} className="flex flex-1 flex-col items-center justify-center w-full h-full">
//               <input {...getInputProps()} />
//               {isDragOver ? (
//                 <MousePointerSquareDashed className="text-blue-900/50 w-16 h-16 mb-2" />
//               ) : isUploading || isPending ? (
//                 <Loader className="animate-spin h-6 w-6 text-zinc-500 mb-2" />
//               ) : (
//                 <Image className="w-16 h-16 mb-2" />
//               )}
//               <div className="flex flex-col justify-center mb-2 text-sm">
//                 {isUploading ? (
//                   <div className="flex flex-col items-center">
//                     <p>Uploading...</p>
//                     <Progress value={uploadProgress} className="mt-2 w-40 h-2 bg-gray-300" />
//                   </div>
//                 ) : isPending ? (
//                   <div className="flex flex-col items-center">
//                     <p>Processing...</p>
//                   </div>
//                 ) : isDragOver ? (
//                   <span className="font-semibold">
//                     Drop file <span>to upload</span>
//                   </span>
//                 ) : (
//                   <p>
//                     <span className="font-semibold">Click here Upload</span> or Drag and drop your files here
//                   </p>
//                 )}
//               </div>
//               {isPending ? null : <p className="text-xs text-zinc-500">only PDF</p>}
//             </div>
//           )}
//         </Dropzone>
//       </div>
//     </div>
//   );
// };

// export default Page;



"use client";

import { Progress } from "@/components/ui/progress";
import { useToast } from "@/components/ui/use-toast";
import { cn } from "@/lib/utils";
import { Image, Loader, MousePointerSquareDashed } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState, useTransition } from "react";
import Dropzone, { FileRejection } from "react-dropzone";
import axios from "axios";
import { BACKEND_URL } from "@/utils/constant";
import { useAuth } from "@/contexts/AuthContext";

const Page = () => {
  const { toast } = useToast();
  const [isDragOver, setIsDragOver] = useState<boolean>(false);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [isPending, startTransition] = useTransition();
  const router = useRouter();
  const { isLoggedIn } = useAuth();

  // Redirect to signin if user is not logged in
  useEffect(() => {
    if (!isLoggedIn) {
      toast({
        title: "SignIn Required",
        description: "Signin required to chat with the PDF.",
        variant: "destructive",
        className: "text-white",
      });
      router.push("/auth/signin");
    }
  }, [isLoggedIn, router, toast]);

  const onDropRejected = (rejectedFiles: FileRejection[]) => {
    const [file] = rejectedFiles;
    setIsDragOver(false);
    toast({
      title: "File Rejected",
      description: `File ${file.file.name} was rejected because it is not a valid supported file.`,
      variant: "destructive",
    });
  };

  // const onDropAccepted = async (acceptedFiles: File[]) => {
  //   setIsUploading(true);
  //   setUploadProgress(0);
  //   setIsDragOver(false);

  //   try {
  //     // 1. Create a local blob URL for the PDF (so we can show it immediately in the chat page)
  //     const pdfBlobUrl = URL.createObjectURL(acceptedFiles[0]);
  //     localStorage.setItem("pdfBlobUrl", pdfBlobUrl);
  //     localStorage.setItem("pdfFileName", acceptedFiles[0].name);

  //     // 2. Upload the file to your backend
  //     const formData = new FormData();
  //     formData.append("file", acceptedFiles[0]);

  //     const response = await axios.post(`${BACKEND_URL}/upload-doc`, formData, {
  //       headers: {
  //         Authorization: `Bearer ${localStorage.getItem("Token")}`,
  //         "Content-Type": "multipart/form-data",
  //       },
  //       onUploadProgress: (progressEvent) => {
  //         if (progressEvent.total) {
  //           const percentCompleted = Math.round(
  //             (progressEvent.loaded * 100) / progressEvent.total
  //           );
  //           setUploadProgress(percentCompleted);
  //         }
  //       },
  //     });

  //     // 3. Handle success
  //     setIsUploading(false);
  //     toast({
  //       title: "PDF uploaded successfully",
  //       description: `File ${acceptedFiles[0].name} was uploaded successfully.`,
  //       variant: "default",
  //     });

  //     // 4. If your server returns a document_id, store it for chat reference
  //     if (response.data && response.data.document_id) {
  //       localStorage.setItem("documentId", response.data.document_id);
  //     }

  //     // 5. Navigate to the chat page
  //     startTransition(() => {
  //       router.push("/chat");
  //     });
  //   } catch (error) {
  //     console.error("Upload error:", error);
  //     setIsUploading(false);
  //     toast({
  //       title: "Upload error",
  //       description: "An error occurred during upload.",
  //       className: "text-white",
  //       variant: "destructive",
  //     });
  //   }
  // };


  const onDropAccepted = async (acceptedFiles: File[]) => {
    setIsUploading(true);
    setUploadProgress(0);
    setIsDragOver(false);
  
    try {
      const formData = new FormData();
      formData.append("file", acceptedFiles[0]);
  
      const response = await axios.post(`${BACKEND_URL}/upload-doc`, formData, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("Token")}`,
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(percentCompleted);
          }
        },
      });
  
      setIsUploading(false);
      toast({
        title: "PDF uploaded successfully",
        description: `File ${acceptedFiles[0].name} was uploaded successfully`,
        variant: "default",
      });
  
      // Save document info to localStorage
      localStorage.setItem("pdfFileName", acceptedFiles[0].name);
      
      if (response.data && response.data.s3_key) {
        // If you want to store the full s3_key
        localStorage.setItem("pdfS3Key", response.data.s3_key);
      }
  
      // Navigate to chat page after successful upload
      startTransition(() => {
        router.push("/chat");
      });
    } catch (error) {
      console.error("Upload error:", error);
      setIsUploading(false);
      toast({
        title: "Upload error",
        description: "An error occurred during upload",
        className: "text-white",
        variant: "destructive",
      });
    }
  };
  return (
    <div
      className={cn(
        "relative h-full flex-1 my-16 w-full dark:border-2 rounded-xl bg-gray-900/5 p-2 ring-1 ring-inset ring-gray-900/10 flex justify-center flex-col items-center",
        {
          "ring-blue-900/25 bg-blue-900/10": isDragOver,
        }
      )}
    >
      <div className="relative flex flex-1 flex-col items-center justify-center w-full">
        <Dropzone
          onDropRejected={onDropRejected}
          onDropAccepted={onDropAccepted}
          accept={{
            "application/pdf": [".pdf"],
          }}
          onDragEnter={() => setIsDragOver(true)}
          onDragLeave={() => setIsDragOver(false)}
        >
          {({ getRootProps, getInputProps }) => (
            <div
              {...getRootProps()}
              className="flex flex-1 flex-col items-center justify-center w-full h-full"
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
                    <span className="font-semibold">Click here to Upload</span> or
                    Drag & Drop your files here
                  </p>
                )}
              </div>
              {isPending ? null : (
                <p className="text-xs text-zinc-500">Only PDF files supported</p>
              )}
            </div>
          )}
        </Dropzone>
      </div>
    </div>
  );
};

export default Page;
