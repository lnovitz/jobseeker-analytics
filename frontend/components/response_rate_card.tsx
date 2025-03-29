"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

import { ClockIcon } from "@/components/icons";

export default function ResponseRateCard() {
	const [lastUpdated, setLastUpdated] = useState<string>("");

	const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/";
	const [value, setValue] = useState(null);
	const router = useRouter();

	useEffect(() => {
		const fetchData = async () => {
			try {
				const response = await fetch(`${apiUrl}/user-response-rate`, {
					method: "GET",
					credentials: "include" // Include cookies for session management
				});

				if (!response.ok) {
					if (response.status === 404) {
						// No data found
					} else {
						throw new Error(`HTTP error! status: ${response.status}`);
					}
				}
				const result = await response.json();
				// eslint-disable-next-line no-console
				console.log(result.value);

				if (result.length === 0) {
					// No data found
				} else {
					setValue(result.value);
				}
				// Set the last updated time (assuming the API provides a timestamp)
				if (result.lastUpdated) {
					setLastUpdated(formatDate(new Date(result.lastUpdated)));
				} else {
					// Fallback to the current time if no timestamp is provided
					setLastUpdated(formatDate(new Date()));
				}
			} catch {
				// Failed to load data
			} finally {
				// Set loading to false
			}
		};

		fetchData();
	}, [router]);

	// Helper function to format the date
	const formatDate = (date: Date): string => {
		const now = new Date();
		const yesterday = new Date();
		yesterday.setDate(now.getDate() - 1);

		const isToday = date.toDateString() === now.toDateString();
		const isYesterday = date.toDateString() === yesterday.toDateString();

		const timeFormatter = new Intl.DateTimeFormat("en-US", {
			hour: "numeric",
			minute: "numeric",
			hour12: true
		});

		if (isToday) {
			return `Today, ${timeFormatter.format(date)}`;
		} else if (isYesterday) {
			return `Yesterday, ${timeFormatter.format(date)}`;
		} else {
			const dateFormatter = new Intl.DateTimeFormat("en-US", {
				month: "short",
				day: "numeric"
			});
			return `${dateFormatter.format(date)}, ${timeFormatter.format(date)}`;
		}
	};

	return (
		<div className="flex flex-col justify-center bg-gray-100 dark:bg-gray-800 shadow-md rounded-lg p-7 md:h-[350px]">
			<p className="text-8xl font-bold text-blue-600 dark:text-blue-400 mb-1">{value}%</p>
			<h3 className="text-xl font-medium text-gray-700 dark:text-gray-300 mb-4">% Response Rate</h3>
			<div className="flex gap-2 text-base text-gray-500 dark:text-gray-400">
				<ClockIcon className="self-center" />
				<span>Last Updated: {lastUpdated}</span>
			</div>
		</div>
	);
}
