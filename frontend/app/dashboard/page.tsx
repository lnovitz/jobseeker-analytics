"use client";

import React from "react";
import { Table, TableHeader, TableBody, TableColumn, TableRow, TableCell } from "@heroui/table";
import { Select, SelectItem } from "@heroui/react";
import { Button } from "@heroui/react";

export const dates = [
	{ key: "30-days", label: "30 days" },
	{ key: "60-days", label: "60 days" },
	{ key: "90-days", label: "90 days" },
	{ key: "6-months", label: "6 months" },
	{ key: "9-months", label: "9 months" },
	{ key: "1-year", label: "1 year" },
	{ key: "2-years", label: "2 years" },
	{ key: "3-years", label: "3 years" }
];

export default function Dashboard() {
	const apiUrl = process.env.NEXT_PUBLIC_API_URL!;
	// Mock data for the table
	const data = [
		{
			company_name: "Company A",
			application_status: "Pending",
			received_at: "2025-03-01",
			subject: "Software Engineer"
		},
		{
			company_name: "Company B",
			application_status: "Accepted",
			received_at: "2025-03-02",
			subject: "Product Manager"
		},
		{
			company_name: "Company C",
			application_status: "Rejected",
			received_at: "2025-03-03",
			subject: "Data Analyst"
		}
	];

	// Columns for the table
	const columns = [
		{ key: "company_name", label: "Company Name" },
		{ key: "application_status", label: "Application Status" },
		{ key: "received_at", label: "Received At" },
		{ key: "subject", label: "Subject" }
	];

	// Function to get data for each cell
	const getKeyValue = (item: any, columnKey: string) => {
		return item[columnKey] || "--"; // Safely handle missing data
	};

	return (
		<div className="p-6">
			<div className="flex flex-col md:flex-row justify-between items-start md:items-center mt-4 gap-4">
				<div className="flex-shrink-0">
					<h2 className="text-xl md:text-3xl font-bold text-foreground mb-4 md:mb-0">
						Your Job Application Data
					</h2>
				</div>

				<div className="flex flex-col md:flex-row justify-end items-stretch md:items-center gap-4 w-full md:w-auto">
					<Select
						className="min-w-[200px] flex-1 h-12"
						classNames={{
							trigger: "h-full text-sm px-4",
							label: "text-xs",
							value: "text-sm"
						}}
						defaultSelectedKeys={["90-days"]}
						label="Start Date"
						labelPlacement="inside"
					>
						{dates.map((date) => (
							<SelectItem key={date.key} className="text-sm">
								{date.label}
							</SelectItem>
						))}
					</Select>

					<Button
						className="min-w-[200px] flex-1 h-14 truncate text-white text-base"
						color="primary"
						data-testid="sync-new-data"
						radius="lg"
					>
						Sync New Data
					</Button>

					<Button
						download
						as="a"
						className="min-w-[200px] flex-1 h-14 truncate text-white text-base"
						color="success"
						data-testid="download-csv"
						href={`${apiUrl}/download-file`}
						radius="lg"
					>
						Download CSV
					</Button>
				</div>
			</div>

			<div className="overflow-x-auto bg-white shadow-md rounded-lg mt-6">
				<Table aria-label="Example table with mock data" data-testid="jobs-table">
					<TableHeader>
						{/* Render table columns */}
						{columns.map((column) => (
							<TableColumn key={column.key}>{column.label}</TableColumn>
						))}
					</TableHeader>
					<TableBody>
						{data.length > 0 ? (
							data.map((item, index) => (
								<TableRow key={index}>
									{/* Render a TableCell for each column */}
									{columns.map((column) => (
										<TableCell key={column.key}>{getKeyValue(item, column.key)}</TableCell>
									))}
								</TableRow>
							))
						) : (
							<TableRow>
								{/* Empty row that spans all 4 columns */}
								<TableCell className="p-4 text-center" colSpan={4}>
									No data available
								</TableCell>
							</TableRow>
						)}
					</TableBody>
				</Table>
			</div>
		</div>
	);
}
