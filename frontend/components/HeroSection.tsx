import { Button } from "@heroui/react";

import { ChevronRightIcon } from "@/components/icons";

const HeroSection = () => {
	return (
		<section className="py-12 md:py-20 text-center">
			<h1 className="text-4xl md:text-6xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-indigo-600 leading-tight max-w-4xl mx-auto">
				Treat Job Hunting Like a Sales Funnel
			</h1>

			<p className="text-xl md:text-2xl text-default-500 mb-10 max-w-3xl mx-auto">
				Track response rates, follow-ups, and conversions, just like a business. Be data-driven.
			</p>

			<div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
				<Button
					className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-6 text-lg h-auto"
					color="primary"
					endContent={<ChevronRightIcon size={20} />}
					onPress={() => {
						document
							.querySelector('[key="waitlist"]')
							?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
						setTimeout(() => {
							document.getElementById("email-input")?.focus();
							document
								.getElementById("email-input")
								?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
						}, 100);
					}}
				>
					Join the Waitlist
				</Button>

				<Button
					className="px-6 py-6 text-lg h-auto"
					variant="bordered"
					onPress={() => {
						document
							.querySelector('[key="developer"]')
							?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
						setTimeout(() => {
							document.getElementById("run_local")?.focus();
							document
								.getElementById("run_local")
								?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
							document.getElementById("request-setup-email-input")?.scrollIntoView({
								behavior: "smooth",
								block: "start",
								inline: "nearest"
							});
							document.getElementById("request-setup-session-email-input")?.focus();
							document
								.getElementById("request-setup-session-email-input")
								?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
						}, 100);
					}}
				>
					Run Locally
				</Button>
			</div>

			<div className="relative overflow-hidden rounded-xl border border-muted shadow-xl mx-auto max-w-5xl">
				<div className="bg-muted/50 absolute top-0 left-0 right-0 h-12 flex items-center px-4">
					<div className="flex space-x-2">
						<div className="h-3 w-3 rounded-full bg-red-500" />
						<div className="h-3 w-3 rounded-full bg-yellow-500" />
						<div className="h-3 w-3 rounded-full bg-green-500" />
					</div>
				</div>
				<div className="pt-12 pb-2">
					<img alt="jobba.help application screenshot" className="w-full h-auto" src="/sankey_diagram.png" />
					<div className="bg-background/80 backdrop-blur-sm py-2 px-4 text-center">
						<p className="text-sm text-default-600 font-medium">
							Application flow analysis — made with{" "}
							<span className="text-purple-600 font-bold">jobba.help</span>
						</p>
					</div>
				</div>
			</div>
		</section>
	);
};

export default HeroSection;
