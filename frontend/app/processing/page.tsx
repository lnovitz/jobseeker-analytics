"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { addToast } from "@heroui/react";

import Spinner from "../../components/spinner";

import { checkAuth } from "@/utils/auth";

const ProcessingPage = () => {
	const router = useRouter();
	const apiUrl = process.env.NEXT_PUBLIC_API_URL!;

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
			<p className="text-lg mt-4">
				Your job is being processed. You will be redirected to the download page once it&#39;s ready.
			</p>
		</div>
	);
};

export default ProcessingPage;
