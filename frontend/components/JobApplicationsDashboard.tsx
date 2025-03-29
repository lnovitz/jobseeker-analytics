"use client";

import React, { useState, useEffect } from "react";
import { Table, TableHeader, TableBody, TableColumn, TableRow, TableCell } from "@heroui/table";
import {
	Button,
	Dropdown,
	DropdownItem,
	DropdownMenu,
	DropdownSection,
	DropdownTrigger,
	Modal,
	ModalBody,
	ModalContent,
	ModalFooter,
	ModalHeader,
	Tooltip
} from "@heroui/react";

import { DownloadIcon, SortIcon, TrashIcon } from "@/components/icons";

export interface Application {
	id?: string;
	company_name: string;
	application_status: string;
	received_at: string;
	job_title: string;
	subject: string;
	email_from: string;
}

interface JobApplicationsDashboardProps {
	title?: string;
	data: Application[];
	loading: boolean;
	downloading: boolean;
	onDownloadCsv: () => void;
	onDownloadSankey: () => void;
	initialSortKey?: string;
	extraHeader?: React.ReactNode;
}

// Load sort key from localStorage or use default
const getInitialSortKey = (key: string) => {
	return typeof window !== "undefined" ? localStorage.getItem("sortKey") || key : key;
};

export default function JobApplicationsDashboard({
	title = "Job Applications Dashboard",
	data,
	loading,
	downloading,
	onDownloadCsv,
	onDownloadSankey,
	initialSortKey = "Date (Newest)",
	extraHeader
}: JobApplicationsDashboardProps) {
	const [sortedData, setSortedData] = useState<Application[]>([]);
	const [selectedKeys, setSelectedKeys] = useState(new Set([getInitialSortKey(initialSortKey)]));
	const [showDelete, setShowDelete] = useState(false);

	const selectedValue = React.useMemo(() => Array.from(selectedKeys).join(", ").replace(/_/g, ""), [selectedKeys]);

	// Sort data based on selected key
	useEffect(() => {
		const sortData = () => {
			const sorted = [...data];
			const sortKey = Array.from(selectedKeys)[0];

			switch (sortKey) {
				case "Date (Newest)":
					sorted.sort((a, b) => new Date(b.received_at).getTime() - new Date(a.received_at).getTime());
					break;
				case "Date (Oldest)":
					sorted.sort((a, b) => new Date(a.received_at).getTime() - new Date(b.received_at).getTime());
					break;
				case "Company":
					sorted.sort((a, b) => a.company_name.localeCompare(b.company_name));
					break;
				case "Job Title":
					sorted.sort((a, b) => a.job_title.localeCompare(b.job_title));
					break;
				case "Status":
					sorted.sort((a, b) => a.application_status.localeCompare(b.application_status));
					break;
				default:
					break;
			}
			setSortedData(sorted);
		};

		if (data.length > 0) {
			sortData();
		} else {
			setSortedData([]);
		}
	}, [selectedKeys, data]);

	// Handle sorting selection change and store it in localStorage
	const handleSortChange = (keys: Set<string>) => {
		const sortKey = Array.from(keys)[0];
		localStorage.setItem("sortKey", sortKey);
		setSelectedKeys(new Set([sortKey]));
	};

	return (
		<div className="p-6">
			{extraHeader}
			<Modal isOpen={showDelete} onOpenChange={(isOpen) => setShowDelete(isOpen)}>
				<ModalContent>
					{(onClose) => (
						<>
							<ModalHeader className="flex flex-col gap-1">Confirm Removal</ModalHeader>
							<ModalBody>
								<p>
									Are you sure you want to remove this row? Every job application impacts your
									metrics, so it's important to keep all records unless we accidentally made a mistake
									and picked up a non-job-related record.
								</p>
							</ModalBody>
							<ModalFooter>
								<Button color="default" variant="ghost" onPress={onClose}>
									Cancel
								</Button>
								<Button color="danger" onPress={onClose}>
									Yes, remove it
								</Button>
							</ModalFooter>
						</>
					)}
				</ModalContent>
			</Modal>
			<div className="flex items-center justify-between mb-4">
				<h1 className="text-2xl font-bold">{title}</h1>
				<div className="flex gap-x-4">
					<Dropdown>
						<DropdownTrigger>
							<Button
								className="pl-3"
								color="primary"
								isDisabled={!data || data.length === 0}
								startContent={<SortIcon />}
								variant="bordered"
							>
								{selectedValue}
							</Button>
						</DropdownTrigger>
						<DropdownMenu
							disallowEmptySelection
							aria-label="Single selection example"
							selectedKeys={selectedKeys}
							selectionMode="single"
							variant="flat"
							onSelectionChange={(keys) => handleSortChange(keys as Set<string>)}
						>
							<DropdownSection title="Sort By">
								<DropdownItem key="Date (Newest)">Date Received (Newest First)</DropdownItem>
								<DropdownItem key="Date (Oldest)">Date Received (Oldest First)</DropdownItem>
								<DropdownItem key="Company">Company (A-Z)</DropdownItem>
								<DropdownItem key="Job Title">Job Title (A-Z)</DropdownItem>
								<DropdownItem key="Status">Application Status</DropdownItem>
							</DropdownSection>
						</DropdownMenu>
					</Dropdown>
					<Button
						color="primary"
						isDisabled={!data || data.length === 0}
						isLoading={downloading}
						startContent={<DownloadIcon />}
						onPress={onDownloadSankey}
					>
						Download Sankey Diagram
					</Button>
					<Button
						color="success"
						isDisabled={!data || data.length === 0}
						isLoading={downloading}
						startContent={<DownloadIcon />}
						onPress={onDownloadCsv}
					>
						Download CSV
					</Button>
				</div>
			</div>

			{loading ? (
				<p>Loading applications...</p>
			) : (
				<div className="overflow-x-auto bg-white shadow-md rounded-lg">
					<Table aria-label="Applications Table">
						<TableHeader>
							<TableColumn>Company</TableColumn>
							<TableColumn>Status</TableColumn>
							<TableColumn>Received</TableColumn>
							<TableColumn>Job Title</TableColumn>
							<TableColumn>Subject</TableColumn>
							<TableColumn>Sender</TableColumn>
							<TableColumn>Actions</TableColumn>
						</TableHeader>
						<TableBody>
							{sortedData.map((item) => (
								<TableRow
									key={item.id || item.received_at}
									className="hover:bg-default-100 transition-colors"
								>
									<TableCell>{item.company_name || "--"}</TableCell>
									<TableCell>
										<span
											className={`inline-flex items-center justify-center px-2 py-1 rounded ${
												item.application_status.toLowerCase() === "rejected"
													? "bg-red-100 text-red-800"
													: "bg-green-100 text-green-800"
											}`}
										>
											{item.application_status || "--"}
										</span>
									</TableCell>
									<TableCell>{new Date(item.received_at).toLocaleDateString() || "--"}</TableCell>
									<TableCell>{item.job_title || "--"}</TableCell>
									<TableCell className="max-w-[300px] truncate">{item.subject || "--"}</TableCell>
									<TableCell>{item.email_from || "--"}</TableCell>
									<TableCell className="text-center">
										<Tooltip content="Remove">
											<Button
												isIconOnly
												size="sm"
												variant="light"
												onPress={() => setShowDelete(!showDelete)}
											>
												<TrashIcon className="text-gray-800 dark:text-gray-300" />
											</Button>
										</Tooltip>
									</TableCell>
								</TableRow>
							))}
						</TableBody>
					</Table>
				</div>
			)}
		</div>
	);
}
