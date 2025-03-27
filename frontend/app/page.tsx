"use client";

import { EmailRegistration } from "@/components/EmailRegistration";

export default function Home() {
	return (
		<div className="min-h-screen bg-gray-50">
			<nav className="bg-white shadow-sm">
				<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
					<div className="flex justify-between h-16 items-center">
						<div className="flex-shrink-0">
							<h1 className="text-xl font-bold text-gray-900">Jobba</h1>
						</div>
					</div>
				</div>
			</nav>

			<main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
				<div className="bg-white shadow rounded-lg">
					<EmailRegistration />
				</div>
			</main>
		</div>
	);
}
