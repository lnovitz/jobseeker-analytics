"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { addToast, Progress } from "@heroui/react";

import Spinner from "../../components/spinner";

import { checkAuth } from "@/utils/auth";

const ProcessingPage = () => {
	const router = useRouter();
	const apiUrl = process.env.NEXT_PUBLIC_API_URL!;
	const [progress, setProgress] = useState(0);

	useEffect(() => {
		const process = async () => {
			// Check if user is logged in
			const isAuthenticated = await checkAuth(apiUrl);
			if (!isAuthenticated) {
				addToast({
					title: "You need to be logged in to access this page.",
					color: "warning"
				});
				router.push("/");
				return;
			}

			const interval = setInterval(async () => {
				try {
					const res = await fetch(`${apiUrl}/processing`, {
						method: "GET",
						credentials: "include"
					});

					const result = await res.json();
					if (result.total_emails === 0) {
						setProgress(100);
					} else {
						setProgress(100 * (result.processed_emails / result.total_emails));
					}
					if (result.message === "Processing complete") {
						clearInterval(interval);
						router.push("/dashboard");
					}
				} catch {
					router.push("/logout");
				}
			}, 3000);

			return () => clearInterval(interval);
		};

		process();
	}, [router]);

	return (
		<div className="flex flex-col items-center justify-center h-screen">
			<h1 className="text-3xl font-semibold mb-4">We are processing your job!</h1>
			<Spinner />
			<div className="mb-3" />
			<Progress
				aria-label="Downloading..."
				className="max-w-md"
				showValueLabel={true}
				size="md"
				value={progress}
			/>
			<div className="mb-3" />
			<p className="text-lg mt-4">
				Your job is being processed. You will be redirected to the download page once it&#39;s ready.
			</p>
		</div>
	);
};

export default ProcessingPage;
