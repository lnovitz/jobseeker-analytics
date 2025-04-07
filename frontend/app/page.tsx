"use client";

import { useState } from "react";
import { Button, Card, Tabs, Tab } from "@heroui/react";

import { UsersIcon, LineChartIcon, CheckCircle2Icon, PlayIcon } from "@/components/icons";
import { Navbar } from "@/components/navbar"; // Import the Navbar
import Footer from "@/components/Footer";
import WaitlistForm from "@/components/WaitlistForm";
import DeveloperInfo from "@/components/DeveloperInfo";
import HeroSection from "@/components/HeroSection";

const Index = () => {
	const [tab, setTab] = useState("waitlist");

	const handleWatchDemo = () => {
		window.open("https://www.youtube.com/shorts/YT7qzTh2Q7A", "_blank");
	};

	return (
		<div className="flex flex-col min-h-screen">
			<main className="flex-grow bg-gradient-to-b from-background to-background/95">
				<Navbar /> {/* Place the Navbar at the top level */}
				<div className="container mx-auto px-4 py-6 space-y-16">
					<HeroSection />

					<div className="max-w-4xl mx-auto">
						<Tabs aria-label="Options" selectedKey={tab} onSelectionChange={(key) => setTab(key as string)}>
							<Tab key="waitlist" title="Join Waitlist">
								<div className="space-y-4 mt-4">
									<WaitlistForm />
								</div>
							</Tab>
							<Tab key="developer" id="run_local" title="Run Locally">
								<div className="space-y-4 mt-4">
									<DeveloperInfo />
								</div>
							</Tab>
						</Tabs>
					</div>

					<section className="max-w-5xl mx-auto py-8">
						<h2 className="text-3xl font-bold text-center mb-10">Why jobba.help?</h2>
						<div className="grid md:grid-cols-3 gap-8">
							<Card>
								<div className="p-6">
									<LineChartIcon className="text-purple-500 mb-4" size={48} />
									<h3 className="text-xl font-semibold mb-2">Data-driven Job Search</h3>
									<p className="text-default-500">
										Track application statistics like response rates and follow-ups to optimize your
										approach.
									</p>
								</div>
							</Card>

							<Card>
								<div className="p-6">
									<CheckCircle2Icon className="text-purple-500 mb-4" size={48} />
									<h3 className="text-xl font-semibold mb-2">Automated Tracking</h3>
									<p className="text-default-500">
										No more spreadsheets. We automatically track your applications and their
										statuses.
									</p>
								</div>
							</Card>

							<Card>
								<div className="p-6">
									<UsersIcon className="text-purple-500 mb-4" size={48} />
									<h3 className="text-xl font-semibold mb-2">Community Support</h3>
									<p className="text-default-500">
										Join a community of job seekers sharing strategies and success stories.
									</p>
								</div>
							</Card>
						</div>
					</section>

					<section className="max-w-3xl mx-auto bg-secondary/50 rounded-lg p-8 flex flex-col items-center text-center">
						<h2 className="text-2xl font-bold mb-4">Watch a Quick Demo</h2>
						<p className="text-default-600 mb-6">See how jobba.help transforms your job search approach</p>
						<Button
							className="bg-purple-600 hover:bg-purple-700"
							color="primary"
							startContent={<PlayIcon size={16} />}
							variant="solid"
							onPress={handleWatchDemo}
						>
							Watch Demo
						</Button>
					</section>
				</div>
			</main>

			<Footer />
		</div>
	);
};

export default Index;
