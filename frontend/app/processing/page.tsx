"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Spinner from "../../components/spinner"; // Assuming you have a spinner component

const ProcessingPage = () => {
    const [isProcessing, setIsProcessing] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const interval = setInterval(async () => {
            try {
                console.log("Checking processing status...");
                const res = await fetch("http://localhost:8000/processing", {
                    method: "GET",
                    credentials: "include", // Ensure cookies are sent with the request
                });

                // Parse JSON response
                const result = await res.json();
                
                if (result.message === "Processing complete") {
                    console.log("Processing complete, redirecting...");
                    clearInterval(interval); // Stop the polling
                    router.push(result.redirect_url); // Redirect to the URL specified in the response
                }
            } catch (error) {
                console.error("Error checking processing status:", error);
            }
        }, 3000); // Poll every 3 seconds

        return () => clearInterval(interval); // Cleanup interval on unmount
    }, [router]);

    return (
        <div className="flex flex-col items-center justify-center h-screen">
            <h1 className="text-3xl font-semibold mb-4">We are processing your job!</h1>
            <Spinner />
            <p className="text-lg mt-4">
                Your job is being processed. You will be redirected to the download page once it&#39;s ready.
            </p>
        </div>
    );
};

export default ProcessingPage;