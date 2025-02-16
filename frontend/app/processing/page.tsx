"use client";
import Spinner from "../../components/spinner";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const ProcessingPage = () => {

	const [data, setData] = useState<{ message: string } | null>(null);
        const [isProcessing, setIsProcessing] = useState(true);
        const router = useRouter(); // Hook for navigation

        async function fetchProcessingData() {
            try {
                console.log("Starting to fetch processing data...");
                const res = await fetch("http://localhost:8000/processing", {
                    method: "GET",
                    credentials: "include", // Include credentials if needed
                });

                // Check if response is successful (status 2xx)
                if (!res.ok) {
                    throw new Error("Failed to fetch processing data.");
                }

                const result = await res.json();
                setData(result);

                // If processing is done, redirect to success page
                if (result && result.message === "Processing complete") {
                    console.log("Processing complete, redirecting to success page...");
                    router.push("/success"); // Navigate to the success page
                }
            } catch (error) {
            
                setData({ message: "Error fetching data: " + error });
            }
        }

        useEffect(() => {
            fetchProcessingData();
        }, []);

	// The code above updated for connection.
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
