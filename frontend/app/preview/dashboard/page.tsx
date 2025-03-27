"use client";

import React, { useState, useEffect } from "react";
import { Modal, ModalBody, ModalContent, ModalFooter, ModalHeader, useDisclosure, Button } from "@heroui/react";
import { useRouter } from "next/navigation";

import JobApplicationsDashboard, { Application } from "@/components/JobApplicationsDashboard";
import { mockData } from "@/utils/mockData";

export default function PreviewDashboard() {
	const { isOpen, onOpen, onClose } = useDisclosure();
	const [data, setData] = useState<Application[]>([]);
	const [loading, setLoading] = useState(true);
	const [downloading, setDownloading] = useState(false);
	const router = useRouter();

	useEffect(() => {
		setLoading(true);
		const dataTimeout = setTimeout(() => {
			setData(mockData);
			setLoading(false);
		}, 1500);

		const openTimeout = setTimeout(() => {
			onOpen();
		}, 10000);

		return () => {
			clearTimeout(dataTimeout);
			clearTimeout(openTimeout);
		};
	}, [onOpen]);

	// Handle CSV download
	async function downloadCsv() {
		setDownloading(true);
		// Mock CSV generation (no api call)
		const mockCsvContent =
			"Company,Status,Received,Job Title,Subject,Sender\n" +
			mockData
				.map(
					(item) =>
						`${item.company_name},${item.application_status},${new Date(item.received_at).toLocaleDateString()},${item.job_title},${item.subject},${item.email_from}`
				)
				.join("\n");

		const blob = new Blob([mockCsvContent], { type: "text/csv" });
		const link = document.createElement("a");
		const url = URL.createObjectURL(blob);
		link.href = url;
		link.download = `job_applications_${new Date().toISOString().split("T")[0]}.csv`;
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
		URL.revokeObjectURL(url);
		setDownloading(false);
	}

	// Handle Sankey download
	async function downloadSankey() {
		setDownloading(true);
		// Mock Sankey generation (no api call)
		// Download frontend/public/sankey_diagram.png
		const link = document.createElement("a");
		link.href = "/sankey_diagram.png";
		link.download = `sankey_diagram_${new Date().toISOString().split("T")[0]}.png`;
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
		setDownloading(false);
	}

	const PromoModal = (
		<Modal backdrop="blur" isOpen={isOpen} size="xl" onClose={onClose}>
			<ModalContent>
				{(onClose) => (
					<>
						<ModalHeader className="flex flex-col gap-1">
							Enjoying the preview? Join the waitlist!
						</ModalHeader>
						<ModalBody>
							<p>
								By joining the waitlist, you'll receive updates on new features and an invitation to
								signup when we launch outside of beta.
							</p>
						</ModalBody>
						<ModalFooter>
							<Button color="danger" variant="light" onPress={onClose}>
								Close
							</Button>
							<Button color="primary" onPress={() => router.push("/")}>
								Sign Up Now
							</Button>
						</ModalFooter>
					</>
				)}
			</ModalContent>
		</Modal>
	);

	return (
		<JobApplicationsDashboard
			data={data}
			downloading={downloading}
			extraHeader={PromoModal}
			loading={loading}
			title="Preview Dashboard"
			onDownloadCsv={downloadCsv}
			onDownloadSankey={downloadSankey}
		/>
	);
}
