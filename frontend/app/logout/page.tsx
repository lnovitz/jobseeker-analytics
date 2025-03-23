"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function LogoutPage() {
	const router = useRouter();
	const apiUrl = process.env.NEXT_PUBLIC_API_URL!;

	useEffect(() => {
		async function performLogout() {
			try {
				// Call your logout API endpoint
				await fetch(`${apiUrl}/logout`, {
					method: "POST",
					credentials: "include"
				});
			} finally {
				// Redirect to login page regardless of success/failure
				router.push("/");
			}
		}

		performLogout();
	}, [router]);

	return <div>Logging you out...</div>;
}
