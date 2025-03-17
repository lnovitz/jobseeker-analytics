"use client";

import { useState, useEffect, Fragment } from "react";
import { useRouter } from "next/navigation";
import { useSearchParams } from "next/navigation";
import { CalendarDate } from "@internationalized/date";
import { Table, TableHeader, TableBody, TableColumn, TableRow, TableCell } from "@heroui/table";
import { Button, DatePicker, Modal, ModalHeader, ModalBody, ModalFooter } from "@heroui/react";
import { addToast } from "@heroui/toast";

import { DownloadIcon } from "@/components/icons";

interface Application {
	id?: string;
	company_name: string;
	application_status: string;
	received_at: string;
	subject: string;
	email_from: string;
}

export default function Dashboard() {
	const [showModal, setShowModal] = useState(true);
	const [startDate, setStartDate] = useState<CalendarDate | null>(null);
	const [selectedDate, setSelectedDate] = useState<CalendarDate | null>(null);
	const [sessionData, setSessionData] = useState(null);
	const searchParams = useSearchParams();
	const token = searchParams.get("token");
	const router = useRouter();
	const [data, setData] = useState<Application[]>([]);
	const [loading, setLoading] = useState(true);
	const [downloading, setDownloading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

	useEffect(() => {
		const fetchData = async () => {
			try {
				const response = await fetch(`${apiUrl}/get-emails`, {
					method: "GET",
					credentials: "include" // Include cookies for session management
				});

				if (!response.ok) {
					if (response.status === 404) {
						setError("No applications found");
					} else {
						throw new Error(`HTTP error! status: ${response.status}`);
					}
				}

				const result = await response.json();

				if (result.length === 0) {
					setError("No applications found");
				} else {
					setData(result);
				}
			} catch {
				setError("Failed to load applications");
			} finally {
				setLoading(false);
			}
		};

		fetchData();
		fetchSessionData();
	}, [router]);

	async function downloadCsv() {
		setDownloading(true);
		try {
			const response = await fetch(`${apiUrl}/process-csv`, {
				method: "GET",
				credentials: "include"
			});

			if (!response.ok) {
				let description = "Something went wrong. Please try again.";

				if (response.status === 429) {
					description = "Download limit reached. Please wait before trying again.";
				} else {
					description = "Please try again or contact help@jobba.help if the issue persists.";
				}

				addToast({
					title: "Failed to download CSV",
					description,
					color: "danger"
				});

				return;
			}

			// Create a download link to trigger the file download
			const blob = await response.blob();
			const link = document.createElement("a");
			const url = URL.createObjectURL(blob);
			link.href = url;
			link.download = `job_applications_${new Date().toISOString().split("T")[0]}.csv`;
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
			URL.revokeObjectURL(url);
		} catch {
			addToast({
				title: "Something went wrong",
				description: "Please try again",
				color: "danger"
			});
		} finally {
			setDownloading(false);
		}
	}

	const fetchSessionData = async () => {
		try {
			const response = await fetch("http://localhost:8000/api/session-data");
			const data = await response.json();
			setSessionData(data);
		} catch (error) {
			console.error("Error fetching session data:", error);
		}
	};

	const handleConfirm = async () => {
		console.log("Confirm button clicked");
		if (!selectedDate) {
			console.error("No start date selected");
			return;
		}
		try {
			setStartDate(selectedDate);
			setShowModal(false);
			// Save the start date
			await fetch("http://localhost:8000/api/save-start-date", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ start_date: selectedDate.toString() })
			});
			//Pass token directly in request (ignoring session storage rn)
			const emailResponse = await fetch("http://localhost:8000/api/fetch-emails", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Authorization: `Bearer ${token}`
				},
				body: JSON.stringify({})
			});
			const emailData = await emailResponse.json();
			console.log("Fetch Emails Response:", emailData);
			pollProcessingStatus();
		} catch (error) {
			console.error("Error in handleConfirm:", error);
		}
	};

	const pollProcessingStatus = async () => {
		const interval = setInterval(async () => {
			try {
				const response = await fetch("http://localhost:8000/processing");
				const text = await response.text();
				console.log("API Response:", text);
				const data = JSON.parse(text);
				if (data.message === "Processing complete") {
					clearInterval(interval);
					router.replace(data.redirect_url);
				}
			} catch (error) {
				console.error("Error parsing JSON:", error);
			}
		}, 5000); // Poll every 5 seconds
	};

	return (
		<div className="flex flex-col items-center justify-center text-center pt-64">
			{/* Modal */}
			<Modal isOpen={showModal} onClose={() => setShowModal(false)}>
				<ModalHeader>
					<h2 className="text-xl font-semibold text-black">
						Please enter the start date of your current job search:
					</h2>
				</ModalHeader>
				<ModalBody>
					<DatePicker
						className="mt-4 w-full p-2 border rounded-lg"
						value={selectedDate}
						onChange={(date) => setSelectedDate(date as CalendarDate)}
					/>
				</ModalBody>
				<ModalFooter>
					<Button
						className="mt-4 w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
						onPress={handleConfirm}
					>
						Confirm
					</Button>
				</ModalFooter>
			</Modal>

			<div className="flex items-center justify-between mb-4">
				<h1 className="text-2xl font-bold">Job Applications Dashboard</h1>
				<div className="flex gap-x-4">
					<Button
						color="success"
						isLoading={downloading}
						startContent={<DownloadIcon />}
						onPress={downloadCsv}
					>
						Download CSV
					</Button>
				</div>
			</div>

			{loading ? (
				<p>Loading applications...</p>
			) : error ? (
				<div className="text-red-500">
					<p>{error}</p>
					<Button color="warning" onPress={() => window.location.reload()}>
						Try again
					</Button>
				</div>
			) : (
				<div className="overflow-x-auto bg-white shadow-md rounded-lg">
					<Table aria-label="Applications Table">
						<TableHeader>
							<TableColumn>Company</TableColumn>
							<TableColumn>Status</TableColumn>
							<TableColumn>Received</TableColumn>
							<TableColumn>Subject</TableColumn>
							<TableColumn>Sender</TableColumn>
						</TableHeader>
						<TableBody>
							{data.map((item) => (
								<TableRow key={item.id || item.received_at}>
									<TableCell>{item.company_name || "--"}</TableCell>
									<TableCell>
										<span
											className={`px-2 py-1 rounded ${
												item.application_status.toLowerCase() === "rejected"
													? "bg-red-100 text-red-800"
													: "bg-green-100 text-green-800"
											}`}
										>
											{item.application_status || "--"}
										</span>
									</TableCell>
									<TableCell>{new Date(item.received_at).toLocaleDateString() || "--"}</TableCell>
									<TableCell className="max-w-[300px] truncate">{item.subject || "--"}</TableCell>
									<TableCell>{item.email_from || "--"}</TableCell>
								</TableRow>
							))}
						</TableBody>
					</Table>
				</div>
			)}
		</div>
	);
}
