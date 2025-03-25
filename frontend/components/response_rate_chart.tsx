"use client";
import { BarChart, Bar, XAxis, YAxis, Cell, ResponsiveContainer, Tooltip, CartesianGrid } from "recharts";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface ResponseData {
	title: string;
	rate: number;
}

// const data: ResponseData[] = [
// 	{ title: "Software Engineer", rate: 72 },
// 	{ title: "Product Manager", rate: 68 },
// 	{ title: "Data Scientist", rate: 65 },
// 	{ title: "UX Designer", rate: 58 },
// 	{ title: "DevOps Engineer", rate: 70 },
// 	{ title: "test", rate: 80 },
// ];

const BLUE_COLOR = "#3b82f6";

export default function JobTitleResponseChart() {
	const router = useRouter();
	const [activeIndex, setActiveIndex] = useState<number | null>(null);
	const [data, setData] = useState<ResponseData[]>([]);


	const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

	useEffect(() => {
		const fetchData = async () => {
			try {
				const response = await fetch(`${apiUrl}/get-response-rate`, {
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

				if (result.length === 0) {
					// No data found
				} else {
					setData(result);
				}
			} catch {
				// Failed to load data
			} finally {
				// Set loading to false
			}
		};

		fetchData();
	}, [router]);

	return (
		<div className="bg-gray p-6 rounded-xl border border-[#1e293b]">
			<div className="flex justify-between items-center mb-6">
				<h2 className="text-white text-xl font-semibold">Response Rate based on Job Titles</h2>
			</div>

			<div className="h-[300px]">
				<ResponsiveContainer height="100%" width="100%">
					<BarChart
						data={data}
						margin={{ top: 5, right: 20, left: 0, bottom: 60 }}
						onMouseLeave={() => setActiveIndex(null)}
					>
						<defs>
							<linearGradient id="barGradient" x1="0" x2="0" y1="0" y2="1">
								<stop offset="0%" stopColor="#60a5fa" /> {/* Lighter blue */}
								<stop offset="100%" stopColor={BLUE_COLOR} /> {/* Your exact blue */}
							</linearGradient>
						</defs>

						<YAxis
							axisLine={{ stroke: "#334155" }}
							domain={[0, 100]}
							tick={{ fill: "#94a3b8", fontSize: 12 }}
							tickLine={{ stroke: "#334155" }}
							type="number"
						/>

						<CartesianGrid horizontal={true} stroke="#1e293b" strokeDasharray="3 3" vertical={false} />

						<XAxis
							angle={-45}
							axisLine={{ stroke: "#334155" }}
							dataKey="title"
							height={30}
							interval={0}
							textAnchor="end"
							tick={{ fill: "#e2e8f0", fontSize: 12 }}
							tickLine={{ stroke: "#334155" }}
							type="category"
						/>

						<Tooltip
							contentStyle={{
								background: "#1e293b",
								borderColor: BLUE_COLOR, // Blue border to match
								borderRadius: "6px",
								color: "#f8fafc"
							}}
							cursor={{ fill: "rgba(59, 130, 246, 0.1)" }} // Blue tint
							formatter={(value: number) => [`${value}%`, "Response Rate"]}
						/>

						<Bar
							animationDuration={1000}
							dataKey="rate"
							name="Response Rate"
							radius={[4, 4, 0, 0]}
							onMouseEnter={(_, index) => setActiveIndex(index)}
						>
							{data.map((entry, index) => (
								<Cell
									key={`cell-${index}`}
									fill={index === activeIndex ? "url(#barGradient)" : BLUE_COLOR}
									stroke={index === activeIndex ? "#93c5fd" : "none"} // Light blue border on hover
									strokeWidth={index === activeIndex ? 2 : 0}
								/>
							))}
						</Bar>
					</BarChart>
				</ResponsiveContainer>
			</div>
		</div>
		
	);
}
